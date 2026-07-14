# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller-спека для пересборки ZoVscalpick в .exe из восстановленного байткода.

Собрать:  pyinstaller ZoVscalpick.spec --noconfirm
Результат: dist/ZoVscalpick/ZoVscalpick.exe (+ папка _internal и ассеты рядом).

Логика приложения — в app/zovscalpick_main.pyc (полный оригинальный функционал);
launcher.py лишь выполняет его как __main__.
"""

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

HERE = os.path.abspath(os.path.dirname(SPEC))
APP = os.path.join(HERE, "app")
ASSETS = os.path.join(HERE, "assets")

# --- Собственные модули приложения и ассеты (кладём в корень бандла) --------
datas = [
    (os.path.join(APP, "zovscalpick_main.pyc"), "."),
    (os.path.join(APP, "app_i18n.pyc"), "."),
    (os.path.join(APP, "mexc_proto"), "mexc_proto"),
    (os.path.join(APP, "stock_proto"), "stock_proto"),
    # Ассеты — и в бандл, и (после сборки) рядом с exe (см. postbuild-копирование).
    (os.path.join(ASSETS, "svg"), "svg"),
    (os.path.join(ASSETS, "sound"), "sound"),
    (os.path.join(ASSETS, "locales"), "locales"),
]
binaries = []
# Stdlib-подмодули, которые импортирует приложение (скрыты внутри байткода,
# поэтому анализатор их не находит). Список восстановлен из анализа импортов.
hiddenimports = [
    "winsound", "zoneinfo",
    "win32api", "win32event", "win32evtlog",
    "google.protobuf",
    "logging.handlers",
    "concurrent.futures",
    "urllib.parse", "urllib.request", "urllib.error",
    "asyncio", "queue", "gzip", "hashlib", "uuid", "weakref",
    "atexit", "signal", "socket", "struct", "subprocess",
    "platform", "traceback", "gc", "math", "random", "datetime",
    "mexc_proto", "mexc_proto.simple_protobuf_decoder", "stock_proto",
]
# multiprocessing тянет платформенные подмодули — берём целиком.
hiddenimports += collect_submodules("multiprocessing")

# --- Полная сборка сторонних пакетов (данные, бинарники, подмодули) ---------
# Импорты внутри .pyc не видны анализатору, поэтому подтягиваем пакеты явно.
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
    except Exception as exc:  # пакет может отсутствовать — пропускаем
        print(f"[spec] collect_all({pkg!r}) пропущен: {exc}")

block_cipher = None

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
    console=False,           # GUI-приложение, без консольного окна
    icon=os.path.join(ASSETS, "svg", "icon.ico"),
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="ZoVscalpick",
)
