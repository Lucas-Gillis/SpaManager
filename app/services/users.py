from __future__ import annotations

from typing import Dict, Iterable, Optional

from app.core.auth import Role
from app.models.user import User


class InMemoryUserService:
    """Simple user store for demo purposes."""

    _users: Dict[str, dict] = {
        "owner": {
            "username": "owner",
            "password": "spa-owner",
            "full_name": "Olivia Owner",
            "role": Role.OWNER,
            "scopes": ["appointments:write", "clients:write", "staff:manage"],
        },
        "manager": {
            "username": "manager",
            "password": "spa-manager",
            "full_name": "Mark Manager",
            "role": Role.MANAGER,
            "scopes": ["appointments:write", "clients:write"],
        },
        "staff": {
            "username": "staff",
            "password": "spa-staff",
            "full_name": "Sara Staff",
            "role": Role.STAFF,
            "scopes": ["appointments:read", "clients:read"],
        },
    }

    def __init__(self):
        self._users = self._users.copy()

    def authenticate(self, username: str, password: str) -> Optional[User]:
        record = self._users.get(username)
        if not record or record["password"] != password:
            return None
        return User(**{k: v for k, v in record.items() if k != "password"})

    def list_users(self) -> Iterable[User]:
        for record in self._users.values():
            yield User(**{k: v for k, v in record.items() if k != "password"})
