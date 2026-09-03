"""
Build script to compile Albion Auto Market Seller into a standalone portable .exe
Usage: python build_exe.py
"""

import os
import shutil
import subprocess
import sys


def find_tesseract_install():
    candidates = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR"),
        r"C:\tools\tesseract",
    ]
    which_tess = shutil.which("tesseract.exe") or shutil.which("tesseract")
    if which_tess:
        candidates.insert(0, os.path.dirname(which_tess))

    for c in candidates:
        if os.path.isfile(os.path.join(c, "tesseract.exe")):
            return c
    return None


def main():
    print("=" * 60)
    print("🚀 Building Albion Auto Market Seller Standalone Executable")
    print("=" * 60)

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=pynput.mouse._win32",
        "--hidden-import=customtkinter",
        "--collect-all=customtkinter",
        "--collect-all=pytesseract",
        "--collect-all=PIL",
        "--name=AutoMarketSeller",
        "AutoSeller.py",
    ]

    tesseract_dir = find_tesseract_install()
    if tesseract_dir:
        print(f"✅ Found Tesseract at: {tesseract_dir}")
        print("📦 Bundling portable Tesseract inside the executable...")
        cmd.extend(["--add-data", f"{tesseract_dir};tesseract"])
    else:
        print("ℹ️ Tesseract not found in system paths. Executable will search system paths at runtime.")

    if os.path.isdir("templates"):
        cmd.extend(["--add-data", "templates;templates"])

    print(f"\nRunning command:\n{' '.join(cmd)}\n")
    ret = subprocess.call(cmd)

    if ret == 0:
        print("\n" + "=" * 60)
        print("🎉 BUILD SUCCESSFUL!")
        print("📁 Executable location: dist/AutoMarketSeller.exe")
        print("=" * 60)
    else:
        print("\n❌ Build failed with exit code:", ret)
        sys.exit(ret)


if __name__ == "__main__":
    main()
