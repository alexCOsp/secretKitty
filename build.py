"""build.py — Package secretKitty into a single Windows .exe using PyInstaller.

HOW TO RUN:
    1. Make sure you are in the project root (where this file lives).
    2. Install build dependencies once:
           pip install pyinstaller pillow
    3. Run the build:
           python build.py
    4. Find your .exe inside:   dist/secretKitty.exe

WHAT THIS SCRIPT DOES (step by step):
    1. Checks that PyInstaller is installed.
    2. Converts assets/secret_kitty_icon.png → assets/secret_kitty_icon.ico
       (Windows .exe files require .ico format, not .png).
    3. Calls PyInstaller with all the right flags to produce one .exe.
    4. Reports success or failure with a clear message.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURATION — edit these when the project grows
# ---------------------------------------------------------------------------

# The Python file that starts your app.
# ⚠️  main.py is currently a CLI stub (just prints to terminal).
#     When you wire up the real GUI through main.py, change IS_GUI to True.
ENTRY_POINT: str = "main.py"

# The name that appears on the .exe file (no spaces, no .exe extension).
APP_NAME: str = "secretKitty"

# Set to True when your entry point opens a GUI window.
# True  → hides the black console window (correct for GUI apps).
# False → keeps the console visible (correct for CLI apps).
IS_GUI: bool = True

# Folders / files that must travel with the .exe at runtime.
# Format: list of ("source_path", "dest_folder_inside_exe") tuples.
# The assets folder holds the cat icon and SVG used by the GUI.
DATA_FILES: list[tuple[str, str]] = [
    ("assets", "assets"),  # bundles the whole assets/ folder
]

# Icon paths.
ICON_PNG: Path = Path("assets/secret_kitty_icon.png")
ICON_ICO: Path = Path("assets/secret_kitty_icon.ico")  # auto-generated

# ---------------------------------------------------------------------------
# STEP 1 — Check that PyInstaller is available
# ---------------------------------------------------------------------------


def check_pyinstaller() -> None:
    """Abort early with a helpful message if PyInstaller is not installed."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("[✗] PyInstaller is not installed.")
        print("    Fix: pip install pyinstaller")
        sys.exit(1)
    print("[✓] PyInstaller found.")


# ---------------------------------------------------------------------------
# STEP 2 — Convert PNG icon → ICO
# ---------------------------------------------------------------------------


def convert_icon() -> list[str]:
    """Convert assets/secret_kitty_icon.png to .ico and return the CLI flag.

    PyInstaller only accepts .ico on Windows.
    We use Pillow to convert from .png on the fly.

    Returns:
        A list containing ["--icon", "path/to/icon.ico"] if conversion
        succeeded, or an empty list if it failed (build continues without icon).
    """
    if not ICON_PNG.exists():
        print(f"[!] Icon not found at {ICON_PNG} — skipping custom icon.")
        return []

    try:
        from PIL import Image  # Pillow must be installed
    except ImportError:
        print("[!] Pillow is not installed — cannot convert .png to .ico.")
        print("    Fix: pip install pillow")
        print("    Continuing without a custom icon...")
        return []

    try:
        img = Image.open(ICON_PNG).convert("RGBA")

        # Windows expects multiple icon sizes inside one .ico file.
        # These are the standard sizes shown in Explorer, taskbar, and ALT+TAB.
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ICON_ICO, format="ICO", sizes=sizes)

        print(f"[✓] Icon converted: {ICON_PNG} → {ICON_ICO}")
        return ["--icon", str(ICON_ICO)]

    except Exception as exc:
        print(f"[!] Icon conversion failed: {exc}")
        print("    Continuing without a custom icon...")
        return []


# ---------------------------------------------------------------------------
# STEP 3 — Assemble and run the PyInstaller command
# ---------------------------------------------------------------------------


def build(icon_flags: list[str]) -> None:
    """Run PyInstaller to produce dist/secretKitty.exe.

    Key PyInstaller flags explained:
        --onefile          Pack Python + all dependencies into ONE .exe.
                           Easier to share, but slightly slower on first launch
                           because it unpacks to a temp folder each time.

        --windowed         Hide the black console window that Windows normally
                           shows for Python programs. Only use for GUI apps.
                           (disabled here because main.py is still a CLI stub)

        --name             The filename for the .exe (without extension).

        --add-data         Bundle extra files / folders into the .exe.
                           Windows syntax: "source;dest"
                           On launch, PyInstaller unpacks them to a temp folder.
                           Your code must use sys._MEIPASS to find them at
                           runtime (see note in README).

        --hidden-import    PyInstaller sometimes misses modules that are loaded
                           dynamically (e.g., cryptography backends).
                           We list the most common ones here to be safe.

        --collect-all      Collect ALL data files and sub-packages for a
                           given package. Needed for PySide6 because it ships
                           dozens of C extension plugins and Qt DLLs that
                           PyInstaller won't discover automatically.
    """
    # Build the --add-data flags (one flag pair per data entry).
    # Windows uses semicolon as separator: "src;dest"
    add_data_flags: list[str] = []
    for src, dest in DATA_FILES:
        add_data_flags += ["--add-data", f"{src};{dest}"]

    # --windowed hides the terminal; only correct for GUI apps.
    windowed_flags: list[str] = ["--windowed"] if IS_GUI else []

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        # --- Output mode ---
        "--onefile",  # single .exe file
        # --- GUI / console ---
        *windowed_flags,  # empty list = keep console (CLI mode)
        # --- Naming ---
        "--name",
        APP_NAME,
        # --- Bundle extra files ---
        *add_data_flags,
        # --- Hidden imports (cryptography internals PyInstaller may miss) ---
        "--hidden-import",
        "cryptography",
        "--hidden-import",
        "cryptography.hazmat.primitives.kdf.pbkdf2",
        "--hidden-import",
        "cryptography.hazmat.backends",
        "--hidden-import",
        "cryptography.hazmat.backends.openssl",
        "--hidden-import",
        "cryptography.fernet",
        # --- PySide6: collect all Qt plugins, translations, and DLLs ---
        # This makes the build larger (~60-100 MB) but ensures the GUI works.
        # If you are NOT using PySide6 yet, you can comment this line out.
        "--collect-all",
        "PySide6",
        # --- Icon ---
        *icon_flags,
        # --- Entry point ---
        ENTRY_POINT,
    ]

    print("\n[*] Running PyInstaller with the following command:")
    print("    " + " ".join(cmd))
    print("\n    This may take 1-3 minutes on the first run...\n")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        exe_path = Path("dist") / f"{APP_NAME}.exe"
        print("\n" + "=" * 60)
        print("[✓] BUILD SUCCEEDED")
        print(f"    Your .exe is at: {exe_path.resolve()}")
        print("=" * 60)
        print("\nShare ONLY the .exe file — users do not need Python installed.")
    else:
        print("\n" + "=" * 60)
        print(f"[✗] BUILD FAILED (exit code {result.returncode})")
        print("=" * 60)
        print("\nCommon fixes:")
        print("  • Run:  pip install pyinstaller pillow")
        print("  • Make sure you are in the project root folder.")
        print("  • Check the error above for missing modules.")
        sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("  secretKitty — Windows .exe build script")
    print("=" * 60 + "\n")

    check_pyinstaller()  # Step 1: verify PyInstaller exists
    icon_flags = convert_icon()  # Step 2: PNG → ICO conversion
    build(icon_flags)  # Step 3: run PyInstaller


if __name__ == "__main__":
    main()
