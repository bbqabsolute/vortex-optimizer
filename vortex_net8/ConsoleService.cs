using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading.Tasks;

namespace VortexNet8
{
    public static class ConsoleService
    {
        private static NamedPipeServerStream? _pipeServer;
        private static StreamWriter? _pipeWriter;
        private static Process? _consoleProcess;
        private static bool _isConsoleOpen = false;
        private static readonly object _consoleLock = new();
        private static readonly ConcurrentQueue<string> _pendingMessages = new();

        public static bool IsOpen
        {
            get
            {
                lock (_consoleLock)
                {
                    return _isConsoleOpen && _consoleProcess != null && !_consoleProcess.HasExited;
                }
            }
        }

        public static void OpenConsole(string gameName = "", string gamePath = "")
        {
            lock (_consoleLock)
            {
                if (IsOpen)
                {
                    SendMessage($"HEAD|{gameName}|{gamePath}");
                    return;
                }

                CloseConsole();

                try
                {
                    string pipeName = $"VortexConsole_{Environment.ProcessId}_{DateTime.Now.Ticks}";
                    _pipeServer = new NamedPipeServerStream(
                        pipeName,
                        PipeDirection.Out,
                        1,
                        PipeTransmissionMode.Byte,
                        PipeOptions.Asynchronous);

                    string exePath = Environment.ProcessPath ?? Process.GetCurrentProcess().MainModule?.FileName ?? @"C:\Users\bbq\Desktop\VORTEX.exe";
                    var psi = new ProcessStartInfo
                    {
                        FileName = exePath,
                        Arguments = $"--console-monitor {pipeName}",
                        UseShellExecute = true,
                        WorkingDirectory = Path.GetDirectoryName(exePath) ?? AppDomain.CurrentDomain.BaseDirectory
                    };

                    _consoleProcess = Process.Start(psi);
                    _isConsoleOpen = true;

                    // Отправляем заголовок
                    _pendingMessages.Enqueue($"HEAD|{gameName}|{gamePath}");

                    // Фоновая задача ожидания подключения клиента
                    Task.Run(() =>
                    {
                        try
                        {
                            _pipeServer?.WaitForConnection();
                            lock (_consoleLock)
                            {
                                if (_pipeServer != null && _pipeServer.IsConnected)
                                {
                                    _pipeWriter = new StreamWriter(_pipeServer, Encoding.UTF8) { AutoFlush = true };
                                    while (_pendingMessages.TryDequeue(out var msg))
                                    {
                                        _pipeWriter.WriteLine(msg);
                                    }
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            Debug.WriteLine($"[ConsoleService] Pipe connection error: {ex.Message}");
                        }
                    });
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[ConsoleService] OpenConsole error: {ex.Message}");
                }
            }
        }

        private static void SendMessage(string line)
        {
            lock (_consoleLock)
            {
                if (_pipeWriter != null)
                {
                    try
                    {
                        _pipeWriter.WriteLine(line);
                        return;
                    }
                    catch
                    {
                        // Клиент закрыл окно консоли (нажал [X])
                        CloseConsole();
                    }
                }
                else if (_isConsoleOpen)
                {
                    _pendingMessages.Enqueue(line);
                }
            }
        }

        public static void LogProgress(int percent, string message)
        {
            SendMessage($"PROG|{percent}|{message}");
        }

        public static void Log(string message)
        {
            SendMessage($"LOG|{message}");
        }

        public static void CloseConsole()
        {
            lock (_consoleLock)
            {
                _isConsoleOpen = false;
                try
                {
                    _pipeWriter?.WriteLine("BYE|");
                    _pipeWriter?.Dispose();
                }
                catch { }
                _pipeWriter = null;

                try
                {
                    _pipeServer?.Dispose();
                }
                catch { }
                _pipeServer = null;

                try
                {
                    if (_consoleProcess != null && !_consoleProcess.HasExited)
                    {
                        _consoleProcess.Kill();
                    }
                }
                catch { }
                _consoleProcess = null;
            }
        }
    }
}
