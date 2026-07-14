"""
Загрузчик Scalpick для пересборки в .exe.

Оригинальное приложение — единый модуль (восстановленный байткод
``zovscalpick_main.pyc``). Он полностью рабочий, поэтому здесь мы не
переписываем логику, а просто выполняем его как главный модуль (__main__),
предварительно добавив в путь поиска соседние модули приложения
(app_i18n, mexc_proto, stock_proto).

Работает и «как есть» (python launcher.py), и внутри PyInstaller-сборки
(sys.frozen). Ассеты (svg/, sound/, locales/) само приложение ищет рядом с
exe и в папке бандла — сборочный скрипт кладёт их в оба места.
"""

from __future__ import annotations

import marshal
import os
import sys


def _resource_root() -> str:
    """Каталог, где лежат bundled-модули приложения."""
    if getattr(sys, "frozen", False):
        # PyInstaller распаковывает данные в sys._MEIPASS.
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def run() -> None:
    root = _resource_root()
    if root not in sys.path:
        sys.path.insert(0, root)

    main_pyc = os.path.join(root, "zovscalpick_main.pyc")
    with open(main_pyc, "rb") as fh:
        fh.read(16)  # пропустить 16-байтовый заголовок .pyc (magic+flags+mtime+size)
        code = marshal.loads(fh.read())

    # ВАЖНО: выполняем байткод в СОБСТВЕННЫХ globals этого модуля (__main__),
    # а не в отдельном словаре. Тогда все функции приложения попадают в
    # sys.modules['__main__'], и multiprocessing (spawn) корректно находит
    # worker-функции в дочерних процессах — как при обычном запуске скрипта.
    g = globals()
    g["__file__"] = os.path.join(root, "zovscalpick_main.py")
    exec(code, g)


if __name__ == "__main__":
    # Обязательно для frozen-сборок с multiprocessing: в дочернем процессе
    # freeze_support внутри самого приложения (блок if __name__=='__main__')
    # перехватит запуск задачи. Здесь достаточно эмулировать запуск скрипта.
    run()
