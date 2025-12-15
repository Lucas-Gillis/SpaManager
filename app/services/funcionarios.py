from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, Iterable, Optional, Tuple

from decimal import Decimal

from ..models.funcionarios import (
    Funcionario,
    FuncionarioCreate,
    FuncionarioServico,
    FuncionarioServicoCreate,
    FuncionarioStatusUpdate,
    FuncionarioUpdate,
)

class MockFuncionarioService:
    """
    In-memory mock for `funcionario` and `funcionario_servico` tables.
    """

    def __init__(self):
        now = datetime.utcnow()
        self._id_sequence = count(1)
        # Base funcionarios
        self._funcionarios: Dict[int, Funcionario] = {
            1: Funcionario(
                id=1,
                nome="Sara Staff",
                sexo="F",
                tipo_funcionario="TECNICO",
                email="staff@example.com",
                elegivel_comissao=True,
                ativo=True,
                created_at=now,
                updated_at=now,
            ),
            2: Funcionario(
                id=2,
                nome="Mark Manager",
                sexo="M",
                tipo_funcionario="ADMINISTRATIVO",
                email="manager@example.com",
                elegivel_comissao=False,
                salario_fixo_mensal=Decimal("500.00"),
                ativo=True,
                created_at=now,
                updated_at=now,
            ),
        }
        # Initialise sequence after seeded data
        self._id_sequence = count(len(self._funcionarios) + 1)

        # funcionario_servico entries keyed by (funcionario_id, servico_id)
        self._funcionario_servicos: Dict[Tuple[int, int], FuncionarioServico] = {}

    # Funcionario CRUD

    def list_funcionarios(self) -> Iterable[Funcionario]:
        return sorted(self._funcionarios.values(), key=lambda f: f.nome)

    def get_funcionario(self, funcionario_id: int) -> Optional[Funcionario]:
        return self._funcionarios.get(funcionario_id)

    def create_funcionario(self, payload: FuncionarioCreate) -> Funcionario:
        identifier = next(self._id_sequence)
        now = datetime.utcnow()
        funcionario = Funcionario(
            id=identifier,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        self._funcionarios[identifier] = funcionario
        return funcionario

    def update_funcionario(
        self,
        funcionario_id: int,
        payload: FuncionarioUpdate,
    ) -> Optional[Funcionario]:
        existing = self._funcionarios.get(funcionario_id)
        if not existing:
            return None

        updated = existing.model_copy(
            update={
                **{k: v for k, v in payload.model_dump(exclude_unset=True).items()},
                "updated_at": datetime.utcnow(),
            }
        )
        self._funcionarios[funcionario_id] = updated
        return updated

    def update_status(
        self,
        funcionario_id: int,
        payload: FuncionarioStatusUpdate,
    ) -> Optional[Funcionario]:
        existing = self._funcionarios.get(funcionario_id)
        if not existing:
            return None
        updated = existing.model_copy(
            update={"ativo": payload.ativo, "updated_at": datetime.utcnow()}
        )
        self._funcionarios[funcionario_id] = updated
        return updated

    # Funcionario x Servico

    def list_funcionario_servicos(self, funcionario_id: int) -> Iterable[FuncionarioServico]:
        return sorted(
            (
                fs
                for (fid, _), fs in self._funcionario_servicos.items()
                if fid == funcionario_id
            ),
            key=lambda fs: fs.servico_id,
        )

    def create_or_update_funcionario_servico(
        self,
        payload: FuncionarioServicoCreate,
    ) -> FuncionarioServico:
        key = (payload.funcionario_id, payload.servico_id)
        existing = self._funcionario_servicos.get(key)
        if existing:
            updated = existing.model_copy(
                update=payload.model_dump(exclude={"funcionario_id", "servico_id"}, exclude_unset=True),
            )
            self._funcionario_servicos[key] = updated
            return updated

        created = FuncionarioServico(**payload.model_dump())
        self._funcionario_servicos[key] = created
        return created

