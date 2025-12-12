from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class ClienteBase(BaseModel):
    nome: str
    sexo: Optional[Literal["M", "F", "O"]] = None
    data_nascimento: Optional[date] = None
    como_conheceu_id: Optional[int] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    saldo_credito: Optional[Decimal] = None
    observacoes: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class Cliente(ClienteBase):
    id: int
    created_at: datetime
    updated_at: datetime
