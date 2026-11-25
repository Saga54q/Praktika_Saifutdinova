"""Инициализация схемы базы данных."""

from __future__ import annotations

from pathlib import Path

from database.connection import get_connection


CREATE_SERVICE_REQUESTS_TABLE = """
CREATE TABLE IF NOT EXISTS service_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    customer TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'новая',
    work_description TEXT NOT NULL DEFAULT ''
)
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status)",
    "CREATE INDEX IF NOT EXISTS idx_service_requests_category ON service_requests(category)",
    "CREATE INDEX IF NOT EXISTS idx_service_requests_created_at ON service_requests(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_service_requests_customer ON service_requests(customer)",
]


def initialize_database(db_path: str | Path | None = None) -> None:
    """Создаёт таблицы и индексы, если они отсутствуют."""
    with get_connection(db_path) as connection:
        connection.execute(CREATE_SERVICE_REQUESTS_TABLE)
        for index_sql in CREATE_INDEXES:
            connection.execute(index_sql)
