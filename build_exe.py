"""Build de l'exécutable Windows via PyInstaller.

Usage :
    python build_exe.py

Génère :
    dist/Triskell Sales Tunnel/Triskell Sales Tunnel.exe

DECISION: build "onedir" (dossier) plutôt que "onefile". Démarrage 2-3× plus
rapide, debug plus facile, antivirus moins paranos.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
SPEC_FILE = PROJECT_ROOT / "triskell_sales_tunnel.spec"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller absent — installation…")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller>=6.0"]
        )


def clean_previous_build() -> None:
    for d in (DIST_DIR, BUILD_DIR):
        if d.exists():
            print(f"Nettoyage {d.name}/")
            shutil.rmtree(d, ignore_errors=True)


def run_pyinstaller() -> int:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        str(SPEC_FILE),
    ]
    print(">>", " ".join(cmd))
    return subprocess.call(cmd, cwd=PROJECT_ROOT)


def main() -> int:
    if not SPEC_FILE.exists():
        print(f"[ERR] Spec introuvable : {SPEC_FILE}")
        return 1

    ensure_pyinstaller()
    clean_previous_build()

    rc = run_pyinstaller()
    if rc != 0:
        print(f"[ERR] Build echoue (code {rc})")
        return rc

    target = DIST_DIR / "Triskell Sales Tunnel" / "Triskell Sales Tunnel.exe"
    if target.exists():
        size_mb = target.stat().st_size / (1024 * 1024)
        print()
        print(f"[OK] Build OK -- {target}")
        print(f"     Taille .exe : {size_mb:.1f} MB")
        print(f"     Dossier complet : {target.parent}")
        return 0

    print("[!!] Build termine mais binaire introuvable, verifie dist/.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
