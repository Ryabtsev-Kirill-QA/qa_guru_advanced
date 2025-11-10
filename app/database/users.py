from typing import Iterable, Type
from fastapi import HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select
from app.database.engine import engine
from app.models.User import User, UserCreate


def get_user(user_id: int) -> User | None:
    with Session(engine) as session:
        return session.get(User, user_id)


def get_users() -> Page[User]:
    with Session(engine) as session:
        return paginate(session, select(User))


def create_user(user_data: UserCreate) -> User:
    user_dict = user_data.model_dump()
    user = User(**user_dict)

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def update_user(user_id: int, user: User) -> Type[User]:
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
