from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request, status

from ..core.auth import (
    AuthenticatedUser,
    Role,
    auth_config,
    authorize,
    get_current_user,
)
from ..models.funcionarios import (
    Funcionario,
    FuncionarioCreate,
    FuncionarioServico,
    FuncionarioServicoCreate,
    FuncionarioStatusUpdate,
    FuncionarioUpdate,
)
from ..models.appointments import Appointment
from ..services.appointments import InMemoryAppointmentService
from ..services.funcionarios import MockFuncionarioService


router = APIRouter()
funcionario_service = MockFuncionarioService()
appointment_service = InMemoryAppointmentService()


@router.get("/", response_model=List[Funcionario], summary="List funcionarios")
@auth_config(minimum_role=Role.MANAGER)
async def list_funcionarios(
    current_user: AuthenticatedUser = Depends(authorize),
):
    return list(funcionario_service.list_funcionarios())


@router.get(
    "/{funcionario_id}",
    response_model=Funcionario,
    summary="Retrieve funcionario profile",
)
@auth_config(minimum_role=Role.MANAGER)
async def get_funcionario(
    funcionario_id: int = Path(gt=0),
    current_user: AuthenticatedUser = Depends(authorize),
):
    funcionario = funcionario_service.get_funcionario(funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    return funcionario


@router.post(
    "/",
    response_model=Funcionario,
    status_code=status.HTTP_201_CREATED,
    summary="Create funcionario",
)
@auth_config(minimum_role=Role.MANAGER, scopes={"staff:manage"})
async def create_funcionario(
    payload: FuncionarioCreate,
    current_user: AuthenticatedUser = Depends(authorize),
):
    return funcionario_service.create_funcionario(payload)


@router.put(
    "/{funcionario_id}",
    response_model=Funcionario,
    summary="Update funcionario",
)
@auth_config(minimum_role=Role.MANAGER, scopes={"staff:manage"})
async def update_funcionario(
    funcionario_id: int = Path(gt=0),
    payload: FuncionarioUpdate = Body(...),
    current_user: AuthenticatedUser = Depends(authorize),
):
    funcionario = funcionario_service.update_funcionario(funcionario_id, payload)
    if not funcionario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    return funcionario


@router.patch(
    "/{funcionario_id}/status",
    response_model=Funcionario,
    summary="Update funcionario status",
)
@auth_config(minimum_role=Role.MANAGER, scopes={"staff:manage"})
async def update_funcionario_status(
    funcionario_id: int = Path(gt=0),
    payload: FuncionarioStatusUpdate = Body(...),
    current_user: AuthenticatedUser = Depends(authorize),
):
    funcionario = funcionario_service.update_status(funcionario_id, payload)
    if not funcionario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    return funcionario


@router.get(
    "/{funcionario_id}/servicos",
    response_model=List[FuncionarioServico],
    summary="List services assigned to funcionario",
)
@auth_config(minimum_role=Role.MANAGER)
async def list_funcionario_servicos(
    funcionario_id: int = Path(gt=0),
    current_user: AuthenticatedUser = Depends(authorize),
):
    # Ensure funcionario exists
    funcionario = funcionario_service.get_funcionario(funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    return list(funcionario_service.list_funcionario_servicos(funcionario_id))


@router.post(
    "/{funcionario_id}/servicos",
    response_model=FuncionarioServico,
    status_code=status.HTTP_201_CREATED,
    summary="Assign service to funcionario",
)
@auth_config(minimum_role=Role.MANAGER, scopes={"staff:manage"})
async def create_funcionario_servico(
    funcionario_id: int = Path(gt=0),
    payload: FuncionarioServicoCreate = Body(...),
    current_user: AuthenticatedUser = Depends(authorize),
):
    if payload.funcionario_id != funcionario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Body funcionario_id must match path parameter",
        )

    funcionario = funcionario_service.get_funcionario(funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionario not found")

    return funcionario_service.create_or_update_funcionario_servico(payload)


@router.get(
    "/{funcionario_id}/agenda",
    response_model=List[Appointment],
    summary="List agenda for funcionario",
)
@auth_config(minimum_role=Role.STAFF)
async def list_funcionario_agenda(
    request: Request,
    funcionario_id: int = Path(gt=0),
    current_user: AuthenticatedUser = Depends(authorize),
):
    # For now, we approximate agenda by filtering appointments whose staff_member
    # name matches the funcionario's nome in the mock data.
    funcionario = funcionario_service.get_funcionario(funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")

    # Access rules:
    # - MANAGER and above can see all agendas.
    # - Funcionarios of tipo ADMINISTRATIVO can see all agendas.
    # - Other staff can only see their own agenda.
    is_manager = current_user.role >= Role.MANAGER
    is_admin_staff = False

    if not is_manager and current_user.full_name:
        # Try to resolve the current user as a funcionario to inspect tipo_funcionario.
        for f in funcionario_service.list_funcionarios():
            if f.nome == current_user.full_name:
                is_admin_staff = f.tipo_funcionario == "ADMINISTRATIVO"
                break

    if not (is_manager or is_admin_staff) and current_user.full_name != funcionario.nome:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden to access other agendas")

    all_appointments = appointment_service.list_appointments()
    return [
        appt
        for appt in all_appointments
        if appt.staff_member == funcionario.nome
    ]
