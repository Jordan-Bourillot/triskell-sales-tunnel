# -*- mode: python ; coding: utf-8 -*-
"""Spec PyInstaller — build .exe autonome.

Build :
    pyinstaller --clean triskell_sales_tunnel.spec

Le binaire final : dist/Triskell Sales Tunnel/Triskell Sales Tunnel.exe
"""

from pathlib import Path

PROJECT_ROOT = Path.cwd()

block_cipher = None

# --- Sources & assets ---------------------------------------------------------
datas = []
# customtkinter livre ses thèmes sous forme de fichiers JSON / ressources.
# PyInstaller les rate parfois — on les récupère via collect_data_files.
try:
    from PyInstaller.utils.hooks import collect_data_files  # type: ignore
    datas += collect_data_files("customtkinter")
except Exception:
    pass

# Logos produits
products_dir = PROJECT_ROOT / "triskell_sales_tunnel" / "assets" / "products"
if products_dir.exists():
    for f in products_dir.iterdir():
        if f.is_file():
            datas.append((str(f), "triskell_sales_tunnel/assets/products"))

# Icône de l'app (taskbar / titlebar runtime)
app_icon_ico = PROJECT_ROOT / "triskell_sales_tunnel" / "assets" / "triskell_icon.ico"
app_icon_png = PROJECT_ROOT / "triskell_sales_tunnel" / "assets" / "triskell_icon.png"
for f in (app_icon_ico, app_icon_png):
    if f.exists():
        datas.append((str(f), "triskell_sales_tunnel/assets"))

hiddenimports = [
    "customtkinter",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    "pyperclip",
    "reportlab",
    "reportlab.pdfgen",
    "reportlab.lib",
    "docx",
    # Modules internes
    "triskell_sales_tunnel.steps.step_product",
    "triskell_sales_tunnel.steps.step_client",
    "triskell_sales_tunnel.steps.step_channel",
    "triskell_sales_tunnel.steps.step_template",
    "triskell_sales_tunnel.steps.step_settings",
    "triskell_sales_tunnel.widgets.triskell_logo",
    "triskell_sales_tunnel.widgets.step_indicator",
    "triskell_sales_tunnel.widgets.components",
    "triskell_sales_tunnel.ai",
    "triskell_sales_tunnel.exporters",
]

a = Analysis(
    ["run.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tkinter.test", "test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Triskell Sales Tunnel",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app, pas de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(app_icon_ico) if app_icon_ico.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Triskell Sales Tunnel",
)
