from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)

    artigos = relationship("Artigo", back_populates="categoria")
