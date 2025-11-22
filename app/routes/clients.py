from typing import List

from fastapi import APIRouter, HTTPException, Path, status

from ..core.auth import Role, auth_config
from ..models.clients import Client, ClientCreate
from ..services.clients import InMemoryClientService

router = APIRouter()
client_service = InMemoryClientService()

@router.get("/", response_model=List[Client], summary="List clients")
@auth_config(minimum_role=Role.STAFF)
async def list_clients():
    return list(client_service.list_clients())


@router.get("/{client_id}", response_model=Client, summary="Retrieve client profile")
@auth_config(minimum_role=Role.STAFF)
async def get_client(client_id: int = Path(gt=0)):
    client = client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
@auth_config(minimum_role=Role.MANAGER, scopes={"clients:write"})
async def create_client(payload: ClientCreate):
    return client_service.create_client(payload)
