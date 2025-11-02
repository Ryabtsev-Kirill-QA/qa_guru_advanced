from datetime import datetime
from pydantic import BaseModel


class AppStatus(BaseModel):
    database: bool
