import pytest
import requests
from http import HTTPStatus
from models.AppStatus import AppStatus


class TestStatusEndpoint:
    """Тесты для эндпоинта /status"""

    def test_status(self, app_url):
        response = requests.get(f"{app_url}/status")
        data = response.json()

        assert response.status_code == HTTPStatus.OK
        assert data["status"] == "ok"

        AppStatus.model_validate(data)

    def test_service_not_running(self, app_url):
        try:
            requests.get(f"{app_url}/status", timeout=5)
            pytest.skip("Сервис запущен на порту 8002")
        except requests.exceptions.ConnectionError:
            assert False, "Ошибка подключения"

