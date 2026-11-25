"""Тесты модуля регистрации и учёта заявок."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.initialization import initialize_database  # noqa: E402
from modules.requests.repository import RequestRepository  # noqa: E402
from modules.requests.service import RequestService, ValidationError  # noqa: E402


class RequestModuleTestCase(unittest.TestCase):
    """Проверка основных функций модуля заявок."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.db_path)
        self.service = RequestService(db_path=self.db_path)

        self.valid_data = {
            "customer": "Отдел бухгалтерии",
            "equipment_type": "Ноутбук Dell Latitude",
            "category": "неисправность оборудования",
            "description": "Не включается после нажатия кнопки питания.",
            "priority": "высокий",
            "status": "новая",
            "work_description": "",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_request(self):
        request_id = self.service.create_request(self.valid_data)
        request = self.service.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request.customer, "Отдел бухгалтерии")
        self.assertEqual(request.status, "новая")

    def test_edit_request(self):
        request_id = self.service.create_request(self.valid_data)
        updated = dict(self.valid_data)
        updated["customer"] = "Отдел кадров"
        updated["priority"] = "средний"
        updated["work_description"] = "Проведена первичная диагностика."
        result = self.service.update_request(request_id, updated)
        self.assertTrue(result)
        request = self.service.get_request(request_id)
        self.assertEqual(request.customer, "Отдел кадров")
        self.assertEqual(request.priority, "средний")
        self.assertEqual(request.work_description, "Проведена первичная диагностика.")

    def test_delete_request(self):
        request_id = self.service.create_request(self.valid_data)
        result = self.service.delete_request(request_id)
        self.assertTrue(result)
        self.assertIsNone(self.service.get_request(request_id))

    def test_search_requests(self):
        self.service.create_request(self.valid_data)
        other = dict(self.valid_data)
        other["customer"] = "Склад"
        other["equipment_type"] = "Принтер HP"
        other["description"] = "Замятие бумаги."
        other["category"] = "диагностика"
        other_id = self.service.create_request(other)

        by_id = self.service.search_requests(str(other_id))
        self.assertEqual(len(by_id), 1)
        self.assertEqual(by_id[0].id, other_id)

        by_customer = self.service.search_requests("Склад")
        self.assertEqual(len(by_customer), 1)
        self.assertEqual(by_customer[0].customer, "Склад")

    def test_filter_requests(self):
        self.service.create_request(self.valid_data)
        second = dict(self.valid_data)
        second["category"] = "установка программного обеспечения"
        second["status"] = "в работе"
        second["description"] = "Установить офисный пакет."
        self.service.create_request(second)

        filtered_category = self.service.filter_requests(category="установка программного обеспечения")
        self.assertEqual(len(filtered_category), 1)
        self.assertEqual(filtered_category[0].category, "установка программного обеспечения")

        filtered_status = self.service.filter_requests(status="в работе")
        self.assertEqual(len(filtered_status), 1)
        self.assertEqual(filtered_status[0].status, "в работе")

        filtered_both = self.service.filter_requests(
            category="неисправность оборудования",
            status="новая",
        )
        self.assertEqual(len(filtered_both), 1)

    def test_change_status(self):
        request_id = self.service.create_request(self.valid_data)
        result = self.service.change_status(request_id, "в работе")
        self.assertTrue(result)
        request = self.service.get_request(request_id)
        self.assertEqual(request.status, "в работе")

    def test_save_and_reload_after_restart(self):
        request_id = self.service.create_request(self.valid_data)
        # Имитация перезапуска приложения: новый сервис/репозиторий с тем же файлом БД.
        restarted_service = RequestService(db_path=self.db_path)
        request = restarted_service.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request.id, request_id)
        self.assertEqual(request.customer, self.valid_data["customer"])

    def test_invalid_input(self):
        invalid = dict(self.valid_data)
        invalid["customer"] = ""
        invalid["category"] = "несуществующая категория"
        with self.assertRaises(ValidationError):
            self.service.create_request(invalid)

    def test_invalid_status_change(self):
        request_id = self.service.create_request(self.valid_data)
        with self.assertRaises(ValidationError):
            self.service.change_status(request_id, "неверный статус")

    def test_delete_nonexistent_request(self):
        with self.assertRaises(ValidationError):
            self.service.delete_request(99999)


if __name__ == "__main__":
    unittest.main()
