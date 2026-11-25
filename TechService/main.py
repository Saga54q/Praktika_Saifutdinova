"""Точка входа в приложение Техсервис."""

from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# Обеспечивает корректные импорты при запуске файла напрямую.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.initialization import initialize_database  # noqa: E402
from modules.requests.service import RequestService  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


def main() -> None:
    """Инициализирует базу данных и запускает главное окно приложения."""
    initialize_database()

    root = tk.Tk()
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:
        pass

    service = RequestService()
    MainWindow(root, service)
    root.mainloop()


if __name__ == "__main__":
    main()
