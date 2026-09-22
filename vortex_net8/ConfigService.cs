using System;
using System.IO;
using System.Collections.Generic;

namespace VortexNet8
{
    public static class ConfigService
    {
        private static readonly string ConfigDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config");
        private static readonly string ConfigFile = Path.Combine(ConfigDir, "settings.cfg");

        private static readonly Dictionary<string, string> DefaultSettings = new()
        {
            { "LAUNCH_EPIC", "1" },
            { "START_MINIMIZED", "1" },
            { "CLOSE_TO_TRAY", "1" },
            { "AUTO_OPTIMIZE_GAME", "1" },
            { "AUTO_TURBO_INPUT", "1" },
            { "MINIMIZE_ON_LAUNCH", "1" },
            { "RESOLUTION_WIDTH", "1920" },
            { "RESOLUTION_HEIGHT", "1080" },
            { "RESOLUTION_REFRESH", "180" },
            { "DNS_PRIMARY", "8.8.8.8" },
            { "DNS_SECONDARY", "8.8.4.4" },
            { "PRESET", "PRO_COMPETITIVE" },
            { "EPIC_PATH", @"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe" },
            { "FPS_BOOST", "1" },
            { "CPU_UNPARK", "1" },
            { "MSI_MODE", "1" },
            { "MOUSE_OPTIMIZE", "1" },
            { "FORTNITE_INI", "1" },
            { "RAM_CLEANUP", "1" },
            { "KILL_USELESS", "1" },
            { "HIGH_PRIORITY", "1" },
            { "DISABLE_DVRGAME", "1" },
            { "VISUAL_EFFECTS", "1" },
            { "NAGLE_OFF", "1" }
        };

        private static Dictionary<string, string> _current = new(DefaultSettings);

        static ConfigService()
        {
            Load();
        }

        public static string Get(string key, string defaultValue = "")
        {
            if (_current.TryGetValue(key, out var val))
                return val;
            return defaultValue;
        }

        public static bool GetBool(string key, bool defaultValue = false)
        {
            string val = Get(key, defaultValue ? "1" : "0");
            return val == "1" || val.Equals("true", StringComparison.OrdinalIgnoreCase);
        }

        public static void Set(string key, string value)
        {
            _current[key] = value;
            Save();
        }

        public static void SetBool(string key, bool value)
        {
            Set(key, value ? "1" : "0");
        }

        public static void ResetToDefaults()
        {
            _current = new Dictionary<string, string>(DefaultSettings);
            Save();
        }

        public static void Load()
        {
            try
            {
                if (!Directory.Exists(ConfigDir))
                    Directory.CreateDirectory(ConfigDir);

                if (!File.Exists(ConfigFile))
                {
                    Save();
                    return;
                }

                foreach (var line in File.ReadAllLines(ConfigFile))
                {
                    var trimmed = line.Trim();
                    if (string.IsNullOrEmpty(trimmed) || trimmed.StartsWith("#") || !trimmed.Contains('='))
                        continue;

                    int idx = trimmed.IndexOf('=');
                    string k = trimmed.Substring(0, idx).Trim();
                    string v = trimmed.Substring(idx + 1).Trim();
                    _current[k] = v;
                }
            }
            catch { }
        }

        public static void Save()
        {
            try
            {
                if (!Directory.Exists(ConfigDir))
                    Directory.CreateDirectory(ConfigDir);

                var lines = new List<string>
                {
                    "# VORTEX Configuration File",
                    $"# Saved at: {DateTime.Now}"
                };

                foreach (var kvp in _current)
                {
                    lines.Add($"{kvp.Key}={kvp.Value}");
                }

                File.WriteAllLines(ConfigFile, lines);
            }
            catch { }
        }
    }
}
