from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Awaitable, Callable, Iterable, Optional

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from .security import decode_access_token


class Role(IntEnum):
    GUEST = 1
    STAFF = 2
    MANAGER = 3
    ADMIN = 4
    OWNER = 5

    @classmethod
    def from_value(cls, value: int | str | Role) -> "Role":
        if isinstance(value, Role):
            return value
        return cls(int(value))


class TokenPayload(BaseModel):
    sub: str
    role: Role = Role.GUEST
    scopes: list[str] = Field(default_factory=list)
    full_name: Optional[str] = None


class AuthenticatedUser(BaseModel):
    username: str
    role: Role
    scopes: set[str]
    full_name: Optional[str] = None

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes

    def has_scopes(self, required_scopes: Iterable[str]) -> bool:
        return set(required_scopes).issubset(self.scopes)

    def has_role(self, required_role: Role) -> bool:
        return self.role >= required_role


@dataclass(frozen=True)
class AuthConfig:
    required: bool = True
    minimum_role: Optional[Role] = Role.STAFF
    scopes: frozenset[str] = frozenset()


def auth_config(
    *,
    required: bool = True,
    minimum_role: Optional[Role] = Role.STAFF,
    scopes: Optional[Iterable[str]] = None,
):
    config = AuthConfig(required=required, minimum_role=minimum_role, scopes=frozenset(scopes or []))

    def decorator(func):
        setattr(func, "__auth_config__", config)
        return func

    return decorator


def get_auth_config(endpoint) -> AuthConfig:
    return getattr(endpoint, "__auth_config__", AuthConfig())


def build_user(payload: TokenPayload) -> AuthenticatedUser:
    return AuthenticatedUser(
        username=payload.sub,
        role=payload.role,
        scopes=set(payload.scopes),
        full_name=payload.full_name,
    )


class AuthMiddleware(BaseHTTPMiddleware):
    ALWAYS_PUBLIC_PATHS = {
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
    }

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
        if request.url.path in self.ALWAYS_PUBLIC_PATHS:
            return await call_next(request)

        endpoint = request.scope.get("endpoint")

        if endpoint is None:
            return await call_next(request)

        config = get_auth_config(endpoint)

        if not config.required:
            return await call_next(request)

        token = self._extract_token(request)
        payload = TokenPayload(**decode_access_token(token))
        user = build_user(payload)

        self._enforce_role(user, config.minimum_role)
        self._enforce_scopes(user, config.scopes)
        request.state.user = user

        return await call_next(request)

    @staticmethod
    def _extract_token(request: Request) -> str:
        header = request.headers.get("Authorization")
        if not header or not header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
        return header.split(" ", 1)[1]

    @staticmethod
    def _enforce_role(user: AuthenticatedUser, minimum_role: Optional[Role]):
        if minimum_role is None:
            return
        if user.role < minimum_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role for resource")

    @staticmethod
    def _enforce_scopes(user: AuthenticatedUser, required_scopes: Iterable[str]):
        missing = set(required_scopes).difference(user.scopes)
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scopes: {', '.join(sorted(missing))}",
            )


def get_current_user(request: Request) -> AuthenticatedUser | None:
    return getattr(request.state, "user", None)
