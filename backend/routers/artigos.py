from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user, require_admin
from ..models.artigo import Artigo
from ..models.usuario import Usuario
from ..models.visualizacao import Visualizacao
from ..schemas.artigo import ArtigoCreate, ArtigoResponse, ArtigoUpdate
from ..services.artigo_service import log_search_query

router = APIRouter(prefix="/api/artigos", tags=["artigos"])

# ─── Rotas ESTÁTICAS — devem vir ANTES de /{artigo_id} ──────────────────────


@router.get("/populares", response_model=List[ArtigoResponse])
def get_populares(db: Session = Depends(get_db)):
    return db.query(Artigo).order_by(desc(Artigo.total_visualizacoes)).limit(5).all()


@router.get("/recentes", response_model=List[ArtigoResponse])
def get_recentes(db: Session = Depends(get_db)):
    return db.query(Artigo).order_by(desc(Artigo.data_criacao)).limit(5).all()


@router.get("/busca", response_model=List[ArtigoResponse])
async def search_artigos(
    q: str = Query(..., min_length=1, description="Termo de busca"),
    db: Session = Depends(get_db),
):
    artigos = (
        db.query(Artigo)
        .filter(
            or_(
                Artigo.titulo.ilike(f"%{q}%"),
                Artigo.problema.ilike(f"%{q}%"),
                Artigo.solucao.ilike(f"%{q}%"),
            )
        )
        .all()
    )
    # Log assíncrono no MongoDB (falha silenciosa se MongoDB indisponível)
    try:
        await log_search_query(q, None, len(artigos))
    except Exception:
        pass
    return artigos


# ─── Rotas de coleção ────────────────────────────────────────────────────────


@router.get("/", response_model=List[ArtigoResponse])
def list_artigos(
    sistema: Optional[str] = None,
    categoria_id: Optional[int] = None,
    autor_id: Optional[int] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Artigo)
    if sistema:
        query = query.filter(Artigo.sistema == sistema)
    if categoria_id:
        query = query.filter(Artigo.categoria_id == categoria_id)
    if autor_id:
        query = query.filter(Artigo.autor_id == autor_id)
    if q:
        query = query.filter(
            or_(
                Artigo.titulo.ilike(f"%{q}%"),
                Artigo.problema.ilike(f"%{q}%"),
                Artigo.solucao.ilike(f"%{q}%"),
            )
        )
    return query.offset((page - 1) * limit).limit(limit).all()


@router.post("/", response_model=ArtigoResponse, status_code=status.HTTP_201_CREATED)
def create_artigo(
    artigo: ArtigoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    new_art = Artigo(**artigo.model_dump(), autor_id=current_user.id)
    db.add(new_art)
    db.commit()
    db.refresh(new_art)
    return new_art


# ─── Rotas DINÂMICAS — /{artigo_id} ─────────────────────────────────────────


@router.get("/{artigo_id}", response_model=ArtigoResponse)
def get_artigo(artigo_id: int, db: Session = Depends(get_db)):
    artigo = db.query(Artigo).filter(Artigo.id == artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado.")
    return artigo


@router.put("/{artigo_id}", response_model=ArtigoResponse)
def update_artigo(
    artigo_id: int,
    update: ArtigoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    artigo = db.query(Artigo).filter(Artigo.id == artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado.")
    if artigo.autor_id != current_user.id and current_user.nivel != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar este artigo.")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(artigo, key, value)
    db.commit()
    db.refresh(artigo)
    return artigo


@router.delete("/{artigo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artigo(
    artigo_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    artigo = db.query(Artigo).filter(Artigo.id == artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado.")
    db.delete(artigo)
    db.commit()


@router.post("/{artigo_id}/visualizar", status_code=status.HTTP_200_OK)
def registrar_visualizacao(
    artigo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    artigo = db.query(Artigo).filter(Artigo.id == artigo_id).first()
    if not artigo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado.")
    artigo.total_visualizacoes += 1
    db.add(Visualizacao(artigo_id=artigo_id, usuario_id=current_user.id))
    db.commit()
    return {"detail": "Visualização registrada."}
