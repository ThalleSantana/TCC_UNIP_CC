from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..deps import get_db, get_current_user
from ..services.sentiment import MockSentimentProvider

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/analyze")
def analyze_post(req: schemas.AnalyzeRequest, 
                 db: Session = Depends(get_db), 
                 current_user: models.User = Depends(get_current_user)):
    # TODO: coletar comentários reais da plataforma indicada (req.platform, req.url)
    # Por enquanto, comentários fictícios:
    fake_comments = [
        {"author": "user1", "text": "Amei esse produto, ficou perfeito!"},
        {"author": "user2", "text": "Ruim demais, não recomendo."},
        {"author": "user3", "text": "Achei ok, nada demais."},
        {"author": "user4", "text": "Maravilhoso! Gostei bastante."},
        {"author": "user5", "text": "Péssimo atendimento."},
    ]

    analyzer = MockSentimentProvider()
    labels = analyzer.analyze([c["text"] for c in fake_comments])

    analysis = models.PostAnalysis(
        platform=req.platform.lower().strip(),
        url=str(req.url),
        status="completed",
        owner_id=current_user.id
    )
    db.add(analysis)
    db.flush()

    pos = neg = neu = 0
    for c, (label, score) in zip(fake_comments, labels):
        if label == "positive":
            pos += 1
        elif label == "negative":
            neg += 1
        else:
            neu += 1
        db.add(models.Comment(
            analysis_id=analysis.id,
            author=c.get("author"),
            text=c["text"],
            label=label,
            score=score
        ))
    analysis.summary_positive = pos
    analysis.summary_negative = neg
    analysis.summary_neutral = neu

    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "summary": {"positive": pos, "negative": neg, "neutral": neu},
        "message": "Análise concluída (mock)."
    }
