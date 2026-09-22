"""
================================================================================
  VORTEX v5.0 - MODERN GRAPHICAL INSTALLER
  Фирменный установщик соревновательного оптимизатора Fortnite
================================================================================
"""

import os
import sys
import shutil
import zipfile
import threading
import time
import ctypes
import subprocess
import winreg
from tkinter import filedialog
from PIL import Image

try:
    import customtkinter as ctk
except ImportError:
    ctypes.windll.user32.MessageBoxW(0, "CustomTkinter not installed", "Error", 0x10)
    sys.exit(1)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_main": "#080C14",
    "bg_card": "#101724",
    "border": "#1C273A",
    "accent_blue": "#2563EB",
    "accent_cyan": "#00F0FF",
    "accent_green": "#10B981",
    "text_white": "#F8FAFC",
    "text_gray": "#94A3B8",
}


def get_default_install_dir():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        is_admin = False

    prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    local_app = os.environ.get("LOCALAPPDATA", "")
    if is_admin and os.path.exists(prog_files):
        return os.path.join(prog_files, "VORTEX")
    elif local_app:
        return os.path.join(local_app, "Programs", "VORTEX")
    return r"C:\VORTEX"


def create_shortcut(target_path, shortcut_path, icon_path="", working_dir="", description=""):
    try:
        os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)
        ps_script = (
            f'$WshShell = New-Object -ComObject WScript.Shell; '
            f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
            f'$Shortcut.TargetPath = "{target_path}"; '
            f'$Shortcut.WorkingDirectory = "{working_dir}"; '
            f'$Shortcut.Description = "{description}"; '
        )
        if icon_path and os.path.exists(icon_path):
            ps_script += f'$Shortcut.IconLocation = "{icon_path},0"; '
        ps_script += '$Shortcut.Save()'

        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            creationflags=0x08000000, # CREATE_NO_WINDOW
            check=True
        )
        return True
    except Exception as e:
        print(f"Error creating shortcut {shortcut_path}: {e}")
        return False


def register_uninstall(install_dir, exe_path, ico_path, uninstall_path):
    keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\VORTEX"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\VORTEX")
    ]
    for root_key, sub_key in keys:
        try:
            with winreg.CreateKeyEx(root_key, sub_key, 0, winreg.KEY_ALL_ACCESS) as k:
                winreg.SetValueEx(k, "DisplayName", 0, winreg.REG_SZ, "VORTEX — Fortnite Competitive Optimizer")
                winreg.SetValueEx(k, "DisplayVersion", 0, winreg.REG_SZ, "5.0.0")
                winreg.SetValueEx(k, "Publisher", 0, winreg.REG_SZ, "VORTEX Performance Lab")
                winreg.SetValueEx(k, "InstallLocation", 0, winreg.REG_SZ, install_dir)
                winreg.SetValueEx(k, "DisplayIcon", 0, winreg.REG_SZ, ico_path if os.path.exists(ico_path) else exe_path)
                winreg.SetValueEx(k, "UninstallString", 0, winreg.REG_SZ, f'"{uninstall_path}"')
                winreg.SetValueEx(k, "EstimatedSize", 0, winreg.REG_DWORD, 95000)
                winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)
            break
        except Exception:
            continue


class VortexInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Установка VORTEX v5.0")
        self.geometry("640x570")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])

        # Determine bundle paths
        if getattr(sys, "frozen", False):
            self.base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.payload_zip = os.path.join(self.base_dir, "app_payload.zip")
        self.default_dir = get_default_install_dir()

        # Try to set window icon
        ico_file = os.path.join(self.base_dir, "assets", "icons", "vortex_logo.ico")
        if not os.path.exists(ico_file):
            ico_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "vortex_logo.ico")
        if os.path.exists(ico_file):
            try:
                self.iconbitmap(ico_file)
            except Exception:
                pass

        self.install_dir_var = ctk.StringVar(value=self.default_dir)
        self.create_desktop_var = ctk.BooleanVar(value=True)
        self.create_startmenu_var = ctk.BooleanVar(value=True)
        self.autostart_var = ctk.BooleanVar(value=True)
        self.launch_after_var = ctk.BooleanVar(value=True)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=24, pady=24)

        self.show_page_config()

    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_page_config(self):
        self.clear_container()

        card = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="both", expand=True, padx=4, pady=4)

        # Header Title
        title_box = ctk.CTkFrame(card, fg_color="transparent")
        title_box.pack(pady=(24, 4))

        vortex_lbl = ctk.CTkLabel(
            title_box,
            text="V O R T E X",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COLORS["text_white"]
        )
        vortex_lbl.pack()

        ver_lbl = ctk.CTkLabel(
            title_box,
            text="v5.0 • Unleash Competitive Performance",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["accent_cyan"]
        )
        ver_lbl.pack(pady=(2, 0))

        # Description
        desc_lbl = ctk.CTkLabel(
            card,
            text="Мастер установит VORTEX на ваш компьютер.\nПриложение настроит Windows и сетевой стек для максимального FPS и минимального пинга в Fortnite.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_gray"],
            justify="center"
        )
        desc_lbl.pack(pady=(12, 16), padx=20)

        # Install path frame
        path_frame = ctk.CTkFrame(card, fg_color="transparent")
        path_frame.pack(fill="x", padx=36, pady=(0, 16))

        path_title = ctk.CTkLabel(
            path_frame,
            text="Папка для установки:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_white"]
        )
        path_title.pack(anchor="w", pady=(0, 6))

        input_box = ctk.CTkFrame(path_frame, fg_color="transparent")
        input_box.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            input_box,
            textvariable=self.install_dir_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=38,
            corner_radius=8,
            border_color=COLORS["border"],
            fg_color="#0D131F"
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            input_box,
            text="Обзор...",
            width=90,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            corner_radius=8,
            command=self.browse_folder
        )
        browse_btn.pack(side="right")

        # Checkboxes
        cb_frame = ctk.CTkFrame(card, fg_color="transparent")
        cb_frame.pack(fill="x", padx=40, pady=(0, 20))

        cb_desktop = ctk.CTkCheckBox(
            cb_frame,
            text="Создать ярлык на Рабочем столе",
            variable=self.create_desktop_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_white"],
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8"
        )
        cb_desktop.pack(anchor="w", pady=4)

        cb_start = ctk.CTkCheckBox(
            cb_frame,
            text="Создать ярлык в меню «Пуск»",
            variable=self.create_startmenu_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_white"],
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8"
        )
        cb_start.pack(anchor="w", pady=4)

        cb_autostart = ctk.CTkCheckBox(
            cb_frame,
            text="Запускать VORTEX вместе с Windows (автозагрузка в трей)",
            variable=self.autostart_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_white"],
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8"
        )
        cb_autostart.pack(anchor="w", pady=4)

        cb_launch = ctk.CTkCheckBox(
            cb_frame,
            text="Запустить VORTEX сразу после установки",
            variable=self.launch_after_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_white"],
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8"
        )
        cb_launch.pack(anchor="w", pady=4)

        # Bottom Action
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=36, pady=(10, 20), side="bottom")

        install_btn = ctk.CTkButton(
            action_frame,
            text="УСТАНОВИТЬ VORTEX",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=46,
            corner_radius=10,
            command=self.start_installation
        )
        install_btn.pack(fill="x")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.install_dir_var.get())
        if folder:
            self.install_dir_var.set(os.path.join(folder, "VORTEX"))

    def start_installation(self):
        target_dir = self.install_dir_var.get().strip()
        if not target_dir:
            return

        self.clear_container()

        card = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="both", expand=True, padx=4, pady=4)

        # Header Title
        vortex_lbl = ctk.CTkLabel(
            card,
            text="Установка VORTEX...",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_white"]
        )
        vortex_lbl.pack(pady=(40, 10))

        self.progress_bar = ctk.CTkProgressBar(
            card,
            width=480,
            height=14,
            corner_radius=7,
            fg_color="#0D131F",
            progress_color=COLORS["accent_blue"]
        )
        self.progress_bar.pack(pady=(20, 15))
        self.progress_bar.set(0.0)

        self.status_lbl = ctk.CTkLabel(
            card,
            text="Инициализация установщика...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_gray"]
        )
        self.status_lbl.pack(pady=(0, 20))

        # Log box
        self.log_box = ctk.CTkTextbox(
            card,
            width=480,
            height=140,
            corner_radius=10,
            fg_color="#080C14",
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#CBD5E1"
        )
        self.log_box.pack(pady=(0, 20))

        threading.Thread(target=self._run_install_thread, args=(target_dir,), daemon=True).start()

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def _run_install_thread(self, target_dir):
        try:
            self.status_lbl.configure(text="Создание целевой папки...")
            self.log(f"[INSTALL] Целевая папка: {target_dir}")
            os.makedirs(target_dir, exist_ok=True)
            self.progress_bar.set(0.15)
            time.sleep(0.3)

            # Unpack payload
            if os.path.exists(self.payload_zip):
                self.status_lbl.configure(text="Распаковка компонентов VORTEX...")
                self.log(f"[INSTALL] Распаковка архива {os.path.basename(self.payload_zip)}...")
                with zipfile.ZipFile(self.payload_zip, 'r') as zf:
                    file_list = zf.infolist()
                    total = len(file_list)
                    for idx, member in enumerate(file_list):
                        zf.extract(member, target_dir)
                        if idx % 10 == 0:
                            frac = 0.15 + (idx / total) * 0.55
                            self.progress_bar.set(frac)
                self.log("[INSTALL] + Файлы успешно извлечены")
            else:
                # If running from dev folder, copy dist/VORTEX or current files
                dev_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "VORTEX")
                if os.path.exists(dev_dist):
                    self.status_lbl.configure(text="Копирование файлов приложения...")
                    self.log("[INSTALL] Копирование из dist/VORTEX...")
                    shutil.copytree(dev_dist, target_dir, dirs_exist_ok=True)
                else:
                    self.log("[INSTALL] ! Payload zip не найден, копирование исходных каталогов...")
                    for d in ["core", "assets", "config"]:
                        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), d)
                        dst = os.path.join(target_dir, d)
                        if os.path.exists(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)

            self.progress_bar.set(0.75)
            time.sleep(0.3)

            exe_path = os.path.join(target_dir, "VORTEX.exe")
            ico_path = os.path.join(target_dir, "assets", "icons", "vortex_logo.ico")
            uninstall_path = os.path.join(target_dir, "uninstall.exe")

            # Create Shortcuts
            self.status_lbl.configure(text="Создание ярлыков Windows...")
            if self.create_desktop_var.get():
                user_desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "VORTEX.lnk")
                self.log(f"[INSTALL] Создание ярлыка: {user_desktop}")
                create_shortcut(exe_path, user_desktop, ico_path, target_dir, "VORTEX - Unleash Competitive Performance")

            if self.create_startmenu_var.get():
                sm_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\VORTEX")
                sm_lnk = os.path.join(sm_dir, "VORTEX.lnk")
                un_lnk = os.path.join(sm_dir, "Удалить VORTEX.lnk")
                self.log(f"[INSTALL] Создание группы меню Пуск: {sm_dir}")
                create_shortcut(exe_path, sm_lnk, ico_path, target_dir, "VORTEX - Unleash Competitive Performance")
                if os.path.exists(uninstall_path):
                    create_shortcut(uninstall_path, un_lnk, ico_path, target_dir, "Удалить VORTEX")

            self.progress_bar.set(0.90)
            time.sleep(0.2)

            # Registry integration
            self.status_lbl.configure(text="Регистрация в Windows...")
            self.log("[INSTALL] Регистрация в списке установленных программ Windows...")
            register_uninstall(target_dir, exe_path, ico_path, uninstall_path)

            # Autostart registration if checked
            if self.autostart_var.get():
                self.status_lbl.configure(text="Настройка автозагрузки Windows...")
                self.log("[INSTALL] Настройка автозапуска (Windows Task Scheduler /rl highest)...")
                try:
                    sch_cmd = f'schtasks /create /tn "VORTEX_Optimizer" /tr "\"{exe_path}\" --minimized" /sc onlogon /rl highest /f'
                    subprocess.run(sch_cmd, shell=True, capture_output=True, creationflags=0x08000000)
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as k:
                            winreg.SetValueEx(k, "VORTEX", 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
                    except Exception:
                        pass
                    target_cfg = os.path.join(target_dir, "config", "settings.cfg")
                    if os.path.exists(target_cfg):
                        with open(target_cfg, "a", encoding="utf-8") as f:
                            f.write("\nAUTOSTART=1\nSTART_MINIMIZED=1\nCLOSE_TO_TRAY=1\n")
                    self.log("[INSTALL] ✓ Автозагрузка успешно настроена")
                except Exception as ex:
                    self.log(f"[INSTALL WARN] Автозагрузка: {ex}")

            self.progress_bar.set(1.0)
            self.status_lbl.configure(text="✓ Установка завершена!")
            self.log("[INSTALL] ✓ Установка VORTEX v5.0 полностью завершена!")
            time.sleep(0.5)

            self.after(0, lambda: self.show_page_finished(exe_path))

        except Exception as e:
            self.status_lbl.configure(text=f"Ошибка установки: {e}")
            self.log(f"[INSTALL ERROR] {e}")

    def show_page_finished(self, exe_path):
        self.clear_container()

        card = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="both", expand=True, padx=4, pady=4)

        # Success Icon / Badge
        success_lbl = ctk.CTkLabel(
            card,
            text="✓",
            font=ctk.CTkFont(family="Segoe UI", size=56, weight="bold"),
            text_color=COLORS["accent_green"]
        )
        success_lbl.pack(pady=(40, 6))

        title_lbl = ctk.CTkLabel(
            card,
            text="Установка успешно завершена!",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_white"]
        )
        title_lbl.pack(pady=(0, 10))

        sub_lbl = ctk.CTkLabel(
            card,
            text=f"VORTEX v5.0 готов к работе на вашем компьютере.\nПапка: {self.install_dir_var.get()}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_gray"],
            justify="center"
        )
        sub_lbl.pack(pady=(0, 30))

        # Bottom Button
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=50, pady=(10, 30), side="bottom")

        finish_btn = ctk.CTkButton(
            action_frame,
            text="ЗАПУСТИТЬ VORTEX" if self.launch_after_var.get() else "ГОТОВО",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=46,
            corner_radius=10,
            command=lambda: self.finish_installation(exe_path)
        )
        finish_btn.pack(fill="x")

    def finish_installation(self, exe_path):
        if self.launch_after_var.get() and os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), close_fds=True)
            except Exception as e:
                print("Error launching:", e)
        self.destroy()


if __name__ == "__main__":
    app = VortexInstaller()
    app.mainloop()
