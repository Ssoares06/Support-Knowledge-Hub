from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Visualizacao(Base):
    __tablename__ = "visualizacoes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    artigo_id = Column(Integer, ForeignKey("artigos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_visualizacao = Column(DateTime(timezone=True), server_default=func.now())

    artigo = relationship("Artigo", back_populates="visualizacoes")
    usuario = relationship("Usuario")
