using System;
using System.IO;
using System.Threading;
using System.Windows;
using System.Runtime.InteropServices;
using WpfApp = System.Windows.Application;

namespace VortexNet8
{
    public partial class App : WpfApp
    {
        private const string MutexName = "VORTEX_Optimizer_SingleInstance_Mutex";
        private const string RestoreEventName = "VORTEX_Optimizer_Restore_Event";

        private static Mutex? _instanceMutex;
        private static EventWaitHandle? _restoreEvent;

        [DllImport("shell32.dll", SetLastError = true)]
        private static extern int SetCurrentProcessExplicitAppUserModelID([MarshalAs(UnmanagedType.LPWStr)] string AppID);

        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        protected override void OnStartup(StartupEventArgs e)
        {
            try
            {
                SetCurrentProcessExplicitAppUserModelID("VORTEX.Performance.Optimizer");
            }
            catch { }

            if (e.Args.Length > 0 && string.Equals(e.Args[0], "--console-monitor", StringComparison.OrdinalIgnoreCase))
            {
                ConsoleMonitor.Run(e.Args);
                Environment.Exit(0);
                return;
            }

            string logFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup_log.txt");
            try
            {
                File.AppendAllText(logFile, $"[{DateTime.Now}] OnStartup started\n");
            }
            catch { }

            AppDomain.CurrentDomain.UnhandledException += (s, ev) =>
            {
                try
                {
                    File.AppendAllText(logFile, $"[{DateTime.Now}] Unhandled Exception: {ev.ExceptionObject}\n");
                }
                catch { }
            };

            DispatcherUnhandledException += (s, ev) =>
            {
                try
                {
                    File.AppendAllText(logFile, $"[{DateTime.Now}] Dispatcher Unhandled: {ev.Exception}\n");
                }
                catch { }
                ev.Handled = true;
            };

            bool createdNew = true;
            try
            {
                _instanceMutex = new Mutex(true, MutexName, out createdNew);
            }
            catch (Exception ex)
            {
                try { File.AppendAllText(logFile, $"[{DateTime.Now}] Mutex ex: {ex}\n"); } catch { }
            }

            if (!createdNew)
            {
                try
                {
                    using var ev = EventWaitHandle.OpenExisting(RestoreEventName);
                    ev.Set();
                }
                catch { }

                Shutdown();
                return;
            }

            try
            {
                _restoreEvent = new EventWaitHandle(false, EventResetMode.AutoReset, RestoreEventName);
                var listenerThread = new Thread(() =>
                {
                    while (true)
                    {
                        try
                        {
                            _restoreEvent.WaitOne();
                            WpfApp.Current?.Dispatcher.Invoke(() =>
                            {
                                if (WpfApp.Current.MainWindow != null)
                                {
                                    WpfApp.Current.MainWindow.Show();
                                    WpfApp.Current.MainWindow.WindowState = WindowState.Normal;
                                    WpfApp.Current.MainWindow.Activate();
                                    WpfApp.Current.MainWindow.Topmost = true;
                                    WpfApp.Current.MainWindow.Topmost = false;
                                    WpfApp.Current.MainWindow.Focus();
                                }
                            });
                        }
                        catch { }
                    }
                })
                {
                    IsBackground = true
                };
                listenerThread.Start();
            }
            catch { }
            ShutdownMode = ShutdownMode.OnExplicitShutdown;
            base.OnStartup(e);

            try
            {
                File.AppendAllText(logFile, $"[{DateTime.Now}] Creating MainWindow...\n");
                var mainWindow = new MainWindow();
                MainWindow = mainWindow;
                mainWindow.Show();
                File.AppendAllText(logFile, $"[{DateTime.Now}] MainWindow shown successfully!\n");
            }
            catch (Exception ex)
            {
                File.AppendAllText(logFile, $"[{DateTime.Now}] MainWindow creation error: {ex}\n");
            }
        }

        protected override void OnExit(ExitEventArgs e)
        {
            string logFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup_log.txt");
            try
            {
                File.AppendAllText(logFile, $"[{DateTime.Now}] OnExit called! Code={e.ApplicationExitCode}, StackTrace:\n{Environment.StackTrace}\n");
            }
            catch { }

            try
            {
                FilterKeysService.ResetDefault();
            }
            catch { }

            try
            {
                _instanceMutex?.ReleaseMutex();
                _instanceMutex?.Dispose();
            }
            catch { }

            base.OnExit(e);
        }
    }
}
