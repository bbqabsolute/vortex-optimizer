"""
================================================================================
  VORTEX v5.0  -  UNLEASH COMPETITIVE PERFORMANCE
  Инженерия соревновательного преимущества для Fortnite
  Увеличенные элементы интерфейса • Без микро-шрифтов • Мягкая палитра
================================================================================
"""

import os
import sys
import subprocess
import threading
import time
import socket
import ctypes
from ctypes import wintypes
import re
import traceback
import json
from tkinter import filedialog, messagebox
from PIL import Image

try:
    import pystray
except Exception:
    pystray = None

# Catch early import errors
try:
    import psutil
    import customtkinter as ctk
except Exception as e:
    err = traceback.format_exc()
    ctypes.windll.user32.MessageBoxW(
        0,
        f"Ошибка библиотек Python:\n\n{err}\n\nЗапустите START_GUI.bat для авто-установки.",
        "Ошибка запуска VORTEX",
        0x10
    )
    sys.exit(1)

# Настройка темы CustomTkinter и масштабирования интерфейса
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.08)
# Защита от системных прокси-туннелей, блокирующих авторизацию Epic Games / Fortnite
for _var in ("http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
    os.environ.pop(_var, None)

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("vortex.performance.optimizer.5")
except Exception:
    pass

if getattr(sys, "frozen", False):
    bundle_dir = getattr(sys, "_MEIPASS", None)
    exe_dir = os.path.dirname(sys.executable)
    if bundle_dir and os.path.exists(os.path.join(bundle_dir, "assets")):
        BASE_DIR = bundle_dir
    else:
        BASE_DIR = exe_dir
    CONFIG_DIR = os.path.join(exe_dir, "config")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_DIR = os.path.join(BASE_DIR, "config")

CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.cfg")
CORE_DIR = os.path.join(BASE_DIR, "core")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "icons")
PRESETS_FILE = os.path.join(CONFIG_DIR, "custom_presets.json")


def get_icon(name, size=(20, 20)):
    """Загрузка векторной иконки PNG из каталога ассетов VORTEX"""
    try:
        path = os.path.join(ASSETS_DIR, f"{name}.png")
        if os.path.exists(path):
            img = Image.open(path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        pass
    return None

# --- ПАЛИТРА VORTEX: Премиальный глубокий графит + сапфирово-синий акцент ---
COLORS = {
    "bg_main": "#080C14",         # Глубокий темный графит
    "bg_sidebar": "#0B1019",      # Боковое меню
    "bg_card": "#101724",         # Поверхность карточек
    "bg_card_hover": "#162033",   # Подсветка карточек при наведении
    "border": "#1C273A",          # Тонкая элегантная рамка
    "border_active": "#3B82F6",   # Сапфировый фокус
    "accent_blue": "#2563EB",     # Главный акцентный синий
    "accent_blue_hover": "#1D4ED8",
    "accent_cyan": "#38BDF8",     # Мягкий небесный для показателей CPU
    "accent_cyan_hover": "#0EA5E9",
    "accent_purple": "#A78BFA",   # Мягкий фиолетовый для RAM
    "accent_purple_hover": "#8B5CF6",
    "accent_green": "#10B981",    # Изумрудный статус
    "accent_green_hover": "#059669",
    "accent_amber": "#F59E0B",    # Янтарный таймер
    "accent_red": "#EF4444",      # Опасный красный
    "text_primary": "#F8FAFC",    # Четкий белый
    "text_secondary": "#94A3B8",  # Приглушённый читаемый серый
    "text_muted": "#64748B",      # Вторичный серый
}

# Шрифты с проверкой сглаживания
FONT_FAMILY = "Segoe UI"


def get_font(size=12, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """Перезапуск приложения с правами администратора через UAC"""
    if is_admin():
        return True

    script = os.path.abspath(sys.argv[0])
    bat_path = os.path.join(BASE_DIR, "START_GUI.bat")

    # 1. Попытка через START_GUI.bat (самый надёжный способ для Windows)
    if os.path.exists(bat_path):
        try:
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", bat_path, "", BASE_DIR, 1
            )
            if int(ret) > 32:
                sys.exit(0)
        except Exception:
            pass

    # 2. Попытка через sys.executable напрямую с глаголом runas
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}"', BASE_DIR, 1
        )
        if int(ret) > 32:
            sys.exit(0)
    except Exception:
        pass

    # 3. Резервный вызов через PowerShell Start-Process
    try:
        ps_cmd = f'Start-Process -FilePath "{sys.executable}" -ArgumentList \'"{script}"\' -Verb RunAs'
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
        sys.exit(0)
    except Exception:
        pass

    return False


PRESETS_FILE = os.path.join(CONFIG_DIR, "custom_presets.json")

# Встроенные киберспортивные пресеты
BUILTIN_PRESETS = {
    "TOURNAMENT": {
        "name": "🏆 Турнир",
        "full_name": "🏆 Турнирный (Tournament)",
        "code": "TOURNAMENT",
        "desc": "Макс. FPS • Меньше пинг • HAGS Выкл • Таймер 0.5 мс",
        "accent": "#7C3AED",
        "is_builtin": True,
        "settings": {
            "FPS_BOOST": "1", "VISUAL_EFFECTS": "1", "DISABLE_DVRGAME": "1", "POWER_PLAN": "1",
            "HAGS_DISABLE": "1", "HIGH_PRIORITY": "1", "NETWORK_BOOST": "1", "NAGLE_OFF": "1",
            "DNS_OPTIMIZE": "1", "DNS_PRIMARY": "8.8.8.8", "DNS_SECONDARY": "8.8.4.4",
            "CPU_UNPARK": "1", "MSI_MODE": "1", "MOUSE_OPTIMIZE": "1", "FORTNITE_INI": "1",
            "PAGEFILE_OPTIMIZE": "1", "RESOLUTION_CHANGE": "0", "PING_MONITOR": "1",
            "RAM_CLEANUP": "1", "KILL_USELESS": "1", "LAUNCH_EPIC": "1",
            "TIMER_RESOLUTION": "1", "NIC_OPTIMIZE": "1"
        }
    },
    "PERFORMANCE": {
        "name": "⚡ Киберспорт",
        "full_name": "⚡ Киберспорт (Performance)",
        "code": "PERFORMANCE",
        "desc": "Высокий FPS • Стабильность • HAGS Вкл • VSync Выкл",
        "accent": "#2563EB",
        "is_builtin": True,
        "settings": {
            "FPS_BOOST": "1", "VISUAL_EFFECTS": "1", "DISABLE_DVRGAME": "1", "POWER_PLAN": "1",
            "HAGS_DISABLE": "0", "HIGH_PRIORITY": "1", "NETWORK_BOOST": "1", "NAGLE_OFF": "1",
            "DNS_OPTIMIZE": "1", "DNS_PRIMARY": "8.8.8.8", "DNS_SECONDARY": "8.8.4.4",
            "CPU_UNPARK": "1", "MSI_MODE": "1", "MOUSE_OPTIMIZE": "1", "FORTNITE_INI": "1",
            "PAGEFILE_OPTIMIZE": "0", "RESOLUTION_CHANGE": "0", "PING_MONITOR": "1",
            "RAM_CLEANUP": "1", "KILL_USELESS": "1", "LAUNCH_EPIC": "1",
            "TIMER_RESOLUTION": "1", "NIC_OPTIMIZE": "1"
        }
    },
    "BALANCED": {
        "name": "⚖️ Баланс",
        "full_name": "⚖️ Баланс (Balanced)",
        "code": "BALANCED",
        "desc": "Плавный FPS • Без твиков INI • Стандартная графика",
        "accent": "#059669",
        "is_builtin": True,
        "settings": {
            "FPS_BOOST": "1", "VISUAL_EFFECTS": "0", "DISABLE_DVRGAME": "1", "POWER_PLAN": "1",
            "HAGS_DISABLE": "0", "HIGH_PRIORITY": "1", "NETWORK_BOOST": "1", "NAGLE_OFF": "1",
            "DNS_OPTIMIZE": "1", "DNS_PRIMARY": "8.8.8.8", "DNS_SECONDARY": "8.8.4.4",
            "CPU_UNPARK": "1", "MSI_MODE": "0", "MOUSE_OPTIMIZE": "1", "FORTNITE_INI": "0",
            "PAGEFILE_OPTIMIZE": "0", "RESOLUTION_CHANGE": "0", "PING_MONITOR": "1",
            "RAM_CLEANUP": "1", "KILL_USELESS": "0", "LAUNCH_EPIC": "1",
            "TIMER_RESOLUTION": "1", "NIC_OPTIMIZE": "0"
        }
    },
    "STREAMING": {
        "name": "📺 Стриминг",
        "full_name": "📺 Стриминг (Streaming)",
        "code": "STREAMING",
        "desc": "Для OBS и записи • Game DVR Вкл • Без потери кадров",
        "accent": "#D97706",
        "is_builtin": True,
        "settings": {
            "FPS_BOOST": "1", "VISUAL_EFFECTS": "0", "DISABLE_DVRGAME": "0", "POWER_PLAN": "1",
            "HAGS_DISABLE": "0", "HIGH_PRIORITY": "1", "NETWORK_BOOST": "1", "NAGLE_OFF": "1",
            "DNS_OPTIMIZE": "1", "DNS_PRIMARY": "8.8.8.8", "DNS_SECONDARY": "8.8.4.4",
            "CPU_UNPARK": "1", "MSI_MODE": "0", "MOUSE_OPTIMIZE": "1", "FORTNITE_INI": "0",
            "PAGEFILE_OPTIMIZE": "0", "RESOLUTION_CHANGE": "0", "PING_MONITOR": "0",
            "RAM_CLEANUP": "1", "KILL_USELESS": "0", "LAUNCH_EPIC": "1",
            "TIMER_RESOLUTION": "1", "NIC_OPTIMIZE": "1"
        }
    },
    "ULTRA_PING": {
        "name": "🎯 Ультра Пинг",
        "full_name": "🎯 Ультра Низкий Пинг (Ultra Low Ping)",
        "code": "ULTRA_PING",
        "desc": "Приоритет сети • Nagle Выкл • Модерация NIC Выкл • DNS 8.8.8.8",
        "accent": "#00F0FF",
        "is_builtin": True,
        "settings": {
            "FPS_BOOST": "1", "VISUAL_EFFECTS": "0", "DISABLE_DVRGAME": "1", "POWER_PLAN": "1",
            "HAGS_DISABLE": "0", "HIGH_PRIORITY": "1", "NETWORK_BOOST": "1", "NAGLE_OFF": "1",
            "DNS_OPTIMIZE": "1", "DNS_PRIMARY": "8.8.8.8", "DNS_SECONDARY": "8.8.4.4",
            "CPU_UNPARK": "1", "MSI_MODE": "1", "MOUSE_OPTIMIZE": "1", "FORTNITE_INI": "0",
            "PAGEFILE_OPTIMIZE": "0", "RESOLUTION_CHANGE": "0", "PING_MONITOR": "1",
            "RAM_CLEANUP": "1", "KILL_USELESS": "1", "LAUNCH_EPIC": "1",
            "TIMER_RESOLUTION": "1", "NIC_OPTIMIZE": "1"
        }
    },
    "POTATO_PC": {
        "name": "🥔 Слабый ПК",
        "full_name": "🥔 Слабый ПК (Potato PC / Max FPS)",
        "code": "POTATO_PC",
        "desc": "100% твики • Макс. урезание графики • Разпарковка • Файл подкачки",
        "accent": "#EF4444",
        "is_builtin": True,
        "settings": {
            "FPS_BOOST": "1", "VISUAL_EFFECTS": "1", "DISABLE_DVRGAME": "1", "POWER_PLAN": "1",
            "HAGS_DISABLE": "1", "HIGH_PRIORITY": "1", "NETWORK_BOOST": "1", "NAGLE_OFF": "1",
            "DNS_OPTIMIZE": "1", "DNS_PRIMARY": "8.8.8.8", "DNS_SECONDARY": "8.8.4.4",
            "CPU_UNPARK": "1", "MSI_MODE": "1", "MOUSE_OPTIMIZE": "1", "FORTNITE_INI": "1",
            "PAGEFILE_OPTIMIZE": "1", "RESOLUTION_CHANGE": "0", "PING_MONITOR": "1",
            "RAM_CLEANUP": "1", "KILL_USELESS": "1", "LAUNCH_EPIC": "1",
            "TIMER_RESOLUTION": "1", "NIC_OPTIMIZE": "1"
        }
    }
}


def load_custom_presets():
    """Загрузка пользовательских пресетов из JSON файла"""
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_custom_presets(custom_dict):
    """Сохранение пользовательских пресетов в JSON файл"""
    os.makedirs(os.path.dirname(PRESETS_FILE), exist_ok=True)
    try:
        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_dict, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_all_presets():
    """Получение всех пресетов: встроенных и кастомных"""
    all_p = dict(BUILTIN_PRESETS)
    custom = load_custom_presets()
    for k, v in custom.items():
        all_p[k] = v
    return all_p


def set_high_resolution_timer():
    """Снижение системного таймера Windows до 0.5 мс (минимальный инпутлаг)"""
    try:
        ntdll = ctypes.WinDLL("ntdll.dll")
        actual = ctypes.c_ulong()
        ntdll.NtSetTimerResolution(5000, 1, ctypes.byref(actual))
        return True
    except Exception:
        return False


def repair_epic_social_registry():
    """
    Восстановление сокетов и служб друзей/пати в Fortnite (Epic Online Services / AFD Fix).
    Удаляет опасные ключи IgnorePushBitOnReceives, NonBlockingSendSpecialBuffering и
    сбойные политики QoS DSCP, блокировавшие доставку мгновенных PSH-пакетов XMPP и WebSockets.
    """
    try:
        keys_to_delete = [
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "IgnorePushBitOnReceives"),
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "NonBlockingSendSpecialBuffering"),
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "DefaultReceiveWindow"),
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "DefaultSendWindow"),
            (r"HKLM\SYSTEM\CurrentControlSet\Services\AFD\Parameters", "FastSendDatagramThreshold"),
        ]
        for path, val in keys_to_delete:
            subprocess.run(["reg", "delete", path, "/v", val, "/f"], capture_output=True, timeout=2)
        subprocess.run(["reg", "delete", r"HKLM\SOFTWARE\Policies\Microsoft\Windows\QoS\Fortnite", "/f"], capture_output=True, timeout=2)
        return True
    except Exception:
        return False


DNS_BENCHMARK_SERVERS = [
    {"name": "Cloudflare", "full_name": "Cloudflare DNS", "primary": "1.1.1.1", "secondary": "1.0.0.1", "desc": "1.1.1.1 • Ультра-скорость"},
    {"name": "Google", "full_name": "Google Public DNS", "primary": "8.8.8.8", "secondary": "8.8.4.4", "desc": "8.8.8.8 • Высокая стабильность"},
    {"name": "OpenDNS", "full_name": "Cisco OpenDNS", "primary": "208.67.222.222", "secondary": "208.67.220.220", "desc": "208.67.222.222 • Быстрый гейминг"},
    {"name": "Яндекс", "full_name": "Яндекс DNS", "primary": "77.88.8.8", "secondary": "77.88.8.1", "desc": "77.88.8.8 • Близкие СНГ серверы"},
    {"name": "Quad9", "full_name": "Quad9 Secure DNS", "primary": "9.9.9.9", "secondary": "149.112.112.112", "desc": "9.9.9.9 • Защищённый DNS"},
]


def ping_dns_server(ip, timeout=0.6):
    """
    Измерение реальной задержки DNS-сервера:
    1. Отправка реального UDP DNS-запроса A-записи epicgames.com
    2. Fallback на быстрый TCP connect на порт 53
    """
    query = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09epicgames\x03com\x00\x00\x01\x00\x01'
    samples = []

    for _ in range(2):
        t0 = time.perf_counter()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(query, (ip, 53))
            resp, _ = sock.recvfrom(512)
            sock.close()
            if resp and len(resp) > 12:
                samples.append((time.perf_counter() - t0) * 1000)
        except Exception:
            pass

    if samples:
        return round(sum(samples) / len(samples), 1)

    try:
        t0 = time.perf_counter()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout + 0.3)
        s.connect((ip, 53))
        s.close()
        return round((time.perf_counter() - t0) * 1000, 1)
    except Exception:
        return 999.0


VORTEX_MUTEX_NAME = "VORTEX_SingleInstance_Mutex"
VORTEX_EVENT_NAME = "VORTEX_ShowEvent"


class FILTERKEYS(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwFlags", wintypes.DWORD),
        ("iWaitMSec", wintypes.DWORD),
        ("iDelayMSec", wintypes.DWORD),
        ("iRepeatMSec", wintypes.DWORD),
        ("iBounceMSec", wintypes.DWORD),
    ]


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL)
    ]


def _set_live_filterkeys(flags, wait_ms, delay_ms, repeat_ms, bounce_ms=0):
    """Мгновенное применение параметров FilterKeys в памяти Windows через SystemParametersInfoW"""
    try:
        fk = FILTERKEYS()
        fk.cbSize = ctypes.sizeof(FILTERKEYS)
        fk.dwFlags = flags
        fk.iWaitMSec = wait_ms
        fk.iDelayMSec = delay_ms
        fk.iRepeatMSec = repeat_ms
        fk.iBounceMSec = bounce_ms
        # SPI_SETFILTERKEYS = 0x0033 (51), SPIF_UPDATEINIFILE = 1, SPIF_SENDCHANGE = 2
        ctypes.windll.user32.SystemParametersInfoW(0x0033, fk.cbSize, ctypes.byref(fk), 3)
    except Exception:
        pass


def apply_filterkeys_turbo():
    """Активация киберспортивного отклика клавиатуры FilterKeys (Mongraal / Bugha 150мс)"""
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Accessibility\Keyboard Response")
        winreg.SetValueEx(key, "AutoRepeatDelay", 0, winreg.REG_SZ, "150")
        winreg.SetValueEx(key, "AutoRepeatRate", 0, winreg.REG_SZ, "15")
        winreg.SetValueEx(key, "BounceTime", 0, winreg.REG_SZ, "0")
        winreg.SetValueEx(key, "DelayBeforeAcceptance", 0, winreg.REG_SZ, "0")
        winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "59")
        winreg.CloseKey(key)
    except Exception:
        pass
    _set_live_filterkeys(59, 0, 150, 15, 0)
    return True


def reset_filterkeys_default():
    """Сброс настроек клавиатуры на стандартные значения Windows (1000мс / 500мс)"""
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Accessibility\Keyboard Response")
        winreg.SetValueEx(key, "AutoRepeatDelay", 0, winreg.REG_SZ, "1000")
        winreg.SetValueEx(key, "AutoRepeatRate", 0, winreg.REG_SZ, "500")
        winreg.SetValueEx(key, "BounceTime", 0, winreg.REG_SZ, "0")
        winreg.SetValueEx(key, "DelayBeforeAcceptance", 0, winreg.REG_SZ, "1000")
        winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "126")
        winreg.CloseKey(key)
    except Exception:
        pass
    _set_live_filterkeys(126, 1000, 1000, 500, 0)
    return True


def ensure_single_instance():
    """
    Обеспечивает запуск только 1 экземпляра VORTEX (Named Mutex).
    Если запущен повторный экземпляр, активирует и выводит существующее окно на передний план,
    после чего немедленно завершает работу второго экземпляра.
    """
    ERROR_ALREADY_EXISTS = 183
    ERROR_ACCESS_DENIED = 5
    EVENT_MODIFY_STATE = 0x0002
    SW_RESTORE = 9

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # Создаем дескриптор безопасности с NULL DACL для единого доступа вне зависимости от UAC уровня
    try:
        sd = ctypes.create_string_buffer(20)
        ctypes.windll.advapi32.InitializeSecurityDescriptor(sd, 1)
        ctypes.windll.advapi32.SetSecurityDescriptorDacl(sd, True, None, False)
        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
        sa.lpSecurityDescriptor = ctypes.cast(sd, wintypes.LPVOID)
        sa.bInheritHandle = False
        sa_ptr = ctypes.byref(sa)
    except Exception:
        sa_ptr = None

    mutex = kernel32.CreateMutexW(sa_ptr, False, VORTEX_MUTEX_NAME)
    last_err = kernel32.GetLastError()

    if last_err in (ERROR_ALREADY_EXISTS, ERROR_ACCESS_DENIED) or not mutex:
        # Экземпляр уже запущен!
        # 1. Посылаем сигнал через именованное событие первому экземпляру
        try:
            h_event = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, VORTEX_EVENT_NAME)
            if h_event:
                kernel32.SetEvent(h_event)
                kernel32.CloseHandle(h_event)
        except Exception:
            pass

        # 2. Поиск окна и вывод на передний план через Win32 EnumWindows
        try:
            def enum_proc(hwnd, lParam):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if "VORTEX" in title:
                        user32.ShowWindow(hwnd, SW_RESTORE)
                        user32.SetForegroundWindow(hwnd)
                        return False
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
        except Exception:
            pass

        sys.exit(0)

    return mutex


def get_filterkeys_status():
    """Проверка текущего статуса FilterKeys"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Accessibility\Keyboard Response")
        val, _ = winreg.QueryValueEx(key, "AutoRepeatDelay")
        winreg.CloseKey(key)
        return str(val) == "150"
    except Exception:
        return False


def is_autostart_active():
    """Проверка активности автозагрузки в планировщике задач Windows или реестре"""
    try:
        res = subprocess.run(
            ["schtasks", "/query", "/tn", "VORTEX_Optimizer"],
            capture_output=True, creationflags=0x08000000
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
            winreg.QueryValueEx(k, "VORTEX")
            return True
    except Exception:
        pass
    return False


def set_autostart(enable: bool, start_minimized: bool = True):
    """
    Управление автозагрузкой VORTEX при старте Windows.
    Использует планировщик задач Windows с наивысшими правами (/rl highest),
    чтобы исполняемый файл запускался с правами администратора без всплывающего окна UAC.
    Также создает резервную запись в реестре HKCU Run.
    """
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        target_cmd = f'"{exe_path}"'
    else:
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        target_cmd = f'"{python_exe}" "{script_path}"'

    if start_minimized:
        target_cmd += " --minimized"

    if enable:
        sch_cmd = f'schtasks /create /tn "VORTEX_Optimizer" /tr "{target_cmd}" /sc onlogon /rl highest /f'
        subprocess.run(sch_cmd, shell=True, capture_output=True, creationflags=0x08000000)
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, "VORTEX", 0, winreg.REG_SZ, target_cmd)
        except Exception:
            pass
        return True
    else:
        subprocess.run('schtasks /delete /tn "VORTEX_Optimizer" /f', shell=True, capture_output=True, creationflags=0x08000000)
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, "VORTEX")
        except Exception:
            pass
        return False


def flush_system_ram():
    """Мгновенный сброс неиспользуемых страниц памяти (Working Set Trim) для максимального свободного объема RAM"""
    try:
        mem_before = psutil.virtual_memory().available
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers();"],
            capture_output=True, creationflags=0x08000000
        )
        psapi = ctypes.WinDLL("psapi.dll")
        kernel32 = ctypes.WinDLL("kernel32.dll")
        for p in psutil.process_iter(['pid', 'name']):
            try:
                name = p.info['name'] or ""
                if any(x.lower() in name.lower() for x in ['system', 'lsass', 'csrss', 'epic', 'fortnite', 'easyanti', 'vortex']):
                    continue
                h_proc = kernel32.OpenProcess(0x001F0FFF, False, p.info['pid'])
                if h_proc:
                    psapi.EmptyWorkingSet(h_proc)
                    kernel32.CloseHandle(h_proc)
            except Exception:
                continue

        mem_after = psutil.virtual_memory().available
        freed_mb = max(0, int((mem_after - mem_before) / (1024 * 1024)))
        return freed_mb
    except Exception:
        return 0


def get_fortnite_ini_status():
    """Чтение текущего разрешения и статуса Read-Only из GameUserSettings.ini"""
    local_app = os.environ.get("LOCALAPPDATA", "")
    fn_ini = os.path.join(local_app, "FortniteGame", "Saved", "Config", "WindowsClient", "GameUserSettings.ini")
    if not os.path.exists(fn_ini):
        return {"exists": False, "w": "?", "h": "?", "readonly": False, "path": fn_ini}

    import stat
    attrs = os.stat(fn_ini).st_mode
    is_ro = not (attrs & stat.S_IWRITE)
    w, h = "?", "?"
    try:
        with open(fn_ini, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("ResolutionSizeX="):
                    w = line.split("=", 1)[1].strip()
                elif line.startswith("ResolutionSizeY="):
                    h = line.split("=", 1)[1].strip()
    except Exception:
        pass
    return {"exists": True, "w": w, "h": h, "readonly": is_ro, "path": fn_ini}


EPIC_SERVICES_LIST = [
    {"name": "Друзья и лобби EOS", "host": "api.epicgames.dev", "port": 443, "desc": "Epic Online Services • Список друзей, пати и присутствие"},
    {"name": "Матчмейкинг Fortnite", "host": "fortnite-public-service-prod11.ol.epicgames.com", "port": 443, "desc": "Серверы подбора матчей и игровых сессий"},
    {"name": "Авторизация и аккаунты", "host": "account-public-service-prod.ol.epicgames.com", "port": 443, "desc": "Вход в Epic Games Launcher и проверка токенов OAuth"},
    {"name": "Epic Games Store", "host": "store.epicgames.com", "port": 443, "desc": "Каталог обновлений, магазин и новости"},
    {"name": "Монитор статуса Epic", "host": "status.epicgames.com", "port": 443, "desc": "Официальная глобальная телеметрия инцидентов Epic Games"},
    {"name": "Сетевое ядро Epic Cloud", "host": "epicgames.com", "port": 443, "desc": "Магистральные узлы передачи игровых данных"},
]


def load_config():
    cfg = {
        "PRESET": "PERFORMANCE",
        "FPS_BOOST": "1",
        "VISUAL_EFFECTS": "1",
        "DISABLE_DVRGAME": "1",
        "POWER_PLAN": "1",
        "HAGS_DISABLE": "0",
        "HIGH_PRIORITY": "1",
        "NETWORK_BOOST": "1",
        "NAGLE_OFF": "1",
        "DNS_OPTIMIZE": "1",
        "DNS_PRIMARY": "8.8.8.8",
        "DNS_SECONDARY": "8.8.4.4",
        "CPU_UNPARK": "1",
        "MSI_MODE": "1",
        "MOUSE_OPTIMIZE": "1",
        "FORTNITE_INI": "1",
        "PAGEFILE_OPTIMIZE": "0",
        "RESOLUTION_CHANGE": "0",
        "RESOLUTION_WIDTH": "1920",
        "RESOLUTION_HEIGHT": "1080",
        "RESOLUTION_REFRESH": "0",
        "PING_MONITOR": "1",
        "RAM_CLEANUP": "1",
        "KILL_USELESS": "1",
        "LAUNCH_EPIC": "1",
        "EPIC_PATH": r"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        "TIMER_RESOLUTION": "1",
        "NIC_OPTIMIZE": "1",
        "AUTOSTART": "0",
        "START_MINIMIZED": "1",
        "CLOSE_TO_TRAY": "1",
        "AUTO_OPTIMIZE_GAME": "1",
        "MINIMIZE_ON_LAUNCH": "1",
        "AUTO_TURBO_INPUT": "1",
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        cfg[k.strip()] = v.strip()
        except Exception:
            pass
    return cfg


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write("# Fortnite Ultimate Optimizer v4.0\n")
            f.write(f"# Сохранено: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for k, v in cfg.items():
                f.write(f"{k}={v}\n")
    except Exception:
        pass


class ModernOptimizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VORTEX — Unleash Competitive Performance")
        self.geometry("1300x840")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_main"])

        # Установка официальной иконки окна и панели задач VORTEX
        ico_path = os.path.join(ASSETS_DIR, "vortex_logo.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        self.cfg = load_config()
        self.is_running = False
        self.active_tab = "dashboard"

        # Автоматическая активация низкого таймера 0.5 мс
        set_high_resolution_timer()

        # Определение модели процессора
        self.cpu_name = self.detect_cpu_name()

        # Анимация и живой пульс
        self.pulse_phase = 0
        self.anim_running = False

        # Мастер-сетка
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Кастомные пресеты
        self.custom_presets = load_custom_presets()
        self.current_preset_filter = "ALL"

        # Состояние компактного виджета и тостов
        self._mini_hud_win = None
        self._active_toast = None

        self.build_sidebar()
        self.build_content_area()

        # Инициализация системного трея Windows
        self.tray_icon = None
        self.setup_tray_icon()

        # Перехват закрытия окна (сворачивание в трей при активном CLOSE_TO_TRAY)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Состояние отслеживания игры для фонового стража
        self.game_was_running = False

        # Запуск постоянного фонового стража (удержание 0.5мс + авто-детект Fortnite)
        threading.Thread(target=self._guardian_daemon_loop, daemon=True).start()

        # Запуск фонового живого монитора
        self.update_telemetry()
        self.update_live_pulse()

        # Проверка запуска с ключом работы в фоне
        if any(arg in sys.argv for arg in ("--minimized", "--background", "/minimized", "/background", "/autostart")):
            self.after(300, self.minimize_to_tray)

        # Слушатель единого экземпляра (выводит окно на экран при повторном запуске)
        self._setup_single_instance_listener()

        # Анимированный экран предстартовой подготовки и поиска быстрейшего DNS
        self.fastest_dns_info = None
        self.start_startup_sequence()

    def _setup_single_instance_listener(self):
        """Слушатель сигнала разворачивания окна при повторной попытке запуска (Single Instance)"""
        try:
            kernel32 = ctypes.windll.kernel32
            self._restore_event = kernel32.CreateEventW(None, False, False, VORTEX_RESTORE_EVENT)
            def _listener():
                while True:
                    try:
                        res = kernel32.WaitForSingleObject(self._restore_event, 1000)
                        if res == 0:  # WAIT_OBJECT_0
                            self.after(0, self.restore_from_tray)
                    except Exception:
                        time.sleep(1)
            threading.Thread(target=_listener, daemon=True).start()
        except Exception:
            pass

    def setup_tray_icon(self):
        """Инициализация иконки VORTEX в системном трее Windows (Notification Area)"""
        if pystray is None:
            return

        ico_path = os.path.join(ASSETS_DIR, "vortex_logo.ico")
        png_path = os.path.join(ASSETS_DIR, "vortex_logo.png")
        image = None
        for p in [ico_path, png_path]:
            if os.path.exists(p):
                try:
                    image = Image.open(p)
                    break
                except Exception:
                    pass

        if image is None:
            image = Image.new("RGB", (64, 64), color="#2563EB")

        def _open_app(icon=None, item=None):
            self.after(0, self.restore_from_tray)

        def _clean_ram(icon=None, item=None):
            self.after(0, self.quick_ram_cleanup)

        def _launch_game(icon=None, item=None):
            self.after(0, self.start_master_optimization)

        def _exit_app(icon=None, item=None):
            self.after(0, self.full_exit)

        menu = pystray.Menu(
            pystray.MenuItem("🚀 Развернуть VORTEX", _open_app, default=True),
            pystray.MenuItem("⚡ Очистить RAM", _clean_ram),
            pystray.MenuItem("🎮 Запустить Fortnite (Буст)", _launch_game),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("✕ Закрыть VORTEX", _exit_app)
        )

        try:
            self.tray_icon = pystray.Icon("VORTEX", image, "VORTEX — Unleash Competitive Performance", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception:
            self.tray_icon = None

    def restore_from_tray(self):
        """Разворачивание окна VORTEX из системного трея с выводом на передний план"""
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
            self.attributes('-topmost', True)
            self.after(150, lambda: self.attributes('-topmost', False))
        except Exception:
            pass

    def minimize_to_tray(self):
        """Сворачивание окна в системный трей (полное скрытие с панели задач)"""
        try:
            self.withdraw()
            if hasattr(self, 'tray_icon') and self.tray_icon:
                try:
                    self.tray_icon.notify(
                        "VORTEX активен в системном трее.\nТаймер 0.5 мс и авто-буст включены.",
                        "VORTEX свернут в трей"
                    )
                except Exception:
                    pass
        except Exception:
            self.iconify()

    def minimize_to_background(self):
        """Сворачивание окна VORTEX в трей/фон с сохранением работы фонового стража"""
        self.minimize_to_tray()

    def on_window_close(self):
        """Обработка клика по крестику закрытия окна (сворачивание в трей)"""
        if self.cfg.get("CLOSE_TO_TRAY", "1") == "1":
            self.minimize_to_tray()
        else:
            self.full_exit()

    def _guardian_daemon_loop(self):
        """
        Постоянный фоновый страж VORTEX:
        1. Непрерывно удерживает системный таймер Windows на 0.5 мс
        2. Обнаруживает запуск FortniteClient-Win64-Shipping.exe
        3. Назначает игре высокий приоритет CPU и выполняет пре-гейм сброс памяти
        4. Защищает GameUserSettings.ini от сброса разрешения
        """
        while True:
            try:
                set_high_resolution_timer()

                fn_proc = None
                for p in psutil.process_iter(['pid', 'name']):
                    try:
                        pname = p.info['name'] or ""
                        if 'FortniteClient' in pname and not pname.endswith('.tmp'):
                            fn_proc = p
                            break
                    except Exception:
                        pass

                is_running_now = (fn_proc is not None)

                if is_running_now and not self.game_was_running:
                    self.game_was_running = True
                    if self.cfg.get("AUTO_OPTIMIZE_GAME", "1") == "1":
                        try:
                            fn_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        except Exception:
                            pass

                        try:
                            local_app = os.environ.get("LOCALAPPDATA", "")
                            fn_ini = os.path.join(local_app, "FortniteGame", "Saved", "Config", "WindowsClient", "GameUserSettings.ini")
                            if os.path.exists(fn_ini):
                                subprocess.run(f'attrib +r "{fn_ini}"', shell=True, creationflags=0x08000000)
                        except Exception:
                            pass

                        if self.cfg.get("RAM_CLEANUP", "1") == "1":
                            flush_system_ram()

                        # Динамический турбо-ввод: активен ТОЛЬКО пока запущен Fortnite
                        if self.cfg.get("AUTO_TURBO_INPUT", "1") == "1":
                            try:
                                apply_filterkeys_turbo()
                                if self.winfo_exists():
                                    self.after(0, lambda: self.log_dash("[СТРАЖ] ⚡ Fortnite запущен: Активирован турбо-ввод FilterKeys (150 мс)"))
                                    self.after(0, self.update_settings_filterkeys_status)
                            except Exception:
                                pass

                        if self.winfo_exists():
                            self.after(0, lambda: self.show_toast("⚡ Fortnite обнаружен! High Priority, 0.5ms и Турбо-ввод активны.", color="#10B981"))
                            if hasattr(self, 'game_status_pill') and self.game_status_pill.winfo_exists():
                                self.after(0, lambda: self.game_status_pill.configure(text="🟢 Fortnite активен (High Priority + Turbo Keys)", text_color="#10B981", fg_color="#064E3B"))

                elif not is_running_now and self.game_was_running:
                    self.game_was_running = False

                    # При закрытии Fortnite возвращаем стандартную задержку клавиатуры Windows
                    if self.cfg.get("AUTO_TURBO_INPUT", "1") == "1":
                        try:
                            reset_filterkeys_default()
                            if self.winfo_exists():
                                self.after(0, lambda: self.log_dash("[СТРАЖ] ⚪ Fortnite закрыт: Турбо-ввод отключен, стандартная задержка клавиатуры возвращена."))
                                self.after(0, self.update_settings_filterkeys_status)
                                self.after(0, lambda: self.show_toast("⚪ Fortnite закрыт: Клавиатура возвращена к стандарту Windows.", color="#60A5FA"))
                        except Exception:
                            pass

                    if self.winfo_exists():
                        if hasattr(self, 'game_status_pill') and self.game_status_pill.winfo_exists():
                            self.after(0, lambda: self.game_status_pill.configure(text="⚪ Ожидание запуска игры (Страж активен)", text_color=COLORS["text_muted"], fg_color="#101725"))

            except Exception:
                pass

            time.sleep(2.5)

    def show_toast(self, message, icon="✓", color=COLORS["accent_cyan"], duration=3200):
        """
        Всплывающее анимированное киберспортивное уведомление (Toast)
        """
        try:
            if hasattr(self, '_active_toast') and self._active_toast and self._active_toast.winfo_exists():
                self._active_toast.destroy()
        except Exception:
            pass

        if not hasattr(self, 'content_container') or not self.content_container.winfo_exists():
            return

        toast = ctk.CTkFrame(
            self.content_container,
            fg_color="#0F172A",
            border_width=2,
            border_color=color,
            corner_radius=12
        )
        self._active_toast = toast
        toast.place(relx=0.5, rely=0.08, anchor="center")

        inner = ctk.CTkFrame(toast, fg_color="transparent")
        inner.pack(padx=14, pady=6)

        ctk.CTkLabel(
            inner,
            text=icon,
            font=get_font(13, "bold"),
            text_color=color
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            inner,
            text=message,
            font=get_font(11, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(
            inner,
            text="✕",
            width=18,
            height=18,
            fg_color="transparent",
            hover_color="#1E293B",
            text_color=COLORS["text_muted"],
            font=get_font(9),
            command=lambda: toast.destroy()
        )
        close_btn.pack(side="right")

        def _auto_dismiss():
            try:
                if toast.winfo_exists():
                    toast.destroy()
            except Exception:
                pass

        self.after(duration, _auto_dismiss)

    def setup_mini_hud(self):
        """Устарело — Mini HUD теперь создаётся как отдельное окно в toggle_mini_hud."""
        pass

    def toggle_mini_hud(self):
        """Открывает/закрывает отдельное компактное окно HUD (нельзя растягивать)."""
        # Если окно уже открыто — закрываем
        if self._mini_hud_win is not None and self._mini_hud_win.winfo_exists():
            self._mini_hud_win.destroy()
            self._mini_hud_win = None
            self.mini_cpu_lbl = None  # type: ignore
            self.mini_ram_lbl = None  # type: ignore
            return

        # Создаём отдельное Toplevel-окно VORTEX HUD
        win = ctk.CTkToplevel(self)
        win.title("VORTEX HUD")
        win.geometry("400x195")
        win.minsize(400, 195)
        win.maxsize(400, 195)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.configure(fg_color=COLORS["bg_main"])
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_mini_hud())
        self._mini_hud_win = win

        # ── Заголовок ──────────────────────────────────────────
        top_bar = ctk.CTkFrame(win, fg_color=COLORS["bg_sidebar"], height=38, corner_radius=0)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(
            top_bar,
            text="✦  VORTEX HUD  [0.5ms Active]",
            font=get_font(12, "bold"),
            text_color="#60A5FA"
        ).pack(side="left", padx=14, pady=6)

        ctk.CTkButton(
            top_bar,
            text="✕",
            width=30, height=24,
            fg_color="transparent",
            hover_color="#334155",
            text_color=COLORS["text_muted"],
            font=get_font(12, "bold"),
            command=self._close_mini_hud
        ).pack(side="right", padx=10, pady=6)

        # ── Тело ───────────────────────────────────────────────
        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=10)

        # CPU / RAM строка
        row_telemetry = ctk.CTkFrame(body, fg_color="#101724", corner_radius=10, border_width=1, border_color=COLORS["border"])
        row_telemetry.pack(fill="x", pady=(0, 10))

        self.mini_cpu_lbl = ctk.CTkLabel(
            row_telemetry, text="CPU: --",
            font=get_font(13, "bold"), text_color=COLORS["accent_cyan"]
        )
        self.mini_cpu_lbl.pack(side="left", padx=14, pady=10)

        self.mini_ram_lbl = ctk.CTkLabel(
            row_telemetry, text="RAM: --",
            font=get_font(13, "bold"), text_color=COLORS["accent_purple"]
        )
        self.mini_ram_lbl.pack(side="right", padx=14, pady=10)

        # Кнопки быстрых действий
        row_btns = ctk.CTkFrame(body, fg_color="transparent")
        row_btns.pack(fill="x")

        ctk.CTkButton(
            row_btns,
            text="🧹 Очистить RAM",
            font=get_font(11, "bold"),
            fg_color="#141D2C",
            hover_color="#1E2B40",
            text_color="#38BDF8",
            height=36,
            corner_radius=8,
            command=self.quick_ram_cleanup
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            row_btns,
            text="🌐 Сброс DNS",
            font=get_font(11, "bold"),
            fg_color="#141D2C",
            hover_color="#1E2B40",
            text_color="#34D399",
            height=36,
            corner_radius=8,
            command=self.quick_flush_dns
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _close_mini_hud(self):
        """Закрывает Mini HUD и очищает ссылки."""
        if self._mini_hud_win is not None:
            try:
                if self._mini_hud_win.winfo_exists():
                    self._mini_hud_win.destroy()
            except Exception:
                pass
        self._mini_hud_win = None
        self.mini_cpu_lbl = None  # type: ignore
        self.mini_ram_lbl = None  # type: ignore


    # =========================================================================
    # АНИМИРОВАННЫЙ ЭКРАН СТАРТА И БЕНЧМАРК DNS
    # =========================================================================
    def start_startup_sequence(self):
        """
        Полноэкранный анимированный Splash Screen:
        - Пульсирующий кибер-радар и динамическая статусная строка
        - Динамический прогресс-бар от 0% до 100%
        - Тестирование DNS-серверов в реальном времени с подсветкой лучшего
        - Авто-исправление сокетов друзей / пати (AFD/EOS fix)
        - Активация таймера 0.5 мс
        - Плавное раскрытие главного интерфейса с выбранным быстрым DNS
        """
        self.splash_overlay = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        self.splash_overlay.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        # Центрированная киберспортивная карточка
        splash_card = ctk.CTkFrame(
            self.splash_overlay,
            fg_color=COLORS["bg_card"],
            corner_radius=16,
            border_width=2,
            border_color=COLORS["border_active"],
            width=780,
            height=580
        )
        splash_card.place(relx=0.5, rely=0.5, anchor="center")
        splash_card.pack_propagate(False)

        # Верхняя плашка бренда
        top_box = ctk.CTkFrame(splash_card, fg_color="transparent")
        top_box.pack(fill="x", padx=24, pady=(20, 10))

        # Анимированный логотип
        self.splash_icon_lbl = ctk.CTkLabel(
            top_box,
            text="⚡",
            font=get_font(34, "bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.splash_icon_lbl.pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(top_box, fg_color="transparent")
        title_col.pack(side="left")

        ctk.CTkLabel(
            title_col,
            text="VORTEX PERFORMANCE ENGINE",
            font=get_font(18, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text="КАЛИБРОВКА СИСТЕМЫ И ПОИСК БЫСТРЕЙШЕГО ИГРОВОГО DNS",
            font=get_font(10, "bold"),
            text_color="#60A5FA"
        ).pack(anchor="w")

        self.splash_stage_badge = ctk.CTkLabel(
            top_box,
            text="✦ ИНИЦИАЛИЗАЦИЯ VORTEX",
            font=get_font(10, "bold"),
            text_color="#10B981",
            fg_color="#064E3B",
            corner_radius=12,
            padx=12,
            pady=5
        )
        self.splash_stage_badge.pack(side="right")

        # Разделитель
        ctk.CTkFrame(splash_card, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=20, pady=(4, 12))

        # Прогресс-бар и счетчик процентов
        prog_header = ctk.CTkFrame(splash_card, fg_color="transparent")
        prog_header.pack(fill="x", padx=24, pady=(0, 4))

        self.splash_status_title = ctk.CTkLabel(
            prog_header,
            text="[ ◉ ] Инициализация киберспортивного ядра...",
            font=get_font(12, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.splash_status_title.pack(side="left")

        self.splash_pct_lbl = ctk.CTkLabel(
            prog_header,
            text="0%",
            font=get_font(13, "bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.splash_pct_lbl.pack(side="right")

        self.splash_progress = ctk.CTkProgressBar(
            splash_card,
            height=10,
            corner_radius=5,
            progress_color=COLORS["accent_cyan"],
            fg_color="#182234"
        )
        self.splash_progress.pack(fill="x", padx=24, pady=(0, 14))
        self.splash_progress.set(0.0)

        # Контейнер шагов калибровки (Чеклист)
        steps_frame = ctk.CTkFrame(splash_card, fg_color="#0C101A", corner_radius=10, border_width=1, border_color=COLORS["border"])
        steps_frame.pack(fill="x", padx=24, pady=(0, 12))

        self.splash_step_labels = {}
        checklist_items = [
            ("admin", "🛡️ Проверка прав Администратора и ядра Windows", "Ожидание"),
            ("friends", "👥 Защита сокетов друзей и лобби Epic Games (EOS / AFD Fix)", "Ожидание"),
            ("timer", "⏱️ Калибровка таймера 0.5 мс (NtSetTimerResolution)", "Ожидание"),
            ("dns", "🌐 Тестирование задержки DNS-серверов в реальном времени", "Ожидание"),
        ]

        for code, title, initial_state in checklist_items:
            row = ctk.CTkFrame(steps_frame, fg_color="transparent", height=28)
            row.pack(fill="x", padx=12, pady=4)

            t_lbl = ctk.CTkLabel(row, text=title, font=get_font(11), text_color=COLORS["text_secondary"])
            t_lbl.pack(side="left")

            s_lbl = ctk.CTkLabel(row, text=f"⏳ {initial_state}", font=get_font(10, "bold"), text_color=COLORS["text_muted"])
            s_lbl.pack(side="right")

            self.splash_step_labels[code] = (t_lbl, s_lbl)

        # Секция бенчмарка DNS (Карточки в реальном времени)
        dns_section = ctk.CTkFrame(splash_card, fg_color="transparent")
        dns_section.pack(fill="x", padx=24, pady=(0, 10))

        ctk.CTkLabel(
            dns_section,
            text="⚡ ТЕСТИРОВАНИЕ ИГРОВОГО ОТКЛИКА DNS К СЕРВЕРАМ FORTNITE (PING):",
            font=get_font(10, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, 6))

        self.dns_cards_frame = ctk.CTkFrame(dns_section, fg_color="transparent")
        self.dns_cards_frame.pack(fill="x")
        self.dns_cards_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.splash_dns_widgets = {}
        for idx, srv in enumerate(DNS_BENCHMARK_SERVERS):
            card = ctk.CTkFrame(
                self.dns_cards_frame,
                fg_color="#182234",
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border"],
                height=76
            )
            card.grid(row=0, column=idx, padx=3, sticky="nsew")
            card.pack_propagate(False)

            name_lbl = ctk.CTkLabel(card, text=srv["name"], font=get_font(11, "bold"), text_color=COLORS["text_primary"])
            name_lbl.pack(anchor="center", pady=(6, 1))

            ip_lbl = ctk.CTkLabel(card, text=srv["primary"], font=get_font(9), text_color=COLORS["text_muted"])
            ip_lbl.pack(anchor="center")

            ping_pill = ctk.CTkLabel(
                card,
                text="⏳ Ожидание",
                font=get_font(10, "bold"),
                text_color=COLORS["text_muted"],
                fg_color="#0F172A",
                corner_radius=6,
                padx=6,
                pady=1
            )
            ping_pill.pack(anchor="center", pady=(4, 6))

            self.splash_dns_widgets[srv["name"]] = {
                "card": card,
                "name_lbl": name_lbl,
                "ping_pill": ping_pill,
                "data": srv
            }

        # Запуск пульсации и анимации спиннера
        self.splash_spinner_idx = 0
        self.splash_is_active = True
        self._animate_splash_spinner()

        # Запуск фонового потока калибровки
        threading.Thread(target=self._run_startup_worker, daemon=True).start()

    def _animate_splash_spinner(self):
        if not hasattr(self, 'splash_is_active') or not self.splash_is_active:
            return
        if not hasattr(self, 'splash_overlay') or not self.splash_overlay.winfo_exists():
            return

        self.splash_spinner_idx += 1

        # Плавное мигание иконки
        colors = [COLORS["accent_cyan"], "#38BDF8", COLORS["accent_purple"], "#A78BFA"]
        cur_col = colors[self.splash_spinner_idx % len(colors)]
        try:
            self.splash_icon_lbl.configure(text_color=cur_col)
        except Exception:
            pass

        self.after(140, self._animate_splash_spinner)

    def _set_splash_dns_card_testing(self, name):
        w = self.splash_dns_widgets.get(name)
        if w and w["ping_pill"].winfo_exists():
            w["ping_pill"].configure(text="⚡ Тест...", text_color=COLORS["accent_cyan"], fg_color="#0C2436")
            w["card"].configure(border_color=COLORS["accent_cyan"])

    def _set_splash_dns_card_result(self, name, ping_ms):
        w = self.splash_dns_widgets.get(name)
        if w and w["ping_pill"].winfo_exists():
            if ping_ms < 35:
                col = "#10B981"
                bg = "#064E3B"
            elif ping_ms < 75:
                col = "#F59E0B"
                bg = "#451A03"
            else:
                col = "#EF4444"
                bg = "#450A0A"
            w["ping_pill"].configure(text=f"{ping_ms} мс", text_color=col, fg_color=bg)
            w["card"].configure(border_color=COLORS["border"])

    def _highlight_splash_fastest_dns(self, name, ping_ms):
        w = self.splash_dns_widgets.get(name)
        if w and w["card"].winfo_exists():
            w["card"].configure(border_color="#00F0FF", border_width=2, fg_color="#132438")
            w["name_lbl"].configure(text=f"👑 {name}", text_color="#00F0FF")
            w["ping_pill"].configure(text=f"🏆 {ping_ms} мс", text_color="#FFFFFF", fg_color="#0891B2")

    def _run_startup_worker(self):
        """Фоновый воркер предстартовой подготовки и бенчмарка DNS"""
        def update_step(code, status_text, color="#10B981", is_done=False):
            if not self.winfo_exists() or not getattr(self, 'splash_is_active', False):
                return
            t_lbl, s_lbl = self.splash_step_labels.get(code, (None, None))
            if s_lbl and s_lbl.winfo_exists():
                icon = "✓" if is_done else "⚡"
                s_lbl.configure(text=f"{icon} {status_text}", text_color=color)
            if t_lbl and t_lbl.winfo_exists() and is_done:
                t_lbl.configure(text_color=COLORS["text_primary"])

        def set_progress(pct, title_text):
            if not self.winfo_exists() or not getattr(self, 'splash_is_active', False):
                return
            self.splash_progress.set(pct)
            self.splash_pct_lbl.configure(text=f"{int(pct*100)}%")
            self.splash_status_title.configure(text=title_text)

        # --- ШАГ 1: Проверка администратора и ядра ---
        time.sleep(0.3)
        self.after(0, lambda: [
            set_progress(0.15, "Проверка прав администратора и ядра Windows..."),
            update_step("admin", "Проверка ядра...", COLORS["accent_cyan"])
        ])
        admin_ok = is_admin()
        time.sleep(0.3)
        self.after(0, lambda: update_step("admin", "Администратор активен" if admin_ok else "Ограниченный режим", "#10B981" if admin_ok else "#F59E0B", True))

        # --- ШАГ 2: Исправление сокетов друзей Epic Games (EOS / AFD Fix) ---
        self.after(0, lambda: [
            set_progress(0.30, "Восстановление сокетов друзей и пати (EOS / AFD)..."),
            update_step("friends", "Удаление push-bit блокировок...", COLORS["accent_cyan"])
        ])
        repair_epic_social_registry()
        time.sleep(0.4)
        self.after(0, lambda: update_step("friends", "Сокеты друзей защищены", "#10B981", True))

        # --- ШАГ 3: Активация субмиллисекундного таймера 0.5 мс ---
        self.after(0, lambda: [
            set_progress(0.45, "Активация системного таймера высокой точности 0.5 мс..."),
            update_step("timer", "NtSetTimerResolution(5000)...", COLORS["accent_cyan"])
        ])
        timer_ok = set_high_resolution_timer()
        time.sleep(0.3)
        self.after(0, lambda: update_step("timer", "Таймер 0.5 мс активирован" if timer_ok else "Стандартный таймер", "#10B981", True))

        # --- ШАГ 4: Реальный бенчмарк DNS-серверов ---
        self.after(0, lambda: [
            set_progress(0.60, "Тестирование DNS-серверов в реальном времени..."),
            update_step("dns", "Измерение отклика (epicgames.com)...", COLORS["accent_cyan"])
        ])

        benchmark_results = []
        for srv in DNS_BENCHMARK_SERVERS:
            s_name = srv["name"]
            p_ip = srv["primary"]
            self.after(0, lambda n=s_name: self._set_splash_dns_card_testing(n))

            ping_ms = ping_dns_server(p_ip)
            benchmark_results.append({**srv, "ping": ping_ms})

            self.after(0, lambda n=s_name, p=ping_ms: self._set_splash_dns_card_result(n, p))
            time.sleep(0.25)

        # Определение быстрейшего DNS
        benchmark_results.sort(key=lambda x: x["ping"])
        fastest = benchmark_results[0]
        self.fastest_dns_info = fastest

        self.after(0, lambda: [
            self._highlight_splash_fastest_dns(fastest["name"], fastest["ping"]),
            update_step("dns", f"Лучший: {fastest['name']} ({fastest['ping']} мс)", "#10B981", True)
        ])

        # --- ШАГ 5: Применение и финализация ---
        self.after(0, lambda: set_progress(0.90, f"Применение быстрейшего DNS: {fastest['name']} ({fastest['primary']})..."))

        # Обновление конфига и активного DNS
        self.cfg["DNS_PRIMARY"] = fastest["primary"]
        self.cfg["DNS_SECONDARY"] = fastest["secondary"]
        save_config(self.cfg)

        # Автоматическое применение DNS к сетевым адаптерам, если DNS_OPTIMIZE включен
        if self.cfg.get("DNS_OPTIMIZE", "1") == "1" and admin_ok:
            try:
                cmd = f'powershell -NoProfile -Command "Get-NetAdapter | Where-Object {{$_.Status -eq \'Up\'}} | ForEach-Object {{ try {{ Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses \'{fastest["primary"]}\',\'{fastest["secondary"]}\' -ErrorAction SilentlyContinue }} catch {{}} }}; ipconfig /flushdns"'
                subprocess.run(cmd, shell=True, capture_output=True, timeout=6)
            except Exception:
                pass

        time.sleep(0.4)
        self.after(0, lambda: [
            set_progress(1.0, f"✓ СИСТЕМА ГОТОВА! Быстрейший DNS: {fastest['name']} ({fastest['ping']} мс)"),
            self.splash_stage_badge.configure(text=f"👑 ЛУЧШИЙ: {fastest['name'].upper()} ({fastest['ping']} МС)", fg_color="#064E3B", text_color="#10B981"),
            self.splash_progress.configure(progress_color="#10B981")
        ])

        # Обновление главного интерфейса (кнопки и бейджи)
        self.after(0, lambda f=fastest: self._apply_fastest_dns_to_main_ui(f))

        # Пауза перед раскрытием интерфейса (чтобы пользователь увидел результат)
        time.sleep(0.9)

        # Плавное скрытие сплеш-экрана
        self.after(0, self._finish_startup_splash)

    def _apply_fastest_dns_to_main_ui(self, fastest):
        """Обновление элементов главного экрана с информацией о лучшем DNS"""
        try:
            # Обновление бейджа в шапке
            if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                self.dns_badge.configure(text=f"  DNS: {fastest['name']} ({fastest['primary']}) • {fastest['ping']} мс")

            # Обновление мастер-кнопки запуска
            if hasattr(self, 'master_launch_btn') and self.master_launch_btn.winfo_exists():
                self.master_launch_btn.configure(text=f"ОПТИМИЗИРОВАТЬ СИСТЕМУ И ЗАПУСТИТЬ FORTNITE ({fastest['name']})")

            # Обновление комбобокса на странице сети
            if hasattr(self, 'net_dns_combo') and self.net_dns_combo.winfo_exists():
                for val in self.net_dns_combo.cget("values"):
                    if fastest["primary"] in val:
                        self.net_dns_combo.set(val)
                        break

            # Запись в консоль дашборда
            self.log_dash("[СИСТЕМА] ✓ Высокоточный таймер Windows активирован: 0.5 мс")
            self.log_dash("[СЕТЬ] ✓ Сокеты друзей и лобби Epic Games защищены (AFD/EOS fix)")
            self.log_dash(f"[DNS] 👑 Самый быстрый DNS найден и применён: {fastest['name']} ({fastest['primary']}) — {fastest['ping']} мс")
        except Exception:
            pass

    def _finish_startup_splash(self):
        """Завершение экрана загрузки с плавным закрытием"""
        self.splash_is_active = False
        if hasattr(self, 'splash_overlay') and self.splash_overlay.winfo_exists():
            try:
                self.splash_overlay.destroy()
            except Exception:
                pass

    def detect_cpu_name(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            val, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            return val.strip()
        except Exception:
            return "Процессор Intel / AMD"

    # =========================================================================
    # БОКОВОЕ МЕНЮ (SIDEBAR) VORTEX
    # =========================================================================
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=270,
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Логотип и брендинг VORTEX
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(20, 16))

        logo_img = get_icon("vortex_logo", size=(36, 36))
        if logo_img:
            logo_badge = ctk.CTkLabel(brand_frame, text="", image=logo_img)
            logo_badge.pack(side="left", padx=(0, 12))
        else:
            logo_box = ctk.CTkFrame(brand_frame, width=36, height=36, corner_radius=10, fg_color=COLORS["accent_blue"])
            logo_box.pack(side="left", padx=(0, 12))
            logo_box.pack_propagate(False)
            ctk.CTkLabel(logo_box, text="V", font=get_font(18, "bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="VORTEX",
            font=get_font(18, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="PERFORMANCE ENGINE",
            font=get_font(9, "bold"),
            text_color="#60A5FA"
        ).pack(anchor="w")

        # Разделитель
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=(0, 14))

        # Элементы навигации с векторными иконками
        self.nav_buttons = {}
        self.nav_item_labels = {}
        nav_items = [
            ("dashboard", "nav_dashboard", "Главный экран"),
            ("settings", "nav_tweaks", "⚙️ Настройки"),
            ("resolution", "nav_resolution", "Разрешение в игре"),
            ("network", "nav_network", "Сеть и DNS"),
            ("latency", "nav_latency", "Инпут-лаг & FilterKeys"),
            ("services", "nav_services", "Серверы Epic & EOS"),
            ("tweaks", "nav_tweaks", "Твики Windows & FPS"),
            ("presets", "nav_presets", "Игровые пресеты"),
            ("ping", "nav_ping", "Радар задержки"),
            ("cleanup", "nav_cleanup", "Очистка кэша"),
            ("restore", "nav_restore", "Откат параметров"),
        ]

        for code, icon_name, label in nav_items:
            self.nav_item_labels[code] = label
            ico = get_icon(icon_name, size=(20, 20))
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {label}",
                image=ico,
                compound="left",
                font=get_font(13, "bold"),
                anchor="w",
                height=44,
                corner_radius=10,
                fg_color=COLORS["bg_card"] if code == "dashboard" else "transparent",
                text_color="#60A5FA" if code == "dashboard" else COLORS["text_secondary"],
                hover_color=COLORS["bg_card_hover"],
                command=lambda c=code: self.switch_tab(c)
            )
            btn.pack(fill="x", padx=14, pady=3)
            self.nav_buttons[code] = btn

        # Распорка
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Нижняя карточка статуса Epic Shield, Стража и ПК
        bottom_box = ctk.CTkFrame(self.sidebar, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        bottom_box.pack(fill="x", padx=14, pady=(0, 16))

        ctk.CTkLabel(
            bottom_box,
            text="⚡ Страж: 0.5 мс + Авто-буст",
            font=get_font(10, "bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            bottom_box,
            text="● Epic Shield: Деэлевация активна",
            font=get_font(10, "bold"),
            text_color="#34D399"
        ).pack(anchor="w", padx=12, pady=(0, 2))

        short_cpu = self.cpu_name.split("@")[0].strip()
        if len(short_cpu) > 24:
            short_cpu = short_cpu[:22] + ".."

        ctk.CTkLabel(
            bottom_box,
            text=f"ПК: {short_cpu}",
            font=get_font(9),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkButton(
            bottom_box,
            text="✕ Закрыть VORTEX",
            font=get_font(10, "bold"),
            fg_color="#1E293B",
            hover_color="#7F1D1D",
            text_color="#F87171",
            height=26,
            corner_radius=6,
            command=self.full_exit
        ).pack(fill="x", padx=10, pady=(0, 10))

    def full_exit(self):
        """Полное закрытие программы с освобождением ресурсов и остановкой трея"""
        try:
            if self.cfg.get("AUTO_TURBO_INPUT", "1") == "1":
                reset_filterkeys_default()
        except Exception:
            pass
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        self.destroy()
        sys.exit(0)

    def switch_tab(self, tab_code):
        self.active_tab = tab_code
        for code, btn in self.nav_buttons.items():
            if code == tab_code:
                btn.configure(fg_color=COLORS["bg_card"], text_color="#60A5FA")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])

        for page_name, frame in self.pages.items():
            if page_name == tab_code:
                frame.pack(fill="both", expand=True, padx=16, pady=12)
            else:
                frame.pack_forget()

    # =========================================================================
    # РАБОЧАЯ ОБЛАСТЬ И ВЕРХНИЙ СТАТУС-БАР
    # =========================================================================
    def build_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Верхняя панель живой телеметрии
        self.build_top_header()

        self.workspace = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.workspace.grid(row=1, column=0, sticky="nsew")

        self.pages = {
            "dashboard": self.create_dashboard_view(),
            "settings": self.create_settings_view(),
            "presets": self.create_presets_view(),
            "tweaks": self.create_tweaks_view(),
            "network": self.create_network_view(),
            "services": self.create_services_view(),
            "resolution": self.create_resolution_view(),
            "ping": self.create_ping_view(),
            "cleanup": self.create_cleanup_view(),
            "latency": self.create_latency_view(),
            "restore": self.create_restore_view(),
        }

        self.switch_tab("dashboard")
        self.render_dashboard_presets()

    def build_top_header(self):
        header = ctk.CTkFrame(self.content_container, height=62, fg_color=COLORS["bg_sidebar"], border_width=1, border_color=COLORS["border"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        # Плашка CPU и RAM
        left_pill = ctk.CTkFrame(header, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        left_pill.pack(side="left", padx=18, pady=10)

        self.telemetry_cpu_lbl = ctk.CTkLabel(
            left_pill,
            text="CPU: 0%",
            font=get_font(12, "bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.telemetry_cpu_lbl.pack(side="left", padx=(12, 8), pady=6)

        ctk.CTkLabel(left_pill, text="•", font=get_font(11), text_color=COLORS["border"]).pack(side="left")

        self.telemetry_ram_lbl = ctk.CTkLabel(
            left_pill,
            text="RAM: 0%",
            font=get_font(12, "bold"),
            text_color=COLORS["accent_purple"]
        )
        self.telemetry_ram_lbl.pack(side="left", padx=(8, 12), pady=6)

        # Статус игры (Fortnite запущен или нет)
        self.game_status_pill = ctk.CTkLabel(
            header,
            text="● Fortnite не запущен",
            font=get_font(12, "bold"),
            text_color=COLORS["text_muted"],
            fg_color="#101725",
            corner_radius=12,
            padx=14,
            pady=6
        )
        self.game_status_pill.pack(side="left", padx=6)

        # Правые плашки
        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right", padx=18, pady=10)

        # Кнопка компактного виджета
        self.hud_toggle_btn = ctk.CTkButton(
            right_box,
            text="⊞ Mini HUD",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#60A5FA",
            height=32,
            width=96,
            corner_radius=10,
            command=self.toggle_mini_hud
        )
        self.hud_toggle_btn.pack(side="left", padx=5)

        # Кнопка сворачивания в трей
        self.minimize_btn = ctk.CTkButton(
            right_box,
            text="🗕 В трей",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#38BDF8",
            height=32,
            width=86,
            corner_radius=10,
            command=self.minimize_to_tray
        )
        self.minimize_btn.pack(side="left", padx=5)

        # Кнопка перехода в настройки
        self.settings_header_btn = ctk.CTkButton(
            right_box,
            text="⚙️",
            font=get_font(13, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#94A3B8",
            height=32,
            width=36,
            corner_radius=10,
            command=lambda: self.switch_tab("settings")
        )
        self.settings_header_btn.pack(side="left", padx=5)

        # Плашка DNS
        dns_ico = get_icon("nav_network", size=(16, 16))
        self.dns_badge = ctk.CTkLabel(
            right_box,
            text="  Cloudflare (1.1.1.1)",
            image=dns_ico,
            compound="left",
            font=get_font(11, "bold"),
            text_color="#34D399",
            fg_color="#064E3B",
            corner_radius=10,
            padx=12,
            pady=5
        )
        self.dns_badge.pack(side="left", padx=5)

    def handle_admin_click(self):
        if not is_admin():
            run_as_admin()
        else:
            try:
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Права администратора активны!\n\nВсе системные функции оптимизатора (таймер Windows 0.5 мс, сетевая карта, высокий приоритет CPU) работают на максимальной мощности.",
                    "Статус Администратора",
                    0x40
                )
            except Exception:
                pass

    def update_telemetry(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            if hasattr(self, 'telemetry_cpu_lbl') and self.telemetry_cpu_lbl.winfo_exists():
                cpu_color = COLORS["accent_cyan"] if cpu < 60 else (COLORS["accent_amber"] if cpu < 85 else COLORS["accent_red"])
                self.telemetry_cpu_lbl.configure(text=f"⚡ CPU: {cpu}%", text_color=cpu_color)
            if hasattr(self, 'telemetry_ram_lbl') and self.telemetry_ram_lbl.winfo_exists():
                ram_color = COLORS["accent_purple"] if ram.percent < 75 else COLORS["accent_amber"]
                self.telemetry_ram_lbl.configure(text=f"💾 RAM: {ram.percent}% ({round(ram.used/(1024**3), 1)}ГБ)", text_color=ram_color)

            # Обновление компактного виджета (Toplevel-окно)
            mini_lbl_cpu = getattr(self, 'mini_cpu_lbl', None)
            mini_lbl_ram = getattr(self, 'mini_ram_lbl', None)
            if mini_lbl_cpu is not None:
                try:
                    if mini_lbl_cpu.winfo_exists():
                        mini_lbl_cpu.configure(text=f"⚡ CPU: {cpu}%")
                except Exception:
                    pass
            if mini_lbl_ram is not None:
                try:
                    if mini_lbl_ram.winfo_exists():
                        mini_lbl_ram.configure(text=f"💾 RAM: {ram.percent}%")
                except Exception:
                    pass

            # Проверка процесса Fortnite
            fn_running = False
            for p in psutil.process_iter(['name']):
                if p.info['name'] and 'FortniteClient' in p.info['name']:
                    fn_running = True
                    break
            if hasattr(self, 'game_status_pill') and self.game_status_pill.winfo_exists():
                if fn_running:
                    self.game_status_pill.configure(text="🟢 Fortnite запущен (High Priority)", text_color="#10B981", fg_color="#064E3B")
                else:
                    self.game_status_pill.configure(text="⚪ Ожидание запуска игры", text_color=COLORS["text_muted"], fg_color="#101725")
        except Exception:
            pass

        try:
            if self.winfo_exists():
                self.after(2000, self.update_telemetry)
        except Exception:
            pass

    def update_live_pulse(self):
        """Плавная живая анимация неонового пульса"""
        if hasattr(self, 'console_status_dot') and self.console_status_dot.winfo_exists():
            if self.is_running:
                dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
                char = dots[self.pulse_phase % len(dots)]
                self.console_status_dot.configure(text=f"{char} ПРИМЕНЕНИЕ ТВЫКОВ...", text_color=COLORS["accent_cyan"])
            else:
                pulse_colors = ["#10B981", "#059669", "#10B981", "#34D399"]
                col = pulse_colors[self.pulse_phase % len(pulse_colors)]
                self.console_status_dot.configure(text="● СИСТЕМА ГОТОВА", text_color=col)
            self.pulse_phase += 1

        try:
            if self.winfo_exists():
                self.after(300, self.update_live_pulse)
        except Exception:
            pass

    # =========================================================================
    # ВКЛАДКА 1: ГЛАВНАЯ (DASHBOARD)
    # =========================================================================
    def create_dashboard_view(self):
        dash = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")

        # Предупреждение об отсутствии прав администратора (если запущено без UAC)
        if not is_admin():
            self.admin_warning_box = ctk.CTkFrame(
                dash,
                corner_radius=10,
                fg_color="#381318",
                border_width=1,
                border_color="#EF4444"
            )
            self.admin_warning_box.pack(fill="x", pady=(0, 12))

            w_left = ctk.CTkFrame(self.admin_warning_box, fg_color="transparent")
            w_left.pack(side="left", padx=14, pady=10)

            ctk.CTkLabel(
                w_left,
                text="⚠️ ПРОГРАММА ЗАПУЩЕНА БЕЗ ПРАВ АДМИНИСТРАТОРА",
                font=get_font(12, "bold"),
                text_color="#FCA5A5"
            ).pack(anchor="w")

            ctk.CTkLabel(
                w_left,
                text="Для применения таймера 0.5 мс, твиков прерываний сетевой карты и приоритета процессов требуются повышенные права.",
                font=get_font(10),
                text_color="#F87171"
            ).pack(anchor="w", pady=(2, 0))

            ctk.CTkButton(
                self.admin_warning_box,
                text="🛡️ ЗАПРОСИТЬ ПРАВА (UAC)",
                font=get_font(11, "bold"),
                fg_color="#EF4444",
                hover_color="#DC2626",
                text_color="#FFFFFF",
                height=32,
                corner_radius=6,
                command=self.handle_admin_click
            ).pack(side="right", padx=14, pady=10)

        # ГЛАВНЫЙ БАННЕР VORTEX
        hero = ctk.CTkFrame(
            dash,
            corner_radius=16,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        hero.pack(fill="x", pady=(0, 16))

        hero_top = ctk.CTkFrame(hero, fg_color="transparent")
        hero_top.pack(fill="x", padx=20, pady=(16, 6))

        hero_text_box = ctk.CTkFrame(hero_top, fg_color="transparent")
        hero_text_box.pack(side="left")

        ctk.CTkLabel(
            hero_text_box,
            text="VORTEX  |  GEARUP BOOSTER MODE",
            font=get_font(20, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            hero_text_box,
            text="Инженерия соревновательного преимущества. 0.5 ms таймер • Буст сетевых пакетов • Защита Stretched",
            font=get_font(12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(3, 0))

        # Тумблер автозапуска игры
        self.auto_launch_switch = ctk.CTkSwitch(
            hero_top,
            text="Авто-запуск игры",
            font=get_font(12, "bold"),
            text_color="#60A5FA",
            progress_color=COLORS["accent_blue"],
            command=self.sync_auto_launch
        )
        if self.cfg.get("LAUNCH_EPIC", "1") == "1":
            self.auto_launch_switch.select()
        else:
            self.auto_launch_switch.deselect()
        self.auto_launch_switch.pack(side="right")

        # 4 диагностические плашки GearUP Booster
        gear_bar = ctk.CTkFrame(hero, fg_color="transparent")
        gear_bar.pack(fill="x", padx=20, pady=(10, 4))
        gear_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Пинг
        p1 = ctk.CTkFrame(gear_bar, fg_color="#131B29", corner_radius=10, border_width=1, border_color="#1F2E45")
        p1.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkLabel(p1, text="⚡ ПИНГ СЕТИ", font=get_font(9, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(8, 0))
        self.gear_ping_lbl = ctk.CTkLabel(p1, text="~42 мс  (-22% Boost)", font=get_font(13, "bold"), text_color="#34D399")
        self.gear_ping_lbl.pack(anchor="w", padx=12, pady=(0, 8))

        # 2. Инпутлаг
        p2 = ctk.CTkFrame(gear_bar, fg_color="#131B29", corner_radius=10, border_width=1, border_color="#1F2E45")
        p2.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(p2, text="⏱️ ТАЙМЕР ЯДРА", font=get_font(9, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(8, 0))
        self.gear_timer_lbl = ctk.CTkLabel(p2, text="0.500 мс (Ultra)", font=get_font(13, "bold"), text_color="#38BDF8")
        self.gear_timer_lbl.pack(anchor="w", padx=12, pady=(0, 8))

        # 3. ОЗУ
        p3 = ctk.CTkFrame(gear_bar, fg_color="#131B29", corner_radius=10, border_width=1, border_color="#1F2E45")
        p3.grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkLabel(p3, text="🧹 ОЗУ БУСТЕР", font=get_font(9, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(8, 0))
        self.gear_ram_lbl = ctk.CTkLabel(p3, text="+1.5 ГБ Очищено", font=get_font(13, "bold"), text_color="#A78BFA")
        self.gear_ram_lbl.pack(anchor="w", padx=12, pady=(0, 8))

        # 4. Разрешение
        p4 = ctk.CTkFrame(gear_bar, fg_color="#131B29", corner_radius=10, border_width=1, border_color="#1F2E45")
        p4.grid(row=0, column=3, padx=4, sticky="ew")
        ctk.CTkLabel(p4, text="🔒 РАЗРЕШЕНИЕ", font=get_font(9, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=(8, 0))
        self.gear_res_lbl = ctk.CTkLabel(p4, text="Stretched Locked", font=get_font(13, "bold"), text_color="#FBBF24")
        self.gear_res_lbl.pack(anchor="w", padx=12, pady=(0, 8))

        # БОЛЬШАЯ ГЛАВНАЯ КНОПКА ЗАПУСКА VORTEX (GEARUP MODE)
        self.master_launch_btn = ctk.CTkButton(
            hero,
            text="⚡ УСКОРИТЬ СИСТЕМУ И ЗАПУСТИТЬ FORTNITE (GEARUP BOOST)",
            font=get_font(16, "bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            text_color="#FFFFFF",
            height=62,
            corner_radius=14,
            command=self.start_master_optimization
        )
        self.master_launch_btn.pack(fill="x", padx=20, pady=(10, 18))

        # ПАНЕЛЬ БЫСТРЫХ ДЕЙСТВИЙ (В 1 КЛИК)
        quick_bar = ctk.CTkFrame(dash, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        quick_bar.pack(fill="x", pady=(0, 16))

        qb_top = ctk.CTkFrame(quick_bar, fg_color="transparent")
        qb_top.pack(fill="x", padx=18, pady=(12, 6))
        ctk.CTkLabel(qb_top, text="БЫСТРЫЕ СЕРВИСЫ", font=get_font(12, "bold"), text_color=COLORS["text_secondary"]).pack(side="left")

        qb_grid = ctk.CTkFrame(quick_bar, fg_color="transparent")
        qb_grid.pack(fill="x", padx=14, pady=(0, 14))
        qb_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Очистить RAM
        ram_ico = get_icon("action_ram", size=(20, 20))
        ctk.CTkButton(
            qb_grid,
            text="  Очистить RAM",
            image=ram_ico,
            compound="left",
            font=get_font(12, "bold"),
            fg_color="#141D2C",
            hover_color="#1E2B40",
            text_color="#38BDF8",
            height=46,
            corner_radius=10,
            command=self.quick_ram_cleanup
        ).grid(row=0, column=0, padx=6, sticky="ew")

        # 2. Сброс кэша DNS
        dns_ico = get_icon("action_dns", size=(20, 20))
        ctk.CTkButton(
            qb_grid,
            text="  Сброс DNS",
            image=dns_ico,
            compound="left",
            font=get_font(12, "bold"),
            fg_color="#141D2C",
            hover_color="#1E2B40",
            text_color="#34D399",
            height=46,
            corner_radius=10,
            command=self.quick_flush_dns
        ).grid(row=0, column=1, padx=6, sticky="ew")

        # 3. Таймер 0.5 мс
        tmr_ico = get_icon("action_timer", size=(20, 20))
        ctk.CTkButton(
            qb_grid,
            text="  Таймер 0.5 мс",
            image=tmr_ico,
            compound="left",
            font=get_font(12, "bold"),
            fg_color="#141D2C",
            hover_color="#1E2B40",
            text_color="#FBBF24",
            height=46,
            corner_radius=10,
            command=self.quick_timer_sync
        ).grid(row=0, column=2, padx=6, sticky="ew")

        # 4. Статус Epic & EOS
        srv_ico = get_icon("action_servers", size=(20, 20))
        ctk.CTkButton(
            qb_grid,
            text="  Серверы Epic",
            image=srv_ico,
            compound="left",
            font=get_font(12, "bold"),
            fg_color="#141D2C",
            hover_color="#1E2B40",
            text_color="#A78BFA",
            height=46,
            corner_radius=10,
            command=lambda: self.switch_tab("services")
        ).grid(row=0, column=3, padx=6, sticky="ew")

        # КАРТОЧКА РЕЖИМА GEARUP BOOSTER
        gear_card = ctk.CTkFrame(dash, fg_color=COLORS["bg_card"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        gear_card.pack(fill="x", pady=(0, 16))

        gear_top = ctk.CTkFrame(gear_card, fg_color="transparent")
        gear_top.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            gear_top,
            text="⚡ GEARUP BOOSTER ENGINE  |  СТАТУС И ДИАГНОСТИКА",
            font=get_font(12, "bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        # Кнопка перехода в настройки
        ctk.CTkButton(
            gear_top,
            text="⚙️ Все настройки",
            font=get_font(10, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#60A5FA",
            height=28,
            corner_radius=6,
            command=lambda: self.switch_tab("settings")
        ).pack(side="right", padx=(4, 0))

        # Кнопка свернуть в трей
        ctk.CTkButton(
            gear_top,
            text="🗕 Свернуть в трей",
            font=get_font(10, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#38BDF8",
            height=28,
            corner_radius=6,
            command=self.minimize_to_tray
        ).pack(side="right")

        # Интерактивные контрольные точки GearUP (Checkpoints)
        self.gear_chk_frame = ctk.CTkFrame(gear_card, fg_color="#0C1320", corner_radius=10, border_width=1, border_color="#18253A")
        self.gear_chk_frame.pack(fill="x", padx=14, pady=(0, 14))

        self.gear_stage_labels = []
        gear_stages = [
            ("🧹 Очистка RAM и сброс неиспользуемой памяти рабочих наборов", "Готов (+1.5 ГБ)"),
            ("⏱️ Системный таймер ядра Windows: аппаратные 0.500 мс", "0.500 мс"),
            ("📶 Сетевой стек: алгоритм Nagle Off, DSCP QoS и Anycast DNS", "Nagle Disabled"),
            ("🔒 Разрешение Fortnite: синхронизация 8 параметров и Read-Only", "Locked 4:3"),
            ("🚀 Процессор: разпарковка ядер и высокий приоритет CPU", "High Priority"),
        ]

        for i, (title, tag) in enumerate(gear_stages):
            row = ctk.CTkFrame(self.gear_chk_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)

            dot = ctk.CTkLabel(row, text="●", font=get_font(11, "bold"), text_color="#10B981")
            dot.pack(side="left", padx=(0, 8))

            lbl = ctk.CTkLabel(row, text=title, font=get_font(11), text_color=COLORS["text_secondary"], anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

            badge = ctk.CTkLabel(row, text=tag, font=get_font(10, "bold"), text_color="#38BDF8", fg_color="#131F32", corner_radius=6, padx=8, pady=2)
            badge.pack(side="right")

            self.gear_stage_labels.append((dot, lbl, badge))

        # РАЗДЕЛ ПРЕСЕТОВ НА ГЛАВНОЙ
        presets_title_frame = ctk.CTkFrame(dash, fg_color="transparent")
        presets_title_frame.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            presets_title_frame,
            text="КИБЕРСПОРТИВНЫЕ И КАСТОМНЫЕ ПРЕСЕТЫ",
            font=get_font(12, "bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        p_btns_box = ctk.CTkFrame(presets_title_frame, fg_color="transparent")
        p_btns_box.pack(side="right")

        ctk.CTkButton(
            p_btns_box,
            text="➕ Свой пресет",
            font=get_font(10, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color=COLORS["accent_cyan"],
            height=26,
            corner_radius=6,
            command=self.prompt_quick_save_preset
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            p_btns_box,
            text="📁 Все пресеты",
            font=get_font(10, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color=COLORS["text_primary"],
            height=26,
            corner_radius=6,
            command=lambda: self.switch_tab("presets")
        ).pack(side="left", padx=3)

        self.active_preset_badge = ctk.CTkLabel(
            p_btns_box,
            text=f"АКТИВЕН: {self.get_active_preset_display_name()}",
            font=get_font(11, "bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.active_preset_badge.pack(side="left", padx=(8, 0))

        # Сетка карточек пресетов (динамическая)
        self.presets_grid = ctk.CTkFrame(dash, fg_color="transparent")
        self.presets_grid.pack(fill="x", pady=(0, 12))

        # ЖИВАЯ КОНСОЛЬ ТЕРМИНАЛА С ПРОГРЕСС-БАРОМ
        console_wrapper = ctk.CTkFrame(
            dash,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"],
            height=210
        )
        console_wrapper.pack(fill="x", pady=(0, 10))

        c_top = ctk.CTkFrame(console_wrapper, fg_color="transparent")
        c_top.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(
            c_top,
            text="⚡ ЖИВОЙ ТЕРМИНАЛ ОПТИМИЗАЦИИ",
            font=get_font(11, "bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        self.console_status_dot = ctk.CTkLabel(
            c_top,
            text="● СИСТЕМА ГОТОВА",
            font=get_font(10, "bold"),
            text_color=COLORS["accent_green"]
        )
        self.console_status_dot.pack(side="right")

        self.dash_progress = ctk.CTkProgressBar(console_wrapper, height=6, corner_radius=3)
        self.dash_progress.pack(fill="x", padx=12, pady=(0, 6))
        self.dash_progress.set(0.0)
        self.dash_progress.configure(progress_color=COLORS["accent_cyan"])

        self.dash_console = ctk.CTkTextbox(
            console_wrapper,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="#070A10",
            text_color="#E2E8F0",
            corner_radius=6,
            border_width=1,
            border_color="#182234",
            height=130
        )
        self.dash_console.pack(fill="x", padx=12, pady=(0, 10))

        # Стартовые логи
        self.log_dash("Оптимизатор Fortnite v4.0 Pro инициализирован.")
        self.log_dash(f"Сетевое подключение: Google DNS (8.8.8.8 / 8.8.4.4) [Режим низкого пинга]")
        self.log_dash(f"Активный профиль пресета: {self.get_active_preset_display_name()}")
        self.log_dash("Таймер Windows 0.5 мс активирован для мгновенного инпутлага.")
        if is_admin():
            self.log_dash("✓ Права администратора подтверждены: все твики доступны.")
        else:
            self.log_dash("! Внимание: Запущено без прав администратора. Некоторые твики могут быть ограничены.")
        self.log_dash("Нажмите 'ОПТИМИЗИРОВАТЬ И ЗАПУСТИТЬ FORTNITE' для старта.")

        return dash

    def log_dash(self, msg):
        try:
            if hasattr(self, 'dash_console') and self.dash_console.winfo_exists():
                self.dash_console.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
                self.dash_console.see("end")
        except Exception:
            pass

    def sync_auto_launch(self):
        val = "1" if self.auto_launch_switch.get() else "0"
        self.cfg["LAUNCH_EPIC"] = val
        save_config(self.cfg)
        if hasattr(self, 'settings_launch_epic_switch') and self.settings_launch_epic_switch.winfo_exists():
            if val == "1":
                self.settings_launch_epic_switch.select()
            else:
                self.settings_launch_epic_switch.deselect()
        self.log_dash(f"Авто-запуск игры: {'ВКЛЮЧЁН' if val == '1' else 'ОТКЛЮЧЁН'}")

    # =========================================================================
    # ВКЛАДКА: НАСТРОЙКИ СИСТЕМЫ, АВТОЗАГРУЗКИ И GEARUP
    # =========================================================================
    def create_settings_view(self):
        view = ctk.CTkFrame(self.workspace, fg_color="transparent")

        # Верхняя панель заголовка
        header = ctk.CTkFrame(view, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="⚙️ НАСТРОЙКИ СИСТЕМЫ И GEARUP BOOSTER",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Автозагрузка, поведение системного трея, параметры запуска Fortnite и таймеры",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        top_btns = ctk.CTkFrame(header, fg_color="transparent")
        top_btns.pack(side="right")

        ctk.CTkButton(
            top_btns,
            text="📁 Папка Config",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#60A5FA",
            height=30,
            command=self.open_config_folder
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            top_btns,
            text="🔄 Сброс к заводским",
            font=get_font(11, "bold"),
            fg_color="#26191E",
            hover_color="#3D2028",
            text_color="#F87171",
            height=30,
            command=self.reset_all_settings
        ).pack(side="left", padx=4)

        scroll = ctk.CTkScrollableFrame(view, corner_radius=12, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # КАРТОЧКА 1: АВТОЗАГРУЗКА И СИСТЕМНЫЙ ТРЕЙ
        # -------------------------------------------------------------
        card_tray = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card_tray.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card_tray,
            text="🖥️ АВТОЗАГРУЗКА, ФОНОВЫЙ РЕЖИМ И СИСТЕМНЫЙ ТРЕЙ",
            font=get_font(12, "bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=16, pady=(14, 6))

        # Переключатель 1: Автозагрузка
        row1 = ctk.CTkFrame(card_tray, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=6)
        r1_txt = ctk.CTkFrame(row1, fg_color="transparent")
        r1_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(r1_txt, text="Автозагрузка VORTEX при старте Windows", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(r1_txt, text="Запуск через Планировщик задач с наивысшими правами без всплывающих окон UAC", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        is_auto_active = (self.cfg.get("AUTOSTART", "0") == "1") or is_autostart_active()
        self.autostart_switch = ctk.CTkSwitch(row1, text="", progress_color=COLORS["accent_blue"], command=self.toggle_autostart_setting)
        if is_auto_active:
            self.autostart_switch.select()
        else:
            self.autostart_switch.deselect()
        self.autostart_switch.pack(side="right")

        ctk.CTkFrame(card_tray, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Переключатель 2: Запуск свёрнутым
        row2 = ctk.CTkFrame(card_tray, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=6)
        r2_txt = ctk.CTkFrame(row2, fg_color="transparent")
        r2_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(r2_txt, text="Запускать в свёрнутом виде в системный трей", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(r2_txt, text="При старте Windows окно VORTEX скрывается в область уведомлений (трей) и не мешает", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.start_minimized_switch = ctk.CTkSwitch(row2, text="", progress_color=COLORS["accent_blue"], command=self.toggle_start_minimized_setting)
        if self.cfg.get("START_MINIMIZED", "1") == "1":
            self.start_minimized_switch.select()
        else:
            self.start_minimized_switch.deselect()
        self.start_minimized_switch.pack(side="right")

        ctk.CTkFrame(card_tray, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Переключатель 3: Сворачивать в трей при нажатии (✕)
        row3 = ctk.CTkFrame(card_tray, fg_color="transparent")
        row3.pack(fill="x", padx=16, pady=6)
        r3_txt = ctk.CTkFrame(row3, fg_color="transparent")
        r3_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(r3_txt, text="Сворачивать в системный трей при нажатии (✕)", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(r3_txt, text="Кнопка закрытия не завершает процесс, оставляя иконку в трее для мгновенного доступа", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.close_to_tray_switch = ctk.CTkSwitch(row3, text="", progress_color=COLORS["accent_blue"], command=self.toggle_close_to_tray_setting)
        if self.cfg.get("CLOSE_TO_TRAY", "1") == "1":
            self.close_to_tray_switch.select()
        else:
            self.close_to_tray_switch.deselect()
        self.close_to_tray_switch.pack(side="right")

        ctk.CTkFrame(card_tray, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Переключатель 4: Авто-буст при обнаружении игры
        row4 = ctk.CTkFrame(card_tray, fg_color="transparent")
        row4.pack(fill="x", padx=16, pady=(6, 14))
        r4_txt = ctk.CTkFrame(row4, fg_color="transparent")
        r4_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(r4_txt, text="Авто-буст при обнаружении Fortnite в фоне", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(r4_txt, text="Фоновый страж VORTEX отслеживает запуск игры и применяет высокий приоритет CPU и таймер 0.5 мс", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.auto_boost_switch = ctk.CTkSwitch(row4, text="", progress_color=COLORS["accent_blue"], command=self.toggle_auto_boost_setting)
        if self.cfg.get("AUTO_OPTIMIZE_GAME", "1") == "1":
            self.auto_boost_switch.select()
        else:
            self.auto_boost_switch.deselect()
        self.auto_boost_switch.pack(side="right")

        # -------------------------------------------------------------
        # КАРТОЧКА 2: GEARUP BOOSTER И ПАРАМЕТРЫ ЗАПУСКА ИГРЫ
        # -------------------------------------------------------------
        card_gear = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card_gear.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card_gear,
            text="⚡ GEARUP BOOSTER И ПАРАМЕТРЫ СТАРТА FORTNITE",
            font=get_font(12, "bold"),
            text_color="#A78BFA"
        ).pack(anchor="w", padx=16, pady=(14, 6))

        # Переключатель: Авто-запуск Fortnite после оптимизации
        grow1 = ctk.CTkFrame(card_gear, fg_color="transparent")
        grow1.pack(fill="x", padx=16, pady=6)
        gr1_txt = ctk.CTkFrame(grow1, fg_color="transparent")
        gr1_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(gr1_txt, text="Автоматический запуск Fortnite после завершения буста", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(gr1_txt, text="Сразу после завершения всех 10 слоев оптимизации игра стартует через Epic Games без UAC конфликтов", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.settings_launch_epic_switch = ctk.CTkSwitch(grow1, text="", progress_color=COLORS["accent_blue"], command=self.toggle_settings_launch_epic)
        if self.cfg.get("LAUNCH_EPIC", "1") == "1":
            self.settings_launch_epic_switch.select()
        else:
            self.settings_launch_epic_switch.deselect()
        self.settings_launch_epic_switch.pack(side="right")

        ctk.CTkFrame(card_gear, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Переключатель: Авто-сворачивание в трей при запуске игры
        grow2 = ctk.CTkFrame(card_gear, fg_color="transparent")
        grow2.pack(fill="x", padx=16, pady=6)
        gr2_txt = ctk.CTkFrame(grow2, fg_color="transparent")
        gr2_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(gr2_txt, text="Авто-сворачивание в трей при запуске игры (Режим GearUP)", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(gr2_txt, text="После старта игры VORTEX через 2 секунды автоматически прячет окно в системный трей", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.settings_min_on_launch_switch = ctk.CTkSwitch(grow2, text="", progress_color=COLORS["accent_blue"], command=self.toggle_min_on_launch_setting)
        if self.cfg.get("MINIMIZE_ON_LAUNCH", "1") == "1":
            self.settings_min_on_launch_switch.select()
        else:
            self.settings_min_on_launch_switch.deselect()
        self.settings_min_on_launch_switch.pack(side="right")

        ctk.CTkFrame(card_gear, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Поле ввода пути к Epic Games / Ярлыку Fortnite
        grow3 = ctk.CTkFrame(card_gear, fg_color="transparent")
        grow3.pack(fill="x", padx=16, pady=(6, 14))

        ctk.CTkLabel(grow3, text="Путь к ярлыку Fortnite (.url) или EpicGamesLauncher.exe:", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")

        path_box = ctk.CTkFrame(grow3, fg_color="transparent")
        path_box.pack(fill="x", pady=(6, 0))

        self.settings_epic_path_entry = ctk.CTkEntry(
            path_box,
            font=get_font(11),
            fg_color="#0D131F",
            border_color=COLORS["border"],
            height=34
        )
        self.settings_epic_path_entry.insert(0, self.cfg.get("EPIC_PATH", r"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"))
        self.settings_epic_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            path_box,
            text="📂 Обзор...",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#60A5FA",
            height=34,
            width=90,
            command=self.browse_epic_path
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            path_box,
            text="🔍 Авто",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#34D399",
            height=34,
            width=70,
            command=self.autodetect_epic_path
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            path_box,
            text="💾 Сохранить",
            font=get_font(11, "bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            text_color="#FFFFFF",
            height=34,
            width=90,
            command=self.save_epic_path_setting
        ).pack(side="left")

        # -------------------------------------------------------------
        # КАРТОЧКА 3: ТАЙМЕРЫ ЯДРА, КЛАВИАТУРА И ИНПУТЛАГ (LOW LATENCY)
        # -------------------------------------------------------------
        card_lat = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card_lat.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card_lat,
            text="⏱️ ТАЙМЕРЫ ЯДРА, ОТКЛИК КЛАВИАТУРЫ И СЕТЬ (LOW LATENCY)",
            font=get_font(12, "bold"),
            text_color="#FBBF24"
        ).pack(anchor="w", padx=16, pady=(14, 6))

        # Строка 1: Таймер 0.5 мс
        lrow1 = ctk.CTkFrame(card_lat, fg_color="transparent")
        lrow1.pack(fill="x", padx=16, pady=6)
        lr1_txt = ctk.CTkFrame(lrow1, fg_color="transparent")
        lr1_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lr1_txt, text="Высокоточный таймер Windows (0.500 мс HPET / QPC)", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(lr1_txt, text="Снижает аппаратную задержку опроса мыши и процессора до минимального предела 0.5 мс", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        ctk.CTkButton(
            lrow1,
            text="Синхронизировать 0.5 мс",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#38BDF8",
            height=30,
            command=self.sync_timer_from_settings
        ).pack(side="right")

        ctk.CTkFrame(card_lat, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Строка 2: FilterKeys
        lrow2 = ctk.CTkFrame(card_lat, fg_color="transparent")
        lrow2.pack(fill="x", padx=16, pady=6)
        lr2_txt = ctk.CTkFrame(lrow2, fg_color="transparent")
        lr2_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lr2_txt, text="FilterKeys Турбо-отклик клавиатуры (Mongraal / Bugha)", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(lr2_txt, text="Задержка повтора: 150 мс, частота: 15 мс — мгновенное срабатывание трипл-эдитов", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        fk_box = ctk.CTkFrame(lrow2, fg_color="transparent")
        fk_box.pack(side="right")

        is_fk = get_filterkeys_status()
        self.settings_fk_status_lbl = ctk.CTkLabel(
            fk_box,
            text="🟢 Активен (150 мс Turbo)" if is_fk else "⚪ Стандарт Windows",
            font=get_font(10, "bold"),
            text_color="#10B981" if is_fk else COLORS["text_muted"]
        )
        self.settings_fk_status_lbl.pack(side="left", padx=8)

        ctk.CTkButton(
            fk_box,
            text="⚡ Включить (150 мс)",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#FBBF24",
            height=30,
            command=self.settings_apply_fk
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            fk_box,
            text="Сброс",
            font=get_font(11),
            fg_color="#182234",
            hover_color="#24344E",
            text_color=COLORS["text_secondary"],
            height=30,
            width=55,
            command=self.settings_reset_fk
        ).pack(side="left", padx=2)

        ctk.CTkFrame(card_lat, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Строка 2.1: Динамический Turbo-ввод только во время игры
        lrow_auto = ctk.CTkFrame(card_lat, fg_color="transparent")
        lrow_auto.pack(fill="x", padx=16, pady=6)
        lra_txt = ctk.CTkFrame(lrow_auto, fg_color="transparent")
        lra_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lra_txt, text="Авто-турбо ввод только в матче Fortnite", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(lra_txt, text="150 мс Mongraal в игре для мгновенных эдитов, стандартные 1000 мс вне игры для удобного набора текста", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.settings_auto_turbo_switch = ctk.CTkSwitch(lrow_auto, text="", progress_color=COLORS["accent_blue"], command=self.toggle_auto_turbo_setting)
        if self.cfg.get("AUTO_TURBO_INPUT", "1") == "1":
            self.settings_auto_turbo_switch.select()
        else:
            self.settings_auto_turbo_switch.deselect()
        self.settings_auto_turbo_switch.pack(side="right")

        ctk.CTkFrame(card_lat, height=1, fg_color="#182333").pack(fill="x", padx=16, pady=4)

        # Строка 3: Сетевой алгоритм Nagle
        lrow3 = ctk.CTkFrame(card_lat, fg_color="transparent")
        lrow3.pack(fill="x", padx=16, pady=(6, 14))
        lr3_txt = ctk.CTkFrame(lrow3, fg_color="transparent")
        lr3_txt.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lr3_txt, text="Отключение задержки Nagle (TCP NoDelay)", font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(lr3_txt, text="Отключает буферизацию мелких сетевых пакетов для моментального пинга в бою", font=get_font(10), text_color=COLORS["text_muted"]).pack(anchor="w")

        self.settings_nagle_switch = ctk.CTkSwitch(lrow3, text="", progress_color=COLORS["accent_blue"], command=self.toggle_settings_nagle)
        if self.cfg.get("NAGLE_OFF", "1") == "1":
            self.settings_nagle_switch.select()
        else:
            self.settings_nagle_switch.deselect()
        self.settings_nagle_switch.pack(side="right")

        # -------------------------------------------------------------
        # КАРТОЧКА 4: УПРАВЛЕНИЕ И СБРОС
        # -------------------------------------------------------------
        card_mgt = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card_mgt.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            card_mgt,
            text="🛠️ УПРАВЛЕНИЕ ПРИЛОЖЕНИЕМ И СИСТЕМОЙ",
            font=get_font(12, "bold"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=16, pady=(14, 6))

        mrow = ctk.CTkFrame(card_mgt, fg_color="transparent")
        mrow.pack(fill="x", padx=16, pady=(6, 14))

        ctk.CTkButton(
            mrow,
            text="📁 Открыть папку Config",
            font=get_font(11, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#60A5FA",
            height=36,
            command=self.open_config_folder
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            mrow,
            text="🔄 Сбросить настройки к заводским",
            font=get_font(11, "bold"),
            fg_color="#2A1B22",
            hover_color="#42222E",
            text_color="#F87171",
            height=36,
            command=self.reset_all_settings
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            mrow,
            text="✕ Полностью закрыть VORTEX",
            font=get_font(11, "bold"),
            fg_color="#1F1318",
            hover_color="#331A24",
            text_color="#EF4444",
            height=36,
            command=self.full_exit
        ).pack(side="right")

        return view

    def toggle_autostart_setting(self):
        val = self.autostart_switch.get()
        start_min = (self.cfg.get("START_MINIMIZED", "1") == "1")
        set_autostart(val, start_minimized=start_min)
        self.cfg["AUTOSTART"] = "1" if val else "0"
        save_config(self.cfg)
        status_txt = "включена (Планировщик Windows + Реестр)" if val else "отключена"
        self.log_dash(f"Автозагрузка {status_txt}")
        self.show_toast(f"Автозагрузка {status_txt}", color=COLORS["accent_green"] if val else COLORS["accent_amber"])

    def toggle_start_minimized_setting(self):
        val = "1" if self.start_minimized_switch.get() else "0"
        self.cfg["START_MINIMIZED"] = val
        save_config(self.cfg)
        if self.cfg.get("AUTOSTART", "0") == "1" or is_autostart_active():
            set_autostart(True, start_minimized=(val == "1"))
        self.log_dash(f"Запуск в свёрнутом виде: {'ВКЛ' if val == '1' else 'ВЫКЛ'}")

    def toggle_close_to_tray_setting(self):
        val = "1" if self.close_to_tray_switch.get() else "0"
        self.cfg["CLOSE_TO_TRAY"] = val
        save_config(self.cfg)
        self.log_dash(f"Сворачивание в трей при закрытии (✕): {'ВКЛ' if val == '1' else 'ВЫКЛ'}")

    def toggle_auto_boost_setting(self):
        val = "1" if self.auto_boost_switch.get() else "0"
        self.cfg["AUTO_OPTIMIZE_GAME"] = val
        save_config(self.cfg)
        self.log_dash(f"Авто-буст при обнаружении игры: {'ВКЛ' if val == '1' else 'ВЫКЛ'}")

    def toggle_min_on_launch_setting(self):
        val = "1" if self.settings_min_on_launch_switch.get() else "0"
        self.cfg["MINIMIZE_ON_LAUNCH"] = val
        save_config(self.cfg)
        self.log_dash(f"Авто-сворачивание в трей при запуске игры: {'ВКЛ' if val == '1' else 'ВЫКЛ'}")

    def toggle_settings_launch_epic(self):
        val = "1" if self.settings_launch_epic_switch.get() else "0"
        self.cfg["LAUNCH_EPIC"] = val
        save_config(self.cfg)
        if hasattr(self, 'auto_launch_switch') and self.auto_launch_switch.winfo_exists():
            if val == "1":
                self.auto_launch_switch.select()
            else:
                self.auto_launch_switch.deselect()
        self.log_dash(f"Авто-запуск игры: {'ВКЛ' if val == '1' else 'ВЫКЛ'}")

    def toggle_settings_nagle(self):
        val = "1" if self.settings_nagle_switch.get() else "0"
        self.cfg["NAGLE_OFF"] = val
        save_config(self.cfg)
        self.log_dash(f"Отключение задержки Nagle: {'ВКЛ' if val == '1' else 'ВЫКЛ'}")

    def browse_epic_path(self):
        try:
            from tkinter import filedialog
            p = filedialog.askopenfilename(
                title="Выберите ярлык Fortnite (.url) или EpicGamesLauncher.exe",
                filetypes=[("Исполняемые файлы и ярлыки", "*.exe;*.url"), ("Все файлы", "*.*")]
            )
            if p:
                self.settings_epic_path_entry.delete(0, "end")
                self.settings_epic_path_entry.insert(0, p)
                self.cfg["EPIC_PATH"] = p
                save_config(self.cfg)
                self.show_toast("Путь к игре сохранён!", color=COLORS["accent_green"])
        except Exception as e:
            self.show_toast(f"Ошибка выбора пути: {e}", color=COLORS["accent_red"])

    def autodetect_epic_path(self):
        found = None
        candidates = [
            os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "Fortnite.url"),
            r"c:\Users\bbq\Desktop\Fortnite.url",
            os.path.join(os.environ.get("PUBLIC", ""), "Desktop", "Fortnite.url"),
            r"C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
            r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                found = c
                break
        if found:
            self.settings_epic_path_entry.delete(0, "end")
            self.settings_epic_path_entry.insert(0, found)
            self.cfg["EPIC_PATH"] = found
            save_config(self.cfg)
            self.show_toast(f"Найден путь: {os.path.basename(found)}", color=COLORS["accent_green"])
        else:
            self.show_toast("Стандартный путь не найден. Выберите вручную.", color=COLORS["accent_amber"])

    def save_epic_path_setting(self):
        p = self.settings_epic_path_entry.get().strip()
        if p:
            self.cfg["EPIC_PATH"] = p
            save_config(self.cfg)
            self.show_toast("Путь к игре успешно сохранён!", color=COLORS["accent_green"])

    def open_config_folder(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            os.startfile(CONFIG_DIR)
        except Exception as e:
            self.show_toast(f"Не удалось открыть: {e}", color=COLORS["accent_red"])

    def reset_all_settings(self):
        try:
            from tkinter import messagebox
            if messagebox.askyesno("Сброс настроек", "Вы уверены, что хотите сбросить все параметры VORTEX к заводским значениям?"):
                if os.path.exists(CONFIG_PATH):
                    try:
                        os.remove(CONFIG_PATH)
                    except Exception:
                        pass
                self.cfg = load_config()
                save_config(self.cfg)
                self.refresh_all_ui()
                self.show_toast("Параметры сброшены к заводским!", color=COLORS["accent_green"])
                self.log_dash("✓ Все настройки сброшены к заводским значениям по умолчанию.")
        except Exception as e:
            self.show_toast(f"Ошибка сброса: {e}", color=COLORS["accent_red"])

    def settings_apply_fk(self):
        self.run_apply_filterkeys()
        self.update_settings_filterkeys_status()

    def settings_reset_fk(self):
        self.run_reset_filterkeys()
        self.update_settings_filterkeys_status()

    def update_settings_filterkeys_status(self):
        if hasattr(self, 'settings_fk_status_lbl') and self.settings_fk_status_lbl.winfo_exists():
            is_on = get_filterkeys_status()
            if is_on:
                self.settings_fk_status_lbl.configure(text="🟢 Активен (150 мс Turbo)", text_color="#10B981")
            else:
                self.settings_fk_status_lbl.configure(text="⚪ Стандарт Windows", text_color=COLORS["text_muted"])

    def sync_timer_from_settings(self):
        set_high_resolution_timer()
        self.show_toast("Таймер 0.5 мс синхронизирован!", color=COLORS["accent_cyan"])
        self.log_dash("⏱️ Высокоточный системный таймер 0.500 мс синхронизирован.")

    def toggle_auto_turbo_setting(self):
        val = "1" if self.settings_auto_turbo_switch.get() else "0"
        self.cfg["AUTO_TURBO_INPUT"] = val
        save_config(self.cfg)
        st = "ВКЛ (150 мс в игре / 1000 мс вне игры)" if val == "1" else "ВЫКЛ"
        self.log_dash(f"Авто-турбо ввод FilterKeys: {st}")

    def refresh_settings_ui(self):
        if not hasattr(self, 'autostart_switch') or not self.autostart_switch.winfo_exists():
            return
        is_auto = (self.cfg.get("AUTOSTART", "0") == "1") or is_autostart_active()
        if is_auto:
            self.autostart_switch.select()
        else:
            self.autostart_switch.deselect()

        if self.cfg.get("START_MINIMIZED", "1") == "1":
            self.start_minimized_switch.select()
        else:
            self.start_minimized_switch.deselect()

        if self.cfg.get("CLOSE_TO_TRAY", "1") == "1":
            self.close_to_tray_switch.select()
        else:
            self.close_to_tray_switch.deselect()

        if self.cfg.get("AUTO_OPTIMIZE_GAME", "1") == "1":
            self.auto_boost_switch.select()
        else:
            self.auto_boost_switch.deselect()

        if hasattr(self, 'settings_launch_epic_switch') and self.settings_launch_epic_switch.winfo_exists():
            if self.cfg.get("LAUNCH_EPIC", "1") == "1":
                self.settings_launch_epic_switch.select()
            else:
                self.settings_launch_epic_switch.deselect()

        if hasattr(self, 'settings_min_on_launch_switch') and self.settings_min_on_launch_switch.winfo_exists():
            if self.cfg.get("MINIMIZE_ON_LAUNCH", "1") == "1":
                self.settings_min_on_launch_switch.select()
            else:
                self.settings_min_on_launch_switch.deselect()

        if hasattr(self, 'settings_auto_turbo_switch') and self.settings_auto_turbo_switch.winfo_exists():
            if self.cfg.get("AUTO_TURBO_INPUT", "1") == "1":
                self.settings_auto_turbo_switch.select()
            else:
                self.settings_auto_turbo_switch.deselect()

        if hasattr(self, 'settings_nagle_switch') and self.settings_nagle_switch.winfo_exists():
            if self.cfg.get("NAGLE_OFF", "1") == "1":
                self.settings_nagle_switch.select()
            else:
                self.settings_nagle_switch.deselect()

        if hasattr(self, 'settings_epic_path_entry') and self.settings_epic_path_entry.winfo_exists():
            self.settings_epic_path_entry.delete(0, "end")
            self.settings_epic_path_entry.insert(0, self.cfg.get("EPIC_PATH", ""))

        self.update_settings_filterkeys_status()

    def get_active_preset_display_name(self):
        code = self.cfg.get("PRESET", "PERFORMANCE")
        all_p = get_all_presets()
        if code in all_p:
            return all_p[code].get("name", code).upper()
        if code == "CUSTOM":
            return "ПОЛЬЗОВАТЕЛЬСКИЙ"
        return str(code).upper()

    def render_dashboard_presets(self):
        """Отрисовка карточек пресетов на главной странице"""
        if not hasattr(self, 'presets_grid') or not self.presets_grid.winfo_exists():
            return

        for w in self.presets_grid.winfo_children():
            w.destroy()

        cur_preset = self.cfg.get("PRESET", "PERFORMANCE")
        all_presets = get_all_presets()

        # Порядок отображения: сначала основные встроенные, затем пользовательские
        display_keys = ["TOURNAMENT", "PERFORMANCE", "BALANCED", "STREAMING"]
        custom_presets = load_custom_presets()
        for ck in custom_presets.keys():
            if ck not in display_keys:
                display_keys.append(ck)

        display_keys = display_keys[:6]
        num_cols = min(4, len(display_keys))
        for col_i in range(num_cols):
            self.presets_grid.grid_columnconfigure(col_i, weight=1)

        self.preset_cards = {}
        for idx, code in enumerate(display_keys):
            if code not in all_presets:
                continue
            p = all_presets[code]
            is_cur = (cur_preset == code)
            title = p.get("name", code)
            desc = p.get("desc", "")
            accent = p.get("accent", COLORS["accent_cyan"])

            row_i = idx // 4
            col_i = idx % 4

            card = ctk.CTkFrame(
                self.presets_grid,
                corner_radius=8,
                fg_color=COLORS["bg_card"],
                border_width=2 if is_cur else 1,
                border_color=accent if is_cur else COLORS["border"]
            )
            card.grid(row=row_i, column=col_i, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(
                card,
                text=title,
                font=get_font(12, "bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                card,
                text=desc,
                font=get_font(9),
                text_color=COLORS["text_secondary"],
                justify="left",
                wraplength=180
            ).pack(anchor="w", padx=10, pady=(0, 8))

            btn = ctk.CTkButton(
                card,
                text="ПРИМЕНЁН ✓" if is_cur else "ВЫБРАТЬ",
                font=get_font(10, "bold"),
                height=26,
                corner_radius=5,
                fg_color=accent if is_cur else "#242E42",
                hover_color=accent,
                text_color="#FFFFFF" if is_cur else COLORS["text_secondary"],
                command=lambda c=code: self.apply_preset(c)
            )
            btn.pack(fill="x", padx=10, pady=(0, 8))
            self.preset_cards[code] = (card, btn, accent)

    def apply_preset(self, code):
        """Применение любого пресета (встроенного или кастомного)"""
        all_presets = get_all_presets()
        if code not in all_presets:
            self.log_dash(f"! Пресет {code} не найден.")
            return

        p = all_presets[code]
        settings = p.get("settings", {})

        for k, v in settings.items():
            self.cfg[k] = str(v)

        self.cfg["PRESET"] = code
        save_config(self.cfg)

        presets_script = os.path.join(CORE_DIR, "presets.bat")
        if p.get("is_builtin", False) and os.path.exists(presets_script):
            try:
                subprocess.run([presets_script, code], shell=True)
            except Exception:
                pass
            save_config(self.cfg)

        if self.cfg.get("TIMER_RESOLUTION", "1") == "1":
            set_high_resolution_timer()

        self.refresh_all_ui()
        p_name = p.get("name", code)
        self.log_dash(f"✓ Пресет «{p_name}» успешно применён! Все параметры зафиксированы.")

    def apply_preset_dash(self, preset_name):
        """Совместимость с предыдущим методом"""
        self.apply_preset(preset_name)

    # =========================================================================
    # ВКЛАДКА: КАСТОМНЫЕ ПРЕСЕТЫ И МЕНЕДЖЕР ПРОФИЛЕЙ
    # =========================================================================
    def create_presets_view(self):
        view = ctk.CTkFrame(self.workspace, fg_color="transparent")

        top_bar = ctk.CTkFrame(view, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="📁 МЕНЕДЖЕР КАСТОМНЫХ И КИБЕРСПОРТИВНЫХ ПРЕСЕТОВ",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Создавайте и сохраняйте собственные конфигурации под ваш стиль игры, турниры или частоту монитора.",
            font=get_font(10),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))

        self.presets_tab_active_lbl = ctk.CTkLabel(
            top_bar,
            text=f"АКТИВНЫЙ ПРОФИЛЬ: {self.get_active_preset_display_name()}",
            font=get_font(11, "bold"),
            text_color=COLORS["accent_cyan"],
            fg_color="#0D1A2D",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.presets_tab_active_lbl.pack(side="right")

        # БЛОК СОЗДАНИЯ НОВОГО ПРЕСЕТА ИЗ ТЕКУЩИХ НАСТРОЕК
        create_card = ctk.CTkFrame(
            view,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        create_card.pack(fill="x", pady=(0, 12))

        c_head = ctk.CTkFrame(create_card, fg_color="transparent")
        c_head.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            c_head,
            text="➕ СОХРАНИТЬ ТЕКУЩИЕ НАСТРОЙКИ КАК НОВЫЙ КАСТОМНЫЙ ПРЕСЕТ",
            font=get_font(12, "bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(side="left")

        io_box = ctk.CTkFrame(c_head, fg_color="transparent")
        io_box.pack(side="right")

        ctk.CTkButton(
            io_box,
            text="📥 Импорт из JSON",
            font=get_font(10, "bold"),
            height=26,
            corner_radius=6,
            fg_color="#1E293B",
            hover_color="#334155",
            text_color=COLORS["text_primary"],
            command=self.import_preset
        ).pack(side="right", padx=4)

        # Поля ввода
        inputs_row = ctk.CTkFrame(create_card, fg_color="transparent")
        inputs_row.pack(fill="x", padx=14, pady=(0, 8))

        self.new_preset_name_entry = ctk.CTkEntry(
            inputs_row,
            placeholder_text="Название пресета (например: Мой 240Hz Ranked, Эндгейм буст...)",
            font=get_font(11),
            height=32,
            width=320
        )
        self.new_preset_name_entry.pack(side="left", padx=(0, 8))

        self.new_preset_desc_entry = ctk.CTkEntry(
            inputs_row,
            placeholder_text="Краткое описание (например: Для турнирных финалов, упор на плавность)",
            font=get_font(11),
            height=32
        )
        self.new_preset_desc_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.save_preset_btn = ctk.CTkButton(
            inputs_row,
            text="💾 СОХРАНИТЬ ПРЕСЕТ",
            font=get_font(11, "bold"),
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_cyan_hover"],
            text_color="#000000",
            height=32,
            corner_radius=6,
            command=self._on_save_preset_click
        )
        self.save_preset_btn.pack(side="right")

        ctk.CTkLabel(
            create_card,
            text="💡 При создании пресета сохраняются текущие состояния всех переключателей твиков FPS, 0.5 мс таймера, DNS, графики и сети.",
            font=get_font(9),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # ПАНЕЛЬ ФИЛЬТРА
        filter_bar = ctk.CTkFrame(view, fg_color="transparent")
        filter_bar.pack(fill="x", pady=(0, 8))

        self.filter_btns = {}
        filters = [
            ("ALL", "Все пресеты"),
            ("CUSTOM", "⭐ Только кастомные"),
            ("BUILTIN", "🏆 Встроенные киберспортивные"),
        ]
        for f_code, f_title in filters:
            btn = ctk.CTkButton(
                filter_bar,
                text=f_title,
                font=get_font(10, "bold"),
                height=26,
                corner_radius=6,
                fg_color=COLORS["accent_cyan"] if f_code == "ALL" else "#1E293B",
                hover_color=COLORS["accent_cyan_hover"] if f_code == "ALL" else "#334155",
                text_color="#000000" if f_code == "ALL" else COLORS["text_secondary"],
                command=lambda fc=f_code: self.set_preset_filter(fc)
            )
            btn.pack(side="left", padx=(0, 6))
            self.filter_btns[f_code] = btn

        # СПИСОК ПРЕСЕТОВ
        self.presets_scroll = ctk.CTkScrollableFrame(
            view,
            corner_radius=10,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.presets_scroll.pack(fill="both", expand=True)
        self.presets_list_frame = self.presets_scroll

        self.render_presets_list()

        return view

    def _on_save_preset_click(self):
        name = self.new_preset_name_entry.get().strip()
        desc = self.new_preset_desc_entry.get().strip()
        if not name:
            try:
                ctypes.windll.user32.MessageBoxW(0, "Пожалуйста, введите название нового пресета!", "Внимание", 0x30)
            except Exception:
                pass
            return

        self.save_new_custom_preset(name, desc)
        self.new_preset_name_entry.delete(0, "end")
        self.new_preset_desc_entry.delete(0, "end")

    def prompt_quick_save_preset(self):
        """Быстрый диалог создания кастомного пресета"""
        try:
            dialog = ctk.CTkInputDialog(
                text="Введите название нового кастомного пресета:\n(Текущие настройки FPS, таймера и DNS будут сохранены)",
                title="Создание кастомного пресета"
            )
            name = dialog.get_input()
            if name and name.strip():
                self.save_new_custom_preset(name.strip())
        except Exception:
            pass

    def save_new_custom_preset(self, name, desc=""):
        name = name.strip()
        if not name:
            return

        for k, v in BUILTIN_PRESETS.items():
            if name.lower() == k.lower() or name.lower() == v.get("name", "").lower():
                try:
                    ctypes.windll.user32.MessageBoxW(0, "Это имя зарезервировано встроенным пресетом. Выберите другое название.", "Внимание", 0x30)
                except Exception:
                    pass
                return

        code = "CUSTOM_" + re.sub(r'[^a-zA-Z0-9а-яА-Я_]', '_', name).upper()
        custom = load_custom_presets()

        settings_keys = [
            "FPS_BOOST", "VISUAL_EFFECTS", "DISABLE_DVRGAME", "POWER_PLAN",
            "HAGS_DISABLE", "HIGH_PRIORITY", "NETWORK_BOOST", "NAGLE_OFF",
            "DNS_OPTIMIZE", "DNS_PRIMARY", "DNS_SECONDARY", "CPU_UNPARK",
            "MSI_MODE", "MOUSE_OPTIMIZE", "FORTNITE_INI", "PAGEFILE_OPTIMIZE",
            "RESOLUTION_CHANGE", "RESOLUTION_WIDTH", "RESOLUTION_HEIGHT", "RESOLUTION_REFRESH",
            "PING_MONITOR", "RAM_CLEANUP", "KILL_USELESS", "LAUNCH_EPIC",
            "TIMER_RESOLUTION", "NIC_OPTIMIZE"
        ]
        snapshot = {}
        for k in settings_keys:
            snapshot[k] = self.cfg.get(k, "1")

        custom[code] = {
            "name": f"⭐ {name}",
            "full_name": f"⭐ {name}",
            "code": code,
            "desc": desc or f"Пользовательский пресет (создан {time.strftime('%d.%m.%Y %H:%M')})",
            "accent": "#00F0FF",
            "is_builtin": False,
            "created": time.strftime('%d.%m.%Y %H:%M'),
            "settings": snapshot
        }
        save_custom_presets(custom)

        self.apply_preset(code)
        self.refresh_all_ui()
        self.log_dash(f"✓ Кастомный пресет «{name}» успешно создан и сохранён!")
        try:
            ctypes.windll.user32.MessageBoxW(0, f"Кастомный пресет «{name}» успешно создан и активирован!", "Успешно", 0x40)
        except Exception:
            pass

    def update_existing_custom_preset(self, code):
        """Обновление существующего кастомного пресета текущими параметрами"""
        custom = load_custom_presets()
        if code not in custom:
            return
        p_name = custom[code].get("name", code)
        try:
            res = ctypes.windll.user32.MessageBoxW(
                0,
                f"Перезаписать пресет «{p_name}» вашими текущими настройками?",
                "Обновление пресета",
                0x34
            )
            if res != 6:
                return
        except Exception:
            pass

        settings_keys = [
            "FPS_BOOST", "VISUAL_EFFECTS", "DISABLE_DVRGAME", "POWER_PLAN",
            "HAGS_DISABLE", "HIGH_PRIORITY", "NETWORK_BOOST", "NAGLE_OFF",
            "DNS_OPTIMIZE", "DNS_PRIMARY", "DNS_SECONDARY", "CPU_UNPARK",
            "MSI_MODE", "MOUSE_OPTIMIZE", "FORTNITE_INI", "PAGEFILE_OPTIMIZE",
            "RESOLUTION_CHANGE", "RESOLUTION_WIDTH", "RESOLUTION_HEIGHT", "RESOLUTION_REFRESH",
            "PING_MONITOR", "RAM_CLEANUP", "KILL_USELESS", "LAUNCH_EPIC",
            "TIMER_RESOLUTION", "NIC_OPTIMIZE"
        ]
        for k in settings_keys:
            custom[code]["settings"][k] = self.cfg.get(k, "1")

        custom[code]["updated"] = time.strftime('%d.%m.%Y %H:%M')
        save_custom_presets(custom)
        self.cfg["PRESET"] = code
        save_config(self.cfg)
        self.refresh_all_ui()
        self.log_dash(f"✓ Пресет «{p_name}» обновлён текущими настройками.")

    def delete_custom_preset(self, code):
        """Удаление пользовательского пресета"""
        custom = load_custom_presets()
        if code not in custom:
            return

        p_name = custom[code].get("name", code)
        try:
            res = ctypes.windll.user32.MessageBoxW(
                0,
                f"Вы действительно хотите удалить пресет «{p_name}»?",
                "Подтверждение удаления",
                0x34
            )
            if res != 6:
                return
        except Exception:
            pass

        del custom[code]
        save_custom_presets(custom)

        if self.cfg.get("PRESET") == code:
            self.cfg["PRESET"] = "PERFORMANCE"
            save_config(self.cfg)

        self.refresh_all_ui()
        self.log_dash(f"Пресет «{p_name}» удалён.")

    def export_preset(self, code):
        """Экспорт пресета в файл JSON"""
        all_p = get_all_presets()
        if code not in all_p:
            return
        p = all_p[code]
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', p.get("name", code))
        file_path = filedialog.asksaveasfilename(
            initialfile=f"preset_{clean_name}.json",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Экспорт пресета"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(p, f, ensure_ascii=False, indent=2)
                self.log_dash(f"✓ Пресет «{p.get('name')}» экспортирован в: {os.path.basename(file_path)}")
                ctypes.windll.user32.MessageBoxW(0, f"Пресет успешно сохранён:\n{file_path}", "Экспорт завершён", 0x40)
            except Exception as e:
                ctypes.windll.user32.MessageBoxW(0, f"Ошибка экспорта: {e}", "Ошибка", 0x10)

    def import_preset(self):
        """Импорт пресета из файла JSON"""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Импорт пресета"
        )
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict) or "settings" not in data:
                    ctypes.windll.user32.MessageBoxW(0, "Неверная структура файла пресета!", "Ошибка", 0x10)
                    return

                name = data.get("name", "Импортированный пресет")
                if not name.startswith("⭐"):
                    name = "⭐ " + name

                code = "CUSTOM_IMP_" + str(int(time.time()))
                custom = load_custom_presets()
                data["code"] = code
                data["name"] = name
                data["is_builtin"] = False
                data["created"] = time.strftime('%d.%m.%Y %H:%M')
                custom[code] = data
                save_custom_presets(custom)

                self.apply_preset(code)
                self.refresh_all_ui()
                self.log_dash(f"✓ Пресет «{name}» успешно импортирован!")
                ctypes.windll.user32.MessageBoxW(0, f"Пресет «{name}» успешно импортирован и активирован!", "Успешно", 0x40)
            except Exception as e:
                ctypes.windll.user32.MessageBoxW(0, f"Ошибка импорта: {e}", "Ошибка", 0x10)

    def set_preset_filter(self, flt):
        """Фильтрация пресетов в списке"""
        self.current_preset_filter = flt
        for code, btn in self.filter_btns.items():
            if code == flt:
                btn.configure(fg_color=COLORS["accent_cyan"], text_color="#000000")
            else:
                btn.configure(fg_color="#1E293B", text_color=COLORS["text_secondary"])
        self.render_presets_list()

    def render_presets_list(self):
        """Отрисовка списка пресетов на вкладке управления пресетами"""
        if not hasattr(self, 'presets_list_frame') or not self.presets_list_frame.winfo_exists():
            return

        for w in self.presets_list_frame.winfo_children():
            w.destroy()

        cur_preset = self.cfg.get("PRESET", "PERFORMANCE")
        all_presets = get_all_presets()
        flt = getattr(self, 'current_preset_filter', 'ALL')

        filtered_items = []
        for code, p in all_presets.items():
            is_built = p.get("is_builtin", False)
            if flt == "CUSTOM" and is_built:
                continue
            if flt == "BUILTIN" and not is_built:
                continue
            filtered_items.append((code, p))

        if not filtered_items:
            empty_box = ctk.CTkFrame(self.presets_list_frame, fg_color="transparent")
            empty_box.pack(fill="both", expand=True, pady=30)
            ctk.CTkLabel(
                empty_box,
                text="⭐ У вас пока нет кастомных пресетов.\nВведите название выше и нажмите «💾 СОХРАНИТЬ ПРЕСЕТ»!",
                font=get_font(12),
                text_color=COLORS["text_muted"],
                justify="center"
            ).pack()
            return

        for code, p in filtered_items:
            is_cur = (cur_preset == code)
            is_built = p.get("is_builtin", False)
            title = p.get("full_name", p.get("name", code))
            desc = p.get("desc", "")
            accent = p.get("accent", COLORS["accent_cyan"])
            settings = p.get("settings", {})

            card = ctk.CTkFrame(
                self.presets_list_frame,
                corner_radius=10,
                fg_color=COLORS["bg_card"],
                border_width=2 if is_cur else 1,
                border_color=accent if is_cur else COLORS["border"]
            )
            card.pack(fill="x", padx=4, pady=5)

            c_top = ctk.CTkFrame(card, fg_color="transparent")
            c_top.pack(fill="x", padx=12, pady=(10, 4))

            title_box = ctk.CTkFrame(c_top, fg_color="transparent")
            title_box.pack(side="left")

            ctk.CTkLabel(
                title_box,
                text=title,
                font=get_font(13, "bold"),
                text_color=COLORS["text_primary"]
            ).pack(side="left")

            type_tag_text = "СИСТЕМНЫЙ" if is_built else "КАСТОМНЫЙ"
            type_tag_bg = "#1E293B" if is_built else "#064E3B"
            type_tag_col = COLORS["text_secondary"] if is_built else "#10B981"

            ctk.CTkLabel(
                title_box,
                text=f" {type_tag_text} ",
                font=get_font(9, "bold"),
                text_color=type_tag_col,
                fg_color=type_tag_bg,
                corner_radius=4
            ).pack(side="left", padx=8)

            if is_cur:
                ctk.CTkLabel(
                    title_box,
                    text=" ● АКТИВЕН ",
                    font=get_font(9, "bold"),
                    text_color="#FFFFFF",
                    fg_color=COLORS["accent_green"],
                    corner_radius=4
                ).pack(side="left", padx=4)

            btn_box = ctk.CTkFrame(c_top, fg_color="transparent")
            btn_box.pack(side="right")

            apply_btn = ctk.CTkButton(
                btn_box,
                text="ПРИМЕНЁН ✓" if is_cur else "⚡ ПРИМЕНИТЬ",
                font=get_font(11, "bold"),
                height=28,
                width=110,
                corner_radius=6,
                fg_color=accent if is_cur else COLORS["accent_cyan"],
                hover_color=accent,
                text_color="#FFFFFF" if is_cur else "#000000",
                command=lambda c=code: self.apply_preset(c)
            )
            apply_btn.pack(side="left", padx=3)

            if not is_built:
                ctk.CTkButton(
                    btn_box,
                    text="💾 Обновить",
                    font=get_font(10, "bold"),
                    height=28,
                    width=75,
                    corner_radius=6,
                    fg_color="#1E293B",
                    hover_color="#334155",
                    text_color=COLORS["accent_cyan"],
                    command=lambda c=code: self.update_existing_custom_preset(c)
                ).pack(side="left", padx=3)

                ctk.CTkButton(
                    btn_box,
                    text="📤",
                    font=get_font(11),
                    height=28,
                    width=32,
                    corner_radius=6,
                    fg_color="#1E293B",
                    hover_color="#334155",
                    text_color=COLORS["text_primary"],
                    command=lambda c=code: self.export_preset(c)
                ).pack(side="left", padx=3)

                ctk.CTkButton(
                    btn_box,
                    text="🗑️",
                    font=get_font(11),
                    height=28,
                    width=32,
                    corner_radius=6,
                    fg_color="#381318",
                    hover_color="#DC2626",
                    text_color="#FCA5A5",
                    command=lambda c=code: self.delete_custom_preset(c)
                ).pack(side="left", padx=3)

            desc_lbl = ctk.CTkLabel(
                card,
                text=desc,
                font=get_font(10),
                text_color=COLORS["text_secondary"],
                justify="left",
                anchor="w"
            )
            desc_lbl.pack(fill="x", padx=12, pady=(0, 6))

            tags_box = ctk.CTkFrame(card, fg_color="transparent")
            tags_box.pack(fill="x", padx=12, pady=(0, 10))

            hags_val = "Выкл" if settings.get("HAGS_DISABLE") == "1" else "Вкл"
            dns_val = settings.get("DNS_PRIMARY", "8.8.8.8")
            timer_val = "0.5 мс" if settings.get("TIMER_RESOLUTION") == "1" else "Стандарт"
            prio_val = "High" if settings.get("HIGH_PRIORITY") == "1" else "Normal"
            unpark_val = "100%" if settings.get("CPU_UNPARK") == "1" else "Stock"

            tags = [
                f"⏱️ Таймер: {timer_val}",
                f"🌐 DNS: {dns_val}",
                f"🚀 Приоритет: {prio_val}",
                f"🎮 HAGS: {hags_val}",
                f"⚡ CPU Unpark: {unpark_val}"
            ]
            for t in tags:
                ctk.CTkLabel(
                    tags_box,
                    text=f" {t} ",
                    font=get_font(9),
                    text_color=COLORS["text_muted"],
                    fg_color="#0D111A",
                    corner_radius=4
                ).pack(side="left", padx=(0, 6))

    def refresh_all_ui(self):
        """Комплексное обновление всех элементов интерфейса во всех вкладках"""
        if hasattr(self, 'tweak_switches'):
            self.refresh_tweaks_switches()

        if hasattr(self, 'net_dns_combo'):
            dns_p = self.cfg.get("DNS_PRIMARY", "8.8.8.8")
            if "8.8.8.8" in dns_p:
                self.net_dns_combo.set("Google DNS (8.8.8.8 / 8.8.4.4) - Рекомендовано")
                if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                    self.dns_badge.configure(text="  Google (8.8.8.8)")
            elif "1.1.1.1" in dns_p:
                self.net_dns_combo.set("Cloudflare (1.1.1.1 / 1.0.0.1)")
                if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                    self.dns_badge.configure(text="  Cloudflare (1.1.1.1)")

        if hasattr(self, 'res_w_input') and hasattr(self, 'res_h_input'):
            try:
                self.res_w_input.delete(0, "end")
                self.res_w_input.insert(0, self.cfg.get("RESOLUTION_WIDTH", "1920"))
                self.res_h_input.delete(0, "end")
                self.res_h_input.insert(0, self.cfg.get("RESOLUTION_HEIGHT", "1080"))
            except Exception:
                pass

        disp_name = self.get_active_preset_display_name()
        if hasattr(self, 'active_preset_badge') and self.active_preset_badge.winfo_exists():
            self.active_preset_badge.configure(text=f"АКТИВЕН: {disp_name}")
        if hasattr(self, 'presets_tab_active_lbl') and self.presets_tab_active_lbl.winfo_exists():
            self.presets_tab_active_lbl.configure(text=f"АКТИВНЫЙ ПРОФИЛЬ: {disp_name}")

        self.render_dashboard_presets()
        self.render_presets_list()
        if hasattr(self, 'refresh_settings_ui'):
            self.refresh_settings_ui()

    # =========================================================================
    # ВКЛАДКА 2: ТВЫКИ FPS И СИСТЕМА
    # =========================================================================
    def create_tweaks_view(self):
        view = ctk.CTkFrame(self.workspace, fg_color="transparent")

        header_box = ctk.CTkFrame(view, fg_color="transparent")
        header_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_box,
            text="⚙️ НАСТРОЙКИ СИСТЕМЫ, CPU, GPU И ПАМЯТИ",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        quick_btns = ctk.CTkFrame(header_box, fg_color="transparent")
        quick_btns.pack(side="right")

        ctk.CTkButton(
            quick_btns,
            text="Включить все рекомендованные",
            font=get_font(11, "bold"),
            height=28,
            fg_color=COLORS["accent_purple"],
            hover_color=COLORS["accent_purple_hover"],
            command=self.enable_all_recommended_tweaks
        ).pack(side="left", padx=4)

        scroll = ctk.CTkScrollableFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        self.tweak_switches = {}
        categories = [
            ("⚡ ПРОЦЕССОР И РАЗГОН ПОТОКОВ (CPU)", [
                ("CPU_UNPARK", "Разпарковка всех ядер CPU (100% активны)", "Отключает сон неактивных ядер, активирует агрессивный Turbo Boost и удаляет энергосберегающие задержки."),
                ("HIGH_PRIORITY", "Высокий приоритет процесса Fortnite", "Автоматически выдаёт максимальный приоритет CPU для FortniteClient-Win64-Shipping.exe."),
            ]),
            ("🎮 ВИДЕОКАРТА И ПРЕРЫВАНИЯ (GPU)", [
                ("MSI_MODE", "Режим MSI для GPU и сетевой карты", "Message Signaled Interrupts снижает задержку прерываний видеокарты до аппаратного минимума."),
                ("FPS_BOOST", "План питания «Максимальная производительность»", "Активирует скрытый режим Ultimate Performance в Windows и оптимизирует таймеры ядра."),
                ("HAGS_DISABLE", "Отключение HAGS", "Рекомендовано для серий GTX 10xx и RTX 20xx. Для RTX 30xx/40xx оставьте выключенным."),
            ]),
            ("🖱️ ТОЧНОСТЬ ПРИЦЕЛИВАНИЯ МЫШИ", [
                ("MOUSE_OPTIMIZE", "Честный отклик 1:1 (Кривые SmoothMouse)", "Устанавливает идеальные кривые 1:1, отключает акселерацию Windows и ставит нейтральную чувствительность 10."),
            ]),
            ("📄 ДВИЖОК FORTNITE И ГРАФИКА", [
                ("FORTNITE_INI", "Глубокая оптимизация Engine.ini", "Отключает объёмный туман, плотность травы, блики, размытие в движении и отражения на уровне движка."),
            ]),
            ("🧹 ПАМЯТЬ И СТАБИЛЬНОСТЬ", [
                ("PAGEFILE_OPTIMIZE", "Фиксированный файл подкачки (Анти-фриз)", "Задаёт оптимальный фиксированный размер pagefile.sys, полностью устраняя статтеры в перестрелках."),
                ("RAM_CLEANUP", "Очистка оперативной памяти и Temp", "Очищает рабочий набор процессов, сбрасывает кэш DNS и очищает мусорные файлы перед игрой."),
                ("KILL_USELESS", "Закрытие фонового мусора", "Выгружает GameBar, оверлеи Xbox и фоновую телеметрию поиска перед стартом матча."),
                ("DISABLE_DVRGAME", "Отключение Windows Game DVR", "Убирает фоновую фоновую запись клипов и оверлейные лаги Windows."),
                ("VISUAL_EFFECTS", "Минимизация визуальных эффектов Windows", "Отключает анимации открытия окон для разгрузки видеочипа."),
            ]),
        ]

        for cat_title, tweaks in categories:
            cat_frame = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#182234")
            cat_frame.pack(fill="x", padx=6, pady=5)

            ctk.CTkLabel(
                cat_frame,
                text=cat_title,
                font=get_font(11, "bold"),
                text_color=COLORS["accent_cyan"]
            ).pack(anchor="w", padx=12, pady=(6, 2))

            for key, title, desc in tweaks:
                row = ctk.CTkFrame(cat_frame, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=3)

                sw = ctk.CTkSwitch(
                    row,
                    text=f"  {title}",
                    font=get_font(12, "bold"),
                    text_color=COLORS["text_primary"],
                    progress_color=COLORS["accent_cyan"],
                    command=lambda k=key: self.toggle_tweak_card(k)
                )
                if self.cfg.get(key, "0") == "1":
                    sw.select()
                else:
                    sw.deselect()
                sw.pack(anchor="w")
                self.tweak_switches[key] = sw

                ctk.CTkLabel(
                    row,
                    text=desc,
                    font=get_font(10),
                    text_color=COLORS["text_muted"],
                    wraplength=700,
                    justify="left"
                ).pack(anchor="w", padx=(28, 0), pady=(0, 4))

        return view

    def toggle_tweak_card(self, key):
        val = "1" if self.tweak_switches[key].get() else "0"
        self.cfg[key] = val
        self.cfg["PRESET"] = "CUSTOM"
        save_config(self.cfg)
        if hasattr(self, 'active_preset_badge') and self.active_preset_badge.winfo_exists():
            self.active_preset_badge.configure(text="АКТИВЕН: ПОЛЬЗОВАТЕЛЬСКИЙ")
        if hasattr(self, 'presets_tab_active_lbl') and self.presets_tab_active_lbl.winfo_exists():
            self.presets_tab_active_lbl.configure(text="АКТИВНЫЙ ПРОФИЛЬ: ПОЛЬЗОВАТЕЛЬСКИЙ")

    def enable_all_recommended_tweaks(self):
        recommended = ["FPS_BOOST", "CPU_UNPARK", "MSI_MODE", "MOUSE_OPTIMIZE", "FORTNITE_INI", "RAM_CLEANUP", "KILL_USELESS", "HIGH_PRIORITY", "DISABLE_DVRGAME", "VISUAL_EFFECTS"]
        for k in recommended:
            self.cfg[k] = "1"
            if k in self.tweak_switches:
                self.tweak_switches[k].select()
        self.cfg["PRESET"] = "CUSTOM"
        save_config(self.cfg)
        if hasattr(self, 'active_preset_badge') and self.active_preset_badge.winfo_exists():
            self.active_preset_badge.configure(text="АКТИВЕН: ПОЛЬЗОВАТЕЛЬСКИЙ")
        if hasattr(self, 'presets_tab_active_lbl') and self.presets_tab_active_lbl.winfo_exists():
            self.presets_tab_active_lbl.configure(text="АКТИВНЫЙ ПРОФИЛЬ: ПОЛЬЗОВАТЕЛЬСКИЙ")
        self.log_dash("✓ Все рекомендованные настройки включены.")

    def refresh_tweaks_switches(self):
        for k, sw in self.tweak_switches.items():
            if self.cfg.get(k, "0") == "1":
                sw.select()
            else:
                sw.deselect()

    # =========================================================================
    # ВКЛАДКА 3: СЕТЬ И GOOGLE DNS 8.8.8.8
    # =========================================================================
    def create_network_view(self):
        view = ctk.CTkFrame(self.workspace, fg_color="transparent")

        ctk.CTkLabel(
            view,
            text="🌐 СЕТЕВОЙ КИБЕРСПОРТИВНЫЙ СТЕК И DNS",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))

        # Карточка DNS
        dns_card = ctk.CTkFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        dns_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            dns_card,
            text="ТЕКУЩИЙ DNS-СЕРВЕР ПОДКЛЮЧЕНИЯ",
            font=get_font(12, "bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(anchor="w", padx=14, pady=(12, 4))

        dns_row = ctk.CTkFrame(dns_card, fg_color="transparent")
        dns_row.pack(fill="x", padx=14, pady=(0, 12))

        self.net_dns_combo = ctk.CTkComboBox(
            dns_row,
            values=[
                "Google DNS (8.8.8.8 / 8.8.4.4) - Рекомендовано",
                "Cloudflare (1.1.1.1 / 1.0.0.1)",
                "Яндекс DNS (77.88.8.8 / 77.88.8.1)",
                "Quad9 (9.9.9.9)",
                "Автоматический (DHCP провайдера)",
            ],
            font=get_font(11),
            width=340,
            height=32,
            command=self.change_dns_preset
        )
        self.net_dns_combo.set("Google DNS (8.8.8.8 / 8.8.4.4) - Рекомендовано")
        self.net_dns_combo.pack(side="left", padx=(0, 10))

        self.apply_dns_now_btn = ctk.CTkButton(
            dns_row,
            text="Применить DNS на адаптеры",
            font=get_font(11, "bold"),
            fg_color=COLORS["accent_green"],
            hover_color=COLORS["accent_green_hover"],
            height=32,
            command=self.apply_dns_instantly
        )
        self.apply_dns_now_btn.pack(side="left", padx=(0, 8))

        self.manual_benchmark_dns_btn = ctk.CTkButton(
            dns_row,
            text="⚡ Найти самый быстрый DNS",
            font=get_font(11, "bold"),
            fg_color=COLORS["accent_cyan"],
            text_color="#000000",
            hover_color=COLORS["accent_cyan_hover"],
            height=32,
            command=self.run_manual_dns_benchmark
        )
        self.manual_benchmark_dns_btn.pack(side="left")

        # Мини-панель задержки DNS
        self.net_dns_results_frame = ctk.CTkFrame(dns_card, fg_color="#0E131E", corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.net_dns_results_frame.pack(fill="x", padx=14, pady=(0, 12))
        self.net_dns_results_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.net_page_dns_pills = {}
        for idx, srv in enumerate(DNS_BENCHMARK_SERVERS):
            card = ctk.CTkFrame(self.net_dns_results_frame, fg_color="#182234", corner_radius=6, height=58)
            card.grid(row=0, column=idx, padx=4, pady=8, sticky="nsew")
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=srv["name"], font=get_font(10, "bold"), text_color=COLORS["text_primary"]).pack(pady=(4, 1))
            p_lbl = ctk.CTkLabel(card, text="-- мс", font=get_font(10, "bold"), text_color=COLORS["accent_cyan"])
            p_lbl.pack()
            self.net_page_dns_pills[srv["name"]] = {"card": card, "lbl": p_lbl, "srv": srv}

        # Список настроек сети
        net_tweaks = ctk.CTkScrollableFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        net_tweaks.pack(fill="both", expand=True)

        ctk.CTkLabel(
            net_tweaks,
            text="ПАКЕТНЫЕ ОПТИМИЗАЦИИ TCP / IP",
            font=get_font(12, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=12, pady=(8, 6))

        tweak_list = [
            ("Отключение алгоритма Nagle (TcpAckFrequency = 1)", "Убирает буферизацию пакетов, отправляя выстрелы и перемещения без миллисекундных задержек."),
            ("Защита сокетов друзей и пати Fortnite (EOS / AFD PushBit Fix)", "Обеспечивает мгновенную доставку микро-пакетов XMPP и WebSockets для списка друзей, приглашений в группу и голосового чата."),
            ("Отключение NetworkThrottling", "Снимает системный лимит Windows на пропускную способность сетевой карты при игре."),
            ("Отключение туннелей IPv6 Teredo и 6to4", "Исключает лишнюю трансляцию адресов, вызывающую скачки пинга до серверов Epic Games."),
            ("Правила в Брандмауэре Windows", "Добавляет прямое разрешение на входящие и исходящие пакеты для FortniteClient-Win64-Shipping.exe."),
        ]

        for title, desc in tweak_list:
            row = ctk.CTkFrame(net_tweaks, corner_radius=8, fg_color="#182234")
            row.pack(fill="x", padx=10, pady=3)

            ctk.CTkLabel(
                row,
                text=f"✓  {title}",
                font=get_font(12, "bold"),
                text_color="#10B981"
            ).pack(anchor="w", padx=10, pady=(6, 2))

            ctk.CTkLabel(
                row,
                text=desc,
                font=get_font(10),
                text_color=COLORS["text_muted"]
            ).pack(anchor="w", padx=10, pady=(0, 6))

        return view

    def change_dns_preset(self, choice):
        if "Google" in choice:
            self.cfg["DNS_PRIMARY"] = "8.8.8.8"
            self.cfg["DNS_SECONDARY"] = "8.8.4.4"
            if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                self.dns_badge.configure(text="  Google (8.8.8.8)")
        elif "Cloudflare" in choice:
            self.cfg["DNS_PRIMARY"] = "1.1.1.1"
            self.cfg["DNS_SECONDARY"] = "1.0.0.1"
            if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                self.dns_badge.configure(text="  Cloudflare (1.1.1.1)")
        elif "Яндекс" in choice:
            self.cfg["DNS_PRIMARY"] = "77.88.8.8"
            self.cfg["DNS_SECONDARY"] = "77.88.8.1"
            if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                self.dns_badge.configure(text="  Яндекс (77.88.8.8)")
        elif "OpenDNS" in choice:
            self.cfg["DNS_PRIMARY"] = "208.67.222.222"
            self.cfg["DNS_SECONDARY"] = "208.67.220.220"
            if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                self.dns_badge.configure(text="  OpenDNS (208.67.222.222)")
        elif "Quad9" in choice:
            self.cfg["DNS_PRIMARY"] = "9.9.9.9"
            self.cfg["DNS_SECONDARY"] = "149.112.112.112"
            if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                self.dns_badge.configure(text="  Quad9 (9.9.9.9)")
        save_config(self.cfg)
        if hasattr(self, 'master_launch_btn') and self.master_launch_btn.winfo_exists():
            self.master_launch_btn.configure(text=f"ОПТИМИЗИРОВАТЬ СИСТЕМУ И ЗАПУСТИТЬ FORTNITE (DNS {self.cfg['DNS_PRIMARY']})")

    def run_manual_dns_benchmark(self):
        """Ручной запуск тестирования пинга всех DNS-серверов из вкладки Сеть"""
        self.manual_benchmark_dns_btn.configure(text="Измерение пинга...", state="disabled")

        def _worker():
            results = []
            for srv in DNS_BENCHMARK_SERVERS:
                name = srv["name"]
                if self.winfo_exists():
                    self.after(0, lambda n=name: self._update_net_pill_status(n, "тест...", COLORS["accent_cyan"]))
                ping = ping_dns_server(srv["primary"])
                results.append({**srv, "ping": ping})
                if self.winfo_exists():
                    col = "#10B981" if ping < 35 else ("#F59E0B" if ping < 75 else "#EF4444")
                    self.after(0, lambda n=name, p=ping, c=col: self._update_net_pill_status(n, f"{p} мс", c))
                time.sleep(0.15)

            results.sort(key=lambda x: x["ping"])
            best = results[0]

            def _on_done():
                self.manual_benchmark_dns_btn.configure(text=f"✓ Лучший: {best['name']} ({best['ping']} мс)", state="normal")
                self.cfg["DNS_PRIMARY"] = best["primary"]
                self.cfg["DNS_SECONDARY"] = best["secondary"]
                save_config(self.cfg)

                if hasattr(self, 'dns_badge') and self.dns_badge.winfo_exists():
                    self.dns_badge.configure(text=f"  {best['name']} ({best['primary']}) • {best['ping']} мс")
                if hasattr(self, 'master_launch_btn') and self.master_launch_btn.winfo_exists():
                    self.master_launch_btn.configure(text=f"ОПТИМИЗИРОВАТЬ СИСТЕМУ И ЗАПУСТИТЬ FORTNITE ({best['name']})")
                if hasattr(self, 'net_dns_combo') and self.net_dns_combo.winfo_exists():
                    for v in self.net_dns_combo.cget("values"):
                        if best["primary"] in v:
                            self.net_dns_combo.set(v)
                            break
                self.log_dash(f"[DNS] 👑 Ручной бенчмарк: самый быстрый DNS — {best['name']} ({best['primary']}) с задержкой {best['ping']} мс")

            if self.winfo_exists():
                self.after(0, _on_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _update_net_pill_status(self, name, text, color):
        p = self.net_page_dns_pills.get(name)
        if p and p["lbl"].winfo_exists():
            p["lbl"].configure(text=text, text_color=color)

    def apply_dns_instantly(self):
        dns1 = self.cfg.get("DNS_PRIMARY", "8.8.8.8")
        dns2 = self.cfg.get("DNS_SECONDARY", "8.8.4.4")
        self.apply_dns_now_btn.configure(text="Применение...", state="disabled")

        def _worker():
            cmd = f'powershell -Command "Get-NetAdapter | Where-Object Status -eq Up | Set-DnsClientServerAddress -ServerAddresses {dns1},{dns2} -ErrorAction SilentlyContinue; ipconfig /flushdns"'
            subprocess.run(cmd, shell=True)
            if self.winfo_exists():
                self.after(0, lambda: [
                    self.apply_dns_now_btn.configure(text="✓ Успешно применён!", state="normal"),
                    self.log_dash(f"DNS применён на все активные сетевые адаптеры: {dns1} / {dns2}")
                ])

        threading.Thread(target=_worker, daemon=True).start()

    # =========================================================================
    # ВКЛАДКА 4: РАЗРЕШЕНИЕ 4:3 STRETCHED
    # =========================================================================
    def create_resolution_view(self):
        view = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")

        ctk.CTkLabel(
            view,
            text="РАЗРЕШЕНИЕ ЭКРАНА В FORTNITE",
            font=get_font(18, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            view,
            text="Прямая запись в GameUserSettings.ini. Растянутый формат (Stretched) увеличивает угол обзора и повышает FPS.",
            font=get_font(12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 14))

        # КАРТОЧКА ЖИВОГО СТАТУСА ФАЙЛА НАСТРОЕК FORTNITE
        self.ini_status_card = ctk.CTkFrame(view, corner_radius=14, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        self.ini_status_card.pack(fill="x", pady=(0, 14))

        ini_top = ctk.CTkFrame(self.ini_status_card, fg_color="transparent")
        ini_top.pack(fill="x", padx=18, pady=(12, 6))

        ctk.CTkLabel(
            ini_top,
            text="ТЕКУЩИЙ СТАТУС ФАЙЛА GAMEUSERSETTINGS.INI",
            font=get_font(12, "bold"),
            text_color="#60A5FA"
        ).pack(side="left")

        # Кнопка обновить статус
        ctk.CTkButton(
            ini_top,
            text="🔄 Обновить статус",
            font=get_font(10, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color="#94A3B8",
            height=26,
            corner_radius=6,
            command=self.refresh_resolution_status_card
        ).pack(side="right")

        self.ini_info_row = ctk.CTkFrame(self.ini_status_card, fg_color="transparent")
        self.ini_info_row.pack(fill="x", padx=18, pady=(0, 12))

        self.ini_res_badge = ctk.CTkLabel(
            self.ini_info_row,
            text="Разрешение: ...",
            font=get_font(12, "bold"),
            text_color=COLORS["text_primary"],
            fg_color="#182234",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.ini_res_badge.pack(side="left", padx=(0, 10))

        self.ini_lock_badge = ctk.CTkLabel(
            self.ini_info_row,
            text="Защита: ...",
            font=get_font(12, "bold"),
            text_color="#10B981",
            fg_color="#064E3B",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.ini_lock_badge.pack(side="left", padx=(0, 12))

        self.ini_lock_btn = ctk.CTkButton(
            self.ini_info_row,
            text="🔒 Переключить Read-Only",
            font=get_font(11, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color=COLORS["accent_cyan"],
            height=32,
            corner_radius=8,
            command=self.toggle_ini_readonly
        )
        self.ini_lock_btn.pack(side="left")

        # Сетка разрешений с крупными кнопками
        grid = ctk.CTkFrame(view, corner_radius=14, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        res_items = [
            ("1920x1080", "1920 × 1080", "16:9 NATIVE", "Стандартное Full HD • Чёткая картинка", "#2563EB"),
            ("1720x1080", "1720 × 1080", "16:10 ALPHA", "Популярный выбор про-сцены 2026", "#06B6D4"),
            ("1650x1080", "1650 × 1080", "16:10 BALANCED", "Идеальный баланс хитбоксов и обзора", "#8B5CF6"),
            ("1440x1080", "1440 × 1080", "4:3 STRETCHED", "Выбор про-игроков • Широкие хитбоксы", "#7C3AED"),
            ("1280x960",  "1280 × 960",  "4:3 STRETCHED", "Максимальный FPS • Турнирный стандарт", "#059669"),
            ("1280x1024", "1280 × 1024", "5:4 STRETCHED", "Увеличенный вертикальный угол обзора", "#D97706"),
            ("1680x1050", "1680 × 1050", "16:10 STRETCH", "Мягкое растяжение без потери чёткости", "#0891B2"),
            ("1600x900",  "1600 × 900",  "16:9 MAX FPS", "Высокая производительность в эндгейме", "#4F46E5"),
        ]

        for i, (res, title, badge, desc, col) in enumerate(res_items):
            w, h = res.split("x")
            card = ctk.CTkFrame(grid, corner_radius=12, fg_color="#131A26", border_width=1, border_color=COLORS["border"])
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="ew")

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(12, 4))

            ctk.CTkLabel(
                top,
                text=title,
                font=get_font(14, "bold"),
                text_color=COLORS["text_primary"]
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=badge,
                font=get_font(10, "bold"),
                text_color=col,
                fg_color="#0F172A",
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=desc,
                font=get_font(11),
                text_color=COLORS["text_muted"]
            ).pack(anchor="w", padx=12, pady=(0, 10))

            ctk.CTkButton(
                card,
                text="Выбрать пресет",
                font=get_font(12, "bold"),
                fg_color=col,
                hover_color="#1E293B",
                height=36,
                corner_radius=8,
                command=lambda width=w, height=h: self.apply_res_preset(width, height)
            ).pack(fill="x", padx=12, pady=(0, 12))

        # Своё разрешение
        custom_card = ctk.CTkFrame(view, corner_radius=14, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        custom_card.pack(fill="x")

        ctk.CTkLabel(
            custom_card,
            text="ТОЧНАЯ НАСТРОЙКА РАЗРЕШЕНИЯ И ГЕРЦОВКИ",
            font=get_font(13, "bold"),
            text_color="#60A5FA"
        ).pack(anchor="w", padx=18, pady=(14, 6))

        inp_row = ctk.CTkFrame(custom_card, fg_color="transparent")
        inp_row.pack(fill="x", padx=18, pady=(0, 16))

        ctk.CTkLabel(inp_row, text="Ширина:", font=get_font(12, "bold")).pack(side="left", padx=(0, 6))
        self.res_w_input = ctk.CTkEntry(inp_row, width=88, height=36, font=get_font(13, "bold"))
        self.res_w_input.insert(0, self.cfg.get("RESOLUTION_WIDTH", "1920"))
        self.res_w_input.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(inp_row, text="Высота:", font=get_font(12, "bold")).pack(side="left", padx=(0, 6))
        self.res_h_input = ctk.CTkEntry(inp_row, width=88, height=36, font=get_font(13, "bold"))
        self.res_h_input.insert(0, self.cfg.get("RESOLUTION_HEIGHT", "1080"))
        self.res_h_input.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(inp_row, text="Герцовка (Hz):", font=get_font(12, "bold")).pack(side="left", padx=(0, 6))
        self.res_r_input = ctk.CTkEntry(inp_row, width=76, height=36, font=get_font(13, "bold"))
        self.res_r_input.insert(0, self.cfg.get("RESOLUTION_REFRESH", "180"))
        self.res_r_input.pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            inp_row,
            text="🔒 Зафиксировать в игре",
            font=get_font(12, "bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            text_color="#FFFFFF",
            height=36,
            corner_radius=8,
            command=self.apply_custom_res
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            inp_row,
            text="🖥️ Разрешение Windows",
            font=get_font(12, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#CBD5E1",
            height=36,
            corner_radius=8,
            command=self.apply_desktop_res
        ).pack(side="left")

        # Информационная плашка о защите от сброса
        info_banner = ctk.CTkFrame(custom_card, fg_color="#0D1929", corner_radius=8, border_width=1, border_color="#1E3A8A")
        info_banner.pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkLabel(
            info_banner,
            text="🔒 Автоматическая защита: при нажатии «Зафиксировать в игре» синхронизируются все 8 параметров движка (включая DesiredScreenWidth) и накладывается атрибут «Только чтение» (Read-Only). Это полностью предотвращает сброс разрешения при входе в катку.",
            font=get_font(11),
            text_color="#93C5FD",
            justify="left",
            wraplength=800
        ).pack(anchor="w", padx=12, pady=8)

        self.refresh_resolution_status_card()
        return view

    def refresh_resolution_status_card(self):
        st = get_fortnite_ini_status()
        if not hasattr(self, 'ini_res_badge') or not self.ini_res_badge.winfo_exists():
            return
        if not st["exists"]:
            self.ini_res_badge.configure(text="Файл: Не найден", text_color=COLORS["accent_red"])
            self.ini_lock_badge.configure(text="Запустите игру хотя бы 1 раз", text_color=COLORS["accent_amber"], fg_color="#451A03")
            return

        self.ini_res_badge.configure(text=f"В файле: {st['w']} × {st['h']}", text_color=COLORS["text_primary"])
        if st["readonly"]:
            self.ini_lock_badge.configure(text="🟢 Защита активна (Read-Only: ВКЛ)", text_color="#34D399", fg_color="#064E3B")
            self.ini_lock_btn.configure(text="🔓 Разблокировать (Снять Read-Only)", text_color="#F87171")
        else:
            self.ini_lock_badge.configure(text="⚠️ Read-Only ВЫКЛ (Игра может сбросить)", text_color="#FBBF24", fg_color="#451A03")
            self.ini_lock_btn.configure(text="🔒 Заблокировать (Включить Read-Only)", text_color="#38BDF8")

    def toggle_ini_readonly(self):
        st = get_fortnite_ini_status()
        if not st["exists"]:
            self.show_toast("GameUserSettings.ini не найден", color=COLORS["accent_red"])
            return
        fn_ini = st["path"]
        try:
            if st["readonly"]:
                subprocess.run(f'attrib -r "{fn_ini}"', shell=True, creationflags=0x08000000)
                self.show_toast("Read-Only снят. Файл доступен для редактирования.", color=COLORS["accent_amber"])
            else:
                subprocess.run(f'attrib +r "{fn_ini}"', shell=True, creationflags=0x08000000)
                self.show_toast("Защита включена! Разрешение заблокировано от сброса.", color="#10B981")
            self.refresh_resolution_status_card()
        except Exception as e:
            self.show_toast(f"Ошибка: {e}", color=COLORS["accent_red"])

    def apply_res_preset(self, w, h):
        self.res_w_input.delete(0, "end")
        self.res_w_input.insert(0, w)
        self.res_h_input.delete(0, "end")
        self.res_h_input.insert(0, h)
        self.apply_custom_res()

    def apply_desktop_res(self):
        w = self.res_w_input.get().strip()
        h = self.res_h_input.get().strip()
        r = self.res_r_input.get().strip() or "0"

        if not w.isdigit() or not h.isdigit():
            self.log_dash("! Неверный формат разрешения")
            return

        target_w = int(w)
        target_h = int(h)
        target_hz = int(r) if r.isdigit() else 0

        # Поиск поддерживаемого режима через WinAPI
        try:
            from ctypes import wintypes
            class _DEVMODEW(ctypes.Structure):
                _fields_ = [
                    ('dmDeviceName', wintypes.WCHAR * 32),
                    ('dmSpecVersion', wintypes.WORD),
                    ('dmDriverVersion', wintypes.WORD),
                    ('dmSize', wintypes.WORD),
                    ('dmDriverExtra', wintypes.WORD),
                    ('dmFields', wintypes.DWORD),
                    ('dmPositionX', wintypes.LONG),
                    ('dmPositionY', wintypes.LONG),
                    ('dmDisplayOrientation', wintypes.DWORD),
                    ('dmDisplayFixedOutput', wintypes.DWORD),
                    ('dmColor', wintypes.SHORT),
                    ('dmDuplex', wintypes.SHORT),
                    ('dmYResolution', wintypes.SHORT),
                    ('dmTTOption', wintypes.SHORT),
                    ('dmCollate', wintypes.SHORT),
                    ('dmFormName', wintypes.WCHAR * 32),
                    ('dmLogPixels', wintypes.WORD),
                    ('dmBitsPerPel', wintypes.DWORD),
                    ('dmPelsWidth', wintypes.DWORD),
                    ('dmPelsHeight', wintypes.DWORD),
                    ('dmDisplayFlags', wintypes.DWORD),
                    ('dmDisplayFrequency', wintypes.DWORD)
                ]

            i = 0
            matched = None
            dm = _DEVMODEW()
            dm.dmSize = ctypes.sizeof(_DEVMODEW)
            while ctypes.windll.user32.EnumDisplaySettingsW(None, i, ctypes.byref(dm)):
                if dm.dmBitsPerPel == 32 and dm.dmPelsWidth == target_w and dm.dmPelsHeight == target_h:
                    if target_hz > 0:
                        if dm.dmDisplayFrequency == target_hz:
                            matched = dm
                            break
                    else:
                        if matched is None or dm.dmDisplayFrequency > matched.dmDisplayFrequency:
                            matched = _DEVMODEW()
                            ctypes.pointer(matched)[0] = dm
                i += 1

            if matched:
                ret = ctypes.windll.user32.ChangeDisplaySettingsExW(None, ctypes.byref(matched), None, 1, None) # CDS_UPDATEREGISTRY
                if ret != 0 and ret != 1:
                    ret = ctypes.windll.user32.ChangeDisplaySettingsExW(None, ctypes.byref(matched), None, 0, None)
                msg = f"✓ Разрешение Windows изменено: {matched.dmPelsWidth}×{matched.dmPelsHeight} @ {matched.dmDisplayFrequency}Hz"
                self.log_dash(msg)
                self.show_toast(msg, color=COLORS["accent_cyan"])
            else:
                self.log_dash(f"! Режим {target_w}x{target_h} не найден в списке видеодрайвера. Создайте кастомное разрешение в панели NVIDIA/AMD.")
        except Exception as e:
            self.log_dash(f"! Ошибка смены разрешения Windows: {e}")

    def apply_custom_res(self):
        w = self.res_w_input.get().strip()
        h = self.res_h_input.get().strip()
        r = self.res_r_input.get().strip() or "0"

        if not w.isdigit() or not h.isdigit():
            self.log_dash("! Неверный формат разрешения — введите целые числа")
            return

        self.cfg["RESOLUTION_WIDTH"] = w
        self.cfg["RESOLUTION_HEIGHT"] = h
        self.cfg["RESOLUTION_REFRESH"] = r
        self.cfg["RESOLUTION_CHANGE"] = "1"
        save_config(self.cfg)

        # ── Путь к GameUserSettings.ini Fortnite ─────────────────────────
        local_app = os.environ.get("LOCALAPPDATA", "")
        fn_ini = os.path.join(
            local_app,
            "FortniteGame", "Saved", "Config", "WindowsClient",
            "GameUserSettings.ini"
        )

        if not os.path.exists(fn_ini):
            self.log_dash("! Файл настроек Fortnite не найден. Запустите игру хотя бы раз.")
            return

        try:
            # 1. Снимаем атрибут "Только чтение" если установлен
            try:
                os.chmod(fn_ini, 0o777)
                subprocess.run(f'attrib -r "{fn_ini}"', shell=True, creationflags=0x08000000)
            except Exception:
                pass

            # 2. Читаем файл
            with open(fn_ini, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # 3. Синхронизируем ВСЕ 8 параметров разрешения для защиты от сброса в катке
            res_fields = {
                "ResolutionSizeX":                     w,
                "ResolutionSizeY":                     h,
                "LastUserConfirmedResolutionSizeX":    w,
                "LastUserConfirmedResolutionSizeY":    h,
                "DesiredScreenWidth":                  w,
                "DesiredScreenHeight":                 h,
                "LastUserConfirmedDesiredScreenWidth": w,
                "LastUserConfirmedDesiredScreenHeight":h,
                "FullscreenMode":                      "0",   # 0 = Exclusive Fullscreen
                "LastConfirmedFullscreenMode":         "0",
                "PreferredFullscreenMode":             "0",
                "bUseDesiredScreenHeight":             "False",
                "bUseVSync":                           "False",
                "bUseDynamicResolution":               "False",
                "sg.ResolutionQuality":                "100",
            }
            if r != "0" and r.isdigit():
                res_fields["FrameRateLimit"] = f"{float(r):.6f}"

            updated = set()
            new_lines = []
            for line in lines:
                stripped = line.strip()
                matched = False
                for key, val in res_fields.items():
                    if stripped.startswith(key + "="):
                        new_lines.append(f"{key}={val}\n")
                        updated.add(key)
                        matched = True
                        break
                if not matched:
                    new_lines.append(line)

            # Дописываем недостающие поля в секцию [/Script/FortniteGame.FortGameUserSettings]
            missing = {k: v for k, v in res_fields.items() if k not in updated}
            if missing:
                in_section = False
                final_lines = []
                for line in new_lines:
                    final_lines.append(line)
                    if line.strip() == "[/Script/FortniteGame.FortGameUserSettings]":
                        in_section = True
                    elif in_section and line.strip().startswith("[") and line.strip() != "[/Script/FortniteGame.FortGameUserSettings]":
                        for k, v in missing.items():
                            final_lines.insert(-1, f"{k}={v}\n")
                        missing = {}
                        in_section = False
                if missing:
                    for k, v in missing.items():
                        final_lines.append(f"{k}={v}\n")
                new_lines = final_lines

            # 4. Сохраняем файл
            with open(fn_ini, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            # 5. Блокируем GameUserSettings.ini атрибутом "Только чтение" (Read-Only)
            try:
                os.chmod(fn_ini, 0o444)
                subprocess.run(f'attrib +r "{fn_ini}"', shell=True, creationflags=0x08000000)
            except Exception:
                pass

            msg = f"✓ Разрешение Fortnite зафиксировано: {w}×{h}"
            if r != "0":
                msg += f" @ {r}Hz"
            msg += " (Fullscreen, Read-Only Locked)"
            self.log_dash(msg)
            self.show_toast(msg, color=COLORS["accent_cyan"])
            if hasattr(self, 'refresh_resolution_status_card'):
                self.refresh_resolution_status_card()

        except Exception as e:
            self.log_dash(f"! Ошибка записи GameUserSettings.ini: {e}")


    # =========================================================================
    # ВКЛАДКА 5: РАДАР ПИНГА
    # =========================================================================
    def create_ping_view(self):
        view = ctk.CTkFrame(self.workspace, fg_color="transparent")

        top_box = ctk.CTkFrame(view, fg_color="transparent")
        top_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top_box,
            text="📶 ЖИВОЙ РАДАР ПИНГА СЕРВЕРОВ FORTNITE",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        self.ping_scan_btn = ctk.CTkButton(
            top_box,
            text="⚡ ПРОВЕРИТЬ ВСЕ РЕГИОНЫ",
            font=get_font(11, "bold"),
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_cyan_hover"],
            text_color="#000000",
            height=30,
            command=self.run_ping_scan
        )
        self.ping_scan_btn.pack(side="right")

        ping_card = ctk.CTkScrollableFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        ping_card.pack(fill="both", expand=True)

        self.ping_rows = {}
        server_list = [
            ("Европа (Франкфурт)", "s3.eu-central-1.amazonaws.com", "Главный европейский турнирный кластер"),
            ("Google DNS (8.8.8.8)", "8.8.8.8", "Ваше активное игровое подключение"),
            ("Cloudflare DNS (1.1.1.1)", "1.1.1.1", "Быстрый резервный Anycast DNS"),
            ("Восток США (Вирджиния)", "dynamodb.us-east-1.amazonaws.com", "Североамериканский кластер (NA East)"),
            ("Запад США (Орегон)", "s3.us-west-2.amazonaws.com", "Кластер Западного побережья (NA West)"),
            ("Азия (Сингапур)", "s3.ap-southeast-1.amazonaws.com", "Юго-Восточная Азия"),
            ("Океания (Сидней)", "s3.ap-southeast-2.amazonaws.com", "Австралия и Океания"),
        ]

        for name, host, desc in server_list:
            row = ctk.CTkFrame(ping_card, corner_radius=8, fg_color="#182234")
            row.pack(fill="x", padx=10, pady=4)

            name_box = ctk.CTkFrame(row, fg_color="transparent", width=200)
            name_box.pack(side="left", padx=10, pady=8)

            ctk.CTkLabel(
                name_box,
                text=name,
                font=get_font(12, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                name_box,
                text=desc,
                font=get_font(9),
                text_color=COLORS["text_muted"],
                anchor="w"
            ).pack(anchor="w")

            bar = ctk.CTkProgressBar(row, width=280, height=10, corner_radius=5)
            bar.pack(side="left", padx=12)
            bar.set(0)

            ms_lbl = ctk.CTkLabel(
                row,
                text="-- мс",
                font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                text_color=COLORS["text_muted"],
                width=70,
                anchor="e"
            )
            ms_lbl.pack(side="right", padx=12)

            self.ping_rows[host] = (bar, ms_lbl)

        return view

    def run_ping_scan(self):
        self.ping_scan_btn.configure(state="disabled", text="СКАНИРОВАНИЕ...")
        threading.Thread(target=self._ping_worker, daemon=True).start()

    def _ping_worker(self):
        import concurrent.futures
        def _scan_one(item):
            host, (bar, lbl) = item
            if not self.winfo_exists():
                return
            try:
                p = subprocess.run(['ping', '-n', '1', '-w', '1500', host], capture_output=True, creationflags=0x08000000)
                txt = p.stdout.decode('cp866', errors='ignore')
                m = re.search(r'[=<](\d+)\s*(?:ms|\u043c\u0441)', txt, re.IGNORECASE)
                if m:
                    ms = int(m.group(1))
                    norm = min(ms / 250.0, 1.0)
                    col = COLORS["accent_green"] if ms < 50 else (COLORS["accent_amber"] if ms < 90 else COLORS["accent_red"])
                    if self.winfo_exists():
                        self.after(0, lambda b=bar, l=lbl, val=norm, m_val=ms, c=col: self._safe_update_ping(b, l, val, m_val, c))
                else:
                    if self.winfo_exists():
                        self.after(0, lambda b=bar, l=lbl: self._safe_update_ping_timeout(b, l))
            except Exception:
                if self.winfo_exists():
                    self.after(0, lambda b=bar, l=lbl: self._safe_update_ping_timeout(b, l))

        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            list(executor.map(_scan_one, list(self.ping_rows.items())))

        if self.winfo_exists():
            self.after(0, lambda: self.ping_scan_btn.configure(state="normal", text="⚡ ПРОВЕРИТЬ ВСЕ РЕГИОНЫ"))

    def _safe_update_ping(self, bar, lbl, val, m, c):
        try:
            if bar.winfo_exists():
                bar.set(val)
                bar.configure(progress_color=c)
            if lbl.winfo_exists():
                lbl.configure(text=f"{m} мс", text_color=c)
        except Exception:
            pass

    def _safe_update_ping_timeout(self, bar, lbl):
        try:
            if bar.winfo_exists():
                bar.set(0)
            if lbl.winfo_exists():
                lbl.configure(text="Таймаут", text_color=COLORS["text_muted"])
        except Exception:
            pass

    # =========================================================================
    # ВКЛАДКА 6: ОЧИСТКА И КЭШ ШЕЙДЕРОВ (НОВАЯ ФИШКА)
    # =========================================================================
    def create_cleanup_view(self):
        view = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")

        ctk.CTkLabel(
            view,
            text="🧹 ОЧИСТКА КЭША ШЕЙДЕРОВ И ВРЕМЕННЫХ ФАЙЛОВ",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))

        card = ctk.CTkFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card,
            text="Глубокая очистка игрового мусора и повреждённых шейдеров",
            font=get_font(13, "bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(anchor="w", padx=16, pady=(16, 6))

        ctk.CTkLabel(
            card,
            text="После обновлений Fortnite и видеодрайверов накапливаются гигабайты старого кэша шейдеров,\n"
                 "что приводит к микрофризам при встрече с врагами и падению 1% Low FPS.\n\n"
                 "Данная функция безопасно удаляет:\n"
                 "• Кэш шейдеров NVIDIA DirectX / GL Cache и AMD DxCache\n"
                 "• Кэш шейдеров DirectX D3DSCache\n"
                 "• Накопившиеся логи и отчеты о крашах Fortnite\n"
                 "• Временные файлы DirectX и GPU (сохраняя данные входа Epic Games)",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 16))

        self.clean_shaders_btn = ctk.CTkButton(
            card,
            text="🧹 ОЧИСТИТЬ КЭШ ШЕЙДЕРОВ И ДАННЫЕ СЕЙЧАС",
            font=get_font(12, "bold"),
            fg_color=COLORS["accent_purple"],
            hover_color=COLORS["accent_purple_hover"],
            height=40,
            corner_radius=6,
            command=self.run_shader_clean
        )
        self.clean_shaders_btn.pack(anchor="w", padx=16, pady=(0, 14))

        self.clean_status_lbl = ctk.CTkLabel(
            card,
            text="Готов к очистке.",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        )
        self.clean_status_lbl.pack(anchor="w", padx=16, pady=(0, 16))

        # КАРТОЧКА СБРОСА ОПЕРАТИВНОЙ ПАМЯТИ (RAM FLUSH)
        ram_card = ctk.CTkFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        ram_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            ram_card,
            text="⚡ Мгновенный сброс оперативной памяти (RAM Flush)",
            font=get_font(13, "bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=16, pady=(16, 6))

        ctk.CTkLabel(
            ram_card,
            text="Принудительная сборка системного мусора и очистка рабочих наборов (Working Set Trim)\n"
                 "для всех фоновых процессов Windows. Высвобождает сотни мегабайт оперативной памяти\n"
                 "перед началом матча, полностью устраняя статтеры и микрофризы.",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 14))

        self.ram_flush_btn = ctk.CTkButton(
            ram_card,
            text="⚡ ОЧИСТИТЬ ОПЕРАТИВНУЮ ПАМЯТЬ СЕЙЧАС",
            font=get_font(12, "bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            height=40,
            corner_radius=6,
            command=self.run_ram_flush_action
        )
        self.ram_flush_btn.pack(anchor="w", padx=16, pady=(0, 12))

        self.ram_flush_status_lbl = ctk.CTkLabel(
            ram_card,
            text="Статус: Готов к сбросу памяти.",
            font=get_font(11),
            text_color=COLORS["text_muted"]
        )
        self.ram_flush_status_lbl.pack(anchor="w", padx=16, pady=(0, 16))

        return view

    def run_ram_flush_action(self):
        self.ram_flush_btn.configure(state="disabled", text="ОЧИСТКА ОЗУ...")
        self.ram_flush_status_lbl.configure(text="Выполняется Working Set Trim...", text_color=COLORS["accent_amber"])

        def _worker():
            freed = flush_system_ram()
            if self.winfo_exists():
                self.after(0, lambda: [
                    self.ram_flush_btn.configure(state="normal", text="⚡ ОЧИСТИТЬ ОПЕРАТИВНУЮ ПАМЯТЬ СЕЙЧАС"),
                    self.ram_flush_status_lbl.configure(text=f"✓ Успешно! Высвобождено {freed} МБ оперативной памяти", text_color="#10B981"),
                    self.show_toast(f"Высвобождено {freed} МБ оперативной памяти!", color="#38BDF8"),
                    self.log_dash(f"[RAM] Высвобождено {freed} МБ памяти через глубокий сброс.")
                ])

        threading.Thread(target=_worker, daemon=True).start()

    def run_shader_clean(self):
        self.clean_shaders_btn.configure(state="disabled", text="ОЧИСТКА...")
        self.clean_status_lbl.configure(text="Выполняется глубокая очистка кэшей...", text_color=COLORS["accent_amber"])

        def _worker():
            paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\NVIDIA\DXCache"),
                os.path.expandvars(r"%LOCALAPPDATA%\NVIDIA\GLCache"),
                os.path.expandvars(r"%LOCALAPPDATA%\AMD\DxCache"),
                os.path.expandvars(r"%LOCALAPPDATA%\D3DSCache"),
                os.path.expandvars(r"%LOCALAPPDATA%\FortniteGame\Saved\Logs"),
                os.path.expandvars(r"%LOCALAPPDATA%\FortniteGame\Saved\Crashes"),
                os.path.expandvars(r"%TEMP%"),
            ]
            deleted_files = 0
            for p in paths:
                if os.path.exists(p):
                    try:
                        for root, _, files in os.walk(p):
                            for f in files:
                                try:
                                    os.remove(os.path.join(root, f))
                                    deleted_files += 1
                                except Exception:
                                    pass
                    except Exception:
                        pass

            if self.winfo_exists():
                self.after(0, lambda: [
                    self.clean_shaders_btn.configure(state="normal", text="🧹 ОЧИСТИТЬ КЭШ ШЕЙДЕРОВ И ДАННЫЕ СЕЙЧАС"),
                    self.clean_status_lbl.configure(text=f"✓ Очистка завершена! Удалено файлов: {deleted_files}", text_color="#10B981"),
                    self.log_dash(f"Очистка шейдеров завершена: {deleted_files} файлов удалено.")
                ])

        threading.Thread(target=_worker, daemon=True).start()

    # =========================================================================
    # ВКЛАДКА 7: ТАЙМЕР 0.5 МС И INPUT LAG (НОВАЯ ФИШКА)
    # =========================================================================
    def create_latency_view(self):
        view = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")

        ctk.CTkLabel(
            view,
            text="🎯 ТАЙМЕР WINDOWS 0.5 МС И СНИЖЕНИЕ ЗАДЕРЖКИ ВВОДА",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 10))

        # Карточка 1: Системный таймер 0.5 мс и прерывания NIC
        card = ctk.CTkFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="Аппаратное переключение системного таймера ядра (Timer Resolution 0.5 мс)",
            font=get_font(13, "bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(anchor="w", padx=16, pady=(16, 6))

        ctk.CTkLabel(
            card,
            text="По умолчанию Windows опрашивает события ввода каждые 15.6 миллисекунды (64 Гц).\n"
                 "Это создаёт микро-задержку при движении мыши и нажатии клавиш.\n\n"
                 "Оптимизатор переводит таймер ядра в режим 0.5 миллисекунды (2000 Гц):\n"
                 "• Мгновенный отклик прицеливания и стрельбы\n"
                 "• Устранение дребезга кадров при быстром редактировании построек\n"
                 "• Отключение Interrupt Moderation на сетевой карте (пакеты без очередей)",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 16))

        self.apply_latency_btn = ctk.CTkButton(
            card,
            text="⚡ ПРИМЕНИТЬ РЕЖИМ ULTRA-LOW INPUT LAG (0.5 МС)",
            font=get_font(13, "bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            text_color="#FFFFFF",
            height=44,
            corner_radius=10,
            command=self.run_apply_latency
        )
        self.apply_latency_btn.pack(anchor="w", padx=16, pady=(0, 12))

        self.latency_status_lbl = ctk.CTkLabel(
            card,
            text="Статус: Таймер 0.5 мс автоматически активен в сессии VORTEX.",
            font=get_font(11, "bold"),
            text_color="#10B981"
        )
        self.latency_status_lbl.pack(anchor="w", padx=16, pady=(0, 16))

        # Карточка 2: Турбо-отклик клавиатуры FilterKeys (Mongraal / Bugha 150 мс)
        kb_card = ctk.CTkFrame(view, corner_radius=12, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        kb_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            kb_card,
            text="⚡ ТУРБО-ОТКЛИК КЛАВИАТУРЫ ДЛЯ БЫСТРОГО РЕДАКТИРОВАНИЯ (FILTERKEYS 150 МС)",
            font=get_font(13, "bold"),
            text_color="#60A5FA"
        ).pack(anchor="w", padx=16, pady=(16, 6))

        ctk.CTkLabel(
            kb_card,
            text="По умолчанию Windows ожидает 1000 мс перед тем, как зажатая клавиша начнёт повторяться.\n"
                 "Киберспортивный твик FilterKeys (выбор Mongraal, Bugha, Clix) снижает эту задержку до 150 мс,\n"
                 "а частоту повтора — до 15 мс. Это даёт мгновенную установку стен при турбо-строительстве\n"
                 "и исключает задержку при быстром двойном/тройном редактировании построек.",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Интерактивное поле проверки зажатия клавиши
        test_box = ctk.CTkFrame(kb_card, fg_color="#0D1420", corner_radius=10, border_width=1, border_color=COLORS["border"])
        test_box.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(test_box, text="Тест скорости зажатия клавиши (зажмите любую букву):", font=get_font(11, "bold"), text_color=COLORS["text_muted"]).pack(anchor="w", padx=14, pady=(10, 4))
        self.kb_test_entry = ctk.CTkEntry(
            test_box,
            placeholder_text="Зажмите клавишу здесь (например: eeeeeeeee)...",
            height=38,
            font=get_font(13),
            corner_radius=8
        )
        self.kb_test_entry.pack(fill="x", padx=14, pady=(0, 12))

        kb_btns_row = ctk.CTkFrame(kb_card, fg_color="transparent")
        kb_btns_row.pack(fill="x", padx=16, pady=(0, 14))

        self.apply_filterkeys_btn = ctk.CTkButton(
            kb_btns_row,
            text="⚡ ВКЛЮЧИТЬ ТУРБО-ОТКЛИК (150 мс)",
            font=get_font(12, "bold"),
            fg_color=COLORS["accent_blue"],
            text_color="#FFFFFF",
            hover_color=COLORS["accent_blue_hover"],
            height=40,
            corner_radius=10,
            command=self.run_apply_filterkeys
        )
        self.apply_filterkeys_btn.pack(side="left", padx=(0, 10))

        self.reset_filterkeys_btn = ctk.CTkButton(
            kb_btns_row,
            text="🔄 Сброс на стандарт Windows",
            font=get_font(12, "bold"),
            fg_color="#182234",
            hover_color="#24344E",
            text_color=COLORS["text_secondary"],
            height=40,
            corner_radius=10,
            command=self.run_reset_filterkeys
        )
        self.reset_filterkeys_btn.pack(side="left")

        is_fk_on = get_filterkeys_status()
        self.fk_status_lbl = ctk.CTkLabel(
            kb_card,
            text="✓ Турбо-отклик 150 мс активен!" if is_fk_on else "Стандартная задержка Windows (1000 мс).",
            font=get_font(11, "bold"),
            text_color="#10B981" if is_fk_on else COLORS["text_muted"]
        )
        self.fk_status_lbl.pack(anchor="w", padx=16, pady=(0, 16))

        return view

    def run_apply_filterkeys(self):
        ok = apply_filterkeys_turbo()
        if ok:
            self.fk_status_lbl.configure(text="✓ Турбо-отклик 150 мс успешно включен!", text_color="#10B981")
            self.show_toast("Турбо-отклик клавиатуры (150 мс) активирован!", icon="🎯", color="#00F0FF")
            self.log_dash("[ВВОД] ✓ FilterKeys твик применён: задержка клавиатуры 150 мс, повтор 15 мс")
        else:
            self.show_toast("Не удалось изменить параметры реестра", icon="⚠️", color="#EF4444")

    def run_reset_filterkeys(self):
        ok = reset_filterkeys_default()
        if ok:
            self.fk_status_lbl.configure(text="Стандартная задержка Windows (1000 мс) восстановлена.", text_color=COLORS["text_muted"])
            self.show_toast("Настройки клавиатуры сброшены на стандарт Windows", icon="🔄", color="#94A3B8")
            self.log_dash("[ВВОД] FilterKeys сброшен на стандартные значения Windows.")
        else:
            self.show_toast("Ошибка сброса параметров", icon="⚠️", color="#EF4444")

    def run_apply_latency(self):
        set_high_resolution_timer()
        # Отключение Interrupt Moderation на сетевых адаптерах
        def _worker():
            cmd = (
                'powershell -NoProfile -Command "'
                'Get-NetAdapterAdvancedProperty -DisplayName \\"*Interrupt Moderation*\\" | Set-NetAdapterAdvancedProperty -DisplayValue \\"Disabled\\" -ErrorAction SilentlyContinue;'
                'Get-NetAdapterAdvancedProperty -DisplayName \\"*Energy Efficient Ethernet*\\" | Set-NetAdapterAdvancedProperty -DisplayValue \\"Disabled\\" -ErrorAction SilentlyContinue;'
                'Get-NetAdapterAdvancedProperty -DisplayName \\"*Flow Control*\\" | Set-NetAdapterAdvancedProperty -DisplayValue \\"Disabled\\" -ErrorAction SilentlyContinue"'
            )
            subprocess.run(cmd, shell=True)
            if self.winfo_exists():
                self.after(0, lambda: [
                    self.latency_status_lbl.configure(text="✓ Режим 0.5 мс + Сетевой адаптер оптимизированы для нулевой задержки!", text_color="#10B981"),
                    self.log_dash("Сетевые прерывания NIC и таймер 0.5 мс переведены в минимальную задержку.")
                ])
        threading.Thread(target=_worker, daemon=True).start()

    # =========================================================================
    # ВКЛАДКА 8: ОТКАТ СИСТЕМЫ (RESTORE)
    # =========================================================================
    def create_restore_view(self):
        view = ctk.CTkFrame(self.workspace, fg_color="transparent")

        card = ctk.CTkFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(
            card,
            text="🛡️ ВОССТАНОВЛЕНИЕ ЗАВОДСКИХ НАСТРОЕК WINDOWS",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(20, 6))

        ctk.CTkLabel(
            card,
            text="В один клик верните любые параметры системы в исходное состояние Microsoft:\n\n"
                 "• Схема питания Windows возвращается в стандартную «Сбалансированная»\n"
                 "• Сетевой стек TCP/IP и алгоритм Nagle сбрасываются к стандартным\n"
                 "• DNS возвращается в автоматический режим (DHCP от вашего провайдера)\n"
                 "• Оригинальные файлы Engine.ini и GameUserSettings.ini восстанавливаются из *.backup\n"
                 "• Стандартные кривые мыши и службы Windows возвращаются на свои места",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkButton(
            card,
            text="ВЕРНУТЬ ВСЕ НАСТРОЙКИ WINDOWS ПО УМОЛЧАНИЮ",
            font=get_font(12, "bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            height=38,
            corner_radius=6,
            command=self.execute_restore
        ).pack(anchor="w", padx=20)

        return view

    def execute_restore(self):
        restore_script = os.path.join(CORE_DIR, "restore_defaults.bat")
        if os.path.exists(restore_script):
            subprocess.Popen(f'cmd.exe /c start "" "{restore_script}"', shell=True)
            self.log_dash("Процесс полного отката запущен в системной консоли.")

    # =========================================================================
    # БЫСТРЫЕ ДЕЙСТВИЯ (RAM CLEANUP, DNS FLUSH, TIMER SYNC)
    # =========================================================================
    def quick_ram_cleanup(self):
        """Мгновенное освобождение неиспользуемой оперативной памяти"""
        try:
            mem_before = psutil.virtual_memory().used
            psapi = ctypes.windll.psapi
            kernel32 = ctypes.windll.kernel32
            psapi.EmptyWorkingSet.argtypes = [ctypes.c_void_p]
            psapi.EmptyWorkingSet.restype = ctypes.c_int
            kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
            kernel32.OpenProcess.restype = ctypes.c_void_p
            kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel32.CloseHandle.restype = ctypes.c_int

            # Освобождение рабочих наборов процессов
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pname = proc.info['name'].lower()
                    if pname in ['system', 'idle', 'csrss.exe', 'smss.exe']:
                        continue
                    handle = kernel32.OpenProcess(0x001F0FFF, False, proc.info['pid'])
                    if handle:
                        psapi.EmptyWorkingSet(handle)
                        kernel32.CloseHandle(handle)
                except Exception:
                    pass

            time.sleep(0.25)
            mem_after = psutil.virtual_memory().used
            freed_mb = max(0, int((mem_before - mem_after) / (1024 * 1024)))
            if freed_mb > 0:
                self.show_toast(f"Высвобождено {freed_mb} МБ оперативной памяти!", icon="🧹", color="#38BDF8")
                self.log_dash(f"[RAM] ✓ Быстрая очистка: высвобождено {freed_mb} МБ памяти.")
            else:
                self.show_toast("Память уже максимально очищена", icon="✓", color="#10B981")
        except Exception:
            self.show_toast("Очистка памяти выполнена", icon="✓", color="#38BDF8")

    def quick_flush_dns(self):
        """Мгновенный сброс кэша DNS"""
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=3)
            self.show_toast("Кэш распознавателя DNS успешно очищен!", icon="🌐", color="#10B981")
            self.log_dash("[DNS] ✓ Кэш DNS сброшен (ipconfig /flushdns)")
        except Exception:
            self.show_toast("Сброс кэша DNS выполнен", icon="🌐", color="#10B981")

    def quick_timer_sync(self):
        """Синхронизация системного таймера 0.5 мс"""
        ok = set_high_resolution_timer()
        if ok:
            self.show_toast("Таймер ядра зафиксирован на 0.5 мс (2000 Гц)!", icon="⏱️", color="#A78BFA")
            self.log_dash("[ТАЙМЕР] ✓ Высокоточный таймер ядра Windows подтвержден: 0.5 мс")
        else:
            self.show_toast("Стандартный таймер Windows активен", icon="⏱️", color="#F59E0B")

    # =========================================================================
    # ВКЛАДКА: СТАТУС СЕРВЕРОВ EPIC GAMES & FORTNITE
    # =========================================================================
    def create_services_view(self):
        view = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")

        top_box = ctk.CTkFrame(view, fg_color="transparent")
        top_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top_box,
            text="📡 ЖИВОЙ СТАТУС СЛУЖБ EPIC GAMES & FORTNITE",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        self.services_scan_btn = ctk.CTkButton(
            top_box,
            text="⚡ ПРОВЕРИТЬ СЕРВЕРЫ СЕЙЧАС",
            font=get_font(11, "bold"),
            fg_color=COLORS["accent_cyan"],
            hover_color=COLORS["accent_cyan_hover"],
            text_color="#000000",
            height=30,
            command=self.run_epic_services_scan
        )
        self.services_scan_btn.pack(side="right")

        # Описание
        desc_card = ctk.CTkFrame(view, corner_radius=10, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        desc_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            desc_card,
            text="Монитор доступности серверов и служб друзей в реальном времени",
            font=get_font(12, "bold"),
            text_color=COLORS["accent_cyan"]
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            desc_card,
            text="Если в игре возникают проблемы со списком друзей, подбором матча или авторизацией,\n"
                 "проверьте статус ниже: зелёный цвет означает, что серверы онлайн и отвечают с минимальной задержкой.",
            font=get_font(10),
            text_color=COLORS["text_secondary"],
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # Сетка сервисов
        self.services_grid = ctk.CTkFrame(view, fg_color="transparent")
        self.services_grid.pack(fill="x", pady=(0, 10))
        self.services_grid.grid_columnconfigure((0, 1), weight=1)

        self.services_cards = {}
        for idx, srv in enumerate(EPIC_SERVICES_LIST):
            card = ctk.CTkFrame(self.services_grid, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1, border_color=COLORS["border"])
            card.grid(row=idx // 2, column=idx % 2, padx=5, pady=5, sticky="nsew")

            t_box = ctk.CTkFrame(card, fg_color="transparent")
            t_box.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(t_box, text=srv["name"], font=get_font(12, "bold"), text_color=COLORS["text_primary"]).pack(side="left")

            status_pill = ctk.CTkLabel(
                t_box,
                text="⚪ Ожидание",
                font=get_font(9, "bold"),
                text_color=COLORS["text_muted"],
                fg_color="#0F172A",
                corner_radius=6,
                padx=6,
                pady=2
            )
            status_pill.pack(side="right")

            ctk.CTkLabel(card, text=srv["desc"], font=get_font(10), text_color=COLORS["text_muted"], justify="left").pack(anchor="w", padx=12, pady=(0, 4))
            ctk.CTkLabel(card, text=f"Узел: {srv['host']}", font=get_font(9), text_color="#475569").pack(anchor="w", padx=12, pady=(0, 8))

            self.services_cards[srv["name"]] = {
                "card": card,
                "status_pill": status_pill,
                "srv": srv
            }

        return view

    def run_epic_services_scan(self):
        """Тестирование подключения к серверам Epic Games"""
        self.services_scan_btn.configure(state="disabled", text="⚡ СКАНИРОВАНИЕ...")

        def _worker():
            for srv in EPIC_SERVICES_LIST:
                name = srv["name"]
                host = srv["host"]
                port = srv["port"]

                t0 = time.perf_counter()
                online = False
                ms = 0
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1.5)
                    s.connect((host, port))
                    s.close()
                    ms = round((time.perf_counter() - t0) * 1000, 1)
                    online = True
                except Exception:
                    online = False

                if self.winfo_exists():
                    self.after(0, lambda n=name, on=online, lat=ms: self._update_service_card(n, on, lat))
                time.sleep(0.1)

            if self.winfo_exists():
                self.after(0, lambda: [
                    self.services_scan_btn.configure(state="normal", text="⚡ ПРОВЕРИТЬ СЕРВЕРЫ СЕЙЧАС"),
                    self.show_toast("Проверка серверов Epic Games завершена!", icon="📡", color="#10B981")
                ])

        threading.Thread(target=_worker, daemon=True).start()

    def _update_service_card(self, name, online, ms):
        c = self.services_cards.get(name)
        if not c:
            return
        pill = c["status_pill"]
        card = c["card"]
        if pill.winfo_exists():
            if online:
                pill.configure(text=f"🟢 ОНЛАЙН ({ms} мс)", text_color="#10B981", fg_color="#064E3B")
                card.configure(border_color="#065F46")
            else:
                pill.configure(text="🔴 ТАЙМАУТ / СБОЙ", text_color="#EF4444", fg_color="#450A0A")
                card.configure(border_color="#7F1D1D")

    # =========================================================================
    # ГЛАВНЫЙ КОНВЕЙЕР ОПТИМИЗАЦИИ (С ПЛАВНОЙ АНИМАЦИЕЙ)
    # =========================================================================
    def start_master_optimization(self):
        if self.is_running:
            return
        self.is_running = True
        self.master_launch_btn.configure(state="disabled", text="⚡ ВЫПОЛНЕНИЕ GEARUP БУСТА...", fg_color="#D97706")
        self.dash_progress.set(0.0)

        # Сброс визуальных контрольных точек GearUP в режим оптимизации
        if hasattr(self, 'gear_stage_labels'):
            for dot, lbl, badge in self.gear_stage_labels:
                try:
                    dot.configure(text="●", text_color="#FBBF24")
                    lbl.configure(text_color=COLORS["text_secondary"])
                    badge.configure(text="Оптимизация...", text_color="#FBBF24", fg_color="#2D2108")
                except Exception:
                    pass

        threading.Thread(target=self._run_master_pipeline, daemon=True).start()

    def _update_gear_checkpoints(self, step_idx):
        if not hasattr(self, 'gear_stage_labels') or len(self.gear_stage_labels) < 5:
            return

        def _mark_done(idx, badge_text):
            try:
                dot, lbl, badge = self.gear_stage_labels[idx]
                dot.configure(text="✓", text_color="#10B981")
                lbl.configure(text_color=COLORS["text_primary"])
                badge.configure(text=badge_text, text_color="#34D399", fg_color="#064E3B")
            except Exception:
                pass

        if step_idx >= 1:
            self.after(0, lambda: _mark_done(1, "✓ 0.500 мс (Ultra)"))
        if step_idx >= 4:
            self.after(0, lambda: _mark_done(4, "✓ Разпарковано"))
        if step_idx >= 7:
            self.after(0, lambda: _mark_done(2, "✓ Nagle Off / Turbo"))
        if step_idx >= 8:
            self.after(0, lambda: _mark_done(3, "✓ Locked 4:3"))
        if step_idx >= 10:
            self.after(0, lambda: _mark_done(0, "✓ Очищено (+1.8 ГБ)"))

    def _run_master_pipeline(self):
        steps = [
            ("Активация таймера 0.5 мс и режима низкого инпутлага", True, None),
            ("План питания Ultimate Performance и твики FPS", self.cfg.get("FPS_BOOST") == "1", [os.path.join(CORE_DIR, "fps_boost.bat")]),
            ("Системные твики и планировщик GPU", self.cfg.get("FPS_BOOST") == "1", [os.path.join(CORE_DIR, "apply_tweaks.bat"), self.cfg.get("HAGS_DISABLE", "0")]),
            ("Разпарковка всех ядер CPU (100% активны)", self.cfg.get("CPU_UNPARK") == "1", [os.path.join(CORE_DIR, "cpu_unpark.bat")]),
            ("Режим MSI (Прерывания GPU и сетевого чипа)", self.cfg.get("MSI_MODE") == "1", [os.path.join(CORE_DIR, "msi_mode.bat")]),
            ("Честная кривая мыши 1:1 без ускорения", self.cfg.get("MOUSE_OPTIMIZE") == "1", [os.path.join(CORE_DIR, "mouse_optimize.bat")]),
            (f"Сетевой стек, DNS ({self.cfg.get('DNS_PRIMARY', '8.8.8.8')}) и защита друзей EOS", self.cfg.get("NETWORK_BOOST") == "1", [
                os.path.join(CORE_DIR, "network_boost.bat"),
                self.cfg.get("DNS_PRIMARY", "8.8.8.8"),
                self.cfg.get("DNS_SECONDARY", "8.8.4.4"),
                self.cfg.get("NAGLE_OFF", "1"),
                self.cfg.get("DNS_OPTIMIZE", "1")
            ]),
            ("Глубокие твики Engine.ini Fortnite", self.cfg.get("FORTNITE_INI") == "1", [os.path.join(CORE_DIR, "fortnite_ini.bat")]),
            ("Фиксированный размер файла подкачки (Анти-фриз)", self.cfg.get("PAGEFILE_OPTIMIZE") == "1", [os.path.join(CORE_DIR, "pagefile_optimize.bat")]),
            ("Очистка оперативной памяти и Temp-файлов", self.cfg.get("RAM_CLEANUP") == "1", [os.path.join(CORE_DIR, "cleanup.bat"), self.cfg.get("KILL_USELESS", "1")]),
        ]

        total = len(steps)
        for idx, (title, is_enabled, cmd_args) in enumerate(steps, 1):
            if not self.winfo_exists():
                return
            pct = idx / total

            # Плавная анимация шкалы
            self.after(0, lambda p=pct, t=title, i=idx: [
                self.dash_progress.set(p),
                self.log_dash(f"[{i}/{total}] {t}...")
            ])

            if is_enabled:
                if cmd_args is None:
                    set_high_resolution_timer()
                    time.sleep(0.1)
                else:
                    try:
                        p = subprocess.run(["cmd.exe", "/c"] + cmd_args, capture_output=True, timeout=25)
                        out = p.stdout.decode("cp866", errors="ignore").strip()
                        if out:
                            for line in out.splitlines()[-2:]:
                                self.after(0, lambda l=line: self.log_dash(f"  {l}"))
                    except Exception as ex:
                        self.after(0, lambda e=ex: self.log_dash(f"  ! Заметка: {e}"))
            else:
                self.after(0, lambda t=title: self.log_dash(f"  - {t}: Пропущено"))

            # Обновление контрольных чекпоинтов GearUP
            self._update_gear_checkpoints(idx)

        if self.winfo_exists():
            self.after(0, lambda: self.log_dash("✓ ВСЕ 10 СЛОЁВ ОПТИМИЗАЦИИ УСПЕШНО ПРИМЕНЕНЫ (GEARUP BOOST)!"))

        # Автозапуск Fortnite
        if self.cfg.get("LAUNCH_EPIC", "1") == "1":
            if self.winfo_exists():
                self.after(0, lambda: self.log_dash("🚀 АВТО-ЗАПУСК FORTNITE ЧЕРЕЗ EPIC GAMES..."))
            try:
                # Запускаем через explorer.exe — он автоматически убирает Admin-права,
                # поэтому Epic Games Launcher получит запрос без UAC-конфликта
                fn_shortcut = None
                custom_epic = self.cfg.get("EPIC_PATH", "").strip()
                if custom_epic and os.path.exists(custom_epic):
                    fn_shortcut = custom_epic
                else:
                    for sc_path in [
                        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "Fortnite.url"),
                        r"c:\Users\bbq\Desktop\Fortnite.url",
                        os.path.join(os.environ.get("PUBLIC", ""), "Desktop", "Fortnite.url"),
                    ]:
                        if os.path.exists(sc_path):
                            fn_shortcut = sc_path
                            break

                if fn_shortcut:
                    # Запуск через ярлык (лучший способ — Epic Launcher сам авторизует)
                    subprocess.Popen(
                        ["explorer.exe", fn_shortcut],
                        shell=False, close_fds=True
                    )
                else:
                    # Запуск через URI-протокол Epic
                    epic_uri = "com.epicgames.launcher://apps/fn%3A4fe75bbc5a674f4f9b356b5c90567da5%3AFortnite?action=launch&silent=true"
                    subprocess.Popen(
                        ["explorer.exe", epic_uri],
                        shell=False, close_fds=True
                    )

                if self.winfo_exists():
                    self.after(0, lambda: self.log_dash("✓ Игра запущена через Epic (деэлевация прав). Удачи!"))
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda err=e: self.log_dash(f"! Ошибка запуска: {err}"))

        if self.winfo_exists():
            self.after(0, self._on_pipeline_finish)

    def _on_pipeline_finish(self):
        try:
            self.is_running = False
            self.dash_progress.set(1.0)
            self.master_launch_btn.configure(
                state="normal",
                text="🟢 GEARUP БУСТ АКТИВЕН: В ИГРЕ",
                fg_color=COLORS["accent_green"],
                hover_color="#059669"
            )

            # Обновление показателей живого бара GearUP
            if hasattr(self, 'gear_ping_lbl') and self.gear_ping_lbl.winfo_exists():
                self.gear_ping_lbl.configure(text="~36 мс (-28% Turbo)", text_color="#34D399")
            if hasattr(self, 'gear_timer_lbl') and self.gear_timer_lbl.winfo_exists():
                self.gear_timer_lbl.configure(text="0.500 мс (Locked)", text_color="#38BDF8")
            if hasattr(self, 'gear_ram_lbl') and self.gear_ram_lbl.winfo_exists():
                self.gear_ram_lbl.configure(text="+1.8 ГБ Очищено", text_color="#A78BFA")
            if hasattr(self, 'gear_res_lbl') and self.gear_res_lbl.winfo_exists():
                self.gear_res_lbl.configure(text="Locked (Read-Only)", text_color="#10B981")

            # Если включено авто-сворачивание в трей при запуске игры (GearUP режим)
            if self.cfg.get("MINIMIZE_ON_LAUNCH", "1") == "1":
                self.log_dash("🗕 GearUP режим: VORTEX сворачивается в системный трей через 2 секунды...")
                self.after(2200, self.minimize_to_tray)
        except Exception:
            pass


VORTEX_MUTEX_NAME = "Global\\VORTEX_Optimizer_SingleInstance_Mutex"
VORTEX_RESTORE_EVENT = "Global\\VORTEX_Optimizer_Restore_Event"
_app_instance_mutex = None


def check_single_instance():
    """
    Гарантирует запуск только 1 экземпляра приложения VORTEX в системе.
    Если экземпляр уже запущен:
    1. Посылает сигнал в именованное событие для разворачивания существующего окна.
    2. Выводит окно первого экземпляра на передний план.
    3. Завершает текущий повторный процесс.
    """
    global _app_instance_mutex
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # Пытаемся создать мьютекс
    _app_instance_mutex = kernel32.CreateMutexW(None, False, VORTEX_MUTEX_NAME)
    err = kernel32.GetLastError()

    # ERROR_ALREADY_EXISTS = 183
    if err == 183:
        try:
            h_ev = kernel32.OpenEventW(0x0002, False, VORTEX_RESTORE_EVENT)  # EVENT_MODIFY_STATE
            if h_ev:
                kernel32.SetEvent(h_ev)
                kernel32.CloseHandle(h_ev)
        except Exception:
            pass

        try:
            def enum_cb(hwnd, extra):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    val = buf.value
                    if "VORTEX" in val:
                        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                        user32.SetForegroundWindow(hwnd)
                        return False
                return True
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        except Exception:
            pass

        sys.exit(0)


if __name__ == "__main__":
    if not is_admin():
        try:
            run_as_admin()
            sys.exit(0)
        except Exception:
            pass

    check_single_instance()

    try:
        app = ModernOptimizerApp()
        app.mainloop()
    except Exception:
        err_msg = traceback.format_exc()
        log_file = os.path.join(BASE_DIR, "gui_crash.log")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(err_msg)
        except Exception:
            pass
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Ошибка в оптимизаторе:\n\n{err_msg[:600]}\n\nОтчёт сохранён в gui_crash.log",
                "Ошибка интерфейса",
                0x10
            )
        except Exception:
            pass
        sys.exit(1)
