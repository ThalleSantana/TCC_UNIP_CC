from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..model import models, schemas
from ..services.deps import get_db, get_current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/", response_model=None)
def list_analyses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    rows = (db.query(models.PostAnalysis)
              .filter(models.PostAnalysis.owner_id == current_user.id)
              .order_by(models.PostAnalysis.id.desc())
              .all())
    return [{
        "id": r.id,
        "platform": r.platform,
        "url": r.url,
        "summary_positive": r.summary_positive,
        "summary_neutral": r.summary_neutral,
        "summary_negative": r.summary_negative,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    } for r in rows]


@router.get("/{analysis_id}", response_model=schemas.AnalysisOut)
def get_analysis(analysis_id: int,
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    analysis = db.query(models.PostAnalysis).filter(
        models.PostAnalysis.id == analysis_id,
        models.PostAnalysis.owner_id == current_user.id
    ).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análise não encontrada.")
    return analysis
