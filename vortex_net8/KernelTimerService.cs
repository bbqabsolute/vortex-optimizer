using System;
using System.Runtime.InteropServices;

namespace VortexNet8
{
    public static class KernelTimerService
    {
        [DllImport("ntdll.dll", SetLastError = true)]
        private static extern int NtSetTimerResolution(uint DesiredResolution, [MarshalAs(UnmanagedType.I1)] bool SetResolution, out uint CurrentResolution);

        [DllImport("ntdll.dll", SetLastError = true)]
        private static extern int NtQueryTimerResolution(out uint MinimumResolution, out uint MaximumResolution, out uint CurrentResolution);

        public static bool SetTimer05ms()
        {
            try
            {
                // 5000 units of 100ns = 0.500 ms (500,000 ns = 0.5 ms)
                int status = NtSetTimerResolution(5000, true, out _);
                return status == 0;
            }
            catch
            {
                return false;
            }
        }

        public static double GetCurrentResolutionMs()
        {
            try
            {
                int status = NtQueryTimerResolution(out _, out _, out uint currentRes);
                if (status == 0)
                {
                    // 100ns units -> milliseconds: (currentRes * 100) / 1,000,000 = currentRes / 10000.0
                    return currentRes / 10000.0;
                }
            }
            catch { }
            return 0.500;
        }
    }
}
