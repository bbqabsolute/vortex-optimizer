# ============================================================
#  resolution.ps1 - Fortnite Optimizer
#  Changes display resolution via ChangeDisplaySettingsEx
# ============================================================
param(
    [int]$targetW = 1920,
    [int]$targetH = 1080,
    [int]$targetR = 0
)

# Verify admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[RES] ! Need admin rights to change resolution"
    exit 1
}

$sig = @'
using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;

public class DisplayChanger {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct DEVMODEW {
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)]
        public char[] dmDeviceName;
        public ushort dmSpecVersion;
        public ushort dmDriverVersion;
        public ushort dmSize;
        public ushort dmDriverExtra;
        public uint   dmFields;
        public int    dmPositionX;
        public int    dmPositionY;
        public uint   dmDisplayOrientation;
        public uint   dmDisplayFixedOutput;
        public short  dmColor;
        public short  dmDuplex;
        public short  dmYResolution;
        public short  dmTTOption;
        public short  dmCollate;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)]
        public char[] dmFormName;
        public ushort dmLogPixels;
        public uint   dmBitsPerPel;
        public uint   dmPelsWidth;
        public uint   dmPelsHeight;
        public uint   dmDisplayFlags;
        public uint   dmDisplayFrequency;
        public uint   dmICMMethod;
        public uint   dmICMIntent;
        public uint   dmMediaType;
        public uint   dmDitherType;
        public uint   dmReserved1;
        public uint   dmReserved2;
        public uint   dmPanningWidth;
        public uint   dmPanningHeight;
    }

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern bool EnumDisplaySettingsW(string d, int n, ref DEVMODEW m);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int ChangeDisplaySettingsExW(string d, ref DEVMODEW m, IntPtr h, uint f, IntPtr l);

    public static DEVMODEW MakeDM() {
        var dm = new DEVMODEW();
        dm.dmDeviceName = new char[32];
        dm.dmFormName   = new char[32];
        dm.dmSize       = (ushort)Marshal.SizeOf(dm);
        return dm;
    }

    public static string GetCurrent() {
        var dm = MakeDM();
        EnumDisplaySettingsW(null, -1, ref dm);
        return dm.dmPelsWidth + "x" + dm.dmPelsHeight + " @ " + dm.dmDisplayFrequency + "Hz";
    }

    // Find a valid enumerated mode matching W, H, (optionally freq), then apply it directly
    public static string Apply(int width, int height, int freq) {
        int idx = 0;
        var found = new DEVMODEW();
        bool matched = false;

        var dm = MakeDM();
        while (EnumDisplaySettingsW(null, idx, ref dm)) {
            if (dm.dmBitsPerPel == 32 && dm.dmPelsWidth == (uint)width && dm.dmPelsHeight == (uint)height) {
                if (freq > 0) {
                    if (dm.dmDisplayFrequency == (uint)freq) {
                        found = dm;
                        matched = true;
                        break;
                    }
                } else {
                    // No freq preference - pick highest available
                    if ((int)dm.dmDisplayFrequency > (matched ? (int)found.dmDisplayFrequency : -1)) {
                        found = dm;
                        matched = true;
                    }
                }
            }
            idx++;
        }

        if (!matched) {
            return "NOMATCH";
        }

        // Try CDS_UPDATEREGISTRY first (flag=1), then CDS_NONE (flag=0) as fallback
        int result = ChangeDisplaySettingsExW(null, ref found, IntPtr.Zero, 1, IntPtr.Zero);
        if (result != 0 && result != 1) {
            result = ChangeDisplaySettingsExW(null, ref found, IntPtr.Zero, 0, IntPtr.Zero);
        }
        return "APPLY:" + result + ":" + found.dmPelsWidth + "x" + found.dmPelsHeight + "@" + found.dmDisplayFrequency;
    }
}
'@

try {
    Add-Type -TypeDefinition $sig -Language CSharp -ErrorAction Stop

    $cur = [DisplayChanger]::GetCurrent()
    Write-Host "[RES] Current: $cur"

    $result = [DisplayChanger]::Apply($targetW, $targetH, $targetR)

    if ($result -eq "NOMATCH") {
        Write-Host "[RES] ! Resolution ${targetW}x${targetH} not found in supported modes"
    } else {
        $parts  = $result.Split(':')
        $tag    = $parts[0]
        $code   = [int]$parts[1]
        $modeStr = $parts[2]
        switch ($code) {
             0 { Write-Host "[RES] + Applied: $modeStr" }
             1 { Write-Host "[RES] + Applied (restart required): $modeStr" }
            -1 { Write-Host "[RES] ! Failed to apply (DISP_CHANGE_FAILED)" }
            -2 { Write-Host "[RES] ! Mode not supported (DISP_CHANGE_BADMODE)" }
            -5 { Write-Host "[RES] ! No permission to change resolution" }
            default { Write-Host "[RES] ! Result code: $code for mode: $modeStr" }
        }
    }
} catch {
    Write-Host "[RES] ! Error: $_"
}
