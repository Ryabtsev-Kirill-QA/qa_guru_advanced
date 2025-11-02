import pytest
import requests
from http import HTTPStatus
from app.models.User import User
from app.models.Pagination import Pagination


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]


class TestUsersEndpoint:
    """Тесты для эндпоинта /users"""

    def test_users(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        assert response.status_code == HTTPStatus.OK

        users = response.json()["items"]
        for user in users:
            User.model_validate(user)

    def test_users_no_duplicates(self, users):
        users_ids = [user["id"] for user in users]
        assert len(users_ids) == len(set(users_ids))


class TestUserEndpoint:
    """Тесты для эндпоинта /users/{user_id}"""

    @pytest.mark.parametrize("user_id", [1, 6, 12])
    def test_user(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.OK

        user = response.json()
        User.model_validate(user)

    @pytest.mark.parametrize("user_id", [13])
    def test_user_nonexistent_values(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_user_invalid_values(self, app_url, user_id):
        response = requests.get(f"{app_url}/api/users/{user_id}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestPagination:
    """Тесты для пагинации в эндпоинте /users"""

    def test_default_pagination(self, app_url):
        response = requests.get(f"{app_url}/api/users/")
        users_with_pagination = response.json()

        assert response.status_code == HTTPStatus.OK
        assert len(users_with_pagination) == 5

        users_pagination = response.json()
        Pagination.model_validate(users_pagination)

    @pytest.mark.parametrize("size, expected_pages", [(1, 12), (3, 4), (12, 1)])
    def test_get_users_page_calculation(self, app_url, size, expected_pages):
        response = requests.get(f"{app_url}/api/users/?size={size}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["pages"] == expected_pages

    @pytest.mark.parametrize("page, size, expected_count", [
        (1, 5, 5),
        (2, 5, 5),
        (3, 5, 2),
        (1, 12, 12),
        (2, 12, 0)
    ])
    def test_get_users_different_pages_pagination(self, app_url, page, size, expected_count):
        response = requests.get(f"{app_url}/api/users/?page={page}&size={size}")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["page"] == page
        assert response.json()["size"] == size
        assert len(response.json()["items"]) == expected_count

    def test_get_users_different_data_in_pages(self, app_url):
        response_page1 = requests.get(f"{app_url}/api/users/?page=1&size=6")
        response_page2 = requests.get(f"{app_url}/api/users/?page=2&size=6")

        data_page1 = response_page1.json()
        data_page2 = response_page2.json()

        assert data_page1["items"] != data_page2["items"]
        assert data_page1["page"] == 1
        assert data_page2["page"] == 2
