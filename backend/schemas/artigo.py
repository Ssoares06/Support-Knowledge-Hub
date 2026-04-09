from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from .categoria import CategoriaResponse
from .usuario import UsuarioResponse


class ArtigoBase(BaseModel):
    titulo: str
    problema: str
    causa: Optional[str] = None
    solucao: str
    sistema: Optional[str] = None
    categoria_id: Optional[int] = None
    link_glpi: Optional[str] = None
    link_colmeia: Optional[str] = None


class ArtigoCreate(ArtigoBase):
    pass


class ArtigoUpdate(BaseModel):
    titulo: Optional[str] = None
    problema: Optional[str] = None
    causa: Optional[str] = None
    solucao: Optional[str] = None
    sistema: Optional[str] = None
    categoria_id: Optional[int] = None
    link_glpi: Optional[str] = None
    link_colmeia: Optional[str] = None


class ArtigoResponse(ArtigoBase):
    id: int
    autor_id: int
    data_criacao: date
    total_visualizacoes: int
    categoria: Optional[CategoriaResponse] = None
    autor: Optional[UsuarioResponse] = None

    model_config = ConfigDict(from_attributes=True)
