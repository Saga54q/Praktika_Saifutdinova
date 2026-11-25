"""Окно просмотра подробной информации о заявке."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from modules.requests.models import ServiceRequest
from ui.styles import FONT_HEADER, FONT_LABEL, FONT_MAIN, PADDING


class RequestDetailsWindow(tk.Toplevel):
    """Отображает подробные сведения о выбранной заявке."""

    def __init__(self, parent: tk.Tk, request: ServiceRequest):
        super().__init__(parent)
        self.title(f"Заявка №{request.id}")
        self.geometry("700x520")
        self.transient(parent)
        self.grab_set()

        container = ttk.Frame(self, padding=PADDING)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text=f"Заявка №{request.id}", font=FONT_HEADER).pack(anchor="w", pady=(0, 10))

        details = [
            ("Дата регистрации", request.created_at),
            ("Заказчик / подразделение", request.customer),
            ("Тип оборудования", request.equipment_type),
            ("Категория обращения", request.category),
            ("Приоритет", request.priority),
            ("Текущий статус", request.status),
        ]

        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.X)
        info_frame.columnconfigure(1, weight=1)

        for row, (label, value) in enumerate(details):
            ttk.Label(info_frame, text=f"{label}:", font=FONT_LABEL).grid(
                row=row, column=0, sticky="nw", padx=(0, 10), pady=4
            )
            ttk.Label(info_frame, text=value, font=FONT_MAIN, wraplength=460).grid(
                row=row, column=1, sticky="nw", pady=4
            )

        ttk.Label(container, text="Описание неисправности:", font=FONT_LABEL).pack(anchor="w", pady=(12, 4))
        desc_text = tk.Text(container, height=7, wrap="word", font=FONT_MAIN)
        desc_text.pack(fill=tk.BOTH, expand=True)
        desc_text.insert("1.0", request.description)
        desc_text.configure(state="disabled")

        ttk.Label(container, text="Описание выполненных работ:", font=FONT_LABEL).pack(anchor="w", pady=(12, 4))
        work_text = tk.Text(container, height=7, wrap="word", font=FONT_MAIN)
        work_text.pack(fill=tk.BOTH, expand=True)
        work_text.insert("1.0", request.work_description or "—")
        work_text.configure(state="disabled")

        ttk.Button(container, text="Закрыть", command=self.destroy).pack(anchor="e", pady=(10, 0))
