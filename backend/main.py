from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import Base, engine, mongodb
from .routers import auth_router, artigos_router, categorias_router, usuarios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cria tabelas e conecta ao MongoDB
    Base.metadata.create_all(bind=engine)
    try:
        await mongodb.connect()
    except Exception:
        pass  # MongoDB é opcional (feature de log)
    yield
    # Shutdown
    await mongodb.close()


app = FastAPI(
    title="Support Knowledge Hub API",
    description="API REST para base de conhecimento de suporte técnico.",
    version="2.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Security Headers ────────────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(artigos_router)
app.include_router(categorias_router)
app.include_router(usuarios_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "Support Knowledge Hub API"}
