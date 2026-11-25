"""Главное окно приложения учёта заявок."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from modules.requests.models import CATEGORIES, STATUSES
from modules.requests.service import RequestService, ValidationError
from ui.request_details import RequestDetailsWindow
from ui.request_form import RequestFormWindow
from ui.styles import APP_SIZE, APP_TITLE, FONT_HEADER, FONT_MAIN, PADDING, TABLE_HEIGHT


class MainWindow:
    """Главное окно модуля регистрации и учёта заявок."""

    def __init__(self, root: tk.Tk, service: RequestService):
        self.root = root
        self.service = service
        self.root.title(APP_TITLE)
        self.root.geometry(APP_SIZE)
        self.root.minsize(1100, 650)

        self.search_var = tk.StringVar()
        self.category_filter_var = tk.StringVar(value="Все")
        self.status_filter_var = tk.StringVar(value="Все")
        self.status_change_var = tk.StringVar(value=STATUSES[0])

        self._build_ui()
        self.refresh_requests()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=PADDING)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(container, text="Регистрация и учёт заявок на техническое обслуживание", font=FONT_HEADER)
        header.pack(anchor="w", pady=(0, 10))

        controls = ttk.Frame(container)
        controls.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(controls, text="Поиск:", font=FONT_MAIN).pack(side=tk.LEFT)
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=35)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda _event: self.refresh_requests())

        ttk.Button(controls, text="Найти", command=self.refresh_requests).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="Сбросить", command=self.reset_filters).pack(side=tk.LEFT, padx=2)

        ttk.Label(controls, text="Категория:", font=FONT_MAIN).pack(side=tk.LEFT, padx=(15, 2))
        category_combo = ttk.Combobox(
            controls,
            textvariable=self.category_filter_var,
            values=["Все"] + CATEGORIES,
            state="readonly",
            width=32,
        )
        category_combo.pack(side=tk.LEFT, padx=2)
        category_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_requests())

        ttk.Label(controls, text="Статус:", font=FONT_MAIN).pack(side=tk.LEFT, padx=(10, 2))
        status_combo = ttk.Combobox(
            controls,
            textvariable=self.status_filter_var,
            values=["Все"] + STATUSES,
            state="readonly",
            width=15,
        )
        status_combo.pack(side=tk.LEFT, padx=2)
        status_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_requests())

        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "created_at", "customer", "equipment_type", "category", "priority", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=TABLE_HEIGHT)
        headings = {
            "id": ("№", 60),
            "created_at": ("Дата регистрации", 150),
            "customer": ("Заказчик / подразделение", 220),
            "equipment_type": ("Тип оборудования", 180),
            "category": ("Категория", 260),
            "priority": ("Приоритет", 110),
            "status": ("Статус", 110),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")

        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", lambda _event: self.open_details())

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(actions, text="Создать", command=self.create_request).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Редактировать", command=self.edit_request).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Удалить", command=self.delete_request).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Подробнее", command=self.open_details).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Обновить", command=self.refresh_requests).pack(side=tk.LEFT, padx=2)

        ttk.Label(actions, text="Новый статус:", font=FONT_MAIN).pack(side=tk.LEFT, padx=(20, 4))
        ttk.Combobox(actions, textvariable=self.status_change_var, values=STATUSES, state="readonly", width=15).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(actions, text="Изменить статус", command=self.change_status).pack(side=tk.LEFT, padx=2)

        self.status_label = ttk.Label(container, text="Заявок: 0", font=FONT_MAIN)
        self.status_label.pack(anchor="w", pady=(8, 0))

    def refresh_requests(self) -> None:
        try:
            requests = self.service.filter_requests(
                category=self.category_filter_var.get(),
                status=self.status_filter_var.get(),
                query=self.search_var.get(),
            )
        except ValidationError as error:
            messagebox.showerror("Ошибка фильтрации", str(error), parent=self.root)
            return
        except Exception as error:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заявки: {error}", parent=self.root)
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        for request in requests:
            self.tree.insert(
                "",
                tk.END,
                iid=str(request.id),
                values=(
                    request.id,
                    request.created_at,
                    request.customer,
                    request.equipment_type,
                    request.category,
                    request.priority,
                    request.status,
                ),
            )
        self.status_label.configure(text=f"Заявок: {len(requests)}")

    def reset_filters(self) -> None:
        self.search_var.set("")
        self.category_filter_var.set("Все")
        self.status_filter_var.set("Все")
        self.refresh_requests()

    def get_selected_request_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор заявки", "Выберите заявку в таблице.", parent=self.root)
            return None
        return int(selected[0])

    def create_request(self) -> None:
        RequestFormWindow(self.root, self.service, on_saved=self.refresh_requests)

    def edit_request(self) -> None:
        request_id = self.get_selected_request_id()
        if request_id is None:
            return
        request = self.service.get_request(request_id)
        if request is None:
            messagebox.showerror("Ошибка", "Заявка не найдена.", parent=self.root)
            self.refresh_requests()
            return
        RequestFormWindow(self.root, self.service, on_saved=self.refresh_requests, request=request)

    def delete_request(self) -> None:
        request_id = self.get_selected_request_id()
        if request_id is None:
            return
        request = self.service.get_request(request_id)
        if request is None:
            messagebox.showerror("Ошибка", "Заявка не найдена.", parent=self.root)
            self.refresh_requests()
            return
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить заявку №{request.id} от {request.created_at}?",
            parent=self.root,
        )
        if not confirm:
            return
        try:
            self.service.delete_request(request_id)
            self.refresh_requests()
            messagebox.showinfo("Успешно", "Заявка удалена.", parent=self.root)
        except Exception as error:
            messagebox.showerror("Ошибка", f"Не удалось удалить заявку: {error}", parent=self.root)

    def open_details(self) -> None:
        request_id = self.get_selected_request_id()
        if request_id is None:
            return
        request = self.service.get_request(request_id)
        if request is None:
            messagebox.showerror("Ошибка", "Заявка не найдена.", parent=self.root)
            self.refresh_requests()
            return
        RequestDetailsWindow(self.root, request)

    def change_status(self) -> None:
        request_id = self.get_selected_request_id()
        if request_id is None:
            return
        new_status = self.status_change_var.get()
        try:
            self.service.change_status(request_id, new_status)
            self.refresh_requests()
            messagebox.showinfo("Успешно", f"Статус заявки №{request_id} изменён на «{new_status}».", parent=self.root)
        except Exception as error:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {error}", parent=self.root)
