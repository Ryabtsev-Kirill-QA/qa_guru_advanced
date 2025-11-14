import os
import dotenv
import pytest
import json
from http import HTTPStatus
from faker import Faker
from tests.api_client import UsersApi, StatusApi


@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--env", default="dev")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(scope="session")
def users_api(env):
    return UsersApi(env)


@pytest.fixture(scope="session")
def status_api(env):
    return StatusApi(env)


@pytest.fixture(scope="function")
def fill_test_data(users_api):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = users_api.create_user(user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        users_api.delete_user(user_id)


@pytest.fixture(scope="function")
def create_new_user(users_api):
    fake = Faker()
    new_user_data = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "avatar": fake.image_url()
    }
    response = users_api.create_user(new_user_data)
    assert response.status_code == HTTPStatus.CREATED
    return response.json()


@pytest.fixture(scope="function")
def clean_database(users_api):
    response = users_api.get_users()
    if response.status_code == HTTPStatus.OK:
        users = response.json().get("items", [])
        for user in users:
            users_api.delete_user(user['id'])

    yield

    response = users_api.get_users()
    if response.status_code == HTTPStatus.OK:
        users = response.json().get("items", [])
        for user in users:
            users_api.delete_user(user['id'])


@pytest.fixture
def users(users_api):
    response = users_api.get_users()
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]
