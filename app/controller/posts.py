from dotenv import load_dotenv
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from ..model import models, schemas
from ..services.deps import get_db, get_current_user
from ..services import sentiment_analysis

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/analyze")
def analyze_post(
    req: schemas.AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    video_link = str(req.url)
    load_dotenv()
    api_key = os.getenv("YOUTUBE_KEY")

    resultado = sentiment_analysis.analisar_sentimentos(video_link, api_key)
    if resultado is None:
        raise HTTPException(status_code=400, detail="Vídeo inválido ou sem comentários")

    qtd_pos, qtd_neg, qtd_neu, top_pos, top_neg, top_neu = resultado

    results = {
        "positive": {"count": qtd_pos, "top_words": top_pos},
        "negative": {"count": qtd_neg, "top_words": top_neg},
        "neutral": {"count": qtd_neu, "top_words": top_neu},
    }

    analysis = models.PostAnalysis(
        platform=req.platform.lower().strip(),
        url=str(req.url),
        status="completed",
        owner_id=current_user.id,
        created_at=datetime.now(ZoneInfo("America/Sao_Paulo")),
        summary_positive=results["positive"]["count"],
        summary_negative=results["negative"]["count"],
        summary_neutral=results["neutral"]["count"],
    )

    print(">>> Resultado:", results)
    print(">>> Analysis ID (antes do commit):", analysis.id)
    db.add(analysis)
    db.flush()
    print(">>> Analysis ID (depois do flush):", analysis.id)

    for label, data in results.items():
        for word in data["top_words"]:
            db.add(models.Comment(
                analysis_id=analysis.id,
                author="system",
                text=f"Palavra-chave: {word}",
                label=label,
                score=100
            ))

    try:
        db.commit()
        print(">>> Commit realizado com sucesso")
    except Exception as e:
        print(">>> Erro no commit:", e)
        db.rollback()

    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "summary": results,
        "message": "Análise concluída com provider real."
    }
