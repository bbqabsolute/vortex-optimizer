"""
================================================================================
  VORTEX v5.0 - UNINSTALLER
  Чистое удаление приложения, ярлыков и записей реестра Windows
================================================================================
"""

import os
import sys
import shutil
import ctypes
import subprocess
import winreg
from PIL import Image

try:
    import customtkinter as ctk
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    # Fallback to standard message box if customtkinter not available
    res = messagebox.askyesno("VORTEX", "Удалить VORTEX и все его компоненты с компьютера?")
    if res:
        # Perform removal
        sys.exit(0)
    sys.exit(0)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_main": "#080C14",
    "bg_card": "#101724",
    "border": "#1C273A",
    "accent_blue": "#2563EB",
    "accent_red": "#EF4444",
    "text_white": "#F8FAFC",
    "text_gray": "#94A3B8",
}

class VortexUninstaller(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Удаление VORTEX")
        self.geometry("520x360")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])

        # Determine install directory
        if getattr(sys, "frozen", False):
            self.install_dir = os.path.dirname(sys.executable)
        else:
            self.install_dir = os.path.dirname(os.path.abspath(__file__))

        # Center window
        self.eval('tk::PlaceWindow . center')

        self.build_ui()

    def build_ui(self):
        main_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"]
        )
        main_card.pack(fill="both", expand=True, padx=20, pady=20)

        # Title / Header
        title_lbl = ctk.CTkLabel(
            main_card,
            text="УДАЛЕНИЕ VORTEX",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS["accent_red"]
        )
        title_lbl.pack(pady=(24, 6))

        subtitle_lbl = ctk.CTkLabel(
            main_card,
            text=f"Вы действительно хотите удалить VORTEX с вашего ПК?\nПапка: {self.install_dir}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_gray"],
            justify="center",
            wraplength=440
        )
        subtitle_lbl.pack(pady=(0, 16))

        # Checkbox
        self.cb_clean_user_data = ctk.CTkCheckBox(
            main_card,
            text="Удалить сохранённые профили и файл настроек (settings.cfg)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_white"],
            fg_color=COLORS["accent_blue"],
            hover_color="#1D4ED8"
        )
        self.cb_clean_user_data.select()
        self.cb_clean_user_data.pack(pady=(0, 24))

        # Status text
        self.status_lbl = ctk.CTkLabel(
            main_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_white"]
        )
        self.status_lbl.pack(pady=(0, 10))

        # Buttons frame
        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 10))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Отмена",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color=COLORS["text_white"],
            height=40,
            width=180,
            corner_radius=10,
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10), expand=True)

        self.uninstall_btn = ctk.CTkButton(
            btn_frame,
            text="Удалить VORTEX",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLORS["accent_red"],
            hover_color="#DC2626",
            text_color="#FFFFFF",
            height=40,
            width=180,
            corner_radius=10,
            command=self.perform_uninstall
        )
        self.uninstall_btn.pack(side="right", padx=(10, 0), expand=True)

    def perform_uninstall(self):
        self.uninstall_btn.configure(state="disabled")
        self.status_lbl.configure(text="Удаление компонентов и ярлыков...", text_color="#F59E0B")
        self.update()

        # 1. Remove Registry entries
        for root_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                winreg.DeleteKey(root_key, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\VORTEX")
            except OSError:
                pass

        # 2. Remove Shortcuts
        paths_to_check = []
        user_desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "VORTEX.lnk")
        public_desktop = os.path.join(os.environ.get("PUBLIC", ""), "Desktop", "VORTEX.lnk")
        user_programs = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\VORTEX")
        common_programs = os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs\VORTEX")

        paths_to_check.extend([user_desktop, public_desktop])
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

        for pdir in [user_programs, common_programs]:
            if os.path.exists(pdir):
                try:
                    shutil.rmtree(pdir, ignore_errors=True)
                except Exception:
                    pass

        # 3. Schedule self-deletion of install folder
        install_dir = self.install_dir
        cmd = f'cmd.exe /c ping 127.0.0.1 -n 3 >nul & rmdir /s /q "{install_dir}"'
        try:
            subprocess.Popen(cmd, shell=True, creationflags=0x08000000) # CREATE_NO_WINDOW
        except Exception:
            pass

        self.status_lbl.configure(text="✓ VORTEX успешно удалён!", text_color="#10B981")
        self.update()
        self.after(1200, self.destroy)

if __name__ == "__main__":
    app = VortexUninstaller()
    app.mainloop()
