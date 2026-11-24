"""
Automated PyInstaller Build Script for Nexus Wheel.
Packages NEXUS WHEEL into a standalone Windows 11 executable.
"""

import os
import sys
import subprocess
import shutil

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "main.py")
    icon_path = os.path.join(base_dir, "assets", "app_icon.ico")
    assets_dir = os.path.join(base_dir, "assets")

    print("==================================================")
    print("  BUILDING NEXUS WHEEL FOR WINDOWS 11")
    print("==================================================")

    # Clean previous build artifacts
    for folder in ["build", "dist"]:
        p = os.path.join(base_dir, folder)
        if os.path.exists(p):
            print(f"Cleaning {folder}/...")
            shutil.rmtree(p, ignore_errors=True)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=NexusWheel",
        "--noconsole",
        "--onefile",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};assets",
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=pynput.mouse._win32",
        "--hidden-import=win32gui",
        "--hidden-import=win32con",
        "--hidden-import=win32api",
        "--hidden-import=win32process",
        "--hidden-import=database.schema",
        "--hidden-import=database.db",
        "--clean",
        main_script
    ]

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=base_dir)
    if result.returncode == 0:
        exe_path = os.path.join(base_dir, "dist", "NexusWheel.exe")
        print()
        print("==================================================")
        print("  BUILD SUCCESSFUL!")
        print(f"  Executable created at: {exe_path}")
        print("==================================================")
    else:
        print()
        print("PyInstaller build failed with return code:", result.returncode)

if __name__ == "__main__":
    build()
