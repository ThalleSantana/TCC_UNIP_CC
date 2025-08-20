# app/main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .model.database import Base, engine
from .controller import users, posts, analysis

app = FastAPI(title="Sentiment Analysis MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Novo caminho para os arquivos HTML
BASE_VIEW_DIR = Path(__file__).resolve().parent / "view"
FRONTEND_DIR = Path(__file__).parent / "view" / "html"

# HTML
app.mount("/frontend", StaticFiles(directory=str(BASE_VIEW_DIR / "html"), html=True), name="frontend")

# CSS
app.mount("/css", StaticFiles(directory=str(BASE_VIEW_DIR / "css")), name="css")

# JS
app.mount("/js", StaticFiles(directory=str(BASE_VIEW_DIR / "js")), name="js")

Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(analysis.router)

@app.get("/health")
def health():
    return {"status": "ok", "frontend_dir": str(FRONTEND_DIR)}

# ✅ Redireciona para login.html
@app.get("/")
def root():
    return RedirectResponse(url="/frontend/login.html")

@app.get("/_routes")
def list_routes():
    return [getattr(r, "path", None) for r in app.routes]
