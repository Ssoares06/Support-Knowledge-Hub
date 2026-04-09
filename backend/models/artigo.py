from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Artigo(Base):
    __tablename__ = "artigos"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    titulo = Column(String(200), nullable=False)
    problema = Column(Text, nullable=False)
    causa = Column(Text, nullable=True)
    solucao = Column(Text, nullable=False)
    sistema = Column(String(100), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    link_glpi = Column(String(255), nullable=True)
    link_colmeia = Column(String(255), nullable=True)
    data_criacao = Column(Date, server_default=func.current_date())
    total_visualizacoes = Column(Integer, default=0)

    categoria = relationship("Categoria", back_populates="artigos")
    autor = relationship("Usuario")
    visualizacoes = relationship(
        "Visualizacao", back_populates="artigo", cascade="all, delete-orphan"
    )
