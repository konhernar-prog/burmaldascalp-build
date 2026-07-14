# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller-спека для сборки ZoVscalpick под macOS.

ВАЖНО: PyInstaller не кросс-компилирует — этот файл собирается ТОЛЬКО на macOS
(локально на маке или на macos-раннере GitHub Actions).

Отличия от ZoVscalpick.spec (Windows):
  * убраны Windows-only hiddenimports (winsound, win32api/win32event/win32evtlog);
  * нет .ico-иконки (у macOS свой формат .icns — добавим позже);
  * результат оборачивается в .app-бандл (BUNDLE).

Собрать:  pyinstaller ZoVscalpick-mac.spec --noconfirm
Результат: dist/ZoVscalpick.app
"""

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

HERE = os.path.abspath(os.path.dirname(SPEC))
APP = os.path.join(HERE, "app")
ASSETS = os.path.join(HERE, "assets")

datas = [
    (os.path.join(APP, "zovscalpick_main.pyc"), "."),
    (os.path.join(APP, "app_i18n.pyc"), "."),
    (os.path.join(APP, "mexc_proto"), "mexc_proto"),
    (os.path.join(APP, "stock_proto"), "stock_proto"),
    (os.path.join(ASSETS, "svg"), "svg"),
    (os.path.join(ASSETS, "sound"), "sound"),
    (os.path.join(ASSETS, "locales"), "locales"),
]
binaries = []

# Только кроссплатформенные stdlib-подмодули (без winsound / pywin32).
hiddenimports = [
    "zoneinfo",
    "google.protobuf",
    "logging.handlers",
    "concurrent.futures",
    "urllib.parse", "urllib.request", "urllib.error",
    "asyncio", "queue", "gzip", "hashlib", "uuid", "weakref",
    "atexit", "signal", "socket", "struct", "subprocess",
    "platform", "traceback", "gc", "math", "random", "datetime",
    "mexc_proto", "mexc_proto.simple_protobuf_decoder", "stock_proto",
]
hiddenimports += collect_submodules("multiprocessing")

for pkg in [
    "PyQt6", "aiohttp", "websockets", "websocket", "orjson", "psutil",
    "requests", "google.protobuf", "tzdata", "brotli", "certifi",
    "charset_normalizer", "multidict", "yarl", "frozenlist", "propcache",
    "aiosignal", "attr", "idna",
]:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as exc:
        print(f"[spec] collect_all({pkg!r}) пропущен: {exc}")

a = Analysis(
    ["launcher.py"],
    pathex=[HERE, APP],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ZoVscalpick",
    console=False,               # оконное приложение
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="ZoVscalpick",
)

app = BUNDLE(
    coll,
    name="ZoVscalpick.app",
    icon=None,                   # .icns добавим позже
    bundle_identifier="com.zovscalpick.app",
)
