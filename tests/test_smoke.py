import pytest
import requests
from http import HTTPStatus


class TestStatusEndpoint:
    """Тесты для эндпоинта /status"""

    def test_status(self, status_api):
        response = status_api.get_status()

        assert response.status_code == HTTPStatus.OK
        assert True

    def test_service_not_running(self, status_api):
        try:
            status_api.get_status()
            pytest.skip("Сервис запущен на порту 8002")
        except requests.exceptions.ConnectionError:
            assert False, "Ошибка подключения"
