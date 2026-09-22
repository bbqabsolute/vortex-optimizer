using System;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace VortexNet8
{
    public static class ConsoleMonitor
    {
        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool AllocConsole();

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
        private static extern IntPtr CreateFile(
            string lpFileName,
            uint dwDesiredAccess,
            uint dwShareMode,
            IntPtr lpSecurityAttributes,
            uint dwCreationDisposition,
            uint dwFlagsAndAttributes,
            IntPtr hTemplateFile);

        private const uint GENERIC_WRITE = 0x40000000;
        private const uint FILE_SHARE_WRITE = 0x00000002;
        private const uint OPEN_EXISTING = 0x00000003;

        public static void Run(string[] args)
        {
            if (args.Length < 2) return;
            string pipeName = args[1];

            try
            {
                AllocConsole();
                IntPtr stdHandle = CreateFile("CONOUT$", GENERIC_WRITE, FILE_SHARE_WRITE, IntPtr.Zero, OPEN_EXISTING, 0, IntPtr.Zero);
                if (stdHandle != IntPtr.Zero && stdHandle != new IntPtr(-1))
                {
                    var safeHandle = new SafeFileHandle(stdHandle, true);
                    var fs = new FileStream(safeHandle, FileAccess.Write);
                    var writer = new StreamWriter(fs, Encoding.UTF8) { AutoFlush = true };
                    Console.SetOut(writer);
                    Console.SetError(writer);
                    Console.OutputEncoding = Encoding.UTF8;
                }

                Console.Title = "VORTEX Engine — Мониторинг оптимизации и логов";

                using var client = new NamedPipeClientStream(".", pipeName, PipeDirection.In);
                client.Connect(10000);

                using var reader = new StreamReader(client, Encoding.UTF8);
                string? line;
                while ((line = reader.ReadLine()) != null)
                {
                    if (string.IsNullOrWhiteSpace(line)) continue;

                    string[] parts = line.Split('|', 3);
                    string cmd = parts[0];

                    switch (cmd)
                    {
                        case "HEAD":
                            string gameName = parts.Length > 1 ? parts[1] : "Игра";
                            string gamePath = parts.Length > 2 ? parts[2] : "";
                            PrintHeader(gameName, gamePath);
                            break;

                        case "PROG":
                            if (parts.Length >= 3 && int.TryParse(parts[1], out int percent))
                            {
                                PrintProgress(percent, parts[2]);
                            }
                            break;

                        case "LOG":
                            if (parts.Length >= 2)
                            {
                                PrintLog(parts[1]);
                            }
                            break;

                        case "BYE":
                            return;
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[ConsoleMonitor] Error: {ex.Message}");
            }
        }

        private static void PrintHeader(string gameName, string gamePath)
        {
            try
            {
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine(@"===============================================================================");
                Console.WriteLine(@"     __      __ ____   _____   _______  ______  __  __ ");
                Console.WriteLine(@"     \ \    / // __ \ |  __ \ |__   __||  ____| \ \/ / ");
                Console.WriteLine(@"      \ \  / /| |  | || |__) |   | |   | |__     \  /  ");
                Console.WriteLine(@"       \ \/ / | |  | ||  _  /    | |   |  __|    /  \  ");
                Console.WriteLine(@"        \  /  | |__| || | \ \    | |   | |____  / /\ \ ");
                Console.WriteLine(@"         \/    \____/ |_|  \_\   |_|   |______|/_/  \_\");
                Console.WriteLine(@"                                                       ");
                Console.WriteLine(@"          VORTEX ULTRA OPTIMIZER & ZERO INPUT LAG ENGINE (C# .NET 8)   ");
                Console.WriteLine(@"===============================================================================");
                Console.ResetColor();

                Console.ForegroundColor = ConsoleColor.White;
                Console.Write(" [ИГРА]            : ");
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine(!string.IsNullOrEmpty(gameName) ? gameName : "Выбранная игра");

                Console.ForegroundColor = ConsoleColor.White;
                Console.Write(" [ПУТЬ К ФАЙЛУ]    : ");
                Console.ForegroundColor = ConsoleColor.DarkCyan;
                Console.WriteLine(!string.IsNullOrEmpty(gamePath) ? gamePath : "Стандартный автопоиск");

                Console.ForegroundColor = ConsoleColor.White;
                Console.Write(" [РЕЖИМ ЗАПУСКА]   : ");
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("Ярлык VORTEX (Прямой буст ядра и системы)");

                Console.ForegroundColor = ConsoleColor.White;
                Console.Write(" [ВРЕМЯ СТАРТА]    : ");
                Console.ForegroundColor = ConsoleColor.Gray;
                Console.WriteLine(DateTime.Now.ToString("dd.MM.yyyy HH:mm:ss"));

                Console.ForegroundColor = ConsoleColor.DarkGray;
                Console.WriteLine(" [ИНФО]            : При закрытии этого окна VORTEX продолжит работу в фоне.");

                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine(@"===============================================================================");
                Console.ResetColor();
                Console.WriteLine();
            }
            catch { }
        }

        private static void PrintProgress(int percent, string message)
        {
            try
            {
                string time = DateTime.Now.ToString("HH:mm:ss");

                Console.ForegroundColor = ConsoleColor.DarkGray;
                Console.Write($"[{time}] ");

                if (percent >= 100)
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.Write("[100%] ");
                }
                else if (percent >= 70)
                {
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.Write($"[{percent,3}%] ");
                }
                else if (percent >= 40)
                {
                    Console.ForegroundColor = ConsoleColor.Blue;
                    Console.Write($"[{percent,3}%] ");
                }
                else
                {
                    Console.ForegroundColor = ConsoleColor.Magenta;
                    Console.Write($"[{percent,3}%] ");
                }

                Console.ForegroundColor = ConsoleColor.White;
                Console.WriteLine(message);
                Console.ResetColor();
            }
            catch { }
        }

        private static void PrintLog(string message)
        {
            try
            {
                string time = DateTime.Now.ToString("HH:mm:ss");
                Console.ForegroundColor = ConsoleColor.DarkGray;
                Console.Write($"[{time}] ");

                if (message.Contains("[УСПЕХ]") || message.Contains("[ГОТОВО]") || message.Contains("активн") || message.Contains("запущен"))
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                }
                else if (message.Contains("[ОШИБКА]") || message.Contains("❌"))
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                }
                else if (message.Contains("[ОЖИДАНИЕ]") || message.Contains("⏳"))
                {
                    Console.ForegroundColor = ConsoleColor.Yellow;
                }
                else if (message.Contains("[КЛАВИАТУРА]") || message.Contains("FilterKeys") || message.Contains("DNS"))
                {
                    Console.ForegroundColor = ConsoleColor.Cyan;
                }
                else if (message.Contains("[ПАМЯТЬ]") || message.Contains("RAM") || message.Contains("Standby"))
                {
                    Console.ForegroundColor = ConsoleColor.Magenta;
                }
                else
                {
                    Console.ForegroundColor = ConsoleColor.Gray;
                }

                Console.WriteLine(message);
                Console.ResetColor();
            }
            catch { }
        }
    }
}
