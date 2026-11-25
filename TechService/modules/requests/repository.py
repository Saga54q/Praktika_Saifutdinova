"""Репозиторий для работы с заявками в SQLite."""

from __future__ import annotations

from pathlib import Path

from database.connection import get_connection
from modules.requests.models import ServiceRequest


class RequestRepository:
    """Выполняет CRUD-операции для заявок на техническое обслуживание."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = db_path

    def create(self, request: ServiceRequest) -> int:
        """Создаёт заявку и возвращает её идентификатор."""
        sql = """
        INSERT INTO service_requests (
            created_at, customer, equipment_type, category, description,
            priority, status, work_description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            request.created_at,
            request.customer,
            request.equipment_type,
            request.category,
            request.description,
            request.priority,
            request.status,
            request.work_description,
        )
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(sql, values)
            return int(cursor.lastrowid)

    def get_all(self) -> list[ServiceRequest]:
        """Возвращает все заявки, отсортированные по дате регистрации."""
        sql = "SELECT * FROM service_requests ORDER BY datetime(created_at) DESC, id DESC"
        with get_connection(self.db_path) as connection:
            rows = connection.execute(sql).fetchall()
        return [ServiceRequest.from_row(row) for row in rows]

    def get_by_id(self, request_id: int) -> ServiceRequest | None:
        """Возвращает заявку по идентификатору."""
        sql = "SELECT * FROM service_requests WHERE id = ?"
        with get_connection(self.db_path) as connection:
            row = connection.execute(sql, (request_id,)).fetchone()
        return ServiceRequest.from_row(row) if row else None

    def update(self, request: ServiceRequest) -> bool:
        """Обновляет данные заявки."""
        if request.id is None:
            raise ValueError("Нельзя обновить заявку без идентификатора.")
        sql = """
        UPDATE service_requests
        SET customer = ?, equipment_type = ?, category = ?, description = ?,
            priority = ?, status = ?, work_description = ?
        WHERE id = ?
        """
        values = (
            request.customer,
            request.equipment_type,
            request.category,
            request.description,
            request.priority,
            request.status,
            request.work_description,
            request.id,
        )
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(sql, values)
            return cursor.rowcount > 0

    def delete(self, request_id: int) -> bool:
        """Удаляет заявку по идентификатору."""
        sql = "DELETE FROM service_requests WHERE id = ?"
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(sql, (request_id,))
            return cursor.rowcount > 0

    def update_status(self, request_id: int, status: str) -> bool:
        """Изменяет статус заявки."""
        sql = "UPDATE service_requests SET status = ? WHERE id = ?"
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(sql, (status, request_id))
            return cursor.rowcount > 0

    @staticmethod
    def _matches_query(request: ServiceRequest, query: str) -> bool:
        """Проверяет, соответствует ли заявка поисковому запросу."""
        needle = query.strip().lower()
        if not needle:
            return True
        haystacks = [
            str(request.id or ""),
            request.customer,
            request.equipment_type,
            request.category,
            request.description,
            request.priority,
            request.status,
            request.work_description,
        ]
        return any(needle in value.lower() for value in haystacks)

    def search(self, query: str) -> list[ServiceRequest]:
        """Ищет заявки по номеру, заказчику, оборудованию и описаниям."""
        normalized = query.strip()
        requests = self.get_all()
        if not normalized:
            return requests
        return [request for request in requests if self._matches_query(request, normalized)]

    def filter_requests(
        self,
        category: str | None = None,
        status: str | None = None,
        query: str | None = None,
    ) -> list[ServiceRequest]:
        """Фильтрует заявки по категории, статусу и поисковому запросу."""
        clauses = []
        params: list[str] = []

        if category and category != "Все":
            clauses.append("category = ?")
            params.append(category)

        if status and status != "Все":
            clauses.append("status = ?")
            params.append(status)

        sql = "SELECT * FROM service_requests"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY datetime(created_at) DESC, id DESC"

        with get_connection(self.db_path) as connection:
            rows = connection.execute(sql, params).fetchall()
        requests = [ServiceRequest.from_row(row) for row in rows]

        if query and query.strip():
            requests = [request for request in requests if self._matches_query(request, query)]
        return requests
