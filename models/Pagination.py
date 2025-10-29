from pydantic import BaseModel


class Pagination(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int
