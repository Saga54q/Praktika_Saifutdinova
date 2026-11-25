"""Бизнес-логика модуля заявок."""

from __future__ import annotations

from pathlib import Path

from modules.requests.models import CATEGORIES, PRIORITIES, STATUSES, ServiceRequest
from modules.requests.repository import RequestRepository


class ValidationError(ValueError):
    """Ошибка валидации пользовательских данных."""


class RequestService:
    """Сервис для проверки данных и управления заявками."""

    def __init__(self, repository: RequestRepository | None = None, db_path: str | Path | None = None):
        self.repository = repository or RequestRepository(db_path=db_path)

    def validate_request_data(self, data: dict) -> dict:
        """Проверяет корректность данных заявки и возвращает нормализованные значения."""
        customer = str(data.get("customer", "")).strip()
        equipment_type = str(data.get("equipment_type", "")).strip()
        category = str(data.get("category", "")).strip()
        description = str(data.get("description", "")).strip()
        priority = str(data.get("priority", "")).strip()
        status = str(data.get("status", "новая")).strip() or "новая"
        work_description = str(data.get("work_description", "")).strip()

        errors = []
        if not customer:
            errors.append("Поле «Заказчик или подразделение» обязательно для заполнения.")
        if not equipment_type:
            errors.append("Поле «Тип оборудования» обязательно для заполнения.")
        if not category:
            errors.append("Необходимо выбрать категорию обращения.")
        if not description:
            errors.append("Поле «Описание неисправности» обязательно для заполнения.")
        if not priority:
            errors.append("Необходимо выбрать приоритет заявки.")
        if not status:
            errors.append("Необходимо выбрать статус заявки.")

        if category and category not in CATEGORIES:
            errors.append("Выбрана недопустимая категория обращения.")
        if priority and priority not in PRIORITIES:
            errors.append("Выбран недопустимый приоритет заявки.")
        if status and status not in STATUSES:
            errors.append("Выбран недопустимый статус заявки.")

        if len(customer) > 150:
            errors.append("Поле «Заказчик или подразделение» не должно превышать 150 символов.")
        if len(equipment_type) > 150:
            errors.append("Поле «Тип оборудования» не должно превышать 150 символов.")
        if len(description) > 2000:
            errors.append("Поле «Описание неисправности» не должно превышать 2000 символов.")
        if len(work_description) > 2000:
            errors.append("Поле «Описание выполненных работ» не должно превышать 2000 символов.")

        if errors:
            raise ValidationError("\n".join(errors))

        return {
            "customer": customer,
            "equipment_type": equipment_type,
            "category": category,
            "description": description,
            "priority": priority,
            "status": status,
            "work_description": work_description,
        }

    def create_request(self, data: dict) -> int:
        """Создаёт новую заявку после проверки данных."""
        normalized = self.validate_request_data(data)
        request = ServiceRequest.create_new(**normalized)
        return self.repository.create(request)

    def get_all_requests(self) -> list[ServiceRequest]:
        """Возвращает список всех заявок."""
        return self.repository.get_all()

    def get_request(self, request_id: int) -> ServiceRequest | None:
        """Возвращает заявку по идентификатору."""
        return self.repository.get_by_id(request_id)

    def update_request(self, request_id: int, data: dict) -> bool:
        """Обновляет существующую заявку."""
        existing = self.repository.get_by_id(request_id)
        if existing is None:
            raise ValidationError("Заявка с указанным идентификатором не найдена.")
        normalized = self.validate_request_data(data)
        updated = ServiceRequest(
            id=request_id,
            created_at=existing.created_at,
            **normalized,
        )
        return self.repository.update(updated)

    def delete_request(self, request_id: int) -> bool:
        """Удаляет заявку."""
        if self.repository.get_by_id(request_id) is None:
            raise ValidationError("Заявка с указанным идентификатором не найдена.")
        return self.repository.delete(request_id)

    def change_status(self, request_id: int, status: str) -> bool:
        """Изменяет статус заявки."""
        normalized_status = str(status).strip()
        if normalized_status not in STATUSES:
            raise ValidationError("Выбран недопустимый статус заявки.")
        if self.repository.get_by_id(request_id) is None:
            raise ValidationError("Заявка с указанным идентификатором не найдена.")
        return self.repository.update_status(request_id, normalized_status)

    def search_requests(self, query: str) -> list[ServiceRequest]:
        """Выполняет поиск заявок."""
        return self.repository.search(query)

    def filter_requests(
        self,
        category: str | None = None,
        status: str | None = None,
        query: str | None = None,
    ) -> list[ServiceRequest]:
        """Фильтрует заявки по категории, статусу и запросу."""
        if category and category not in CATEGORIES and category != "Все":
            raise ValidationError("Выбрана недопустимая категория для фильтрации.")
        if status and status not in STATUSES and status != "Все":
            raise ValidationError("Выбран недопустимый статус для фильтрации.")
        return self.repository.filter_requests(category=category, status=status, query=query)
