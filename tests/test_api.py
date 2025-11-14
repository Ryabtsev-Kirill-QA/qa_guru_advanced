import pytest
import requests
from http import HTTPStatus
from faker import Faker
from app.models.User import User
from app.models.Pagination import Pagination


class TestUsersEndpoint:
    """Тесты для эндпоинта /users"""

    def test_users(self, users_api, fill_test_data):
        response = users_api.get_users()
        assert response.status_code == HTTPStatus.OK

        users = response.json()["items"]
        for user in users:
            User.model_validate(user)

    def test_users_no_duplicates(self, users, fill_test_data):
        users_ids = [user["id"] for user in users]
        assert len(users_ids) == len(set(users_ids))


class TestUserEndpoint:
    """Тесты для эндпоинта /users/{user_id}"""

    def test_user(self, users_api, fill_test_data):
        for user_id in (fill_test_data[0], fill_test_data[-1]):
            response = users_api.get_user(user_id)
            assert response.status_code == HTTPStatus.OK
            user = response.json()
            User.model_validate(user)

    @pytest.mark.parametrize("user_id", [10000])
    def test_user_nonexistent_values(self, users_api, user_id):
        response = users_api.get_user(user_id)
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_user_invalid_values(self, users_api, user_id):
        response = users_api.get_user(user_id)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestPagination:
    """Тесты для пагинации в эндпоинте /users"""

    def test_default_pagination(self, users_api, fill_test_data):
        response = users_api.get_users()
        users_with_pagination = response.json()

        assert response.status_code == HTTPStatus.OK
        assert len(users_with_pagination) == 5

        users_pagination = response.json()
        Pagination.model_validate(users_pagination)

    @pytest.mark.parametrize("size, expected_pages", [(1, 12), (3, 4), (12, 1)])
    def test_get_users_page_calculation(self, users_api, size, expected_pages, clean_database, fill_test_data):
        response = users_api.get_users(size=size)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["pages"] == expected_pages

    @pytest.mark.parametrize("page, size, expected_count", [
        (1, 5, 5),
        (2, 5, 5),
        (3, 5, 2),
        (1, 12, 12),
        (2, 12, 0)
    ])
    def test_get_users_different_pages_pagination(self, users_api, page, size, expected_count, clean_database,
                                                  fill_test_data):
        response = users_api.get_users(page=page, size=size)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["page"] == page
        assert response.json()["size"] == size
        assert len(response.json()["items"]) == expected_count

    def test_get_users_different_data_in_pages(self, users_api, fill_test_data):
        response_page1 = users_api.get_users(page=1, size=6)
        response_page2 = users_api.get_users(page=2, size=6)

        data_page1 = response_page1.json()
        data_page2 = response_page2.json()

        assert data_page1["items"] != data_page2["items"]
        assert data_page1["page"] == 1
        assert data_page2["page"] == 2


class TestCreateUser:
    """Тесты на метод POST эндпоинта /users"""

    def test_create_user(self, users_api):
        fake = Faker()
        new_user_data = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }

        response = users_api.create_user(new_user_data)
        new_user = response.json()
        User.model_validate(response.json())

        assert response.status_code == HTTPStatus.CREATED
        assert new_user["email"] == new_user_data["email"]
        assert new_user["first_name"] == new_user_data["first_name"]
        assert new_user["last_name"] == new_user_data["last_name"]

        users_api.delete_user(new_user["id"])

    def test_create_user_missing_field(self, users_api):
        fake = Faker()
        new_user_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }

        response = users_api.create_user(new_user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_invalid_email(self, users_api):
        fake = Faker()
        new_user_data = {
            "email": "invalid_data",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }

        response = users_api.create_user(new_user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestDeleteUser:
    """Тесты на метод DELETE эндпоинта /users"""

    def test_delete_user(self, users_api, create_new_user):
        user_id = create_new_user["id"]
        response = users_api.delete_user(user_id)

        assert response.status_code == HTTPStatus.OK
        get_response = users_api.get_user(user_id)
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_none_existent_user(self, users_api):
        non_existent_user_id = 10000
        response = users_api.delete_user(non_existent_user_id)

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestUpdateUser:
    """Тесты на метод PATCH эндпоинта /users"""

    def test_update_user(self, users_api, create_new_user):
        fake = Faker()
        new_user_data = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }
        user_id = create_new_user["id"]
        response = users_api.update_user(user_id, new_user_data)
        updated_user = response.json()

        assert response.status_code == HTTPStatus.OK
        assert updated_user["email"] == new_user_data["email"]
        assert updated_user["first_name"] == new_user_data["first_name"]
        assert updated_user["last_name"] == new_user_data["last_name"]

        users_api.delete_user(user_id)

    def test_get_user_after_update(self, users_api, create_new_user):
        fake = Faker()
        new_user_data = {"email": fake.email()}
        user_id = create_new_user["id"]
        response = users_api.update_user(user_id, new_user_data)

        assert response.status_code == HTTPStatus.OK
        get_user = users_api.get_user(user_id)
        assert get_user.status_code == HTTPStatus.OK
        get_user_info = get_user.json()
        assert get_user_info["email"] == new_user_data["email"]

        users_api.delete_user(user_id)

    def test_method_not_allowed(self, app_url, users_api, create_new_user):
        fake = Faker()
        new_user_data = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
        }
        user_id = create_new_user["id"]
        response = requests.put(f"{app_url}/api/users/{user_id}", json=new_user_data)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        users_api.delete_user(user_id)
