from pydantic import BaseModel, ConfigDict
from datetime import datetime


class VisualizacaoResponse(BaseModel):
    id: int
    artigo_id: int
    usuario_id: int
    data_visualizacao: datetime

    model_config = ConfigDict(from_attributes=True)
