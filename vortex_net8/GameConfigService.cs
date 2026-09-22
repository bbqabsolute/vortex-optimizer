using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VortexNet8
{
    public class GameSettingEntry
    {
        public string Key { get; set; } = string.Empty;
        public string CustomName { get; set; } = string.Empty;
        public string CustomBackgroundPath { get; set; } = string.Empty;
        public string ExecutablePath { get; set; } = string.Empty;
        public string LaunchUriOrArgs { get; set; } = string.Empty;
        public string ProcessName { get; set; } = string.Empty;
        public string IconEmoji { get; set; } = "🎮";
        public string Description { get; set; } = string.Empty;
        public bool IsCustom { get; set; } = false;
    }

    public class GameConfigData
    {
        public List<GameSettingEntry> Games { get; set; } = new();
    }

    public static class GameConfigService
    {
        private static readonly string ConfigPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "VORTEX",
            "games_config.json");

        public static void SaveConfig(IEnumerable<InstalledGame> games)
        {
            try
            {
                string dir = Path.GetDirectoryName(ConfigPath)!;
                if (!Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }

                var data = new GameConfigData();
                foreach (var g in games)
                {
                    data.Games.Add(new GameSettingEntry
                    {
                        Key = g.Key,
                        CustomName = g.CustomName,
                        CustomBackgroundPath = g.CustomBackgroundPath,
                        ExecutablePath = g.ExecutablePath,
                        LaunchUriOrArgs = g.LaunchUriOrArgs,
                        ProcessName = g.ProcessName,
                        IconEmoji = g.IconEmoji,
                        Description = g.Description,
                        IsCustom = g.IsCustom
                    });
                }

                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(data, options);
                File.WriteAllText(ConfigPath, json);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[GameConfigService] Save error: {ex.Message}");
            }
        }

        public static void ApplyConfig(List<InstalledGame> detectedGames)
        {
            try
            {
                if (!File.Exists(ConfigPath)) return;

                string json = File.ReadAllText(ConfigPath);
                var data = JsonSerializer.Deserialize<GameConfigData>(json);
                if (data == null || data.Games == null) return;

                var existingKeys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                foreach (var g in detectedGames)
                {
                    existingKeys.Add(g.Key);
                }

                foreach (var entry in data.Games)
                {
                    var found = detectedGames.Find(g => string.Equals(g.Key, entry.Key, StringComparison.OrdinalIgnoreCase));
                    if (found != null)
                    {
                        if (!string.IsNullOrEmpty(entry.CustomName))
                        {
                            found.CustomName = entry.CustomName;
                            found.Name = entry.CustomName;
                            found.FullName = entry.CustomName;
                        }
                        if (!string.IsNullOrEmpty(entry.CustomBackgroundPath))
                        {
                            found.CustomBackgroundPath = entry.CustomBackgroundPath;
                        }
                    }
                    else if (entry.IsCustom)
                    {
                        // Пользовательская игра, добавленная ранее
                        var customGame = new InstalledGame
                        {
                            Key = entry.Key,
                            Name = !string.IsNullOrEmpty(entry.CustomName) ? entry.CustomName : (!string.IsNullOrEmpty(entry.ExecutablePath) ? Path.GetFileNameWithoutExtension(entry.ExecutablePath) : "Игра"),
                            FullName = !string.IsNullOrEmpty(entry.CustomName) ? entry.CustomName : (!string.IsNullOrEmpty(entry.ExecutablePath) ? Path.GetFileNameWithoutExtension(entry.ExecutablePath) : "Игра"),
                            CustomName = entry.CustomName,
                            CustomBackgroundPath = entry.CustomBackgroundPath,
                            ExecutablePath = entry.ExecutablePath,
                            LaunchUriOrArgs = entry.LaunchUriOrArgs,
                            ProcessName = !string.IsNullOrEmpty(entry.ProcessName) ? entry.ProcessName : (!string.IsNullOrEmpty(entry.ExecutablePath) ? Path.GetFileNameWithoutExtension(entry.ExecutablePath) : ""),
                            IconEmoji = string.IsNullOrEmpty(entry.IconEmoji) ? "🎮" : entry.IconEmoji,
                            Description = string.IsNullOrEmpty(entry.Description) ? $"Запуск {entry.CustomName} с оптимизацией VORTEX" : entry.Description,
                            IsCustom = true,
                            IsInstalled = File.Exists(entry.ExecutablePath) || (!string.IsNullOrEmpty(entry.LaunchUriOrArgs) && entry.LaunchUriOrArgs.Contains("://"))
                        };
                        detectedGames.Add(customGame);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[GameConfigService] Load error: {ex.Message}");
            }
        }
    }
}
