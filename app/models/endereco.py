from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

EnderecoTipo = Literal["RESIDENCIAL", "COMERCIAL", "OUTRO"]

class EnderecoBase(BaseModel):
    cliente_id: int
    tipo: EnderecoTipo
    logradouro: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro_comunidade: Optional[str] = None
    cidade_area: Optional[str] = None
    referencia: Optional[str] = None


class EnderecoCreate(EnderecoBase):
    pass


class Endereco(EnderecoBase):
    id: int
    created_at: datetime
    updated_at: datetime


class EnderecoUpdateFields(BaseModel):
    logradouro: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro_comunidade: Optional[str] = None
    cidade_area: Optional[str] = None
    referencia: Optional[str] = None


class ClienteEnderecosUpdate(BaseModel):
    residencial: Optional[EnderecoUpdateFields] = None
    comercial: Optional[EnderecoUpdateFields] = None
    outro: Optional[EnderecoUpdateFields] = None
