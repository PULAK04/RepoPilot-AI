# RepoPilot AI

RepoPilot AI is a multi-agent codebase intelligence and software-engineering assistant. It can import a GitHub repository, index source code for retrieval, answer codebase questions, investigate bugs, review code, explain architecture, propose fixes, and validate its own conclusions through an evaluator loop.

## Core architecture

```text
React + TypeScript
        |
   REST + WebSocket
        |
      FastAPI
        |
  Celery background jobs
        |
      LangGraph
        |
Router -> Repository Research -> Orchestrator
                         |-> Code/DB/API/Test workers (parallel)
                         -> Reducer/Fix Agent -> Evaluator
                                      | fail -> retry
                                      -> Final Report
        |
PostgreSQL + Redis + Qdrant
```

## Included features

- Local email/password authentication with JWT
- Public GitHub repository import (private repositories can use `GITHUB_TOKEN`)
- Repository file discovery through GitHub API
- Code-aware text chunking and indexing in Qdrant
- Local hashing embeddings (no embedding API required)
- RAG-based "Ask Your Codebase"
- Multi-agent bug investigation
- Multi-agent code review
- Architecture analysis
- Router -> research -> orchestrator -> parallel workers -> reducer -> evaluator loop
- Suggested root cause and code fix
- Evidence with file paths and snippets
- Redis-backed live progress
- WebSocket status stream
- Celery workers for long-running jobs
- PostgreSQL analysis history
- Docker Compose for frontend, backend, worker, Postgres, Redis and Qdrant
- Pytest smoke tests
- GitHub Actions CI
- Read-only MCP server exposing repository search/metadata/report tools

## Important scope note

This repository is a complete runnable MVP/reference implementation, not a replacement for Cursor/GitHub Copilot. It intentionally limits repository size and file types so that the architecture can be understood, demonstrated and extended during placements/interviews.

## Quick start with Docker

1. Copy environment file:

```bash
cp .env.example .env
```

2. Set an LLM provider in `.env` (OpenAI-compatible providers work):

```env
LLM_API_KEY=your_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

You can also use OpenRouter or another OpenAI-compatible API by changing `LLM_BASE_URL` and `LLM_MODEL`.

3. Start everything:

```bash
docker compose up --build
```

4. Open:

- Frontend: http://localhost:5173
- FastAPI docs: http://localhost:8000/docs
- Qdrant dashboard: http://localhost:6333/dashboard
- MCP Streamable HTTP endpoint: http://localhost:9000/mcp

## Run without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

You still need PostgreSQL, Redis and Qdrant running, or update the URLs in `.env`.

### Celery worker

```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Main workflow

### 1. Add a repository

Paste a URL such as:

```text
https://github.com/owner/repository
```

RepoPilot creates a background indexing job. The worker:

1. Gets the repository default branch.
2. Fetches the recursive file tree.
3. Filters to relevant source/config/documentation files.
4. Downloads text files under configured limits.
5. Chunks them.
6. Creates deterministic hashing embeddings.
7. Stores vectors and metadata in Qdrant.

### 2. Run an analysis

Supported analysis kinds:

- `ask`
- `bug`
- `code_review`
- `architecture`
- `tests`
- `performance`

A bug investigation follows:

```text
Question
   |
Router Agent
   |
Repository RAG Research
   |
Orchestrator
   |---- Code Logic Worker
   |---- API Worker
   |---- Database Worker
   |---- Test/Edge Case Worker
   |
Reducer / Fix Agent
   |
Evaluator
   |-- insufficient -> research again (bounded retry)
   '-- grounded -> final report
```

## API overview

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

POST /api/repositories
GET  /api/repositories
GET  /api/repositories/{id}
POST /api/repositories/{id}/reindex

POST /api/analyses
GET  /api/analyses
GET  /api/analyses/{id}

WS   /ws/analyses/{id}?token=<jwt>
```

## Environment variables

See `.env.example`.

### LLM provider examples

Groq:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

OpenRouter:

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4.1-mini
```

OpenAI:

```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4.1-mini
```

If no LLM key is configured, repository import and retrieval still work; agent outputs use deterministic fallback logic so the UI remains demonstrable, but the quality is intentionally limited.

## Project structure

```text
RepoPilot-AI/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── graph.py
│   │   │   └── state.py
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── services/
│   │   ├── workers/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── mcp_server.py   # read-only MCP repository tools
│   │   └── schemas.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
└── README.md
```

## MCP tools included

The standalone MCP service exposes read-only tools:

```text
repository_info(repo_id)
search_repository(repo_id, query, limit)
get_analysis_report(analysis_id)
```

When Docker Compose is running, connect an MCP client/Inspector to `http://localhost:9000/mcp`.

## Good extensions for V2

- GitHub OAuth instead of a server-side PAT
- Pull-request creation after user approval
- Tree-sitter AST chunking/symbol graph
- Diff-aware re-indexing on new commits
- Official-documentation web research tool
- Sandbox test execution
- Static analyzers such as Ruff, ESLint, Semgrep and Bandit
- Evaluation datasets and regression tests for agent quality
- Human-in-the-loop approval before repository mutations

## Safety/design choice

The MVP is read-only against GitHub. Generated fixes are suggestions only. It does **not** automatically execute arbitrary repository code or push changes. Add sandboxing and explicit user approval before implementing automated execution or PR creation.
