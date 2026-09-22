using System;
using System.Diagnostics;
using System.IO;
using System.Collections.Generic;
using Microsoft.Win32;

namespace VortexNet8
{
    public static class TweaksService
    {
        public static void ApplyAllOptimizations()
        {
            UnparkCpu();
            EnableUltimatePowerPlan();
            ApplyMouse1to1Curves();
            DisableGameDvr();
            OptimizeEngineIni();
            SetFortniteHighPriority();
        }

        public static bool UnparkCpu()
        {
            try
            {
                RunCmd("powercfg -setacvalueindex scheme_current sub_processor CPMINCORES 100");
                RunCmd("powercfg -setdcvalueindex scheme_current sub_processor CPMINCORES 100");
                RunCmd("powercfg -setactive scheme_current");
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool EnableUltimatePowerPlan()
        {
            try
            {
                RunCmd("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 381b4222-f694-41f0-9685-ff5bb260df2e");
                RunCmd("powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e");
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool ApplyMouse1to1Curves()
        {
            try
            {
                using var key = Registry.CurrentUser.OpenSubKey(@"Control Panel\Mouse", true);
                if (key != null)
                {
                    byte[] curveX = new byte[] {
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x15, 0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x40, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0xd0, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x40, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00
                    };
                    byte[] curveY = new byte[] {
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0xFD, 0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x24, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0xFC, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0xC0, 0xBB, 0x01, 0x00, 0x00, 0x00, 0x00
                    };

                    key.SetValue("SmoothMouseXCurve", curveX, RegistryValueKind.Binary);
                    key.SetValue("SmoothMouseYCurve", curveY, RegistryValueKind.Binary);
                    key.SetValue("MouseSensitivity", "10", RegistryValueKind.String);
                    key.SetValue("MouseSpeed", "0", RegistryValueKind.String);
                    key.SetValue("MouseThreshold1", "0", RegistryValueKind.String);
                    key.SetValue("MouseThreshold2", "0", RegistryValueKind.String);
                }
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool DisableGameDvr()
        {
            try
            {
                using (var key = Registry.CurrentUser.CreateSubKey(@"System\GameConfigStore"))
                {
                    key?.SetValue("GameDVR_Enabled", 0, RegistryValueKind.DWord);
                }
                using (var key = Registry.CurrentUser.CreateSubKey(@"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"))
                {
                    key?.SetValue("AppCaptureEnabled", 0, RegistryValueKind.DWord);
                }
                using (var key = Registry.LocalMachine.CreateSubKey(@"SOFTWARE\Policies\Microsoft\Windows\GameDVR"))
                {
                    key?.SetValue("AllowGameDVR", 0, RegistryValueKind.DWord);
                }
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool OptimizeEngineIni()
        {
            try
            {
                string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string engineIni = Path.Combine(localApp, "FortniteGame", "Saved", "Config", "WindowsClient", "Engine.ini");

                if (!File.Exists(engineIni))
                {
                    string dir = Path.GetDirectoryName(engineIni)!;
                    if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
                    File.WriteAllText(engineIni, "[Core.System]\r\nPaths=../../../Engine/Content\r\n\r\n");
                }

                var content = File.ReadAllText(engineIni);
                if (!content.Contains("[SystemSettings]"))
                {
                    string tweaks = "\r\n[SystemSettings]\r\nr.Streaming.FullyLoadUsedTextures=1\r\nr.ShadowQuality=0\r\nr.BloomQuality=0\r\nr.DepthOfFieldQuality=0\r\nr.MotionBlurQuality=0\r\nr.FastBlurThreshold=0\r\nr.LightShaftQuality=0\r\nr.RefractionQuality=0\r\nr.VolumetricFog=0\r\nr.MaterialQualityLevel=0\r\nr.Fog=0\r\n";
                    File.AppendAllText(engineIni, tweaks);
                }
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool SetFortniteHighPriority()
        {
            try
            {
                foreach (var p in Process.GetProcessesByName("FortniteClient-Win64-Shipping"))
                {
                    try { p.PriorityClass = ProcessPriorityClass.High; } catch { }
                }

                const string ifeoKey = @"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\FortniteClient-Win64-Shipping.exe\PerfOptions";
                using (var key = Registry.LocalMachine.CreateSubKey(ifeoKey))
                {
                    key?.SetValue("CpuPriorityClass", 3, RegistryValueKind.DWord);
                }
                return true;
            }
            catch
            {
                return false;
            }
        }

        private static void RunCmd(string cmd)
        {
            using var p = Process.Start(new ProcessStartInfo("cmd.exe", $"/c {cmd}")
            {
                CreateNoWindow = true,
                UseShellExecute = false
            });
            p?.WaitForExit(3000);
        }
    }
}
