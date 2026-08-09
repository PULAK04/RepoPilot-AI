import asyncio
from celery.utils.log import get_task_logger
from sqlalchemy import select
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import Repository, Analysis
from app.services.github import GitHubService
from app.services.repo_parser import chunk_text
from app.services.vector_store import vector_store
from app.services.progress import progress_service
from app.agents.graph import repo_graph

logger = get_task_logger(__name__)


@celery_app.task(name="sync_repository")
def sync_repository_task(repo_id: int):
    db = SessionLocal()
    try:
        repo = db.get(Repository, repo_id)
        if not repo:
            return
        repo.status = "indexing"
        repo.last_error = None
        db.commit()

        gh = GitHubService()
        info = gh.repo_info(repo.owner, repo.name)
        if not repo.branch or repo.branch == "auto":
            repo.branch = info.get("default_branch", "main")
            db.commit()
        files = gh.list_files(repo.owner, repo.name, repo.branch)

        chunks = []
        indexed_files = 0
        for item in files:
            text = gh.get_text_file(repo.owner, repo.name, item["path"], repo.branch)
            if text is None:
                continue
            file_chunks = chunk_text(item["path"], text)
            if file_chunks:
                chunks.extend(file_chunks)
                indexed_files += 1

        vector_store.delete_repo(repo.id)
        vector_store.upsert_chunks(repo.id, chunks)
        repo.status = "ready"
        repo.file_count = indexed_files
        db.commit()
        return {"repo_id": repo.id, "files": indexed_files, "chunks": len(chunks)}
    except Exception as exc:
        logger.exception("Repository indexing failed")
        repo = db.get(Repository, repo_id)
        if repo:
            repo.status = "failed"
            repo.last_error = str(exc)[:2000]
            db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="run_analysis")
def run_analysis_task(analysis_id: int):
    db = SessionLocal()
    try:
        analysis = db.get(Analysis, analysis_id)
        if not analysis:
            return
        analysis.status = "running"
        analysis.progress = 5
        analysis.current_step = "Starting multi-agent analysis"
        db.commit()
        progress_service.set(analysis.id, 5, analysis.current_step)

        initial = {
            "analysis_id": analysis.id,
            "repo_id": analysis.repo_id,
            "kind": analysis.kind,
            "question": analysis.question,
            "findings": [],
            "attempt": 0,
        }
        result = repo_graph.invoke(initial)
        report = result.get("final_report", {})

        analysis.status = "completed"
        analysis.progress = 100
        analysis.current_step = "Completed"
        analysis.result_json = report
        analysis.error = None
        db.commit()
        progress_service.set(analysis.id, 100, "Completed", {"status": "completed"})
        return report
    except Exception as exc:
        logger.exception("Analysis failed")
        analysis = db.get(Analysis, analysis_id)
        if analysis:
            analysis.status = "failed"
            analysis.error = str(exc)[:4000]
            analysis.current_step = "Failed"
            db.commit()
            progress_service.set(analysis.id, analysis.progress or 0, "Failed", {"status": "failed", "error": analysis.error})
        raise
    finally:
        db.close()
