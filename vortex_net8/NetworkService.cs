using System;
using System.Diagnostics;
using System.Net.NetworkInformation;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using Microsoft.Win32;

namespace VortexNet8
{
    public static class NetworkService
    {
        [DllImport("dnsapi.dll", EntryPoint = "DnsFlushResolverCache")]
        private static extern int DnsFlushResolverCache();

        public static bool FlushDns()
        {
            try
            {
                DnsFlushResolverCache();
            }
            catch { }

            try
            {
                using var p = Process.Start(new ProcessStartInfo("ipconfig", "/flushdns")
                {
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
                p?.WaitForExit(3000);
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool ApplyDns(string primary, string secondary)
        {
            try
            {
                ConfigService.Set("DNS_PRIMARY", primary);
                ConfigService.Set("DNS_SECONDARY", secondary);

                // Use PowerShell to set DNS for all connected IPv4 adapters
                string psCmd;
                if (string.IsNullOrEmpty(primary) || primary == "DHCP")
                {
                    psCmd = "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }";
                }
                else
                {
                    string addrs = string.IsNullOrEmpty(secondary) ? $"'{primary}'" : $"'{primary}','{secondary}'";
                    psCmd = $"Get-NetAdapter | Where-Object {{ $_.Status -eq 'Up' }} | ForEach-Object {{ Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses ({addrs}) }}";
                }

                using var p = Process.Start(new ProcessStartInfo("powershell", $"-NoProfile -Command \"{psCmd}\"")
                {
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
                p?.WaitForExit(4000);

                FlushDns();
                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool ApplyTcpNagleTweaks()
        {
            try
            {
                // 1. TcpAckFrequency and TCPNoDelay across all Interfaces
                const string interfacesPath = @"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces";
                using (var interfacesKey = Registry.LocalMachine.OpenSubKey(interfacesPath, true))
                {
                    if (interfacesKey != null)
                    {
                        foreach (var subName in interfacesKey.GetSubKeyNames())
                        {
                            using var sub = interfacesKey.OpenSubKey(subName, true);
                            if (sub != null)
                            {
                                sub.SetValue("TcpAckFrequency", 1, RegistryValueKind.DWord);
                                sub.SetValue("TCPNoDelay", 1, RegistryValueKind.DWord);
                                sub.SetValue("TcpDelAckTicks", 0, RegistryValueKind.DWord);
                            }
                        }
                    }
                }

                // 2. Multimedia Network Throttling Index = -1 (disabled)
                const string mmPath = @"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile";
                using (var mmKey = Registry.LocalMachine.OpenSubKey(mmPath, true))
                {
                    if (mmKey != null)
                    {
                        mmKey.SetValue("NetworkThrottlingIndex", unchecked((int)0xFFFFFFFF), RegistryValueKind.DWord);
                        mmKey.SetValue("SystemResponsiveness", 0, RegistryValueKind.DWord);
                    }
                }

                return true;
            }
            catch
            {
                return false;
            }
        }

        public static bool OptimizeQoS()
        {
            return ApplyTcpNagleTweaks();
        }

        public static async Task<long> PingHostAsync(string host, int timeout = 1200)
        {
            try
            {
                using var p = new Ping();
                var reply = await p.SendPingAsync(host, timeout);
                if (reply.Status == IPStatus.Success)
                    return reply.RoundtripTime;
            }
            catch { }
            return -1;
        }
    }
}
