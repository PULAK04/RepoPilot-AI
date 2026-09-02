from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import User, Repository
from app.schemas import RepositoryCreate, RepositoryOut
from app.services.github import parse_github_url, GitHubService
from app.workers.tasks import sync_repository

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("", response_model=RepositoryOut, status_code=201)
def create_repository(
    payload: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        ref = parse_github_url(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    gh = GitHubService()

    try:
        info = gh.repo_info(ref.owner, ref.name)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not access repository: {exc}"
        )

    branch = payload.branch or info.get("default_branch") or "main"

    existing = db.scalar(
        select(Repository).where(
            Repository.user_id == user.id,
            Repository.owner == ref.owner,
            Repository.name == ref.name,
            Repository.branch == branch,
        )
    )

    if existing:
        return existing

    repo = Repository(
        user_id=user.id,
        owner=ref.owner,
        name=ref.name,
        url=f"https://github.com/{ref.owner}/{ref.name}",
        branch=branch,
        status="queued",
    )

    db.add(repo)
    db.commit()
    db.refresh(repo)

    background_tasks.add_task(sync_repository, repo.id)

    return repo


@router.get("", response_model=list[RepositoryOut])
def list_repositories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(Repository).where(Repository.user_id == user.id).order_by(Repository.created_at.desc())))


@router.get("/{repo_id}", response_model=RepositoryOut)
def get_repository(repo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = db.get(Repository, repo_id)
    if not repo or repo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.post("/{repo_id}/reindex", response_model=RepositoryOut)
def reindex_repository(repo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = db.get(Repository, repo_id)
    if not repo or repo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Repository not found")
    repo.status = "queued"
    repo.last_error = None
    db.commit()
    background_tasks.add_task(sync_repository, repo.id)
    return repo
