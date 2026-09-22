using System;
using System.Diagnostics;
using System.IO;

namespace VortexNet8
{
    public static class ShortcutService
    {
        public static string CleanFileName(string fileName)
        {
            foreach (char c in Path.GetInvalidFileNameChars())
            {
                fileName = fileName.Replace(c, '_');
            }
            return fileName.Trim();
        }

        public static bool CreateDesktopShortcut(InstalledGame game, string? vortexExePath = null)
        {
            try
            {
                Type? shellType = Type.GetTypeFromProgID("WScript.Shell");
                if (shellType == null) return false;

                dynamic? shell = Activator.CreateInstance(shellType);
                if (shell == null) return false;

                string desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                string cleanName = CleanFileName(game.DisplayTitle);
                string shortcutPath = Path.Combine(desktop, $"{cleanName} (VORTEX).lnk");

                dynamic shortcut = shell.CreateShortcut(shortcutPath);

                string exePath = vortexExePath ?? Environment.ProcessPath ?? Process.GetCurrentProcess().MainModule?.FileName ?? @"C:\Users\bbq\Desktop\VORTEX.exe";
                shortcut.TargetPath = exePath;
                shortcut.Arguments = $"--launch \"{game.Key}\" --console";
                shortcut.WorkingDirectory = Path.GetDirectoryName(exePath) ?? @"C:\Users\bbq\Desktop";

                // Устанавливаем иконку оригинальной игры
                if (File.Exists(game.ExecutablePath))
                {
                    shortcut.IconLocation = $"{game.ExecutablePath},0";
                }
                else
                {
                    shortcut.IconLocation = $"{exePath},0";
                }

                shortcut.Description = $"Запуск {game.DisplayTitle} через VORTEX с нулевым инпутлагом и оптимизацией ядра 0.500 мс";
                shortcut.Save();
                return true;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ShortcutService] Create shortcut error: {ex.Message}");
                return false;
            }
        }

        public static InstalledGame? ResolveFile(string filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath)) return null;

            string ext = Path.GetExtension(filePath).ToLowerInvariant();
            string baseName = Path.GetFileNameWithoutExtension(filePath);

            try
            {
                if (ext == ".lnk")
                {
                    Type? shellType = Type.GetTypeFromProgID("WScript.Shell");
                    if (shellType != null)
                    {
                        dynamic? shell = Activator.CreateInstance(shellType);
                        if (shell != null)
                        {
                            dynamic sc = shell.CreateShortcut(filePath);
                            string targetPath = sc.TargetPath?.ToString() ?? "";
                            string arguments = sc.Arguments?.ToString() ?? "";

                            string finalExe = targetPath;
                            string procName = !string.IsNullOrEmpty(finalExe) ? Path.GetFileNameWithoutExtension(finalExe) : baseName;
                            string gameName = baseName;

                            // Очистим название от приставок типа " - Shortcut" или " - Ярлык"
                            gameName = gameName.Replace(" - Shortcut", "", StringComparison.OrdinalIgnoreCase)
                                               .Replace(" - Ярлык", "", StringComparison.OrdinalIgnoreCase).Trim();

                            return new InstalledGame
                            {
                                Key = "custom_" + Guid.NewGuid().ToString("N")[..8],
                                Name = gameName,
                                FullName = gameName,
                                ExecutablePath = finalExe,
                                LaunchUriOrArgs = !string.IsNullOrEmpty(arguments) ? arguments : "",
                                ProcessName = procName,
                                IconEmoji = "🎮",
                                Description = $"Нажмите «ЗАПУСК»: система оптимизируется, и {gameName} откроется автоматически.",
                                IsCustom = true,
                                IsInstalled = File.Exists(finalExe) || !string.IsNullOrEmpty(finalExe)
                            };
                        }
                    }
                }
                else if (ext == ".url")
                {
                    string[] lines = File.ReadAllLines(filePath);
                    string targetUrl = "";
                    foreach (var line in lines)
                    {
                        if (line.StartsWith("URL=", StringComparison.OrdinalIgnoreCase))
                        {
                            targetUrl = line.Substring(4).Trim();
                            break;
                        }
                    }

                    string gameName = baseName.Replace(" - Shortcut", "", StringComparison.OrdinalIgnoreCase)
                                              .Replace(" - Ярлык", "", StringComparison.OrdinalIgnoreCase).Trim();

                    return new InstalledGame
                    {
                        Key = "custom_" + Guid.NewGuid().ToString("N")[..8],
                        Name = gameName,
                        FullName = gameName,
                        ExecutablePath = "",
                        LaunchUriOrArgs = targetUrl,
                        ProcessName = gameName,
                        IconEmoji = "🎮",
                        Description = $"Нажмите «ЗАПУСК»: система оптимизируется, и {gameName} откроется автоматически.",
                        IsCustom = true,
                        IsInstalled = true
                    };
                }
                else if (ext == ".exe")
                {
                    string gameName = baseName;
                    try
                    {
                        var vi = FileVersionInfo.GetVersionInfo(filePath);
                        if (!string.IsNullOrWhiteSpace(vi.ProductName) && vi.ProductName.Length > 2)
                        {
                            gameName = vi.ProductName.Trim();
                        }
                    }
                    catch { }

                    return new InstalledGame
                    {
                        Key = "custom_" + Guid.NewGuid().ToString("N")[..8],
                        Name = gameName,
                        FullName = gameName,
                        ExecutablePath = filePath,
                        LaunchUriOrArgs = "",
                        ProcessName = Path.GetFileNameWithoutExtension(filePath),
                        IconEmoji = "🎮",
                        Description = $"Нажмите «ЗАПУСК»: система оптимизируется, и {gameName} откроется автоматически.",
                        IsCustom = true,
                        IsInstalled = true
                    };
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ShortcutService] Resolve error: {ex.Message}");
            }

            return null;
        }
    }
}
