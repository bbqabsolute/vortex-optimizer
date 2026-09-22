using System;
using System.Diagnostics;
using System.IO;
using Microsoft.Win32;

namespace VortexNet8
{
    public static class AutostartService
    {
        private const string TaskName = "VORTEX_Optimizer";
        private const string RunKey = @"Software\Microsoft\Windows\CurrentVersion\Run";

        public static bool IsAutostartEnabled()
        {
            try
            {
                using var p = Process.Start(new ProcessStartInfo("schtasks", $"/query /tn \"{TaskName}\"")
                {
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
                p?.WaitForExit(2000);
                if (p?.ExitCode == 0) return true;

                using var key = Registry.CurrentUser.OpenSubKey(RunKey);
                return key?.GetValue("VORTEX") != null;
            }
            catch
            {
                return false;
            }
        }

        public static bool EnableAutostart() => SetAutostart(true, true);

        public static bool DisableAutostart() => SetAutostart(false, false);

        public static bool SetAutostart(bool enable, bool minimized = true)
        {
            try
            {
                string exePath = Process.GetCurrentProcess().MainModule?.FileName ?? "";
                if (string.IsNullOrEmpty(exePath)) return false;

                if (enable)
                {
                    string args = minimized ? "--minimized" : "";
                    string cmd = $"schtasks /create /tn \"{TaskName}\" /tr \"\\\"{exePath}\\\" {args}\" /sc onlogon /rl highest /f";
                    using var p = Process.Start(new ProcessStartInfo("cmd.exe", $"/c {cmd}")
                    {
                        CreateNoWindow = true,
                        UseShellExecute = false
                    });
                    p?.WaitForExit(3000);

                    using var key = Registry.CurrentUser.CreateSubKey(RunKey);
                    key?.SetValue("VORTEX", $"\"{exePath}\" {args}");
                    return true;
                }
                else
                {
                    using var p = Process.Start(new ProcessStartInfo("schtasks", $"/delete /tn \"{TaskName}\" /f")
                    {
                        CreateNoWindow = true,
                        UseShellExecute = false
                    });
                    p?.WaitForExit(2000);

                    using var key = Registry.CurrentUser.CreateSubKey(RunKey);
                    key?.DeleteValue("VORTEX", false);
                    return true;
                }
            }
            catch
            {
                return false;
            }
        }
    }
}
