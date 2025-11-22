from datetime import date

from pydantic import BaseModel

from typing import Optional


class Client(BaseModel):
    id: int
    full_name: str
    email: str
    membership_level: str
    last_visit: Optional[date] = None


class ClientCreate(BaseModel):
    full_name: str
    email: str
    membership_level: str
