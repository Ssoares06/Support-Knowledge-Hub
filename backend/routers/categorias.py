from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..middleware.auth_middleware import require_admin
from ..models.categoria import Categoria
from ..schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter(prefix="/api/categorias", tags=["categorias"])


@router.get("/", response_model=List[CategoriaResponse])
def list_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Categoria).offset(skip).limit(limit).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    return categoria


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    if db.query(Categoria).filter(Categoria.nome == categoria.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma categoria com este nome.",
        )
    new_cat = Categoria(**categoria.model_dump())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update_categoria(
    categoria_id: int,
    update: CategoriaUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    db.delete(cat)
    db.commit()
