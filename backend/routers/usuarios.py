from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user, require_admin
from ..models.usuario import Usuario
from ..schemas.usuario import UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
def list_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return db.query(Usuario).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UsuarioResponse)
def get_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    if current_user.nivel != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão.")
    return user


@router.put("/{user_id}", response_model=UsuarioResponse)
def update_usuario(
    user_id: int,
    update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    if current_user.nivel != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão.")
    for key, value in update.model_dump(exclude_unset=True).items():
        # Apenas admin pode alterar nível
        if key == "nivel" and current_user.nivel != "admin":
            continue
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    db.delete(user)
    db.commit()
