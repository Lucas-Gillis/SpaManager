from fastapi import APIRouter, HTTPException, Response, status

from ..core.auth import auth_config
from ..core.security import create_access_token
from ..models.auth import TokenRequest, TokenResponse
from ..services.users import InMemoryUserService

from ..core.auth import AuthMiddleware

router = APIRouter()
user_service = InMemoryUserService()

def _issue_access_token(payload: TokenRequest) -> str:
    user = user_service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        subject=user.username,
        data={"role": int(user.role), "scopes": user.scopes, "full_name": user.full_name},
    )
    return token


@router.post("/token", response_model=TokenResponse, summary="Issue demo access token")
@auth_config(required=False)
async def issue_token(payload: TokenRequest) -> TokenResponse:
    return TokenResponse(access_token=_issue_access_token(payload))


@router.post(
    "/token/cookie",
    response_model=TokenResponse,
    summary="Issue access token and set it as a secure cookie",
)
@auth_config(required=False)
async def issue_token_cookie(payload: TokenRequest, response: Response) -> TokenResponse:
    token = _issue_access_token(payload)
    response.set_cookie(
        key=AuthMiddleware.TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600,
    )
    return TokenResponse(access_token=token)
