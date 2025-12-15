from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, Optional

from ..core.auth import Role
from ..models.user import User


class InMemoryUserService:
    """
    In-memory representation of the `usuario` table and related permissions.

    It keeps extra fields (id, email, tipo_usuario, cliente_id, etc.) in the
    internal records so the mock aligns with the SQL model, while exposing the
    simplified `User` Pydantic model to the rest of the app.
    """

    def __init__(self):
        now = datetime.utcnow()

        # Internal records are modeled after `usuario` + `usuario_modulo`.
        # Keys are usernames used for authentication.
        self._users: Dict[str, dict] = {
            "gaby_dono": {
                "id": 1,
                "username": "gaby_dono",
                "nome": "Gaby",
                "email": "owner@example.com",
                "senha_hash": "gaby_dono",
                "tipo_usuario": "ADMIN",  # ADMIN / FUNCIONARIO / CLIENTE
                "cliente_id": None,
                "funcionario_id": None,
                "ativo": True,
                "created_at": now,
                "updated_at": now,
                "role": Role.OWNER,
                "scopes": ["appointments:write", "clients:write", "staff:manage"],
            },
            "manager": {
                "id": 2,
                "username": "manager",
                "nome": "Mark Manager",
                "email": "manager@example.com",
                "senha_hash": "spa-manager",
                "tipo_usuario": "ADMIN",
                "cliente_id": None,
                "funcionario_id": None,
                "ativo": True,
                "created_at": now,
                "updated_at": now,
                "role": Role.MANAGER,
                "scopes": ["appointments:write", "clients:write"],
            },
            "staff": {
                "id": 3,
                "username": "staff",
                "nome": "Sara Staff",
                "email": "staff@example.com",
                "senha_hash": "spa-staff",
                "tipo_usuario": "FUNCIONARIO",
                "cliente_id": None,
                "funcionario_id": None,
                "ativo": True,
                "created_at": now,
                "updated_at": now,
                "role": Role.STAFF,
                "scopes": ["appointments:read", "clients:read"],
            },
            # Client users, correlated with mocked `cliente` IDs from MockClientService.
            "celia": {
                "id": 4,
                "username": "celia",
                "nome": "Célia Cliente",
                "email": "celia@example.com",
                "senha_hash": "celia-cliente",
                "tipo_usuario": "CLIENTE",
                "cliente_id": 1,  # matches MockClientService client with id=1
                "funcionario_id": None,
                "ativo": True,
                "created_at": now,
                "updated_at": now,
                "role": Role.GUEST,
                "scopes": [],
            },
            "pedro": {
                "id": 5,
                "username": "pedro",
                "nome": "Pedro Patrono",
                "email": "peter@example.com",
                "senha_hash": "pedro-cliente",
                "tipo_usuario": "CLIENTE",
                "cliente_id": 2,  # matches MockClientService client with id=2
                "funcionario_id": None,
                "ativo": True,
                "created_at": now,
                "updated_at": now,
                "role": Role.GUEST,
                "scopes": [],
            },
        }

    def authenticate(self, username: str, password: str) -> Optional[User]:
        record = self._users.get(username)
        print(record)
        if not record:
            return None

        if not record.get("ativo", True):
            return None

        # For the mock, we compare directly with the stored "senha_hash".
        if record.get("senha_hash") != password:
            return None

        return User(
            username=record["username"],
            full_name=record.get("nome"),
            role=record.get("role", Role.STAFF),
            scopes=list(record.get("scopes", [])),
        )

    def list_users(self) -> Iterable[User]:
        # Only staff/admin users are returned here; client accounts are excluded.
        for record in self._users.values():
            if record.get("tipo_usuario") == "CLIENTE":
                continue
            yield User(
                username=record["username"],
                full_name=record.get("nome"),
                role=record.get("role", Role.STAFF),
                scopes=list(record.get("scopes", [])),
            )
