from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import User, Repository, Analysis
from app.schemas import AnalysisCreate, AnalysisOut
from app.workers.tasks import run_analysis_task

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisOut, status_code=201)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = db.get(Repository, payload.repo_id)
    if not repo or repo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.status != "ready":
        raise HTTPException(status_code=409, detail=f"Repository is not ready yet (status={repo.status})")

    analysis = Analysis(
        repo_id=repo.id,
        user_id=user.id,
        kind=payload.kind,
        question=payload.question,
        status="queued",
        progress=0,
        current_step="Queued",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    run_analysis_task.delay(analysis.id)
    return analysis


@router.get("", response_model=list[AnalysisOut])
def list_analyses(repo_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = select(Analysis).where(Analysis.user_id == user.id)
    if repo_id is not None:
        query = query.where(Analysis.repo_id == repo_id)
    query = query.order_by(Analysis.created_at.desc()).limit(100)
    return list(db.scalars(query))


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = db.get(Analysis, analysis_id)
    if not analysis or analysis.user_id != user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
