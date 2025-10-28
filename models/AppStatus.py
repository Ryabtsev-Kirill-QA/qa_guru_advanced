from datetime import datetime
from pydantic import BaseModel


class AppStatus(BaseModel):
    status: str
    users: bool
    timestamp: datetime
