"""
================================================================================
  VORTEX v5.0 - MASTER BUILD SYSTEM
  Сборка VORTEX.exe, uninstaller и автономного установщика VORTEX_Setup.exe
================================================================================
"""

import os
import sys
import shutil
import zipfile
import subprocess
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable

def log(msg):
    clean = str(msg).encode('ascii', errors='replace').decode('ascii')
    print(f"\n{'='*70}\n  {msg}\n{'='*70}", flush=True)

def main():
    start_time = time.time()
    log("[START] SBORKA VORTEX 5.0")

    dist_dir = os.path.join(BASE_DIR, "dist")
    build_dir = os.path.join(BASE_DIR, "build")
    vortex_app_dir = os.path.join(dist_dir, "VORTEX")
    payload_zip = os.path.join(BASE_DIR, "app_payload.zip")
    ico_path = os.path.join(BASE_DIR, "assets", "icons", "vortex_logo.ico")

    os.makedirs(dist_dir, exist_ok=True)

    # Step 1 & 2: Build VORTEX application (onedir)
    app_exe = os.path.join(vortex_app_dir, "VORTEX.exe")
    log("[1/5] Kompilyaciya VORTEX.exe (yadra i GUI s pystray tray support)...")
    cmd_app = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--uac-admin",
        "--name=VORTEX",
        f"--icon={ico_path}",
        "--collect-all=customtkinter",
        "--collect-all=pystray",
        "--add-data=assets;assets",
        "--add-data=core;core",
        "--add-data=config;config",
        "gui.py"
    ]
    subprocess.run(cmd_app, cwd=BASE_DIR, check=True)

    # Ensure assets, core, config are also placed in root of dist/VORTEX
    for d in ["assets", "core", "config"]:
        src = os.path.join(BASE_DIR, d)
        dst = os.path.join(vortex_app_dir, d)
        if os.path.exists(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)

    log("[OK] VORTEX.exe i resursy gotovy v dist/VORTEX/")

    # Step 3: Build uninstall.exe into dist/VORTEX
    uninst_exe = os.path.join(vortex_app_dir, "uninstall.exe")
    if not os.path.exists(uninst_exe):
        log("[2/5] Kompilyaciya uninstall.exe (deinstallyator)...")
        cmd_uninst = [
            PYTHON_EXE, "-m", "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--uac-admin",
            "--name=uninstall",
            f"--icon={ico_path}",
            "--collect-all=customtkinter",
            f"--distpath={vortex_app_dir}",
            "uninstall.py"
        ]
        subprocess.run(cmd_uninst, cwd=BASE_DIR, check=True)
        log("[OK] uninstall.exe uspeshno sozdan v dist/VORTEX/")
    else:
        log("[2/5] uninstall.exe uzhe sozdan v dist/VORTEX/")

    # Step 4: Zip dist/VORTEX into app_payload.zip
    log("[3/5] Arhivaciya dist/VORTEX v app_payload.zip...")
    if os.path.exists(payload_zip):
        os.remove(payload_zip)

    with zipfile.ZipFile(payload_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(vortex_app_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, vortex_app_dir)
                zf.write(abs_path, rel_path)

    zip_size_mb = os.path.getsize(payload_zip) / (1024 * 1024)
    log(f"[OK] app_payload.zip sozdan ({zip_size_mb:.2f} MB)")

    # Step 5: Build VORTEX_Setup.exe
    log("[4/5] Kompilyaciya VORTEX_Setup.exe (avtonomnyj ustanovshchik)...")
    cmd_installer = [
        PYTHON_EXE, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--uac-admin",
        "--name=VORTEX_Setup",
        f"--icon={ico_path}",
        "--collect-all=customtkinter",
        f"--add-data={payload_zip};.",
        "--add-data=assets;assets",
        f"--distpath={dist_dir}",
        "installer_gui.py"
    ]
    subprocess.run(cmd_installer, cwd=BASE_DIR, check=True)
    log("[OK] VORTEX_Setup.exe uspeshno skompilirovan!")

    # Clean up payload zip
    if os.path.exists(payload_zip):
        os.remove(payload_zip)

    installer_path = os.path.join(dist_dir, "VORTEX_Setup.exe")
    desktop_installer = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "VORTEX_Setup.exe")
    if os.path.exists(installer_path):
        try:
            shutil.copy2(installer_path, desktop_installer)
            log(f"[OK] Ustanovshchik skopirovan na Rabochij stol: {desktop_installer}")
        except Exception as e:
            log(f"[WARN] Ne udalos skopirovat na desktop: {e}")

    elapsed = time.time() - start_time
    installer_size_mb = os.path.getsize(installer_path) / (1024 * 1024) if os.path.exists(installer_path) else 0

    log(f"""
[DONE] SBORKA POLNOSTYU ZAVERSHENA ZA {elapsed:.1f} SEK!

Itogi sborki:
1. Prilozhenie: {os.path.join(vortex_app_dir, 'VORTEX.exe')}
2. Deinstallyator: {os.path.join(vortex_app_dir, 'uninstall.exe')}
3. Ustanovshchik: {installer_path} ({installer_size_mb:.2f} MB)
4. Kopiya na Rabochem stole: {desktop_installer}
    """)

if __name__ == "__main__":
    main()
