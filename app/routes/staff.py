from typing import List

from fastapi import APIRouter, HTTPException, Request, status

from app.core.auth import Role, auth_config, get_current_user
from app.models.user import User
from app.services.users import InMemoryUserService

router = APIRouter()
user_service = InMemoryUserService()


@router.get("/me", response_model=User, summary="Current staff profile")
@auth_config(minimum_role=Role.STAFF)
async def read_profile(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated")
    return User(username=user.username, full_name=user.full_name, role=user.role, scopes=sorted(user.scopes))


@router.get("/team", response_model=List[User], summary="List staff members")
@auth_config(minimum_role=Role.ADMIN, scopes={"staff:manage"})
async def list_staff():
    return list(user_service.list_users())
