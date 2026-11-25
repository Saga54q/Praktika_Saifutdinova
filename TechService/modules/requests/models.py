"""Модели и константы модуля заявок на техническое обслуживание."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


CATEGORIES = [
    "неисправность оборудования",
    "установка программного обеспечения",
    "обновление программного обеспечения",
    "настройка программного обеспечения",
    "диагностика",
    "прочее",
]

STATUSES = [
    "новая",
    "в работе",
    "выполнена",
    "отменена",
]

PRIORITIES = [
    "низкий",
    "средний",
    "высокий",
    "критический",
]

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class ServiceRequest:
    """Модель заявки на техническое обслуживание."""

    id: int | None
    created_at: str
    customer: str
    equipment_type: str
    category: str
    description: str
    priority: str
    status: str
    work_description: str = ""

    @classmethod
    def create_new(
        cls,
        customer: str,
        equipment_type: str,
        category: str,
        description: str,
        priority: str,
        status: str = "новая",
        work_description: str = "",
        created_at: str | None = None,
    ) -> "ServiceRequest":
        """Создаёт новую заявку с текущей датой регистрации."""
        return cls(
            id=None,
            created_at=created_at or datetime.now().strftime(DATE_FORMAT),
            customer=customer.strip(),
            equipment_type=equipment_type.strip(),
            category=category.strip(),
            description=description.strip(),
            priority=priority.strip(),
            status=status.strip(),
            work_description=work_description.strip(),
        )

    @classmethod
    def from_row(cls, row) -> "ServiceRequest":
        """Преобразует строку SQLite в модель заявки."""
        return cls(
            id=row["id"],
            created_at=row["created_at"],
            customer=row["customer"],
            equipment_type=row["equipment_type"],
            category=row["category"],
            description=row["description"],
            priority=row["priority"],
            status=row["status"],
            work_description=row["work_description"] or "",
        )

    def to_dict(self) -> dict:
        """Возвращает словарь с данными заявки."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "customer": self.customer,
            "equipment_type": self.equipment_type,
            "category": self.category,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "work_description": self.work_description,
        }
