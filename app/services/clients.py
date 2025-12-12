from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Iterable, Optional

from ..models.clients import Cliente, ClienteCreate


class abc_ClientService(ABC):
    @abstractmethod
    async def list_clients(self) -> Iterable[Cliente]:
        ...

    @abstractmethod
    async def get_client(self, client_id: int) -> Optional[Cliente]:
        ...

    @abstractmethod
    async def create_client(self, request: ClienteCreate) -> Cliente:
        ...


class ClientService(abc_ClientService):
    async def list_clients(self) -> Iterable[Cliente]:
        ...

    async def get_client(self, client_id: int) -> Optional[Cliente]:
        ...

    async def create_client(self, request: ClienteCreate) -> Cliente:
        ...


class MockClientService(abc_ClientService):
    def __init__(self):
        today = date.today()
        now = datetime.utcnow()
        self._clients: Dict[int, Cliente] = {
            1: Cliente(
                id=1,
                nome="Célia Cliente",
                sexo="F",
                data_nascimento=date(1990, 1, 1),
                como_conheceu_id=None,
                telefone="555-0001",
                email="celia@example.com",
                saldo_credito=Decimal("100.00"),
                observacoes=None,
                created_at=now,
                updated_at=now,
            ),
            2: Cliente(
                id=2,
                nome="Pedro Patrono",
                sexo="M",
                data_nascimento=date(1985, 5, 15),
                como_conheceu_id=None,
                telefone="555-0002",
                email="peter@example.com",
                saldo_credito=Decimal("250.00"),
                observacoes="Cliente frequente.",
                created_at=now,
                updated_at=now,
            ),
        }
        self._sequence = max(self._clients.keys())

    async def list_clients(self) -> Iterable[Cliente]:
        return sorted(self._clients.values(), key=lambda client: client.nome)

    async def get_client(self, client_id: int) -> Optional[Cliente]:
        return self._clients.get(client_id)

    async def create_client(self, request: ClienteCreate) -> Cliente:
        self._sequence += 1
        now = datetime.utcnow()
        client = Cliente(
            id=self._sequence,
            created_at=now,
            updated_at=now,
            **request.model_dump(),
        )
        self._clients[self._sequence] = client
        return client
