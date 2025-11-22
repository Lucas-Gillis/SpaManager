from pydantic import BaseModel, Field

from app.core.auth import Role

from typing import Optional


class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: Role = Role.STAFF
    scopes: list[str] = Field(default_factory=list)


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    role: Role = Role.STAFF
    scopes: list[str] = Field(default_factory=list)
