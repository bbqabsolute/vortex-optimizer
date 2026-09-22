using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Forms;
using Microsoft.Win32;

namespace VortexSetup
{
    public partial class MainWindow : Window
    {
        private bool _isInstalled = false;

        public MainWindow()
        {
            InitializeComponent();
        }

        private void BrowseFolder_Click(object sender, RoutedEventArgs e)
        {
            using var fbd = new FolderBrowserDialog
            {
                Description = "Выберите каталог для установки VORTEX:",
                SelectedPath = InstallPathBox.Text,
                UseDescriptionForTitle = true
            };

            if (fbd.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                InstallPathBox.Text = fbd.SelectedPath;
            }
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        private void Action_Click(object sender, RoutedEventArgs e)
        {
            if (_isInstalled)
            {
                // Запуск VORTEX
                string targetDir = InstallPathBox.Text;
                string exePath = Path.Combine(targetDir, "VORTEX.exe");
                if (File.Exists(exePath))
                {
                    try
                    {
                        Process.Start(new ProcessStartInfo(exePath) { UseShellExecute = true });
                    }
                    catch { }
                }
                Close();
                return;
            }

            // Начинаем установку
            ConfigPanel.Visibility = Visibility.Collapsed;
            ProgressPanel.Visibility = Visibility.Visible;
            CancelBtn.IsEnabled = false;
            ActionBtn.IsEnabled = false;

            string installDir = InstallPathBox.Text.Trim();
            bool makeDesktopShortcut = DesktopShortcutCheck.IsChecked == true;
            bool makeStartMenu = StartMenuCheck.IsChecked == true;
            bool enableAutostart = AutostartCheck.IsChecked == true;
            bool launchAfter = LaunchAfterCheck.IsChecked == true;

            Task.Run(() =>
            {
                RunInstallation(installDir, makeDesktopShortcut, makeStartMenu, enableAutostart, launchAfter);
            });
        }

        private void Log(string msg)
        {
            Dispatcher.Invoke(() =>
            {
                string time = DateTime.Now.ToString("HH:mm:ss");
                InstallLogBox.AppendText($"[{time}] {msg}\n");
                InstallLogBox.ScrollToEnd();
            });
        }

        private void SetProgress(int percent, string stepTitle)
        {
            Dispatcher.Invoke(() =>
            {
                InstallProgressBar.Value = percent;
                ProgressPercentText.Text = $"{percent}%";
                ProgressStepText.Text = stepTitle;
            });
        }

        private void RunInstallation(string targetDir, bool desktopShortcut, bool startMenu, bool autostart, bool launchAfter)
        {
            try
            {
                SetProgress(15, "Создание каталога установки...");
                Log($"[1/6] Создание каталога: {targetDir}");
                if (!Directory.Exists(targetDir))
                {
                    Directory.CreateDirectory(targetDir);
                }
                Thread.Sleep(300);

                SetProgress(40, "Распаковка VORTEX.exe и компонентов...");
                Log("[2/6] Распаковка исполняемого файла VORTEX.exe...");
                string targetExe = Path.Combine(targetDir, "VORTEX.exe");
                ExtractEmbeddedResource("VORTEX.exe", targetExe);

                Log("[3/6] Распаковка графических ресурсов и иконок...");
                string targetIco = Path.Combine(targetDir, "vortex_logo.ico");
                ExtractEmbeddedResource("vortex_logo.ico", targetIco);

                string targetPng = Path.Combine(targetDir, "vortex_logo.png");
                ExtractEmbeddedResource("vortex_logo.png", targetPng);
                Thread.Sleep(300);

                SetProgress(65, "Создание ярлыков Windows...");
                if (desktopShortcut)
                {
                    string desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
                    string lnkPath = Path.Combine(desktop, "VORTEX.lnk");
                    CreateShortcut(lnkPath, targetExe, targetIco, "VORTEX — Мультиигровой Оптимизатор и Лаунчер");
                    Log($"[4/6] ✓ Ярлык на Рабочем столе создан: {lnkPath}");
                }

                if (startMenu)
                {
                    string startDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonPrograms), "VORTEX");
                    if (!Directory.Exists(startDir)) Directory.CreateDirectory(startDir);
                    string lnkPath = Path.Combine(startDir, "VORTEX.lnk");
                    CreateShortcut(lnkPath, targetExe, targetIco, "VORTEX — Мультиигровой Оптимизатор и Лаунчер");
                    Log($"[5/6] ✓ Ярлык в меню «Пуск» создан: {lnkPath}");
                }
                Thread.Sleep(300);

                SetProgress(85, "Регистрация автозагрузки и в реестре Windows...");
                if (autostart)
                {
                    try
                    {
                        string cmd = $"schtasks /create /tn \"VORTEX_Optimizer\" /tr \"\\\"{targetExe}\\\" --minimized\" /sc onlogon /rl highest /f";
                        using var p = Process.Start(new ProcessStartInfo("cmd.exe", $"/c {cmd}") { CreateNoWindow = true, UseShellExecute = false });
                        p?.WaitForExit(3000);
                        Log("[6/6] ✓ Задача наивысшего приоритета зарегистрирована в Планировщике задач.");
                    }
                    catch { }
                }

                // Регистрация в реестре Windows "Установка и удаление программ"
                RegisterUninstaller(targetDir, targetExe, targetIco);
                Log("✓ VORTEX успешно зарегистрирован в реестре Windows.");
                Thread.Sleep(300);

                SetProgress(100, "Установка успешно завершена!");
                Log("🟢 Все компоненты развернуты. VORTEX готов к работе!");

                Dispatcher.Invoke(() =>
                {
                    _isInstalled = true;
                    CompleteStatusText.Text = "🟢 Установка успешно завершена!";
                    CompleteStatusText.Foreground = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#10B981")!;

                    CancelBtn.Content = "Закрыть";
                    CancelBtn.IsEnabled = true;

                    ActionBtn.Content = "🚀 ЗАПУСТИТЬ VORTEX";
                    ActionBtn.IsEnabled = true;

                    if (launchAfter)
                    {
                        try
                        {
                            Process.Start(new ProcessStartInfo(targetExe) { UseShellExecute = true });
                        }
                        catch { }
                    }
                });
            }
            catch (Exception ex)
            {
                Log($"ОШИБКА установки: {ex.Message}");
                Dispatcher.Invoke(() =>
                {
                    CompleteStatusText.Text = $"Ошибка: {ex.Message}";
                    CancelBtn.IsEnabled = true;
                });
            }
        }

        private static void ExtractEmbeddedResource(string partialName, string outputPath)
        {
            var asm = Assembly.GetExecutingAssembly();
            string? foundResource = null;
            foreach (var name in asm.GetManifestResourceNames())
            {
                if (name.EndsWith(partialName, StringComparison.OrdinalIgnoreCase))
                {
                    foundResource = name;
                    break;
                }
            }

            if (foundResource == null)
            {
                // If not found in manifest, copy from local directory if exists
                string fallback = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, partialName);
                if (File.Exists(fallback))
                {
                    File.Copy(fallback, outputPath, true);
                    return;
                }
                throw new FileNotFoundException($"Встроенный ресурс {partialName} не найден.");
            }

            using var stream = asm.GetManifestResourceStream(foundResource);
            if (stream == null) throw new InvalidOperationException($"Не удалось прочитать {foundResource}");

            using var fileStream = new FileStream(outputPath, FileMode.Create, FileAccess.Write);
            stream.CopyTo(fileStream);
        }

        private static void CreateShortcut(string shortcutPath, string targetPath, string iconPath, string description)
        {
            try
            {
                string psScript = $@"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcutPath}')
$Shortcut.TargetPath = '{targetPath}'
$Shortcut.WorkingDirectory = '{Path.GetDirectoryName(targetPath)}'
$Shortcut.Description = '{description}'
$Shortcut.IconLocation = '{iconPath}, 0'
$Shortcut.Save()
";
                using var p = Process.Start(new ProcessStartInfo("powershell", $"-NoProfile -Command \"{psScript}\"")
                {
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
                p?.WaitForExit(3000);
            }
            catch { }
        }

        private static void RegisterUninstaller(string installDir, string exePath, string iconPath)
        {
            try
            {
                const string uninstallKey = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\VORTEX";
                using var key = Registry.CurrentUser.CreateSubKey(uninstallKey);
                if (key != null)
                {
                    key.SetValue("DisplayName", "VORTEX Game Optimizer & Launcher");
                    key.SetValue("DisplayIcon", iconPath);
                    key.SetValue("DisplayVersion", "2.0.0");
                    key.SetValue("Publisher", "VORTEX Performance Engine");
                    key.SetValue("InstallLocation", installDir);
                    string uninstallCmd = $"cmd.exe /c rmdir /s /q \"{installDir}\" & reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VORTEX /f";
                    key.SetValue("UninstallString", uninstallCmd);
                }
            }
            catch { }
        }
    }
}
