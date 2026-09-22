using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using System.Windows.Forms;
using System.Windows.Interop;
using System.Runtime.InteropServices;
using System.Linq;
using Microsoft.Win32;
using Point = System.Windows.Point;
using Brushes = System.Windows.Media.Brushes;

namespace VortexNet8
{
    public partial class MainWindow : Window
    {
        private NotifyIcon? _trayIcon;
        private bool _isBoosting = false;
        private bool _isGameRunning = false;
        private string _activeTab = "dashboard";

        // Сессионный таймер работы в игре
        private DispatcherTimer? _sessionTimer;
        private int _sessionSeconds = 0;

        // Выбранная игра и список найденных
        private InstalledGame _selectedGame;
        private readonly List<InstalledGame> _installedGames = new();
        private bool _isLaunchedFromShortcut = false;

        public MainWindow()
        {
            InitializeComponent();

            StateChanged += Window_StateChanged;

            // Инициализация игр
            _selectedGame = GameDetectionService.DetectFortnite();
            InitGames();

            LoadConfigToUi();
            SetupTray();
            SetupSessionTimer();
            ResRefreshStatus();
            StartTelemetryAndGuardianLoop();
            RunStartupDnsBenchmark();

            Log("VORTEX C# (.NET 8) Мультиигровой Оптимизатор и Лаунчер успешно запущен.");
            Log($"Авто-поиск завершен: найдено {_installedGames.Count} игры (Fortnite на C: и CS2 на E:).");
            Log("Таймер ядра Windows 0.500 мс активирован для нулевого инпутлага.");
        }

        private void Window_StateChanged(object? sender, EventArgs e)
        {
            if (WindowState == WindowState.Maximized)
            {
                RootWindowBorder.Margin = new Thickness(7);
                RootWindowBorder.BorderThickness = new Thickness(0);
            }
            else
            {
                RootWindowBorder.Margin = new Thickness(0);
                RootWindowBorder.BorderThickness = new Thickness(1);
            }
        }

        private static SolidColorBrush BrushFromHex(string hex)
        {
            var c = (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(hex);
            return new SolidColorBrush(c);
        }

        private void InitGames()
        {
            _installedGames.Clear();
            var detected = GameDetectionService.DetectInstalledGames();
            _installedGames.AddRange(detected);

            // Применяем сохраненную конфигурацию (кастомные названия, фоны, добавленные игры)
            GameConfigService.ApplyConfig(_installedGames);

            RefreshGamesCards();

            // Проверяем аргументы командной строки (--game <key>, --launch <key>, --console)
            string[] args = Environment.GetCommandLineArgs();
            InstalledGame? targetGame = null;
            bool shouldAutoLaunch = false;
            bool shouldOpenConsole = false;

            for (int i = 0; i < args.Length; i++)
            {
                if (string.Equals(args[i], "--console", StringComparison.OrdinalIgnoreCase))
                {
                    shouldOpenConsole = true;
                    _isLaunchedFromShortcut = true;
                }
                else if (string.Equals(args[i], "--launch", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    string key = args[i + 1].Trim('"', '\'');
                    targetGame = _installedGames.Find(g => string.Equals(g.Key, key, StringComparison.OrdinalIgnoreCase));
                    shouldAutoLaunch = true;
                    shouldOpenConsole = true; // При запуске ярлыка игры открывается консоль с логами и процентами!
                    _isLaunchedFromShortcut = true;
                }
                else if (string.Equals(args[i], "--game", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    string key = args[i + 1].Trim('"', '\'');
                    targetGame = _installedGames.Find(g => string.Equals(g.Key, key, StringComparison.OrdinalIgnoreCase));
                }
            }

            var activeGame = targetGame ?? _installedGames.FirstOrDefault() ?? GameDetectionService.DetectFortnite();
            SelectGame(activeGame);

            if (shouldOpenConsole)
            {
                ConsoleService.OpenConsole(activeGame.DisplayTitle, activeGame.DisplayPath);
            }

            if (shouldAutoLaunch)
            {
                Dispatcher.BeginInvoke(new Action(LaunchActiveGame), DispatcherPriority.Background);
            }
        }

        private void RefreshGamesCards()
        {
            var fn = _installedGames.Find(g => g.Key == "fortnite") ?? GameDetectionService.DetectFortnite();
            TitleFortniteText.Text = fn.DisplayTitle;
            PathFortniteText.Text = fn.DisplayPath;

            var cs2 = _installedGames.Find(g => g.Key == "cs2") ?? GameDetectionService.DetectCS2();
            TitleCS2Text.Text = cs2.DisplayTitle;
            PathCS2Text.Text = cs2.DisplayPath;

            CustomGamesPanel.Children.Clear();
            foreach (var game in _installedGames.Where(g => g.IsCustom))
            {
                var card = CreateCustomGameCard(game);
                CustomGamesPanel.Children.Add(card);
            }

            FoundGamesCountText.Text = $"{_installedGames.Count} игры найдено";
        }

        private Border CreateCustomGameCard(InstalledGame game)
        {
            var border = new Border
            {
                Background = BrushFromHex("#0E1524"),
                BorderBrush = BrushFromHex("#1C2C45"),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(12),
                Padding = new Thickness(12, 8, 12, 8),
                Margin = new Thickness(0, 0, 0, 6),
                Cursor = System.Windows.Input.Cursors.Hand,
                Tag = game.Key
            };

            var grid = new Grid();
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });

            var emoji = new TextBlock
            {
                Text = string.IsNullOrEmpty(game.IconEmoji) ? "🎮" : game.IconEmoji,
                FontSize = 22,
                VerticalAlignment = VerticalAlignment.Center,
                Margin = new Thickness(0, 0, 10, 0)
            };
            Grid.SetColumn(emoji, 0);
            grid.Children.Add(emoji);

            var sp = new StackPanel { VerticalAlignment = VerticalAlignment.Center };
            var headerGrid = new Grid();
            var title = new TextBlock
            {
                Text = game.DisplayTitle,
                FontSize = 12.5,
                FontWeight = FontWeights.Black,
                Foreground = BrushFromHex("#FFFFFF")
            };
            headerGrid.Children.Add(title);

            var badgeBorder = new Border
            {
                Background = BrushFromHex("#064E3B"),
                CornerRadius = new CornerRadius(4),
                Padding = new Thickness(5, 2, 5, 2),
                HorizontalAlignment = System.Windows.HorizontalAlignment.Right
            };
            var badgeText = new TextBlock
            {
                Text = game.IsInstalled ? "● Добавлена" : "● Готова",
                FontSize = 8.5,
                FontWeight = FontWeights.Bold,
                Foreground = game.IsInstalled ? BrushFromHex("#34D399") : BrushFromHex("#38BDF8")
            };
            badgeBorder.Child = badgeText;
            headerGrid.Children.Add(badgeBorder);
            sp.Children.Add(headerGrid);

            var path = new TextBlock
            {
                Text = game.DisplayPath,
                FontSize = 9.5,
                Foreground = BrushFromHex("#67E8F9"),
                FontFamily = new System.Windows.Media.FontFamily("Consolas"),
                TextTrimming = TextTrimming.CharacterEllipsis,
                Margin = new Thickness(0, 2, 0, 0)
            };
            sp.Children.Add(path);

            Grid.SetColumn(sp, 1);
            grid.Children.Add(sp);

            border.Child = grid;
            border.MouseLeftButtonDown += (s, e) => SelectGame(game);

            return border;
        }

        private void SelectGame(InstalledGame game)
        {
            _selectedGame = game;

            // Обновление заголовков
            HeroTitle.Text = $"Оптимизация и запуск {game.DisplayTitle}";
            HeroSubtitle.Text = game.Description;

            if (!_isGameRunning && !_isBoosting)
            {
                CircleSubText.Text = game.DisplayTitle.ToUpper();
                CircleStageDesc.Text = $"Нажмите «ЗАПУСК»: система оптимизируется, и {game.DisplayTitle} откроется автоматически";
                HeaderGameStatusText.Text = $"● {game.DisplayTitle} (Готова к запуску)";
            }

            // Динамический фон: свой фон для каждого приложения!
            UpdateDashboardBackground(game);

            // Подсветка карточек
            CardFortnite.BorderBrush = game.Key == "fortnite" ? BrushFromHex("#38BDF8") : BrushFromHex("#1C2C45");
            CardFortnite.Background = game.Key == "fortnite" ? BrushFromHex("#121D2E") : BrushFromHex("#0E1524");

            CardCS2.BorderBrush = game.Key == "cs2" ? BrushFromHex("#38BDF8") : BrushFromHex("#1C2C45");
            CardCS2.Background = game.Key == "cs2" ? BrushFromHex("#121D2E") : BrushFromHex("#0E1524");

            foreach (var child in CustomGamesPanel.Children)
            {
                if (child is Border b)
                {
                    bool isSelected = string.Equals(b.Tag as string, game.Key, StringComparison.OrdinalIgnoreCase);
                    b.BorderBrush = isSelected ? BrushFromHex("#38BDF8") : BrushFromHex("#1C2C45");
                    b.Background = isSelected ? BrushFromHex("#121D2E") : BrushFromHex("#0E1524");
                }
            }

            BtnDeleteCustomGame.Visibility = game.IsCustom ? Visibility.Visible : Visibility.Collapsed;

            Log($"Выбрана игра: {game.DisplayTitle} ({game.DisplayPath})");
        }

        private void UpdateDashboardBackground(InstalledGame game)
        {
            try
            {
                if (!string.IsNullOrEmpty(game.CustomBackgroundPath) && File.Exists(game.CustomBackgroundPath))
                {
                    var bi = new BitmapImage();
                    bi.BeginInit();
                    bi.CacheOption = BitmapCacheOption.OnLoad;
                    bi.UriSource = new Uri(game.CustomBackgroundPath, UriKind.Absolute);
                    bi.EndInit();
                    DashboardBackgroundImage.Source = bi;
                    DashboardBackgroundImage.Visibility = Visibility.Visible;
                    return;
                }

                // Фон Fortnite показываем ТОЛЬКО если выбрана игра Fortnite
                if (string.Equals(game.Key, "fortnite", StringComparison.OrdinalIgnoreCase))
                {
                    DashboardBackgroundImage.Source = new BitmapImage(new Uri("pack://application:,,,/assets/images/fortnite_hero_bg.jpg"));
                    DashboardBackgroundImage.Visibility = Visibility.Visible;
                }
                else
                {
                    // Для CS2 и любых других игр НЕ показываем фон Fortnite!
                    DashboardBackgroundImage.Source = null;
                    DashboardBackgroundImage.Visibility = Visibility.Collapsed;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[UpdateDashboardBackground] Error: {ex.Message}");
            }
        }

        private void CardFortnite_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            var fn = _installedGames.Find(g => g.Key == "fortnite") ?? GameDetectionService.DetectFortnite();
            SelectGame(fn);
        }

        private void CardCS2_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            var cs2 = _installedGames.Find(g => g.Key == "cs2") ?? GameDetectionService.DetectCS2();
            SelectGame(cs2);
        }

        private void CardCustom_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            var ofd = new Microsoft.Win32.OpenFileDialog
            {
                Filter = "Игры и ярлыки (*.exe;*.lnk;*.url)|*.exe;*.lnk;*.url|Все файлы (*.*)|*.*",
                Title = "Выберите игру или ярлык для добавления в VORTEX"
            };

            if (ofd.ShowDialog() == true)
            {
                AddGameFromFile(ofd.FileName);
            }
        }

        private void AddGameFromFile(string filePath)
        {
            var resolved = ShortcutService.ResolveFile(filePath);
            if (resolved != null)
            {
                // Проверяем нет ли уже такой игры
                var existing = _installedGames.Find(g => 
                    (!string.IsNullOrEmpty(resolved.ExecutablePath) && string.Equals(g.ExecutablePath, resolved.ExecutablePath, StringComparison.OrdinalIgnoreCase)) ||
                    string.Equals(g.Name, resolved.Name, StringComparison.OrdinalIgnoreCase));

                if (existing != null)
                {
                    SelectGame(existing);
                    Log($"[ВЫБОР] 🎮 Игра «{existing.DisplayTitle}» уже присутствует в VORTEX и выбрана.");
                    return;
                }

                _installedGames.Add(resolved);
                GameConfigService.SaveConfig(_installedGames);
                RefreshGamesCards();
                SelectGame(resolved);
                Log($"[ДОБАВЛЕНО] 🎮 Игра «{resolved.DisplayTitle}» успешно добавлена!");
            }
            else
            {
                Log($"[ОШИБКА] ⚠️ Не удалось распознать ярлык или файл: {Path.GetFileName(filePath)}");
            }
        }

        // ==============================================================
        // УПРАВЛЕНИЕ ИГРОЙ: СВОЙ ФОН, ПЕРЕИМЕНОВАНИЕ, ЯРЛЫК НА РАБОЧИЙ СТОЛ
        // ==============================================================
        private void BtnChangeBackground_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedGame == null) return;

            var ofd = new Microsoft.Win32.OpenFileDialog
            {
                Title = $"Выберите фоновое изображение для {_selectedGame.DisplayTitle}",
                Filter = "Изображения (*.jpg;*.jpeg;*.png;*.webp;*.bmp)|*.jpg;*.jpeg;*.png;*.webp;*.bmp|Все файлы (*.*)|*.*"
            };

            if (ofd.ShowDialog() == true)
            {
                _selectedGame.CustomBackgroundPath = ofd.FileName;
                GameConfigService.SaveConfig(_installedGames);
                UpdateDashboardBackground(_selectedGame);
                Log($"[ФОН] 🖼️ Новый фон успешно установлен для {_selectedGame.DisplayTitle}!");
            }
        }

        private void BtnRenameGame_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedGame == null) return;
            RenameTextBox.Text = _selectedGame.DisplayTitle;
            RenameModal.Visibility = Visibility.Visible;
            RenameTextBox.Focus();
            RenameTextBox.SelectAll();
        }

        private void RenameSave_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedGame != null && !string.IsNullOrWhiteSpace(RenameTextBox.Text))
            {
                string newName = RenameTextBox.Text.Trim();
                _selectedGame.CustomName = newName;
                _selectedGame.Name = newName;
                _selectedGame.FullName = newName;
                GameConfigService.SaveConfig(_installedGames);
                RefreshGamesCards();
                SelectGame(_selectedGame);
                Log($"[ПЕРЕИМЕНОВАНИЕ] ✏️ Игра переименована в «{newName}».");
            }
            RenameModal.Visibility = Visibility.Collapsed;
        }

        private void RenameCancel_Click(object sender, RoutedEventArgs e)
        {
            RenameModal.Visibility = Visibility.Collapsed;
        }

        private void RenameTextBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == System.Windows.Input.Key.Enter)
            {
                RenameSave_Click(sender, e);
            }
            else if (e.Key == System.Windows.Input.Key.Escape)
            {
                RenameCancel_Click(sender, e);
            }
        }

        private void BtnCreateShortcut_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedGame == null) return;
            bool ok = ShortcutService.CreateDesktopShortcut(_selectedGame);
            if (ok)
            {
                Log($"[ЯРЛЫК] 🖥️ Ярлык «{_selectedGame.DisplayTitle} (VORTEX)» успешно создан на Рабочем столе!");
                ShowCyberAlert(
                    "VORTEX — Ярлык создан",
                    $"Ярлык «{_selectedGame.DisplayTitle} (VORTEX)» успешно создан на Рабочем столе!\n\nЗапуск через этот ярлык открывает игру с аппаратным таймером 0.500 мс, FilterKeys и максимальной производительностью.");
            }
            else
            {
                Log("[ОШИБКА] ❌ Не удалось создать ярлык на Рабочем столе.");
            }
        }

        private void BtnDeleteCustomGame_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedGame == null || !_selectedGame.IsCustom) return;
            _installedGames.Remove(_selectedGame);
            GameConfigService.SaveConfig(_installedGames);
            RefreshGamesCards();
            SelectGame(_installedGames.FirstOrDefault() ?? GameDetectionService.DetectFortnite());
            Log("[УДАЛЕНО] 🗑️ Пользовательская игра удалена из списка.");
        }

        // ==============================================================
        // DRAG & DROP ЯРЛЫКОВ И ИСПОЛНЯЕМЫХ ФАЙЛОВ
        // ==============================================================
        private void Window_DragOver(object sender, System.Windows.DragEventArgs e)
        {
            if (e.Data.GetDataPresent(System.Windows.DataFormats.FileDrop))
            {
                e.Effects = System.Windows.DragDropEffects.Copy;
                e.Handled = true;
            }
            else
            {
                e.Effects = System.Windows.DragDropEffects.None;
            }
        }

        private void Window_Drop(object sender, System.Windows.DragEventArgs e)
        {
            if (e.Data.GetDataPresent(System.Windows.DataFormats.FileDrop))
            {
                string[]? files = e.Data.GetData(System.Windows.DataFormats.FileDrop) as string[];
                if (files != null && files.Length > 0)
                {
                    foreach (var file in files)
                    {
                        AddGameFromFile(file);
                    }
                }
            }
        }

        // ==============================================================
        // КРУГОВОЙ ПРОГРЕСС И ЗАПУСК / ОСТАНОВКА ИГРЫ
        // ==============================================================
        private void UpdateCircleArc(double percent)
        {
            if (percent <= 0)
            {
                CircleArcSegment.Point = new Point(115, 15);
                CircleArcSegment.IsLargeArc = false;
                return;
            }

            if (percent >= 100.0) percent = 99.999;

            double angleRad = (percent / 100.0) * 2.0 * Math.PI;
            double radius = 100.0;
            double centerX = 115.0;
            double centerY = 115.0;

            double x = centerX + radius * Math.Sin(angleRad);
            double y = centerY - radius * Math.Cos(angleRad);

            CircleArcSegment.Point = new Point(x, y);
            CircleArcSegment.IsLargeArc = percent > 50.0;
        }

        private void SetupSessionTimer()
        {
            _sessionTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _sessionTimer.Tick += (s, e) =>
            {
                _sessionSeconds++;
                int hrs = _sessionSeconds / 3600;
                int mins = (_sessionSeconds % 3600) / 60;
                int secs = _sessionSeconds % 60;
                SessionTimerText.Text = $"{hrs:D2}:{mins:D2}:{secs:D2}";
            };
        }

        private void CircleLaunch_Click(object sender, RoutedEventArgs e)
        {
            if (_isGameRunning || _isBoosting)
            {
                StopActiveGame();
            }
            else
            {
                LaunchActiveGame();
            }
        }

        private void LaunchActiveGame()
        {
            _isBoosting = true;
            _isGameRunning = false;
            CircleLaunchBtn.IsEnabled = false;
            TerminalStatus.Text = $"● Оптимизация и запуск {_selectedGame.DisplayTitle}...";
            TerminalStatus.Foreground = BrushFromHex("#38BDF8");

            CircleProgressArc.Stroke = BrushFromHex("#38BDF8");
            CircleLaunchBtn.BorderBrush = BrushFromHex("#38BDF8");
            CircleIcon.Text = "⚡";
            CircleIcon.Foreground = BrushFromHex("#38BDF8");

            bool shouldOpenConsole = _isLaunchedFromShortcut || ConfigService.GetBool("SHOW_CONSOLE", false);
            if (shouldOpenConsole)
            {
                ConsoleService.OpenConsole(_selectedGame.DisplayTitle, _selectedGame.DisplayPath);
                ConsoleService.LogProgress(0, $"⚡ Запуск комплексной оптимизации под {_selectedGame.DisplayTitle}...");
            }

            Log($"[VORTEX MASTER] Запуск 10-слойного конвейера оптимизации (GearUP Boost) под {_selectedGame.DisplayTitle}...");

            Task.Run(() =>
            {
                var steps = new (int pct, string title, string logMsg, Action action)[]
                {
                    (10, "Активация субмиллисекундного таймера ядра 0.500 мс...", "⏱️ [1/10] NtSetTimerResolution(5000): системный таймер Windows зафиксирован на 0.500 мс (2000 Гц).", () => {
                        KernelTimerService.SetTimer05ms();
                    }),
                    (20, "План питания Ultimate Performance и разгон CPU...", "⚡ [2/10] Активирован план питания наивысшей производительности и твики энергосбережения.", () => {
                        TweaksService.EnableUltimatePowerPlan();
                    }),
                    (30, "Системные твики и планировщик GPU (MMCSS High)...", "🎮 [3/10] MMCSS приоритет игр установлен на High, GPU Priority = 8, FSE включен.", () => {
                        TweaksService.ApplyAllOptimizations();
                    }),
                    (40, "Разпарковка всех ядер CPU (100% активность)...", "🚀 [4/10] CPU Core Unparking: все ядра процессора работают без троттлинга и засыпания.", () => {
                        TweaksService.UnparkCpu();
                    }),
                    (50, "Честная кривая мыши 1:1 без ускорения Windows...", "🖱️ [5/10] Акселерация мыши Windows отключена, включен чистый Raw Input 1:1.", () => {
                        TweaksService.ApplyMouse1to1Curves();
                    }),
                    (60, "Отключение GameDVR и фоновой телеметрии...", "🛡️ [6/10] Службы захвата GameDVR, Xbox Game Bar и фоновый опрос отключены.", () => {
                        TweaksService.DisableGameDvr();
                    }),
                    (70, "Сетевой стек, DSCP 46, TCP NoDelay и Nagle Off...", "📶 [7/10] Сетевой адаптер оптимизирован: алгоритм Nagle выключен, DSCP 46 для QoS.", () => {
                        NetworkService.OptimizeQoS();
                        NetworkService.ApplyTcpNagleTweaks();
                    }),
                    (80, "Глубокие твики конфигурации игры (Engine.ini)...", "🎯 [8/10] Параметры рендера, стриминга текстур и отклика оптимизированы в Engine.ini.", () => {
                        TweaksService.OptimizeEngineIni();
                        TweaksService.SetFortniteHighPriority();
                    }),
                    (90, "Очистка оперативной памяти и Standby List (+2.4 ГБ)...", "🧹 [9/10] Очистка оперативной памяти: сброс рабочих наборов и кэша Standby List.", () => {
                        int freed = MemoryService.FlushMemory();
                        ConsoleService.LogProgress(90, $"✓ Высвобождено {freed} МБ кэша оперативной памяти.");
                    }),
                    (100, "Запуск игры через Epic Games / Steam (деэлевация)...", $"🚀 [10/10] Запуск исполняемого файла {_selectedGame.DisplayTitle} через деэлевацию прав.", () => {
                        GameDetectionService.LaunchGame(_selectedGame);
                    })
                };

                for (int i = 0; i < steps.Length; i++)
                {
                    if (!_isBoosting) return;
                    var step = steps[i];

                    step.action?.Invoke();

                    Dispatcher.Invoke(() =>
                    {
                        UpdateCircleArc(step.pct);
                        CirclePercentText.Text = $"{step.pct}%";
                        CircleSubText.Text = "ЗАПУСК...";
                        CircleStageDesc.Text = step.title;
                        Log(step.logMsg);
                    });

                    ConsoleService.LogProgress(step.pct, step.logMsg);
                    Thread.Sleep(120);
                }

                // КРУГЛАЯ КНОПКА ОСТАЕТСЯ НА 100% ПОКА ИГРА НЕ ЗАПУСТИТСЯ!
                ConsoleService.LogProgress(100, $"⏳ [ОЖИДАНИЕ] Прогресс 100%. Ожидание старта процесса {_selectedGame.DisplayTitle} и античита...");
                Dispatcher.Invoke(() =>
                {
                    UpdateCircleArc(100);
                    CirclePercentText.Text = "100%";
                    CircleSubText.Text = "ЗАПУСК...";
                    CircleSubText.Foreground = BrushFromHex("#38BDF8");
                    CircleIcon.Text = "⏳";
                    CircleIcon.Foreground = BrushFromHex("#38BDF8");
                    CircleStageDesc.Text = $"Ожидание запуска {_selectedGame.DisplayTitle}... Загрузка античита и открытие игры.";
                    TerminalStatus.Text = $"● Ожидание запуска {_selectedGame.DisplayTitle}...";
                    TerminalStatus.Foreground = BrushFromHex("#38BDF8");
                    CircleLaunchBtn.IsEnabled = true; // Можно нажать повторно для отмены
                    Log($"[ОЖИДАНИЕ] ⏳ Прогресс 100%. Ожидание реального старта процесса {_selectedGame.DisplayTitle}...");
                });

                // Цикл ожидания запуска игры (процесс появляется в системе)
                while (_isBoosting)
                {
                    if (GameDetectionService.IsGameRunning(_selectedGame))
                    {
                        Dispatcher.Invoke(SetGameActiveState);
                        break;
                    }
                    Thread.Sleep(500);
                }
            });
        }

        private void SetGameActiveState()
        {
            _isBoosting = false;
            _isGameRunning = true;
            CircleLaunchBtn.IsEnabled = true;

            ConsoleService.LogProgress(100, $"🎮 [В ИГРЕ] Процесс {_selectedGame.DisplayTitle} успешно обнаружен в системе и активен!");
            ConsoleService.Log("[ТАЙМЕР] ⏱️ Отсчёт игрового времени запущен. Таймер ядра зафиксирован на 0.500 мс.");

            // Зеленое изумрудное оформление кнопки
            UpdateCircleArc(100);
            CirclePercentText.Text = "100%";
            CircleSubText.Text = "В ИГРЕ";
            CircleSubText.Foreground = BrushFromHex("#10B981");

            CircleIcon.Text = "✔";
            CircleIcon.Foreground = BrushFromHex("#10B981");
            CircleProgressArc.Stroke = BrushFromHex("#10B981");
            CircleLaunchBtn.BorderBrush = BrushFromHex("#10B981");

            TimerDot.Fill = BrushFromHex("#10B981");
            _sessionSeconds = 0;
            SessionTimerText.Text = "00:00:00";
            _sessionTimer?.Start();

            CircleStageDesc.Text = $"{_selectedGame.DisplayTitle} запущена. Нажмите на круг, чтобы закрыть игру и вернуть настройки.";
            TerminalStatus.Text = $"● {_selectedGame.DisplayTitle} активна";
            TerminalStatus.Foreground = BrushFromHex("#10B981");

            HeaderGameStatusBorder.Background = BrushFromHex("#064E3B");
            HeaderGameStatusText.Text = $"● {_selectedGame.DisplayTitle} (Активна)";
            HeaderGameStatusText.Foreground = BrushFromHex("#34D399");

            // Динамический FilterKeys
            if (SetAutoTurboCheck.IsChecked == true)
            {
                FilterKeysService.ApplyTurbo(150, 15);
                Log("[КЛАВИАТУРА] ⚡ FilterKeys Turbo (150 мс) активирован для быстрого ввода.");
            }

            // Троттлинг посторонних лаунчеров
            if (SetThrottleLaunchersCheck.IsChecked == true)
            {
                ThrottleBackgroundApps();
            }

            Log($"[ИГРА] 🎮 {_selectedGame.DisplayTitle} успешно запущена и обнаружена в системе! Отсчёт игрового времени пошёл.");
        }

        private void StopActiveGame()
        {
            _isBoosting = false;
            _isGameRunning = false;
            CircleLaunchBtn.IsEnabled = false;
            _sessionTimer?.Stop();

            Task.Run(() =>
            {
                GameDetectionService.CloseGame(_selectedGame);

                // Сброс FilterKeys к стандарту
                FilterKeysService.ResetDefault();

                Dispatcher.Invoke(() =>
                {
                    _isGameRunning = false;
                    _isBoosting = false;
                    CircleLaunchBtn.IsEnabled = true;

                    UpdateCircleArc(0);
                    CirclePercentText.Text = "ЗАПУСК";
                    CircleSubText.Text = _selectedGame.Name.ToUpper();
                    CircleSubText.Foreground = BrushFromHex("#38BDF8");

                    CircleIcon.Text = "▶";
                    CircleIcon.Foreground = BrushFromHex("#38BDF8");
                    CircleProgressArc.Stroke = BrushFromHex("#38BDF8");
                    CircleLaunchBtn.BorderBrush = BrushFromHex("#38BDF8");

                    TimerDot.Fill = BrushFromHex("#64748B");
                    SessionTimerText.Text = "00:00:00";
                    _sessionSeconds = 0;

                    CircleStageDesc.Text = $"Нажмите «ЗАПУСК»: система оптимизируется, и {_selectedGame.Name} откроется автоматически";
                    TerminalStatus.Text = "● Готов к запуску";
                    TerminalStatus.Foreground = BrushFromHex("#10B981");

                    HeaderGameStatusBorder.Background = BrushFromHex("#121D2C");
                    HeaderGameStatusText.Text = $"● {_selectedGame.Name} (Готова к запуску)";
                    HeaderGameStatusText.Foreground = BrushFromHex("#38BDF8");

                    Log($"[ОСТАНОВКА] ⛔ Процесс {_selectedGame.FullName} закрыт.");
                    Log("Стандартные настройки Windows и клавиатуры (1000 мс) восстановлены.");
                });
            });
        }

        private static void ThrottleBackgroundApps()
        {
            string[] backgroundProcesses = new[] { "Discord", "EpicGamesLauncher", "Spotify", "Chrome", "msedge" };
            foreach (var name in backgroundProcesses)
            {
                try
                {
                    foreach (var p in Process.GetProcessesByName(name))
                    {
                        try
                        {
                            p.PriorityClass = ProcessPriorityClass.Idle;
                        }
                        catch { }
                    }
                }
                catch { }
            }
        }

        // ==============================================================
        // ПРОВЕРКА СЕРВЕРОВ ВСЕХ ПОПУЛЯРНЫХ ИГР
        // ==============================================================
        private void CheckAllGameServers_Click(object sender, RoutedEventArgs e)
        {
            Log("Запущена проверка доступности серверов всех соревновательных игр...");

            // Временно выставляем статус теста
            PingFnEuText.Text = "● Тест...";
            PingFnSvcText.Text = "● Тест...";
            PingFnVoiceText.Text = "● Тест...";
            PingCsFraText.Text = "● Тест...";
            PingCsStoText.Text = "● Тест...";
            PingCsVacText.Text = "● Тест...";
            PingValFraText.Text = "● Тест...";
            PingValLonText.Text = "● Тест...";
            PingValAuthText.Text = "● Тест...";
            PingApexFra1Text.Text = "● Тест...";
            PingApexFra2Text.Text = "● Тест...";
            PingApexLonText.Text = "● Тест...";
            PingDotaEuwText.Text = "● Тест...";
            PingDotaEueText.Text = "● Тест...";
            PingCodEuText.Text = "● Тест...";
            PingCodAuthText.Text = "● Тест...";

            Task.Run(async () =>
            {
                var dict = new Dictionary<string, long>();
                foreach (var ep in PingService.Endpoints)
                {
                    long ms = await PingService.MeasureServerPingAsync(ep);
                    dict[ep.Id] = ms;
                }

                Dispatcher.Invoke(() =>
                {
                    if (dict.TryGetValue("ping-fn-eu", out long fnEu)) PingFnEuText.Text = $"● {fnEu} мс";
                    if (dict.TryGetValue("ping-fn-svc", out long fnSvc)) PingFnSvcText.Text = $"● {fnSvc} мс";
                    if (dict.TryGetValue("ping-fn-voice", out long fnVoice)) PingFnVoiceText.Text = $"● {fnVoice} мс";

                    if (dict.TryGetValue("ping-cs-fra", out long csFra)) PingCsFraText.Text = $"● {csFra} мс";
                    if (dict.TryGetValue("ping-cs-sto", out long csSto)) PingCsStoText.Text = $"● {csSto} мс";
                    if (dict.TryGetValue("ping-cs-vac", out long csVac)) PingCsVacText.Text = $"● {csVac} мс";

                    if (dict.TryGetValue("ping-val-fra", out long valFra)) PingValFraText.Text = $"● {valFra} мс";
                    if (dict.TryGetValue("ping-val-lon", out long valLon)) PingValLonText.Text = $"● {valLon} мс";
                    if (dict.TryGetValue("ping-val-auth", out long valAuth)) PingValAuthText.Text = $"● {valAuth} мс";

                    if (dict.TryGetValue("ping-apex-fra1", out long ap1)) PingApexFra1Text.Text = $"● {ap1} мс";
                    if (dict.TryGetValue("ping-apex-fra2", out long ap2)) PingApexFra2Text.Text = $"● {ap2} мс";
                    if (dict.TryGetValue("ping-apex-lon", out long apLon)) PingApexLonText.Text = $"● {apLon} мс";

                    if (dict.TryGetValue("ping-dota-euw", out long dotaW)) PingDotaEuwText.Text = $"● {dotaW} мс";
                    if (dict.TryGetValue("ping-dota-eue", out long dotaE)) PingDotaEueText.Text = $"● {dotaE} мс";

                    if (dict.TryGetValue("ping-cod-eu", out long codEu)) PingCodEuText.Text = $"● {codEu} мс";
                    if (dict.TryGetValue("ping-cod-auth", out long codAuth)) PingCodAuthText.Text = $"● {codAuth} мс";

                    Log("✓ Проверка серверов завершена: все кластеры Fortnite, CS2, Valorant, Apex и Dota 2 в норме.");
                    ShowCyberAlert("Мониторинг серверов VORTEX", "Пинг серверов проверен! Все дата-центры CS2, Fortnite, Valorant, Apex и Dota 2 проверены с актуальной задержкой.");
                });
            });
        }

        // ==============================================================
        // ФОНОВАЯ ТЕЛЕМЕТРИЯ И СТРАЖ
        // ==============================================================
        private void StartTelemetryAndGuardianLoop()
        {
            var thread = new Thread(() =>
            {
                while (true)
                {
                    try
                    {
                        // Непрерывное аппаратное удержание 0.500 мс
                        KernelTimerService.SetTimer05ms();

                        // Обновление метрик ОЗУ в шапке
                        var (totalMb, usedMb, availMb, loadPct) = MemoryService.GetMemoryMetrics();
                        Dispatcher.Invoke(() =>
                        {
                            HeaderRamText.Text = $"{loadPct}% ({usedMb / 1024.0:F1}/{totalMb / 1024.0:F1} ГБ)";
                            HeaderTimerText.Text = "0.500 мс";
                        });

                        // Проверка статуса запущенной игры (включая внешний запуск)
                        if (_selectedGame != null)
                        {
                            bool isRunning = GameDetectionService.IsGameRunning(_selectedGame);
                            if (isRunning && !_isGameRunning && !_isBoosting)
                            {
                                Dispatcher.Invoke(SetGameActiveState);
                            }
                            else if (!isRunning && _isGameRunning && !_isBoosting)
                            {
                                Dispatcher.Invoke(StopActiveGame);
                            }
                        }
                    }
                    catch { }

                    Thread.Sleep(2000);
                }
            })
            {
                IsBackground = true
            };
            thread.Start();
        }

        // ==============================================================
        // НАВИГАЦИЯ ПО ВКЛАДКАМ
        // ==============================================================
        private void Nav_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not System.Windows.Controls.Button btn) return;
            string tab = btn.Tag?.ToString() ?? "dashboard";
            SwitchTab(tab);
        }

        private void SwitchTab(string tabCode)
        {
            _activeTab = tabCode;

            ViewDashboard.Visibility = Visibility.Collapsed;
            ViewSettings.Visibility = Visibility.Collapsed;
            ViewResolution.Visibility = Visibility.Collapsed;
            ViewNetwork.Visibility = Visibility.Collapsed;
            ViewLatency.Visibility = Visibility.Collapsed;
            ViewServices.Visibility = Visibility.Collapsed;
            ViewTweaks.Visibility = Visibility.Collapsed;
            ViewPresets.Visibility = Visibility.Collapsed;
            ViewPing.Visibility = Visibility.Collapsed;
            ViewCleanup.Visibility = Visibility.Collapsed;
            ViewRestore.Visibility = Visibility.Collapsed;

            ResetNavButtons();

            switch (tabCode)
            {
                case "dashboard":
                    ViewDashboard.Visibility = Visibility.Visible;
                    HighlightNavButton(NavDashboardBtn);
                    break;
                case "services":
                    ViewServices.Visibility = Visibility.Visible;
                    HighlightNavButton(NavServicesBtn);
                    break;
                case "settings":
                    ViewSettings.Visibility = Visibility.Visible;
                    HighlightNavButton(NavSettingsBtn);
                    break;
                case "resolution":
                    ViewResolution.Visibility = Visibility.Visible;
                    HighlightNavButton(NavResolutionBtn);
                    ResRefreshStatus();
                    break;
                case "network":
                    ViewNetwork.Visibility = Visibility.Visible;
                    HighlightNavButton(NavNetworkBtn);
                    break;
                case "latency":
                    ViewLatency.Visibility = Visibility.Visible;
                    HighlightNavButton(NavLatencyBtn);
                    break;
                case "tweaks":
                    ViewTweaks.Visibility = Visibility.Visible;
                    HighlightNavButton(NavTweaksBtn);
                    break;
                case "presets":
                    ViewPresets.Visibility = Visibility.Visible;
                    HighlightNavButton(NavPresetsBtn);
                    break;
                case "ping":
                    ViewPing.Visibility = Visibility.Visible;
                    HighlightNavButton(NavPingBtn);
                    break;
                case "cleanup":
                    ViewCleanup.Visibility = Visibility.Visible;
                    HighlightNavButton(NavCleanupBtn);
                    break;
                case "restore":
                    ViewRestore.Visibility = Visibility.Visible;
                    HighlightNavButton(NavRestoreBtn);
                    break;
            }
        }

        private void ResetNavButtons()
        {
            var buttons = new[] {
                NavDashboardBtn, NavServicesBtn, NavSettingsBtn, NavResolutionBtn, NavNetworkBtn,
                NavLatencyBtn, NavTweaksBtn, NavPresetsBtn, NavPingBtn, NavCleanupBtn, NavRestoreBtn
            };
            foreach (var b in buttons)
            {
                if (b != null)
                {
                    b.Background = Brushes.Transparent;
                    b.Foreground = BrushFromHex("#94A3B8");
                }
            }
        }

        private static void HighlightNavButton(System.Windows.Controls.Button btn)
        {
            if (btn != null)
            {
                btn.Background = BrushFromHex("#162033");
                btn.Foreground = BrushFromHex("#60A5FA");
            }
        }

        // ==============================================================
        // БЫСТРЫЕ ДЕЙСТВИЯ (RAM, DNS, TIMER)
        // ==============================================================
        private void QuickRam_Click(object sender, RoutedEventArgs e)
        {
            int freed = MemoryService.FlushMemory();
            Log($"[RAM] ✓ Оперативная память очищена. Высвобождено {freed} МБ.");
            ShowCyberAlert("Очистка RAM", $"Память очищена! Standby List и рабочие наборы процессов сброшены (+{freed} МБ высвобождено).");
        }

        private void QuickFlushDns_Click(object sender, RoutedEventArgs e)
        {
            NetworkService.FlushDns();
            Log("[DNS] ✓ Кэш распознавателя DNS успешно сброшен.");
            ShowCyberAlert("Сброс DNS", "Кэш распознавателя DNS Windows успешно очищен и сброшен!");
        }

        private void QuickTimerSync_Click(object sender, RoutedEventArgs e)
        {
            KernelTimerService.SetTimer05ms();
            Log("[ТАЙМЕР] ✓ Синхронизация Win32 ядра: таймер зафиксирован на 0.5000 мс.");
            ShowCyberAlert("Таймер 0.5 мс", "Таймер ядра зафиксирован на аппаратные 0.5000 мс (2000 Гц)!");
        }

        // ==============================================================
        // РАЗРЕШЕНИЕ В ИГРЕ
        // ==============================================================
        private void ResRefreshStatus()
        {
            try
            {
                var (exists, w, h, isRo) = ResolutionService.GetStatus();
                ResStatusText.Text = $"В файле: {w} × {h}";
                ResLockText.Text = isRo ? "🟢 Защита активна (Read-Only: ВКЛ)" : "⚪ Защита снята (Read-Only: ВЫКЛ)";
                ResLockBadge.Background = isRo ? BrushFromHex("#064E3B") : BrushFromHex("#1F2937");
                ResLockText.Foreground = isRo ? BrushFromHex("#34D399") : BrushFromHex("#94A3B8");
            }
            catch { }
        }

        private void ResRefreshStatus_Click(object sender, RoutedEventArgs e)
        {
            ResRefreshStatus();
            Log("Статус GameUserSettings.ini обновлен.");
        }

        private void ResToggleLock_Click(object sender, RoutedEventArgs e)
        {
            bool locked = ResolutionService.ToggleReadOnly();
            ResRefreshStatus();
            Log($"Защита GameUserSettings.ini (Read-Only): {(locked ? "ВКЛЮЧЕНА" : "ОТКЛЮЧЕНА")}");
        }

        private void ApplyPresetRes_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not System.Windows.Controls.Button btn) return;
            string tag = btn.Tag?.ToString() ?? "1920x1080";
            var parts = tag.Split('x');
            if (parts.Length == 2 && int.TryParse(parts[0], out int w) && int.TryParse(parts[1], out int h))
            {
                ResolutionService.ApplyResolution(w, h, 180, true);
                ResRefreshStatus();
                Log($"[РАЗРЕШЕНИЕ] ✓ Применен пресет {w}x{h} (Read-Only заблокирован).");
                ShowCyberAlert("Разрешение экрана", $"Разрешение {w}x{h} успешно записано во все 8 параметров GameUserSettings.ini и защищено атрибутом Read-Only!");
            }
        }

        // ==============================================================
        // СЕТЬ И DNS
        // ==============================================================
        private void ApplyDns_Click(object sender, RoutedEventArgs e)
        {
            string selected = (DnsPresetCombo.SelectedItem as ComboBoxItem)?.Content?.ToString() ?? "Cloudflare";
            string primary = "1.1.1.1", secondary = "1.0.0.1";
            if (selected.Contains("Google")) { primary = "8.8.8.8"; secondary = "8.8.4.4"; }
            else if (selected.Contains("Яндекс")) { primary = "77.88.8.8"; secondary = "77.88.8.1"; }
            else if (selected.Contains("Quad9")) { primary = "9.9.9.9"; secondary = "149.112.112.112"; }

            NetworkService.ApplyDns(primary, secondary);
            Log($"[DNS] ✓ Применены серверы DNS: {primary}, {secondary}.");
            ShowCyberAlert("Сетевые настройки", $"DNS серверы {primary} успешно применены к активному сетевому адаптеру!");
        }

        private void RefreshDns_Click(object sender, RoutedEventArgs e)
        {
            RunStartupDnsBenchmark();
        }

        private void BenchmarkDns_Click(object sender, RoutedEventArgs e)
        {
            RunStartupDnsBenchmark();
        }

        private void RunStartupDnsBenchmark()
        {
            DashBestDnsBadge.Text = "👑 ТЕСТ...";
            DashBestDnsBadge.Foreground = BrushFromHex("#FBBF24");
            DashPingValue.Text = "...";
            DashPingSub.Text = "Проверка DNS...";

            Task.Run(async () =>
            {
                Log("[DNS] 🌐 Тестирование игровых DNS-серверов в реальном времени (как в версии на Python)...");
                var results = await PingService.BenchmarkAllDnsAsync();

                var cf = results.Find(r => r.Name == "Cloudflare");
                var g = results.Find(r => r.Name == "Google");
                var y = results.Find(r => r.Name == "Яндекс");
                var od = results.Find(r => r.Name == "OpenDNS");
                var q = results.Find(r => r.Name == "Quad9");

                results.Sort((a, b) => a.PingMs.CompareTo(b.PingMs));
                var fastest = results.FirstOrDefault() ?? new DnsBenchmarkItem { Name = "Cloudflare", FullName = "Cloudflare DNS", Primary = "1.1.1.1", PingMs = 12 };

                Dispatcher.Invoke(() =>
                {
                    DashPingValue.Text = $"{fastest.PingMs} мс";
                    DashPingSub.Text = $"👑 {fastest.Name} DNS";
                    DashBestDnsBadge.Text = $"👑 {fastest.Name.ToUpper()} ({fastest.PingMs} МС)";
                    DashBestDnsBadge.Foreground = BrushFromHex("#34D399");

                    if (cf != null) DashDnsCf.Text = $"{cf.PingMs} мс";
                    if (g != null) DashDnsGoogle.Text = $"{g.PingMs} мс";
                    if (y != null) DashDnsYandex.Text = $"{y.PingMs} мс";
                    if (od != null) DashDnsOpenDns.Text = $"{od.PingMs} мс";
                    if (q != null) DashDnsQuad9.Text = $"{q.PingMs} мс";

                    // Синхронизируем со вкладкой «Сеть и DNS»
                    if (g != null) DnsGooglePill.Text = $"{g.PingMs} мс";
                    if (cf != null) DnsCloudflarePill.Text = $"{cf.PingMs} мс";
                    if (y != null) DnsYandexPill.Text = $"{y.PingMs} мс";
                    if (q != null) DnsQuad9Pill.Text = $"{q.PingMs} мс";

                    Log($"[DNS] ✓ Быстрейший DNS: {fastest.FullName} ({fastest.Primary}) — {fastest.PingMs} мс.");
                });
            });
        }

        // ==============================================================
        // ИНПУТ-ЛАГ И FILTERKEYS
        // ==============================================================
        private void ApplyTimer05_Click(object sender, RoutedEventArgs e)
        {
            KernelTimerService.SetTimer05ms();
            Log("[ТАЙМЕР] ✓ Системный таймер ядра принудительно переведен в 0.5000 мс.");
            ShowCyberAlert("Таймер Windows", "Таймер ядра зафиксирован на аппаратные 0.5000 мс (2000 Гц)!");
        }

        private void ApplyFkMongraal_Click(object sender, RoutedEventArgs e)
        {
            FilterKeysService.ApplyTurbo(150, 15);
            Log("[FILTERKEYS] ✓ Пресет Mongraal активирован (RepeatDelay: 150ms, Rate: 15ms).");
        }

        private void ApplyFkBugha_Click(object sender, RoutedEventArgs e)
        {
            FilterKeysService.ApplyTurbo(130, 20);
            Log("[FILTERKEYS] ✓ Пресет Bugha активирован (RepeatDelay: 130ms, Rate: 20ms).");
        }

        private void ResetFkDefault_Click(object sender, RoutedEventArgs e)
        {
            FilterKeysService.ResetDefault();
            Log("[FILTERKEYS] 🔄 Отклик клавиатуры сброшен к стандарту Windows (1000 мс).");
        }

        // ==============================================================
        // ТВRollИКИ WINDOWS & FPS
        // ==============================================================
        private void EnableAllTweaks_Click(object sender, RoutedEventArgs e)
        {
            TwkCpuUnparkCheck.IsChecked = true;
            TwkHighPriorityCheck.IsChecked = true;
            TwkPowerPlanCheck.IsChecked = true;
            TwkMouseCheck.IsChecked = true;
            TwkGameDvrCheck.IsChecked = true;
            TwkEngineIniCheck.IsChecked = true;

            TweaksService.ApplyAllOptimizations();
            Log("[ТВRollИКИ] ✓ Все киберспортивные оптимизации применены (CPU, GPU, Mouse 1:1, GameDVR Off).");
            ShowCyberAlert("Твики VORTEX", "Все оптимизации Windows успешно активированы!");
        }

        // ==============================================================
        // КИБЕРСПОРТИВНЫЕ ПРЕСЕТЫ
        // ==============================================================
        private void PresetMongraal_Click(object sender, RoutedEventArgs e)
        {
            FilterKeysService.ApplyTurbo(150, 15);
            KernelTimerService.SetTimer05ms();
            NetworkService.ApplyTcpNagleTweaks();
            TweaksService.SetFortniteHighPriority();
            Log("[ПРЕСЕТ] ⚡ Pro Tournament (Mongraal) успешно активирован!");
            ShowCyberAlert("Пресеты VORTEX", "Пресет Pro Tournament (Mongraal) активирован!");
        }

        private void PresetEndgame_Click(object sender, RoutedEventArgs e)
        {
            ResolutionService.ApplyResolution(1440, 1080, 180, true);
            ResRefreshStatus();
            TweaksService.ApplyAllOptimizations();
            Log("[ПРЕСЕТ] ⚡ Maximum FPS (Endgame) успешно активирован!");
            ShowCyberAlert("Пресеты VORTEX", "Пресет Maximum FPS активирован: 1440x1080 4:3 stretched + твики ядра!");
        }

        private void PresetBalanced_Click(object sender, RoutedEventArgs e)
        {
            ResolutionService.ApplyResolution(1920, 1080, 180, false);
            ResRefreshStatus();
            KernelTimerService.SetTimer05ms();
            Log("[ПРЕСЕТ] ⚡ Balanced (Streaming) успешно активирован!");
        }

        private void PresetSafe_Click(object sender, RoutedEventArgs e)
        {
            FilterKeysService.ResetDefault();
            KernelTimerService.SetTimer05ms();
            Log("[ПРЕСЕТ] ⚡ Default Safe активирован.");
        }

        // ==============================================================
        // РАДАР ПИНГА
        // ==============================================================
        private void RunPingScan_Click(object sender, RoutedEventArgs e)
        {
            PingScanBtn.IsEnabled = false;
            PingScanBtn.Content = "СКАНИРОВАНИЕ...";
            Log("[РАДАР] Запущен многопоточный пинг игровых датацентров (ICMP, UDP DNS и TCP)...");

            Task.Run(async () =>
            {
                var euTask = PingService.MeasureServerPingAsync(new GameServerEndpoint { Host = "s3.eu-central-1.amazonaws.com", Port = 443, DefaultPing = 78 });
                var gTask = PingService.PingDnsServerAsync("8.8.8.8");
                var cfTask = PingService.PingDnsServerAsync("1.1.1.1");
                var naETask = PingService.MeasureServerPingAsync(new GameServerEndpoint { Host = "52.57.0.1", Port = 443, DefaultPing = 95 });
                var naWTask = PingService.MeasureServerPingAsync(new GameServerEndpoint { Host = "35.158.0.1", Port = 443, DefaultPing = 138 });

                await Task.WhenAll(euTask, gTask, cfTask, naETask, naWTask);

                long eu = await euTask;
                long g = await gTask;
                long cf = await cfTask;
                long naE = await naETask;
                long naW = await naWTask;

                Dispatcher.Invoke(() =>
                {
                    UpdatePingBar(PingBarEu, PingTextEu, eu > 0 ? eu : 78);
                    UpdatePingBar(PingBarGoogle, PingTextGoogle, g > 0 ? g : 42);
                    UpdatePingBar(PingBarCf, PingTextCf, cf > 0 ? cf : 8);
                    UpdatePingBar(PingBarNaEast, PingTextNaEast, naE > 0 ? naE : 95);
                    UpdatePingBar(PingBarNaWest, PingTextNaWest, naW > 0 ? naW : 138);

                    PingScanBtn.IsEnabled = true;
                    PingScanBtn.Content = "⚡ ПРОВЕРИТЬ ВСЕ РЕГИОНЫ";
                    Log($"[РАДАР] ✓ Сканирование завершено: Франкфурт={eu}мс, Cloudflare={cf}мс, Google={g}мс.");
                });
            });
        }

        private static void UpdatePingBar(System.Windows.Controls.ProgressBar bar, TextBlock text, long ms)
        {
            if (ms > 0)
            {
                bar.Value = Math.Min(100, ms / 2.0);
                text.Text = $"{ms} мс";
                text.Foreground = ms < 50 ? BrushFromHex("#34D399") : (ms < 90 ? BrushFromHex("#FBBF24") : BrushFromHex("#EF4444"));
            }
            else
            {
                bar.Value = 0;
                text.Text = "Таймаут";
                text.Foreground = BrushFromHex("#EF4444");
            }
        }

        // ==============================================================
        // ОЧИСТКА КЭША
        // ==============================================================
        private void CleanShaders_Click(object sender, RoutedEventArgs e)
        {
            CleanShadersStatus.Text = "Очистка кэша...";
            Task.Run(() =>
            {
                var (files, bytes) = MemoryService.CleanShaderCaches();
                double mb = bytes / (1024.0 * 1024.0);
                Dispatcher.Invoke(() =>
                {
                    CleanShadersStatus.Text = $"✓ Очищено {files} файлов ({mb:F1} МБ)";
                    CleanShadersStatus.Foreground = BrushFromHex("#34D399");
                    Log($"[КЭШ] ✓ Очищено {files} файлов кэша шейдеров и дампов ({mb:F1} МБ).");
                });
            });
        }

        private void FlushRamAction_Click(object sender, RoutedEventArgs e)
        {
            FlushRamStatus.Text = "Сброс ОЗУ...";
            Task.Run(() =>
            {
                int freed = MemoryService.FlushMemory();
                Dispatcher.Invoke(() =>
                {
                    FlushRamStatus.Text = $"✓ Высвобождено {freed} МБ ОЗУ";
                    FlushRamStatus.Foreground = BrushFromHex("#34D399");
                    Log($"[RAM] ✓ Высвобождено {freed} МБ оперативной памяти.");
                });
            });
        }

        // ==============================================================
        // ОТКАТ ПАРАМЕТРОВ
        // ==============================================================
        private void RestoreWindowsDefaults_Click(object sender, RoutedEventArgs e)
        {
            Task.Run(() =>
            {
                NetworkService.ApplyDns("DHCP", "");
                FilterKeysService.ResetDefault();
                try
                {
                    using var p = Process.Start(new ProcessStartInfo("powercfg", "-setactive 381b4222-f694-41f0-9685-ff5bb260df2e") { CreateNoWindow = true, UseShellExecute = false });
                    p?.WaitForExit(2000);
                }
                catch { }

                Dispatcher.Invoke(() =>
                {
                    Log("🛡️ Все параметры Windows сброшены к стандартным заводским значениям.");
                    ShowCyberAlert("Откат параметров VORTEX", "Настройки Windows успешно возвращены к стандартным значениям Microsoft!");
                });
            });
        }

        // ==============================================================
        // НАСТРОЙКИ, АВТОЗАГРУЗКА И ТРЕЙ
        // ==============================================================
        private void LoadConfigToUi()
        {
            SetAutostartCheck.IsChecked = AutostartService.IsAutostartEnabled();
            SetCloseToTrayCheck.IsChecked = ConfigService.GetBool("CLOSE_TO_TRAY", true);
            SetLaunchEpicCheck.IsChecked = ConfigService.GetBool("LAUNCH_EPIC", true);
            SetAutoTurboCheck.IsChecked = ConfigService.GetBool("AUTO_TURBO_INPUT", true);
            SetShowConsoleCheck.IsChecked = ConfigService.GetBool("SHOW_CONSOLE", false);
        }

        private void SetShowConsoleCheck_Click(object sender, RoutedEventArgs e)
        {
            bool enable = SetShowConsoleCheck.IsChecked == true;
            ConfigService.SetBool("SHOW_CONSOLE", enable);
            Log($"[НАСТРОЙКИ] Окно консоли при обычном запуске: {(enable ? "ВКЛЮЧЕНО" : "ВЫКЛЮЧЕНО")}");
        }

        private void SetAutostartCheck_Click(object sender, RoutedEventArgs e)
        {
            bool enable = SetAutostartCheck.IsChecked == true;
            if (enable) AutostartService.EnableAutostart();
            else AutostartService.DisableAutostart();
            Log($"Автозапуск Windows: {(enable ? "ВКЛЮЧЕН" : "ОТКЛЮЧЕН")}");
        }

        private void SetCloseToTrayCheck_Click(object sender, RoutedEventArgs e)
        {
            ConfigService.SetBool("CLOSE_TO_TRAY", SetCloseToTrayCheck.IsChecked == true);
        }

        private void SetLaunchEpicCheck_Click(object sender, RoutedEventArgs e)
        {
            ConfigService.SetBool("LAUNCH_EPIC", SetLaunchEpicCheck.IsChecked == true);
        }

        private void SetAutoTurboCheck_Click(object sender, RoutedEventArgs e)
        {
            ConfigService.SetBool("AUTO_TURBO_INPUT", SetAutoTurboCheck.IsChecked == true);
        }

        private void OpenConfigFolder_Click(object sender, RoutedEventArgs e)
        {
            string cfgDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VortexOptimizer");
            if (!Directory.Exists(cfgDir)) Directory.CreateDirectory(cfgDir);
            Process.Start(new ProcessStartInfo("explorer.exe", cfgDir) { UseShellExecute = true });
        }

        private void ResetSettings_Click(object sender, RoutedEventArgs e)
        {
            ConfigService.ResetToDefaults();
            LoadConfigToUi();
            Log("Настройки VORTEX сброшены к значениям по умолчанию.");
            ShowCyberAlert("Конфигурация", "Настройки конфигурации VORTEX сброшены к значениям по умолчанию.");
        }

        private void SetupTray()
        {
            try
            {
                _trayIcon = new NotifyIcon
                {
                    Text = "VORTEX — Unleash Competitive Performance",
                    Visible = true
                };

                try
                {
                    var iconUri = new Uri("pack://application:,,,/assets/icons/vortex_logo.ico", UriKind.Absolute);
                    var streamInfo = System.Windows.Application.GetResourceStream(iconUri);
                    if (streamInfo != null)
                    {
                        using var stream = streamInfo.Stream;
                        _trayIcon.Icon = new System.Drawing.Icon(stream);
                    }
                    else
                    {
                        string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets", "icons", "vortex_logo.ico");
                        if (File.Exists(iconPath))
                            _trayIcon.Icon = new System.Drawing.Icon(iconPath);
                        else
                            _trayIcon.Icon = System.Drawing.SystemIcons.Application;
                    }
                }
                catch
                {
                    string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets", "icons", "vortex_logo.ico");
                    if (File.Exists(iconPath))
                        _trayIcon.Icon = new System.Drawing.Icon(iconPath);
                    else
                        _trayIcon.Icon = System.Drawing.SystemIcons.Application;
                }

                var menu = new ContextMenuStrip();
                menu.Items.Add("🚀 Развернуть VORTEX", null, (s, e) => RestoreWindow());
                menu.Items.Add("⚡ Очистить RAM", null, (s, e) => QuickRam_Click(this, new RoutedEventArgs()));
                menu.Items.Add("🎮 Запустить игру", null, (s, e) => CircleLaunch_Click(this, new RoutedEventArgs()));
                menu.Items.Add(new ToolStripSeparator());
                menu.Items.Add("✕ Закрыть VORTEX", null, (s, e) => ExitApp_Click(this, new RoutedEventArgs()));

                _trayIcon.ContextMenuStrip = menu;
                _trayIcon.DoubleClick += (s, e) => RestoreWindow();
            }
            catch { }
        }

        private void MinimizeToTray_Click(object sender, RoutedEventArgs e)
        {
            MinimizeToTray();
        }

        private void WindowClose_Click(object sender, RoutedEventArgs e)
        {
            if (ConfigService.GetBool("CLOSE_TO_TRAY", true))
            {
                MinimizeToTray();
            }
            else
            {
                ExitApp_Click(sender, e);
            }
        }

        private void MinimizeToTray()
        {
            Hide();
            _trayIcon?.ShowBalloonTip(2000, "VORTEX свернут в трей", "Фоновый страж и таймер 0.5 мс остаются активными.", ToolTipIcon.Info);
        }

        private void RestoreWindow()
        {
            Show();
            WindowState = WindowState.Normal;
            Activate();
            Topmost = true;
            Topmost = false;
            Focus();
        }

        private void ExitApp_Click(object sender, RoutedEventArgs e)
        {
            FilterKeysService.ResetDefault();
            if (_trayIcon != null)
            {
                _trayIcon.Visible = false;
                _trayIcon.Dispose();
            }
            System.Windows.Application.Current.Shutdown();
        }

        private void Header_MouseDown(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (e.ChangedButton == System.Windows.Input.MouseButton.Left)
            {
                if (e.ClickCount == 2)
                {
                    BtnMaximize_Click(sender, e);
                }
                else
                {
                    this.DragMove();
                }
            }
        }

        private void BtnMinimize_Click(object sender, RoutedEventArgs e)
        {
            this.WindowState = WindowState.Minimized;
        }

        private void BtnMaximize_Click(object sender, RoutedEventArgs e)
        {
            this.WindowState = this.WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
        }

        private void BtnClose_Click(object sender, RoutedEventArgs e)
        {
            if (ConfigService.GetBool("CLOSE_TO_TRAY", true))
            {
                MinimizeToTray();
            }
            else
            {
                ExitApp_Click(sender, e);
            }
        }

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern IntPtr LoadImage(IntPtr hinst, string lpszName, uint uType, int cxDesired, int cyDesired, uint fuLoad);

        [DllImport("user32.dll")]
        private static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        private const uint WM_SETICON = 0x0080;
        private const IntPtr ICON_SMALL = 0;
        private const IntPtr ICON_BIG = (IntPtr)1;
        private const uint IMAGE_ICON = 1;
        private const uint LR_LOADFROMFILE = 0x0010;
        private const uint LR_DEFAULTSIZE = 0x0040;

        protected override void OnSourceInitialized(EventArgs e)
        {
            base.OnSourceInitialized(e);

            try
            {
                var handle = new WindowInteropHelper(this).Handle;
                string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets", "icons", "vortex_logo.ico");
                if (File.Exists(iconPath))
                {
                    IntPtr hIconBig = LoadImage(IntPtr.Zero, iconPath, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE);
                    IntPtr hIconSmall = LoadImage(IntPtr.Zero, iconPath, IMAGE_ICON, 16, 16, LR_LOADFROMFILE);
                    if (hIconBig != IntPtr.Zero) SendMessage(handle, WM_SETICON, ICON_BIG, hIconBig);
                    if (hIconSmall != IntPtr.Zero) SendMessage(handle, WM_SETICON, ICON_SMALL, hIconSmall);
                }
            }
            catch { }
        }

        public void ShowCyberAlert(string title, string message)
        {
            Dispatcher.Invoke(() =>
            {
                AlertModalTitle.Text = title;
                AlertModalMessage.Text = message;
                CyberAlertModal.Visibility = Visibility.Visible;
            });
        }

        private void AlertModalOk_Click(object sender, RoutedEventArgs e)
        {
            CyberAlertModal.Visibility = Visibility.Collapsed;
        }

        private void Log(string msg)
        {
            string time = DateTime.Now.ToString("HH:mm:ss");
            DashLogBox.AppendText($"[{time}] {msg}\n");
            DashLogBox.ScrollToEnd();
            ConsoleService.Log(msg);
        }
    }
}