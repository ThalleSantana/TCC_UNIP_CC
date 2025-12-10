from datetime import datetime
from zoneinfo import ZoneInfo
from ..model import models

def create_analysis_service(platform, url, db, current_user, results):
    analysis = models.PostAnalysis(
        platform=platform.lower().strip(),
        url=str(url),
        status="completed",
        owner_id=current_user.id,
        created_at=datetime.now(ZoneInfo("America/Sao_Paulo")),
        summary_positive=results["positive"]["count"],
        summary_negative=results["negative"]["count"],
        summary_neutral=results["neutral"]["count"],
    )
    db.add(analysis)
    db.flush()

    for label, data in results.items():
        for word in data["top_words"]:
            db.add(models.Comment(
                analysis_id=analysis.id,
                author="system",
                text=f"Palavra-chave: {word}",
                label=label,
                score=100
            ))

    db.commit()
    db.refresh(analysis)
    return analysis
