using System;
using System.Runtime.InteropServices;
using Microsoft.Win32;

namespace VortexNet8
{
    public static class FilterKeysService
    {
        private const string KeyPath = @"Control Panel\Accessibility\Keyboard Response";
        private const uint SPI_SETFILTERKEYS = 0x0033;
        private const uint SPIF_SENDCHANGE = 0x0002;
        private const uint FKF_FILTERKEYSON = 0x00000001;
        private const uint FKF_AVAILABLE = 0x00000002;

        [StructLayout(LayoutKind.Sequential)]
        private struct FILTERKEYS
        {
            public uint cbSize;
            public uint dwFlags;
            public uint iWaitMSec;
            public uint iDelayMSec;
            public uint iRepeatMSec;
            public uint iBounceMSec;
        }

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool SystemParametersInfo(uint uiAction, uint uiParam, ref FILTERKEYS pvParam, uint fWinIni);

        public static bool ApplyTurbo(int delayMs = 150, int repeatMs = 15)
        {
            try
            {
                using var key = Registry.CurrentUser.CreateSubKey(KeyPath);
                if (key != null)
                {
                    key.SetValue("AutoRepeatDelay", delayMs.ToString());
                    key.SetValue("AutoRepeatRate", repeatMs.ToString());
                    key.SetValue("BounceTime", "0");
                    key.SetValue("DelayBeforeAcceptance", "0");
                    key.SetValue("Flags", "126");
                }

                var fk = new FILTERKEYS
                {
                    cbSize = (uint)Marshal.SizeOf<FILTERKEYS>(),
                    dwFlags = FKF_FILTERKEYSON | FKF_AVAILABLE,
                    iWaitMSec = 0,
                    iDelayMSec = (uint)delayMs,
                    iRepeatMSec = (uint)repeatMs,
                    iBounceMSec = 0
                };

                SystemParametersInfo(SPI_SETFILTERKEYS, fk.cbSize, ref fk, SPIF_SENDCHANGE);
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool ResetDefault()
        {
            try
            {
                using var key = Registry.CurrentUser.CreateSubKey(KeyPath);
                if (key != null)
                {
                    key.SetValue("AutoRepeatDelay", "1000");
                    key.SetValue("AutoRepeatRate", "31");
                    key.SetValue("BounceTime", "0");
                    key.SetValue("DelayBeforeAcceptance", "0");
                    key.SetValue("Flags", "122");
                }

                var fk = new FILTERKEYS
                {
                    cbSize = (uint)Marshal.SizeOf<FILTERKEYS>(),
                    dwFlags = 0, // Disable FilterKeys
                    iWaitMSec = 0,
                    iDelayMSec = 1000,
                    iRepeatMSec = 31,
                    iBounceMSec = 0
                };

                SystemParametersInfo(SPI_SETFILTERKEYS, fk.cbSize, ref fk, SPIF_SENDCHANGE);
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool IsTurboActive()
        {
            try
            {
                using var key = Registry.CurrentUser.OpenSubKey(KeyPath);
                var val = key?.GetValue("AutoRepeatDelay")?.ToString();
                return val == "150" || val == "130";
            }
            catch
            {
                return false;
            }
        }
    }
}
