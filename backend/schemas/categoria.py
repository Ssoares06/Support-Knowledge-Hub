from pydantic import BaseModel, ConfigDict
from typing import Optional


class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None


class CategoriaResponse(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
