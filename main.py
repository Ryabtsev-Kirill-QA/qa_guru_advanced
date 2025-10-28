import json
import uvicorn
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, add_pagination, paginate
from datetime import datetime
from models.AppStatus import AppStatus
from models.User import User

app = FastAPI()
add_pagination(app)

users: list[User] = []


@app.get("/status", status_code=HTTPStatus.OK, response_model=AppStatus)
def status():
    users_exist = bool(users)
    return AppStatus(status="ok" if users_exist else "unavailable", users=users_exist,
                     timestamp=datetime.now().isoformat())


@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return users[user_id - 1]


@app.get("/api/users/", status_code=HTTPStatus.OK)
def get_users() -> Page[User]:
    return paginate(users)


if __name__ == "__main__":
    with open("users.json") as f:
        users = json.load(f)

    for user in users:
        User.model_validate(user)

    print("Users loaded")

    uvicorn.run(app, host="localhost", port=8002)
