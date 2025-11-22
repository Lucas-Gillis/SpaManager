from fastapi import APIRouter, HTTPException, status

from app.core.auth import auth_config
from app.core.security import create_access_token
from app.models.auth import TokenRequest, TokenResponse
from app.services.users import InMemoryUserService

router = APIRouter()
user_service = InMemoryUserService()


@router.post("/token", response_model=TokenResponse, summary="Issue demo access token")
@auth_config(required=False)
async def issue_token(payload: TokenRequest) -> TokenResponse:
    user = user_service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        subject=user.username,
        data={"role": int(user.role), "scopes": user.scopes, "full_name": user.full_name},
    )
    return TokenResponse(access_token=token)
