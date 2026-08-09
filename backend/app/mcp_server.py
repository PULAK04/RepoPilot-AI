from mcp.server.fastmcp import FastMCP
from app.db.session import SessionLocal
from app.models import Repository, Analysis
from app.services.vector_store import vector_store

mcp = FastMCP(
    "RepoPilot Repository Tools",
    instructions=(
        "Read-only tools for retrieving indexed repository context and RepoPilot analysis reports. "
        "Use search_repository before making claims about a codebase."
    ),
    stateless_http=True,
    json_response=True,
)
# Docker needs the server to listen outside the container loopback interface.
mcp.settings.host = "0.0.0.0"
mcp.settings.port = 8000


@mcp.tool()
def repository_info(repo_id: int) -> dict:
    """Return metadata for a repository already imported into RepoPilot."""
    db = SessionLocal()
    try:
        repo = db.get(Repository, repo_id)
        if not repo:
            return {"error": "Repository not found"}
        return {
            "id": repo.id,
            "owner": repo.owner,
            "name": repo.name,
            "url": repo.url,
            "branch": repo.branch,
            "status": repo.status,
            "indexed_files": repo.file_count,
        }
    finally:
        db.close()


@mcp.tool()
def search_repository(repo_id: int, query: str, limit: int = 6) -> dict:
    """Search an indexed repository and return the most relevant code/document chunks."""
    safe_limit = max(1, min(limit, 12))
    try:
        results = vector_store.search(repo_id, query, safe_limit)
    except Exception as exc:
        return {"error": str(exc), "results": []}
    return {
        "repo_id": repo_id,
        "query": query,
        "results": [
            {
                "path": item["path"],
                "start_line": item.get("start_line"),
                "end_line": item.get("end_line"),
                "score": round(float(item.get("score", 0)), 4),
                "text": item.get("text", "")[:3000],
            }
            for item in results
        ],
    }


@mcp.tool()
def get_analysis_report(analysis_id: int) -> dict:
    """Return a completed RepoPilot multi-agent analysis report by analysis ID."""
    db = SessionLocal()
    try:
        analysis = db.get(Analysis, analysis_id)
        if not analysis:
            return {"error": "Analysis not found"}
        return {
            "id": analysis.id,
            "repo_id": analysis.repo_id,
            "kind": analysis.kind,
            "question": analysis.question,
            "status": analysis.status,
            "result": analysis.result_json,
            "error": analysis.error,
        }
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
