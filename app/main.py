# app/main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .database import Base, engine
from .routers import users, posts, analysis

# 1) Cria a app ANTES de usar app.*
app = FastAPI(title="Sentiment Analysis MVP", version="0.1.0")

# 2) CORS (útil no dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ajusta SE quiser restringir
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Monta o diretório do frontend (caminho absoluto)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# 4) Banco e rotas
Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(analysis.router)

# 5) Rotas utilitárias
@app.get("/health")
def health():
    return {"status": "ok", "frontend_dir": str(FRONTEND_DIR)}

@app.get("/")
def root():
    return RedirectResponse(url="/frontend/")  # abre o index.html

# (opcional) listar rotas para debug
@app.get("/_routes")
def list_routes():
    return [getattr(r, "path", None) for r in app.routes]
