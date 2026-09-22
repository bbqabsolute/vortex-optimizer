# ⚡ VORTEX — Performance Engine & Multi-Game Launcher

[![.NET 8](https://img.shields.io/badge/.NET-8.0-512BD4?logo=dotnet)](https://dotnet.microsoft.com/)
[![WPF](https://img.shields.io/badge/UI-WPF%20Cyber-00D4FF)](#)
[![Latency](https://img.shields.io/badge/Kernel%20Timer-0.500%20ms-10B981)](#)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#)

**VORTEX** — это высокопроизводительный мультиигровой оптимизатор, лаунчер и игровой диспетчер с глубоким снижением системного инпутлага и задержек сети. Разработан на стеке **C# .NET 8 + WPF** (с поддержкой классического Python-конвейера).

---

## 📥 Скачать VORTEX v1.0.0

| Файл | Описание | Ссылка на скачивание |
| :--- | :--- | :--- |
| 🚀 **VORTEX_Setup.exe** | Автоматический установщик с созданием ярлыков | [**Скачать Setup.exe**](https://github.com/bbqabsolute/vortex-optimizer/releases/download/v1.0.0/VORTEX_Setup.exe) |
| ⚡ **VORTEX.exe** | Портативная версия (не требует установки) | [**Скачать Portable.exe**](https://github.com/bbqabsolute/vortex-optimizer/releases/download/v1.0.0/VORTEX.exe) |
| 📦 **VORTEX_v1.0.0_Portable.zip** | Полный архив (программа + иконки + ридми) | [**Скачать ZIP-архив**](https://github.com/bbqabsolute/vortex-optimizer/releases/download/v1.0.0/VORTEX_v1.0.0_Portable.zip) |

👉 Все релизы доступны на странице: [**Releases**](https://github.com/bbqabsolute/vortex-optimizer/releases)

---

## 🌟 Ключевые возможности

### ⏱️ Аппаратное снижение задержек (Input Lag)
- **Таймер ядра 0.500 мс (2000 Гц)**: фиксация через недокументированный Win32 API `NtSetTimerResolution`.
- **FilterKeys Turbo (Mongraal / Bugha)**: ускорение повтора ввода клавиш (Delay: 150 мс, Repeat: 15 мс) с автоматической активацией только во время игры и возвратом по умолчанию при выходе.
- **MMCSS & GPU Scheduling (HAGS)**: приоритет мультимедиа-планировщика Windows и потоков видеокарты.
- **Честная кривая мыши 1:1**: отключение акселерации Windows (Pointer Speed 6/11, Raw Input).

### 🌐 Сеть и DNS Радар
- **Сырой UDP-бенчмарк DNS**: измерение физической задержки до игровых серверов и DNS (Cloudflare, Google, Яндекс, OpenDNS, Quad9) в реальном времени.
- **QoS DSCP 46 & TCP NoDelay**: отключение алгоритма Нагла и приоритизация игровых пакетов на уровне драйвера NDIS.

### 🎮 Мультиигровая поддержка & Лаунчер
- Авто-обнаружение установленных игр (Fortnite, CS2 и др.).
- Drag & Drop ярлыков (`.lnk`, `.url`, `.exe`) прямо в окно VORTEX.
- Индивидуальные фоны и названия для каждой добавленной игры.
- Создание ярлыков на Рабочем столе с автоматической цепочкой оптимизации и выводом логов в отдельную консоль.

### 🛡️ 10-Слойный конвейер безопасного запуска
1. Фиксация таймера ядра `0.500 мс`.
2. Ultimate Performance план электропитания.
3. GPU Priority & MMCSS High.
4. CPU Core Unparking (100% активных ядер).
5. 1:1 Raw Mouse Curve.
6. Отключение GameDVR и Xbox Bar.
7. Сетевой стек QoS DSCP 46 + TCP NoDelay.
8. Оптимизация `Engine.ini` / конфигов игры.
9. Сброс рабочих наборов и очистка кэша Standby List RAM.
10. Деэлевация прав (`explorer.exe`) для безопасного запуска без конфликтов с античитами EasyAntiCheat / BattlEye.

---

## 🛠️ Сборка проекта

### Требования:
* Windows 10 / 11 (x64)
* [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)

### Сборка C# (.NET 8):
```bash
# Сборка основного приложения
dotnet publish vortex_net8/VortexNet8.csproj -c Release -r win-x64 --self-contained false -p:PublishSingleFile=true -o publish/

# Сборка установщика
dotnet publish vortex_setup/VortexSetup.csproj -c Release -r win-x64 --self-contained false -p:PublishSingleFile=true -o setup_publish/
```

---

## 📄 Лицензия
Распространяется под лицензией MIT. Подробности в файле LICENSE.
