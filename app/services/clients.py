from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Iterable, Optional, Literal

from ..models.clients import Cliente, ClienteCreate
from ..models.endereco import ClienteEnderecosUpdate, Endereco


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

    @abstractmethod
    async def update_client_addresses(
        self,
        client_id: int,
        payload: ClienteEnderecosUpdate,
    ) -> Iterable[Endereco]:
        ...

    @abstractmethod
    async def update_client_credit(
        self,
        client_id: int,
        delta: Decimal,
        operation: Literal["add", "delete"],
    ) -> Optional[Cliente]:
        ...


class ClientService(abc_ClientService):
    async def list_clients(self) -> Iterable[Cliente]:
        ...

    async def get_client(self, client_id: int) -> Optional[Cliente]:
        ...

    async def create_client(self, request: ClienteCreate) -> Cliente:
        ...

    async def update_client_addresses(
        self,
        client_id: int,
        payload: ClienteEnderecosUpdate,
    ) -> Iterable[Endereco]:
        ...

    async def update_client_credit(
        self,
        client_id: int,
        delta: Decimal,
        operation: Literal["add", "delete"],
    ) -> Optional[Cliente]:
        ...


class MockClientService(abc_ClientService):
    def __init__(self):
        today = date.today()
        now = datetime.now()

        self._clients: Dict[int, dict] = {
            1: {
                "cliente": Cliente(
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
                "enderecos": [
                    Endereco(
                        id=1,
                        cliente_id=1,
                        tipo="RESIDENCIAL",
                        logradouro="Rua das Flores",
                        numero="100",
                        complemento=None,
                        bairro_comunidade="Centro",
                        cidade_area="Cidade A",
                        referencia=None,
                        created_at=now,
                        updated_at=now,
                    ),
                    Endereco(
                        id=2,
                        cliente_id=1,
                        tipo="COMERCIAL",
                        logradouro="Av. do Trabalho",
                        numero="200",
                        complemento="Sala 5",
                        bairro_comunidade="Bairro B",
                        cidade_area="Cidade A",
                        referencia="Próximo ao shopping",
                        created_at=now,
                        updated_at=now,
                    ),
                    Endereco(
                        id=3,
                        cliente_id=1,
                        tipo="OUTRO",
                        logradouro="Estrada Velha",
                        numero="SN",
                        complemento=None,
                        bairro_comunidade="Zona Rural",
                        cidade_area="Cidade A",
                        referencia="Sítio da família",
                        created_at=now,
                        updated_at=now,
                    ),
                ],
            },
            2: {
                "cliente": Cliente(
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
                "enderecos": [
                    Endereco(
                        id=4,
                        cliente_id=2,
                        tipo="RESIDENCIAL",
                        logradouro="Rua das Palmeiras",
                        numero="50",
                        complemento=None,
                        bairro_comunidade="Jardins",
                        cidade_area="Cidade B",
                        referencia=None,
                        created_at=now,
                        updated_at=now,
                    ),
                    Endereco(
                        id=5,
                        cliente_id=2,
                        tipo="COMERCIAL",
                        logradouro="Av. Central",
                        numero="500",
                        complemento="Conj. 1203",
                        bairro_comunidade="Centro",
                        cidade_area="Cidade B",
                        referencia="Prédio azul",
                        created_at=now,
                        updated_at=now,
                    ),
                    Endereco(
                        id=6,
                        cliente_id=2,
                        tipo="OUTRO",
                        logradouro="Alameda Lazer",
                        numero="10",
                        complemento=None,
                        bairro_comunidade="Resort",
                        cidade_area="Cidade B",
                        referencia="Clube",
                        created_at=now,
                        updated_at=now,
                    ),
                ],
            },
        }
        self._sequence = max(self._clients.keys())
        self._endereco_sequence = max(
            endereco.id
            for item in self._clients.values()
            for endereco in item["enderecos"]
        )

    async def list_clients(self) -> Iterable[Cliente]:
        return sorted(
            (item["cliente"] for item in self._clients.values()),
            key=lambda client: client.nome,
        )

    async def get_client(self, client_id: int) -> Optional[Cliente]:
        data = self._clients.get(client_id)
        if not data:
            return None
        return data["cliente"]

    async def create_client(self, request: ClienteCreate) -> Cliente:
        self._sequence += 1
        now = datetime.utcnow()
        client = Cliente(
            id=self._sequence,
            created_at=now,
            updated_at=now,
            **request.model_dump(),
        )
        self._clients[self._sequence] = {
            "cliente": client,
            "enderecos": [],
        }
        return client

    async def update_client_addresses(
        self,
        client_id: int,
        payload: ClienteEnderecosUpdate,
    ) -> Iterable[Endereco]:
        data = self._clients.get(client_id)
        if not data:
            return []

        enderecos = data["enderecos"]
        now = datetime.utcnow()

        def upsert(tipo: str, fields_attr: str) -> None:
            fields = getattr(payload, fields_attr)
            if fields is None:
                return

            nonlocal enderecos
            existing = next((e for e in enderecos if e.tipo == tipo), None)
            if existing:
                updated = Endereco(
                    id=existing.id,
                    cliente_id=client_id,
                    tipo=tipo,  # type: ignore[arg-type]
                    logradouro=fields.logradouro,
                    numero=fields.numero,
                    complemento=fields.complemento,
                    bairro_comunidade=fields.bairro_comunidade,
                    cidade_area=fields.cidade_area,
                    referencia=fields.referencia,
                    created_at=existing.created_at,
                    updated_at=now,
                )
                enderecos = [
                    updated if e.id == existing.id else e for e in enderecos
                ]
            else:
                self._endereco_sequence += 1
                created = Endereco(
                    id=self._endereco_sequence,
                    cliente_id=client_id,
                    tipo=tipo,  # type: ignore[arg-type]
                    logradouro=fields.logradouro,
                    numero=fields.numero,
                    complemento=fields.complemento,
                    bairro_comunidade=fields.bairro_comunidade,
                    cidade_area=fields.cidade_area,
                    referencia=fields.referencia,
                    created_at=now,
                    updated_at=now,
                )
                enderecos.append(created)

        upsert("RESIDENCIAL", "residencial")
        upsert("COMERCIAL", "comercial")
        upsert("OUTRO", "outro")

        data["enderecos"] = enderecos
        return enderecos

    async def update_client_credit(
        self,
        client_id: int,
        delta: Decimal,
        operation: Literal["add", "delete"],
    ) -> Optional[Cliente]:
        data = self._clients.get(client_id)
        if not data:
            return None

        client: Cliente = data["cliente"]
        current = client.saldo_credito or Decimal("0.00")
        delta = delta.quantize(Decimal("0.01"))

        if delta < Decimal("0.00"):
            raise ValueError("Delta must be positive")

        if operation == "delete":
            if delta > current:
                raise ValueError("Insufficient credit to subtract requested amount")
            new_balance = current - delta
        elif operation == "add":
            new_balance = current + delta
        else:
            raise ValueError("Invalid operation, must be 'add' or 'delete'")

        # Ensure 2 decimal places
        new_balance = new_balance.quantize(Decimal("0.01"))

        updated = client.model_copy(
            update={
                "saldo_credito": new_balance,
                "updated_at": datetime.now(),
            }
        )
        data["cliente"] = updated
        self._clients[client_id] = data
        return updated
