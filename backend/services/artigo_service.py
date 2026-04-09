from datetime import datetime, UTC
from ..database import mongodb


async def log_search_query(termo: str, usuario_id: int | None, resultados_count: int):
    """Logs a search query to MongoDB collection `logs_busca`."""
    if mongodb.db is None:
        return
    collection = mongodb.db["logs_busca"]
    await collection.insert_one(
        {
            "termo_buscado": termo,
            "usuario_id": usuario_id,
            "timestamp": datetime.now(UTC),
            "resultados_encontrados": resultados_count,
        }
    )
