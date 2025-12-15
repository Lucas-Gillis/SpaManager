from typing import List, Literal
from decimal import Decimal

from fastapi import APIRouter, Body, HTTPException, Path, status
from pydantic import BaseModel, Field

from ..core.auth import Role, auth_config
from ..models.clients import Cliente, ClienteCreate
from ..models.endereco import ClienteEnderecosUpdate, Endereco
from ..services.clients import MockClientService
from ..models.appointments import Appointment
from ..services.appointments import InMemoryAppointmentService

router = APIRouter()
client_service = MockClientService()
appointment_service = InMemoryAppointmentService()


class ClienteSaldoCreditoUpdate(BaseModel):
    delta: Decimal = Field(gt=Decimal("0.00"))
    operation: Literal["add", "delete"]

@router.get("/", response_model=List[Cliente], summary="List clients")
@auth_config(minimum_role=Role.STAFF)
async def list_clients():
    return list(await client_service.list_clients())

@router.get("/{client_id}", response_model=Cliente, summary="Retrieve client profile")
@auth_config(minimum_role=Role.STAFF)
async def get_client(client_id: int = Path(gt=0)):
    client: Cliente | None = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client

@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
@auth_config(minimum_role=Role.MANAGER, scopes={"clients:write"})
async def create_client(payload: ClienteCreate):
    return await client_service.create_client(payload)

@router.put(
    "/{client_id}/enderecos",
    response_model=List[Endereco],
    summary="Update client addresses",
)
@auth_config(minimum_role=Role.MANAGER, scopes={"clients:write"})
async def update_client_addresses(
    client_id: int = Path(gt=0),
    payload: ClienteEnderecosUpdate = Body(...),
):
    client: Cliente | None = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return list(await client_service.update_client_addresses(client_id, payload))


@router.post(
    "/{client_id}/saldo-credito",
    response_model=Cliente,
    summary="Update client credit balance",
)
@auth_config(minimum_role=Role.MANAGER, scopes={"clients:write"})
async def update_client_credit(
    client_id: int = Path(gt=0),
    payload: ClienteSaldoCreditoUpdate = Body(...),
):
    try:
        updated: Cliente | None = await client_service.update_client_credit(
            client_id=client_id,
            delta=payload.delta,
            operation=payload.operation,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return updated


@router.get(
    "/{client_id}/appointments",
    response_model=List[Appointment],
    summary="List client appointments",
)
@auth_config(minimum_role=Role.STAFF)
async def list_client_appointments(client_id: int = Path(gt=0)):
    client: Cliente | None = await client_service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return list(appointment_service.list_client_appointments(client_id))
