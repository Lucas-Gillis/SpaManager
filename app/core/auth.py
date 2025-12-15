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
    TOKEN_COOKIE_NAME = "spa_access_token"

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]):
        # Always attempt to extract a token so user info can be injected on every request.
        try:
            token = self._extract_token(request)
        except HTTPException:
            token = None

        if token is not None:
            try:
                payload = TokenPayload(**decode_access_token(token))
                user = build_user(payload)
            except Exception:
                # On any decoding/validation error, treat as anonymous guest.
                user = AuthenticatedUser(
                    username="",
                    role=Role.GUEST,
                    scopes=set(),
                    full_name=None,
                )
        else:
            # Anonymous/guest user when no valid token is present.
            user = AuthenticatedUser(
                username="",
                role=Role.GUEST,
                scopes=set(),
                full_name=None,
            )

        # Inject user info into the request; per-endpoint enforcement is handled via dependencies.
        request.state.user = user

        return await call_next(request)

    @staticmethod
    def _extract_token(request: Request) -> str:
        header = request.headers.get("Authorization")
        if header and header.startswith("Bearer "):
            return header.split(" ", 1)[1].strip()

        cookie_token = request.cookies.get(AuthMiddleware.TOKEN_COOKIE_NAME)
        if cookie_token:
            return cookie_token

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

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


def authorize(request: Request) -> AuthenticatedUser:
    """
    Dependency to enforce authentication and authorization for an endpoint.

    It reads the AuthConfig attached by `@auth_config` on the resolved endpoint
    and applies `required`, `minimum_role` and `scopes` checks against the
    user injected by AuthMiddleware.
    """
    endpoint = request.scope.get("endpoint")
    config = get_auth_config(endpoint)

    user = get_current_user(request)
    if user is None:
        # Should not generally happen because middleware injects a guest user,
        # but keep a safe default.
        user = AuthenticatedUser(
            username="",
            role=Role.GUEST,
            scopes=set(),
            full_name=None,
        )

    if not config.required:
        return user

    # If auth is required, a guest user (no username) is considered unauthenticated.
    if not user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthenticated",
        )

    # Enforce minimum role if configured.
    if config.minimum_role is not None and user.role < config.minimum_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role for resource",
        )

    # Enforce required scopes, if any.
    missing = set(config.scopes).difference(user.scopes)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing required scopes: {', '.join(sorted(missing))}",
        )

    return user
