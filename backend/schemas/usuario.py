from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    nivel: Optional[str] = "tecnico"


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    nivel: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
