import os
import dotenv
import pytest
import json
import requests
from http import HTTPStatus
from faker import Faker


@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(scope="function")
def fill_test_data(app_url):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())

    user_ids = [user["id"] for user in api_users]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")


@pytest.fixture(scope="function")
def create_new_user(app_url):
    fake = Faker()
    new_user_data = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "avatar": fake.image_url()
    }
    response = requests.post(f"{app_url}/api/users/", json=new_user_data)
    assert response.status_code == HTTPStatus.CREATED
    return response.json()


@pytest.fixture(scope="function")
def clean_database(app_url):
    response = requests.get(f"{app_url}/api/users/")
    if response.status_code == HTTPStatus.OK:
        users = response.json().get("items", [])
        for user in users:
            requests.delete(f"{app_url}/api/users/{user['id']}")

    yield

    response = requests.get(f"{app_url}/api/users/")
    if response.status_code == HTTPStatus.OK:
        users = response.json().get("items", [])
        for user in users:
            requests.delete(f"{app_url}/api/users/{user['id']}")


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]
