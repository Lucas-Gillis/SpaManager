from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel

from ..core.auth import AuthenticatedUser, Role, auth_config, authorize
from ..models.appointments import Appointment, AppointmentCreate, AppointmentStatus
from ..services.appointments import InMemoryAppointmentService


router = APIRouter()
appointment_service = InMemoryAppointmentService()


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


@router.get("/", response_model=List[Appointment])
@auth_config(minimum_role=Role.STAFF)
async def list_appointments(
    current_user: AuthenticatedUser = Depends(authorize),
):
    return list(appointment_service.list_appointments())


@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
@auth_config(minimum_role=Role.MANAGER, scopes={"appointments:write"})
async def create_appointment(
    payload: AppointmentCreate,
    current_user: AuthenticatedUser = Depends(authorize),
):
    return appointment_service.create_appointment(payload)


@router.patch(
    "/{appointment_id}/status",
    response_model=Appointment,
    summary="Update appointment status",
)
@auth_config(minimum_role=Role.STAFF, scopes={"appointments:write"})
async def update_status(
    payload: AppointmentStatusUpdate,
    appointment_id: int = Path(gt=0),
    current_user: AuthenticatedUser = Depends(authorize),
):
    appointment = appointment_service.update_status(appointment_id, payload.status)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment
