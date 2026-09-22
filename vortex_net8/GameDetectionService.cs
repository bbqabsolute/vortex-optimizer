using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using Microsoft.Win32;

namespace VortexNet8
{
    public class InstalledGame
    {
        public string Key { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string FullName { get; set; } = string.Empty;
        public string ExecutablePath { get; set; } = string.Empty;
        public string LaunchUriOrArgs { get; set; } = string.Empty;
        public string ProcessName { get; set; } = string.Empty;
        public string IconEmoji { get; set; } = "🎮";
        public string Description { get; set; } = string.Empty;
        public string CustomBackgroundPath { get; set; } = string.Empty;
        public string CustomName { get; set; } = string.Empty;
        public bool IsCustom { get; set; } = false;
        public bool IsInstalled { get; set; } = false;
        public string DisplayTitle => !string.IsNullOrEmpty(CustomName) ? CustomName : Name;
        public string DisplayPath => string.IsNullOrEmpty(ExecutablePath) ? "Не найдена" : ExecutablePath;
    }

    public static class GameDetectionService
    {
        public static List<InstalledGame> DetectInstalledGames()
        {
            var games = new List<InstalledGame>();

            // 1. Fortnite
            var fnGame = DetectFortnite();
            if (fnGame.IsInstalled)
            {
                games.Add(fnGame);
            }

            // 2. Counter-Strike 2
            var cs2Game = DetectCS2();
            if (cs2Game.IsInstalled)
            {
                games.Add(cs2Game);
            }

            return games;
        }

        public static InstalledGame DetectFortnite()
        {
            var game = new InstalledGame
            {
                Key = "fortnite",
                Name = "Fortnite",
                FullName = "Fortnite Battle Royale",
                ProcessName = "FortniteClient-Win64-Shipping",
                IconEmoji = "🎮",
                Description = "Нажмите «ЗАПУСК»: применится 0.5 мс таймер, FilterKeys 150 мс, Standby RAM и игра откроется.",
                LaunchUriOrArgs = "com.epicgames.launcher://apps/Fortnite?action=launch&silent=true"
            };

            string[] candidatePaths = new[]
            {
                @"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe",
                @"D:\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe",
                @"E:\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe",
                @"C:\Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe"
            };

            foreach (var p in candidatePaths)
            {
                if (File.Exists(p))
                {
                    game.ExecutablePath = p;
                    game.IsInstalled = true;
                    return game;
                }
            }

            // Check Epic Games registry / manifests
            try
            {
                string manifestsDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "Epic", "EpicGamesLauncher", "Data", "Manifests");
                if (Directory.Exists(manifestsDir))
                {
                    foreach (var file in Directory.GetFiles(manifestsDir, "*.item"))
                    {
                        string content = File.ReadAllText(file);
                        if (content.Contains("Fortnite") && content.Contains("InstallLocation"))
                        {
                            int idx = content.IndexOf("\"InstallLocation\":");
                            if (idx >= 0)
                            {
                                int start = content.IndexOf('"', idx + 18) + 1;
                                int end = content.IndexOf('"', start);
                                if (start > 0 && end > start)
                                {
                                    string installLoc = content.Substring(start, end - start).Replace(@"\\", @"\");
                                    string exe = Path.Combine(installLoc, "FortniteGame", "Binaries", "Win64", "FortniteClient-Win64-Shipping.exe");
                                    if (File.Exists(exe))
                                    {
                                        game.ExecutablePath = exe;
                                        game.IsInstalled = true;
                                        return game;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            catch { }

            // Default fallback if found on standard C: path
            game.ExecutablePath = candidatePaths[0];
            game.IsInstalled = File.Exists(candidatePaths[0]);
            return game;
        }

        public static InstalledGame DetectCS2()
        {
            var game = new InstalledGame
            {
                Key = "cs2",
                Name = "CS 2",
                FullName = "Counter-Strike 2",
                ProcessName = "cs2",
                IconEmoji = "💣",
                Description = "Нажмите «ЗАПУСК»: применится 0.5 мс таймер, Reflex Low Latency, сброс памяти и откроется CS2.",
                LaunchUriOrArgs = "steam://rungameid/730"
            };

            string[] candidatePaths = new[]
            {
                @"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe",
                @"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe",
                @"D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe",
                @"C:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe"
            };

            foreach (var p in candidatePaths)
            {
                if (File.Exists(p))
                {
                    game.ExecutablePath = p;
                    game.IsInstalled = true;
                    return game;
                }
            }

            // Check Steam registry install path
            try
            {
                using var key = Registry.CurrentUser.OpenSubKey(@"Software\Valve\Steam");
                var steamPath = key?.GetValue("SteamPath")?.ToString();
                if (!string.IsNullOrEmpty(steamPath))
                {
                    string defaultExe = Path.Combine(steamPath, "steamapps", "common", "Counter-Strike Global Offensive", "game", "bin", "win64", "cs2.exe");
                    if (File.Exists(defaultExe))
                    {
                        game.ExecutablePath = defaultExe;
                        game.IsInstalled = true;
                        return game;
                    }
                }
            }
            catch { }

            game.ExecutablePath = candidatePaths[0];
            game.IsInstalled = File.Exists(candidatePaths[0]);
            return game;
        }

        public static bool IsGameRunning(InstalledGame game)
        {
            if (string.IsNullOrEmpty(game.ProcessName)) return false;
            try
            {
                var procs = Process.GetProcessesByName(game.ProcessName);
                if (procs != null && procs.Length > 0) return true;

                if (game.Key == "fortnite")
                {
                    var f1 = Process.GetProcessesByName("FortniteLauncher");
                    if (f1 != null && f1.Length > 0) return true;
                }
            }
            catch { }
            return false;
        }

        public static bool LaunchGame(InstalledGame game)
        {
            try
            {
                // Prefer URI protocol if available (starts via Steam/Epic directly)
                if (!string.IsNullOrEmpty(game.LaunchUriOrArgs) && game.LaunchUriOrArgs.Contains("://"))
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = game.LaunchUriOrArgs,
                        UseShellExecute = true
                    };
                    Process.Start(psi);
                    return true;
                }

                if (File.Exists(game.ExecutablePath))
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = game.ExecutablePath,
                        WorkingDirectory = Path.GetDirectoryName(game.ExecutablePath) ?? "",
                        UseShellExecute = true
                    };
                    Process.Start(psi);
                    return true;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[GameDetectionService] Launch error: {ex.Message}");
                // Fallback to direct executable start
                try
                {
                    if (File.Exists(game.ExecutablePath))
                    {
                        Process.Start(new ProcessStartInfo
                        {
                            FileName = game.ExecutablePath,
                            UseShellExecute = true
                        });
                        return true;
                    }
                }
                catch { }
            }
            return false;
        }

        public static bool CloseGame(InstalledGame game)
        {
            bool closed = false;
            try
            {
                string[] targets;
                if (game.Key == "fortnite")
                {
                    targets = new[] { "FortniteClient-Win64-Shipping", "FortniteLauncher", "FortniteClient-Win64-Shipping_EAC", "FortniteClient-Win64-Shipping_BE" };
                }
                else if (game.Key == "cs2")
                {
                    targets = new[] { "cs2" };
                }
                else
                {
                    targets = new[] { game.ProcessName };
                }

                foreach (var target in targets)
                {
                    if (string.IsNullOrEmpty(target)) continue;
                    foreach (var proc in Process.GetProcessesByName(target))
                    {
                        try
                        {
                            proc.Kill();
                            proc.WaitForExit(1000);
                            closed = true;
                        }
                        catch { }
                    }
                }
            }
            catch { }
            return closed;
        }
    }
}
