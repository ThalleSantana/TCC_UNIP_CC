# app/main.py
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl
from app.services.sentiment_analysis import analisar_sentimentos
import os
load_dotenv()

from .model.database import Base, engine
from .controller import users, posts, analysis

app = FastAPI(title="EmoSync", version="2.0.0")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
app.mount("/frontend/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/frontend/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
app.mount("/frontend/html", StaticFiles(directory=str(FRONTEND_DIR / "html")), name="html")

Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(analysis.router)

@app.get("/health")
def health():
    return {"status": "ok", "frontend_dir": str(FRONTEND_DIR)}

@app.get("/")
def root():
    return RedirectResponse(url="/frontend/html/login.html")

@app.get("/_routes")
def list_routes():
    return [getattr(r, "path", None) for r in app.routes]

class VideoRequest(BaseModel):
    url: HttpUrl

@app.post("/analyze")
def analyze(video: VideoRequest):
    resultado = analisar_sentimentos(str(video.url), YOUTUBE_KEY)
    if resultado is None:
        return {"error": "Vídeo inválido ou sem comentários"}
    qtd_pos, qtd_neg, qtd_neu, top_pos, top_neg, top_neu = resultado
    return {
        "positivo": qtd_pos,
        "negativo": qtd_neg,
        "neutro": qtd_neu,
        "top_pos": top_pos,
        "top_neg": top_neg,
        "top_neu": top_neu
    }