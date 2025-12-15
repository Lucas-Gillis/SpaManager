from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Annotated

from pydantic import BaseModel, BeforeValidator, ValidationError


FuncionarioSexo = Literal["M", "F", "O"]
TipoFuncionario = Literal["TECNICO", "ADMINISTRATIVO", "AMBOS"]

def chck_cvt_str_dec2(val : str) -> Decimal:
    try:    
        val = str(val).strip().replace(',','.')
        return Decimal(val).quantize(Decimal('0.01'))
    except Exception:
        raise ValueError("Input should be convertable to Decimal")

class FuncionarioBase(BaseModel):
    nome: str
    sexo: Optional[FuncionarioSexo] = None
    tipo_funcionario: TipoFuncionario
    email: Optional[str] = None
    elegivel_comissao: bool = False
    salario_fixo_mensal: Annotated[Decimal, BeforeValidator(chck_cvt_str_dec2)] = Decimal("0.00")
    ativo: bool = True


class FuncionarioCreate(FuncionarioBase):
    pass


class Funcionario(FuncionarioBase):
    id: int
    created_at: datetime
    updated_at: datetime


class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    sexo: Optional[FuncionarioSexo] = None
    tipo_funcionario: Optional[TipoFuncionario] = None
    email: Optional[str] = None
    elegivel_comissao: Optional[bool] = None
    salario_fixo_mensal: Annotated[Decimal, BeforeValidator(chck_cvt_str_dec2)] = Decimal("0.00")
    ativo: Optional[bool] = None


class FuncionarioStatusUpdate(BaseModel):
    ativo: bool


class FuncionarioServicoBase(BaseModel):
    funcionario_id: int
    servico_id: int
    duracao_base_min_func: Optional[int] = None
    preco_base_funcionario: Annotated[Decimal, BeforeValidator(chck_cvt_str_dec2)] = Decimal("0.00")
    comissao_percentual: Annotated[Decimal, BeforeValidator(chck_cvt_str_dec2)] = Decimal("0.00")


class FuncionarioServicoCreate(FuncionarioServicoBase):
    pass


class FuncionarioServico(FuncionarioServicoBase):
    pass

