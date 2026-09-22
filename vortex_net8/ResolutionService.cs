using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace VortexNet8
{
    public static class ResolutionService
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct DEVMODEW
        {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmDeviceName;
            public ushort dmSpecVersion;
            public ushort dmDriverVersion;
            public ushort dmSize;
            public ushort dmDriverExtra;
            public uint dmFields;
            public int dmPositionX;
            public int dmPositionY;
            public uint dmDisplayOrientation;
            public uint dmDisplayFixedOutput;
            public short dmColor;
            public short dmDuplex;
            public short dmYResolution;
            public short dmTTOption;
            public short dmCollate;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmFormName;
            public ushort dmLogPixels;
            public uint dmBitsPerPel;
            public uint dmPelsWidth;
            public uint dmPelsHeight;
            public uint dmDisplayFlags;
            public uint dmDisplayFrequency;
        }

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        private static extern bool EnumDisplaySettingsW(string? lpszDeviceName, int iModeNum, ref DEVMODEW lpDevMode);

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        private static extern int ChangeDisplaySettingsExW(string? lpszDeviceName, ref DEVMODEW lpDevMode, IntPtr hwnd, uint dwflags, IntPtr lParam);

        public static string GetIniPath()
        {
            string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            return Path.Combine(localApp, "FortniteGame", "Saved", "Config", "WindowsClient", "GameUserSettings.ini");
        }

        public static (bool exists, int width, int height, bool isReadOnly) GetStatus()
        {
            string path = GetIniPath();
            if (!File.Exists(path))
                return (false, 1920, 1080, false);

            try
            {
                var fi = new FileInfo(path);
                bool ro = fi.IsReadOnly;
                int w = 1920, h = 1080;

                foreach (var line in File.ReadLines(path))
                {
                    var trimmed = line.Trim();
                    if (trimmed.StartsWith("ResolutionSizeX="))
                    {
                        if (int.TryParse(trimmed.Substring("ResolutionSizeX=".Length), out int rw))
                            w = rw;
                    }
                    else if (trimmed.StartsWith("ResolutionSizeY="))
                    {
                        if (int.TryParse(trimmed.Substring("ResolutionSizeY=".Length), out int rh))
                            h = rh;
                    }
                }

                return (true, w, h, ro);
            }
            catch
            {
                return (true, 1920, 1080, false);
            }
        }

        public static bool ToggleReadOnly()
        {
            string path = GetIniPath();
            if (!File.Exists(path)) return false;

            try
            {
                var fi = new FileInfo(path);
                fi.IsReadOnly = !fi.IsReadOnly;
                return fi.IsReadOnly;
            }
            catch
            {
                return false;
            }
        }

        public static bool ApplyFortniteResolution(int width, int height, int hz)
        {
            string path = GetIniPath();
            if (!File.Exists(path)) return false;

            try
            {
                var fi = new FileInfo(path);
                if (fi.IsReadOnly)
                    fi.IsReadOnly = false;

                var lines = File.ReadAllLines(path);
                var targetFields = new Dictionary<string, string>
                {
                    { "ResolutionSizeX", width.ToString() },
                    { "ResolutionSizeY", height.ToString() },
                    { "LastUserConfirmedResolutionSizeX", width.ToString() },
                    { "LastUserConfirmedResolutionSizeY", height.ToString() },
                    { "DesiredScreenWidth", width.ToString() },
                    { "DesiredScreenHeight", height.ToString() },
                    { "LastUserConfirmedDesiredScreenWidth", width.ToString() },
                    { "LastUserConfirmedDesiredScreenHeight", height.ToString() },
                    { "FullscreenMode", "0" },
                    { "LastConfirmedFullscreenMode", "0" },
                    { "PreferredFullscreenMode", "0" },
                    { "bUseDesiredScreenHeight", "False" },
                    { "bUseVSync", "False" },
                    { "bUseDynamicResolution", "False" },
                    { "sg.ResolutionQuality", "100" }
                };

                if (hz > 0)
                    targetFields["FrameRateLimit"] = $"{hz:F6}";

                var newLines = new List<string>();
                var updated = new HashSet<string>();

                foreach (var line in lines)
                {
                    var trimmed = line.Trim();
                    bool matched = false;
                    foreach (var kvp in targetFields)
                    {
                        if (trimmed.StartsWith(kvp.Key + "="))
                        {
                            newLines.Add($"{kvp.Key}={kvp.Value}");
                            updated.Add(kvp.Key);
                            matched = true;
                            break;
                        }
                    }
                    if (!matched)
                        newLines.Add(line);
                }

                // If any parameters weren't in file, add them to section
                var missing = new Dictionary<string, string>();
                foreach (var kvp in targetFields)
                {
                    if (!updated.Contains(kvp.Key))
                        missing[kvp.Key] = kvp.Value;
                }

                if (missing.Count > 0)
                {
                    int sectionIdx = newLines.FindIndex(l => l.Trim() == "[/Script/FortniteGame.FortGameUserSettings]");
                    if (sectionIdx >= 0)
                    {
                        foreach (var kvp in missing)
                            newLines.Insert(sectionIdx + 1, $"{kvp.Key}={kvp.Value}");
                    }
                    else
                    {
                        newLines.Add("[/Script/FortniteGame.FortGameUserSettings]");
                        foreach (var kvp in missing)
                            newLines.Add($"{kvp.Key}={kvp.Value}");
                    }
                }

                File.WriteAllLines(path, newLines);

                // Lock with Read-Only against in-match resets!
                fi.Refresh();
                fi.IsReadOnly = true;

                ConfigService.Set("RESOLUTION_WIDTH", width.ToString());
                ConfigService.Set("RESOLUTION_HEIGHT", height.ToString());
                if (hz > 0) ConfigService.Set("RESOLUTION_REFRESH", hz.ToString());

                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool ApplyResolution(int width, int height, int hz = 180, bool setReadOnly = true)
        {
            return ApplyFortniteResolution(width, height, hz);
        }

        public static bool ApplyDesktopResolution(int width, int height, int hz)
        {
            try
            {
                DEVMODEW dm = new DEVMODEW();
                dm.dmSize = (ushort)Marshal.SizeOf<DEVMODEW>();

                int i = 0;
                DEVMODEW? matched = null;

                while (EnumDisplaySettingsW(null, i, ref dm))
                {
                    if (dm.dmBitsPerPel == 32 && dm.dmPelsWidth == width && dm.dmPelsHeight == height)
                    {
                        if (hz > 0)
                        {
                            if (dm.dmDisplayFrequency == hz)
                            {
                                matched = dm;
                                break;
                            }
                        }
                        else
                        {
                            if (!matched.HasValue || dm.dmDisplayFrequency > matched.Value.dmDisplayFrequency)
                            {
                                matched = dm;
                            }
                        }
                    }
                    i++;
                }

                if (matched.HasValue)
                {
                    var target = matched.Value;
                    int res = ChangeDisplaySettingsExW(null, ref target, IntPtr.Zero, 1 /* CDS_UPDATEREGISTRY */, IntPtr.Zero);
                    if (res != 0 && res != 1)
                        res = ChangeDisplaySettingsExW(null, ref target, IntPtr.Zero, 0, IntPtr.Zero);
                    return res == 0 || res == 1;
                }
                return false;
            }
            catch
            {
                return false;
            }
        }
    }
}
