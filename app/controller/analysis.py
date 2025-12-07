from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..model import models, schemas
from ..services.deps import get_db, get_current_user
from ..services.sentiment import MockSentimentProvider
from datetime import datetime
from ..controller.posts import analyze_post

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/", response_model=None)
def list_analyses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rows = (
        db.query(models.PostAnalysis)
        .filter(models.PostAnalysis.owner_id == current_user.id)
        .order_by(models.PostAnalysis.id.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "platform": r.platform,
            "url": r.url,
            "summary_positive": r.summary_positive,
            "summary_neutral": r.summary_neutral,
            "summary_negative": r.summary_negative,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

@router.get("/{analysis_id}", response_model=schemas.AnalysisOut)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    analysis = (
        db.query(models.PostAnalysis)
        .filter(
            models.PostAnalysis.id == analysis_id,
            models.PostAnalysis.owner_id == current_user.id
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada."
        )

    return analysis

@router.post("/create", response_model=schemas.AnalysisOut)
def create_analysis(
    data: schemas.AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        result = analyze_post(data.platform, data.url)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar a análise: {str(e)}"
        )

    analysis = models.PostAnalysis(
        owner_id=current_user.id,
        platform=data.platform.lower().strip(),
        url=str(data.url),
        status="completed",
        summary_positive=result.get("summary_positive", 0),
        summary_neutral=result.get("summary_neutral", 0),
        summary_negative=result.get("summary_negative", 0),
        created_at=datetime.utcnow()
    )

    db.add(analysis)
    db.flush()  
    comments = result.get("comments", [])
    for c in comments:
        db.add(models.Comment(
            analysis_id=analysis.id,
            author=c.get("author"),
            text=c.get("text"),
            label=c.get("label"),
            score=c.get("score")
        ))

    db.commit()
    db.refresh(analysis)

    return analysis
