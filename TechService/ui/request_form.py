"""Форма создания и редактирования заявки."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from modules.requests.models import CATEGORIES, PRIORITIES, STATUSES, ServiceRequest
from modules.requests.service import RequestService, ValidationError
from ui.styles import FONT_HEADER, FONT_LABEL, FONT_MAIN, PADDING


class RequestFormWindow(tk.Toplevel):
    """Окно формы для создания или редактирования заявки."""

    def __init__(self, parent: tk.Tk, service: RequestService, on_saved, request: ServiceRequest | None = None):
        super().__init__(parent)
        self.service = service
        self.on_saved = on_saved
        self.request = request
        self.is_edit = request is not None

        self.title("Редактирование заявки" if self.is_edit else "Новая заявка")
        self.geometry("760x640")
        self.transient(parent)
        self.grab_set()

        self.container = ttk.Frame(self, padding=PADDING)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.columnconfigure(1, weight=1)

        title = f"Редактирование заявки №{request.id}" if self.is_edit else "Регистрация новой заявки"
        ttk.Label(self.container, text=title, font=FONT_HEADER).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.customer_var = tk.StringVar(value=request.customer if request else "")
        self.equipment_var = tk.StringVar(value=request.equipment_type if request else "")
        self.category_var = tk.StringVar(value=request.category if request else CATEGORIES[0])
        self.priority_var = tk.StringVar(value=request.priority if request else PRIORITIES[1])
        self.status_var = tk.StringVar(value=request.status if request else STATUSES[0])

        self._build_field("Заказчик / подразделение *", 1, ttk.Entry(self.container, textvariable=self.customer_var))
        self._build_field("Тип оборудования *", 2, ttk.Entry(self.container, textvariable=self.equipment_var))
        self._build_field(
            "Категория обращения *",
            3,
            ttk.Combobox(self.container, textvariable=self.category_var, values=CATEGORIES, state="readonly"),
        )
        self._build_field(
            "Приоритет *",
            4,
            ttk.Combobox(self.container, textvariable=self.priority_var, values=PRIORITIES, state="readonly"),
        )
        self._build_field(
            "Статус *",
            5,
            ttk.Combobox(self.container, textvariable=self.status_var, values=STATUSES, state="readonly"),
        )

        ttk.Label(self.container, text="Описание неисправности *", font=FONT_LABEL).grid(row=6, column=0, sticky="nw", pady=6)
        self.description_text = tk.Text(self.container, height=7, wrap="word", font=FONT_MAIN)
        self.description_text.grid(row=6, column=1, sticky="ew", pady=6)
        if request:
            self.description_text.insert("1.0", request.description)

        ttk.Label(self.container, text="Описание выполненных работ", font=FONT_LABEL).grid(row=7, column=0, sticky="nw", pady=6)
        self.work_text = tk.Text(self.container, height=7, wrap="word", font=FONT_MAIN)
        self.work_text.grid(row=7, column=1, sticky="ew", pady=6)
        if request and request.work_description:
            self.work_text.insert("1.0", request.work_description)

        button_frame = ttk.Frame(self.container)
        button_frame.grid(row=8, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT)

    def _build_field(self, label: str, row: int, widget: tk.Widget) -> None:
        ttk.Label(self.container, text=label, font=FONT_LABEL).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 10))
        widget.grid(row=row, column=1, sticky="ew", pady=6)

    def _collect_data(self) -> dict:
        return {
            "customer": self.customer_var.get(),
            "equipment_type": self.equipment_var.get(),
            "category": self.category_var.get(),
            "description": self.description_text.get("1.0", "end-1c"),
            "priority": self.priority_var.get(),
            "status": self.status_var.get(),
            "work_description": self.work_text.get("1.0", "end-1c"),
        }

    def save(self) -> None:
        data = self._collect_data()
        try:
            if self.is_edit and self.request and self.request.id is not None:
                self.service.update_request(self.request.id, data)
                messagebox.showinfo("Успешно", "Заявка обновлена.", parent=self)
            else:
                self.service.create_request(data)
                messagebox.showinfo("Успешно", "Заявка создана.", parent=self)
            self.on_saved()
            self.destroy()
        except ValidationError as error:
            messagebox.showerror("Ошибка валидации", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заявку: {error}", parent=self)
