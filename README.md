# 🚀 RepoPilot AI

<div align="center">

### Multi-Agent Codebase Intelligence & AI-Native Software Engineering Platform

**Understand repositories. Investigate bugs. Review architecture. Generate fixes. Validate conclusions.**

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C)](https://www.langchain.com/langgraph)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C)](https://qdrant.tech/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Celery](https://img.shields.io/badge/Celery-Background_Jobs-37814A)](https://docs.celeryq.dev/)
[![MCP](https://img.shields.io/badge/MCP-Tool_Server-blueviolet)](https://modelcontextprotocol.io/)

</div>

---

## 📌 Overview

**RepoPilot AI** is a multi-agent software-engineering intelligence platform that analyzes GitHub repositories and helps developers understand, investigate, and improve unfamiliar codebases.

Instead of sending an entire repository to a single LLM prompt, RepoPilot first indexes the repository into a vector database and retrieves only the most relevant code for a given engineering task.

A **LangGraph-based multi-agent pipeline** then routes the task through repository research, specialist agents, synthesis, and an evaluator loop.

RepoPilot can currently perform:

- 💬 Codebase question answering
- 🐛 Bug investigation
- 🔍 AI-assisted code review
- 🏗 Architecture analysis
- 🧪 Test planning and test-generation analysis
- ⚡ Performance analysis
- 🔧 Root-cause and fix suggestions
- ✅ Evidence-grounded evaluation
- 📡 Real-time multi-agent execution tracking
- 🔌 MCP-based repository access
- 📚 Persistent analysis history

---

# 🎯 Why RepoPilot AI?

Large repositories cannot simply be pasted into an LLM context window.

Traditional AI code assistants can also produce confident answers without proving whether those conclusions actually come from the repository.

RepoPilot approaches the problem differently.

```text
Repository
    │
    ▼
Index source code
    │
    ▼
Create searchable vectors
    │
    ▼
Retrieve relevant repository context
    │
    ▼
Multi-Agent Engineering Analysis
    │
    ▼
Evidence-Grounded Conclusion
    │
    ▼
Evaluator Validation
```

The goal is not only:

> "Generate an AI answer."

The goal is:

> **Retrieve the correct repository context, delegate engineering investigation to specialized agents, synthesize their findings, and verify whether the final conclusion is supported by actual code evidence.**

---

# ✨ Core Features

## 🔐 1. Authentication System

RepoPilot includes local email/password authentication.

### Features

- User registration
- User login
- JWT-based authentication
- Password hashing using bcrypt
- Protected REST API endpoints
- User-specific repositories
- User-specific analysis history
- Protected WebSocket connections

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as React Frontend
    participant B as FastAPI Backend
    participant DB as PostgreSQL

    U->>F: Register / Login
    F->>B: Email + Password
    B->>DB: Find/Create User
    DB-->>B: User Record
    B->>B: Verify Password / Generate JWT
    B-->>F: Access Token
    F->>F: Store JWT
    F->>B: Authorization: Bearer TOKEN
    B->>B: Decode JWT
    B-->>F: Protected Resource
```

---

# 🔗 2. GitHub Repository Import

Users can connect a repository by pasting its GitHub URL.

Example:

```text
https://github.com/owner/repository
```

RepoPilot automatically:

1. Parses the GitHub URL.
2. Fetches repository metadata.
3. Detects the default branch.
4. Creates a repository record.
5. Sends repository indexing to a Celery worker.
6. Retrieves the recursive repository tree.
7. Filters supported source/configuration files.
8. Downloads eligible text files.
9. Splits source files into overlapping chunks.
10. Creates vector representations.
11. Stores them in Qdrant.
12. Marks the repository as ready for analysis.

An optional `GITHUB_TOKEN` can be configured for authenticated GitHub requests, higher API limits, and repositories accessible through that token.

---

# 🧠 3. Repository Understanding & Indexing

RepoPilot does not send the complete repository to an LLM.

Instead, repository content is converted into searchable chunks.

### Supported repository content includes

```text
Python
JavaScript
TypeScript
React JSX / TSX
Java
C / C++
C#
Go
Rust
PHP
Ruby
Kotlin
Swift
SQL
HTML
CSS / SCSS
Vue
Svelte

JSON
YAML
TOML
INI

README.md
Dockerfile
docker-compose.yml
package.json
requirements.txt
pyproject.toml
Pipfile
go.mod
Cargo.toml
pom.xml
build.gradle
Shell scripts
```

Large dependency/build directories such as the following are ignored:

```text
node_modules
.git
dist
build
.next
.venv
venv
vendor
coverage
__pycache__
.idea
.vscode
target
```

---

# 🔎 4. RAG-Based Code Retrieval

RepoPilot implements **Retrieval-Augmented Generation for source code**.

When a user asks:

```text
Why is authentication failing after token refresh?
```

RepoPilot does not provide the LLM with every file.

Instead:

```mermaid
flowchart TD

    A[Engineering Question] --> B[Query Vectorization]

    B --> C[Qdrant Vector Search]

    C --> D[Repository Filter<br/>repo_id]

    D --> E[Relevant Code Chunks]

    E --> F[File Paths]
    E --> G[Line Ranges]
    E --> H[Code Snippets]

    F --> I[Agent Context]
    G --> I
    H --> I

    I --> J[Multi-Agent Analysis]
```

Each retrieved chunk contains metadata including:

```text
Repository ID
File Path
Starting Line
Ending Line
Source Text
Similarity Score
```

---

# 🧮 5. Local Embedding / Vectorization

The current MVP intentionally does **not require an external embedding API**.

RepoPilot uses Scikit-learn's `HashingVectorizer` with character n-grams to create deterministic local vectors.

### Current vector configuration

```text
Vector Size: 384

Analyzer:
char_wb

N-Gram Range:
3–5

Distance Metric:
Cosine Similarity
```

Benefits:

- No embedding API key required
- No embedding API cost
- Deterministic indexing
- Fast local development
- Easy deployment for an MVP

A production version can later replace this layer with semantic code embeddings without changing the rest of the architecture.

---

# 🤖 6. Multi-Agent Engineering Analysis

This is the core intelligence layer of RepoPilot.

RepoPilot uses **LangGraph** to implement a structured multi-agent workflow.

```mermaid
flowchart TD

    START((START))

    START --> R[Router Agent]

    R --> RR[Repository RAG Research]

    RR --> O[Orchestrator Agent]

    O --> W1[Specialist Worker 1]
    O --> W2[Specialist Worker 2]
    O --> W3[Specialist Worker 3]
    O --> W4[Specialist Worker 4]

    W1 --> RED[Reducer / Fix Agent]
    W2 --> RED
    W3 --> RED
    W4 --> RED

    RED --> E[Evaluator Agent]

    E -->|Grounded| F[Final Report]

    E -->|Insufficient Evidence| RR

    F --> END((END))
```

The evaluator retry is bounded so the workflow cannot loop forever.

---

# 🧭 7. Router Agent

The Router Agent identifies what type of software-engineering problem the user is asking about.

Possible internal routes include:

```text
codebase_question
bug_investigation
code_review
architecture
test_generation
performance
```

Example:

```text
User:

"Why is the payment verification endpoint returning success
but credits are not being added?"

                ↓

Router

                ↓

bug_investigation
```

The routing step ensures that different engineering tasks receive different investigation strategies.

---

# 🔬 8. Repository Research Agent

After routing, RepoPilot searches Qdrant for repository evidence related to the user's question.

Example:

```text
Question
    │
    ▼
Repository Research
    │
    ├── payment controller
    ├── payment service
    ├── user model
    ├── payment route
    ├── credit update logic
    └── related configuration
```

Initial research retrieves relevant repository chunks.

If the Evaluator determines that evidence is insufficient, the graph can perform another broader research pass.

---

# 🧠 9. Orchestrator Agent

The Orchestrator decomposes the engineering problem into complementary investigation tasks.

For a bug investigation, tasks may include:

```text
1. Trace the primary application logic.

2. Inspect API boundaries, validation and error handling.

3. Inspect database, persistence and cache behavior.

4. Investigate missing tests, regressions and edge cases.
```

The generated tasks are intentionally designed to be:

- Complementary
- Evidence-driven
- Non-overlapping
- Focused on the original engineering question

---

# 👥 10. Parallel Specialist Agents

LangGraph dynamically dispatches specialist workers.

Conceptually:

```text
                       Orchestrator
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Code Logic          API / Auth        Database
       Worker              Worker            Worker
          │                 │                 │
          └────────────┬────┴────────────┬────┘
                       │                 │
                       ▼                 ▼
                    Testing          Edge Cases
                     Worker
                       │
                       ▼
                     Reducer
```

Each specialist receives:

- Original user request
- Analysis type
- Repository evidence
- Specialist task
- Relevant file snippets
- File paths
- Line ranges

Each worker returns structured findings such as:

```json
{
  "task": "Trace authentication logic",
  "summary": "Refresh-token validation and access-token generation are handled separately.",
  "severity": "medium",
  "confidence": 0.87,
  "evidence": [],
  "recommendations": []
}
```

---

# 🧩 11. Reducer / Fix Agent

The Reducer collects findings from all specialist agents and produces one consolidated engineering conclusion.

It generates:

```text
Summary
Root Cause / Conclusion
Suggested Fix
Risk
Files To Review
Optional Patch
```

The Reducer is instructed to:

- Prefer the simplest explanation supported by evidence
- Avoid inventing files
- Avoid inventing line numbers
- Avoid unsupported runtime assumptions
- Answer general codebase questions directly
- Produce a fix only when evidence supports it

---

# ✅ 12. Evaluator Agent

The Evaluator is one of RepoPilot's most important reliability features.

Instead of returning the Reducer's answer immediately:

```text
Reducer
   │
   ▼
Evaluator
   │
   ├── Is the answer supported by repository evidence?
   │
   ├── Does it answer the user's question?
   │
   ├── Are conclusions grounded?
   │
   └── Is more research needed?
```

The Evaluator generates:

```json
{
  "passed": true,
  "confidence": 0.91,
  "reason": "The conclusion is supported by the retrieved repository files.",
  "missing": []
}
```

If validation fails:

```text
Evaluator
    │
    ▼
Additional Repository Research
    │
    ▼
Orchestrator
    │
    ▼
Workers
    │
    ▼
Reducer
    │
    ▼
Evaluator
```

This creates a bounded **research → reason → verify** loop.

---

# 🐛 13. AI Bug Investigation

Users can describe application bugs such as:

```text
Payment verification succeeds but user credits
are not updated in the database.
```

RepoPilot investigates the repository and returns:

### Root Cause

A concise explanation of the most likely problem.

### Evidence

Relevant repository files and source snippets.

### Suggested Fix

An evidence-grounded engineering recommendation.

### Optional Patch

A suggested code modification when appropriate.

### Specialist Findings

Independent findings from multiple worker agents.

### Evaluator Confidence

A grounding/confidence score from the Evaluator.

---

# 💬 14. Ask Your Codebase

Users can ask natural-language questions about repository behavior.

Examples:

```text
How does authentication work?

Where are JWT tokens generated?

How is Redis being used?

Explain the payment flow.

Which files are involved in user registration?

How does data move from the frontend to the database?

Where is the LLM API called?

How is repository caching implemented?
```

RepoPilot performs repository retrieval before answering.

This makes the feature different from a generic LLM chatbot because answers are generated from indexed repository evidence.

---

# 🔍 15. Code Review

RepoPilot can perform repository-level AI-assisted review.

Example request:

```text
Review this repository for the highest-impact
correctness, maintainability, security and
performance issues.
```

The Orchestrator can investigate areas such as:

```text
Correctness

Error Handling

Maintainability

Architecture

Security

Input Validation

Data Handling

Performance

Database Usage

External API Usage

Repeated Work
```

---

# 🏗 16. Architecture Analysis

RepoPilot can analyze the repository and infer:

- Major modules
- Application responsibilities
- Service boundaries
- Request flow
- Data flow
- Persistence layer
- Cache usage
- External integrations
- Queues
- Scaling risks
- Architectural improvement opportunities

Example:

```text
User
  │
  ▼
React Frontend
  │
  ▼
REST API
  │
  ▼
FastAPI
  │
  ├── Authentication
  ├── Repository Management
  ├── Analysis Management
  │
  ▼
Celery
  │
  ▼
LangGraph Agents
  │
  ├── PostgreSQL
  ├── Redis
  ├── Qdrant
  └── LLM Provider
```

---

# 🧪 17. Test Analysis

RepoPilot includes a dedicated `tests` analysis mode.

The system can:

- Identify important code paths
- Identify high-risk endpoints
- Suggest success scenarios
- Suggest failure scenarios
- Suggest authorization tests
- Suggest edge cases
- Infer likely test approaches from repository evidence
- Produce implementation-oriented testing recommendations

The current MVP focuses on **test planning and generation suggestions** rather than executing arbitrary repository code.

---

# ⚡ 18. Performance Analysis

RepoPilot can investigate potential application performance issues.

The Performance Agent focuses on patterns such as:

```text
Repeated database work

Potential N+1-style access patterns

Sequential external API operations

Repeated external calls

Large payloads

Missing pagination

Caching opportunities

Repeated expensive computation

Latency risks

Queueing opportunities

Scalability constraints
```

Recommendations are limited to what can reasonably be inferred from repository evidence.

---

# 📄 19. Evidence-Based Reports

RepoPilot returns repository evidence alongside its conclusions.

Each evidence item contains:

```text
File Path
Starting Line
Ending Line
Retrieval Score
Source Snippet
```

Example UI concept:

```text
Repository Evidence

▼ backend/app/services/auth.py
  Lines 32–61
  Score: 0.8231

  def authenticate_user(...):
      ...
```

This makes AI conclusions inspectable instead of returning unexplained text.

---

# 📊 20. Persistent Analysis History

Every engineering analysis is stored in PostgreSQL.

Users can revisit previous:

```text
Bug Investigations
Code Reviews
Architecture Analyses
Performance Analyses
Testing Analyses
Codebase Questions
```

Stored analysis information includes:

```text
Analysis ID
Repository ID
User ID
Analysis Type
Question
Status
Progress
Current Step
Final JSON Report
Errors
Created Time
Updated Time
```

---

# 📡 21. Real-Time Agent Progress

Multi-agent analysis can take longer than a normal API request.

RepoPilot therefore uses:

```text
Celery
+
Redis
+
WebSockets
```

to execute analysis asynchronously and stream progress to the browser.

---

## Real-Time Execution Flow

```mermaid
sequenceDiagram

    participant U as User
    participant F as React
    participant API as FastAPI
    participant C as Celery
    participant R as Redis
    participant G as LangGraph
    participant WS as WebSocket

    U->>F: Run Analysis
    F->>API: POST /api/analyses

    API->>C: Queue Analysis Job
    API-->>F: Analysis ID

    F->>WS: Connect using Analysis ID + JWT

    C->>G: Execute LangGraph

    G->>R: Save progress
    WS->>R: Read progress
    WS-->>F: Progress update

    G->>R: Update progress
    WS-->>F: Router complete

    G->>R: Update progress
    WS-->>F: Workers running

    G->>R: Update progress
    WS-->>F: Evaluator running

    G-->>C: Final report
    C->>API: Persist report in PostgreSQL

    WS-->>F: 100% Completed
```

---

# ⚙️ Background Job Processing

Long-running work is processed outside the HTTP request lifecycle.

### Repository indexing

```text
POST /repositories
      │
      ▼
FastAPI
      │
      ▼
Create Repository
      │
      ▼
Celery Queue
      │
      ▼
Repository Worker
      │
      ├── GitHub API
      ├── File Filtering
      ├── Chunking
      ├── Vectorization
      └── Qdrant Indexing
```

### Engineering analysis

```text
POST /analyses
      │
      ▼
FastAPI
      │
      ▼
Create Analysis
      │
      ▼
Celery
      │
      ▼
LangGraph
      │
      ▼
Final Report
      │
      ▼
PostgreSQL
```

This prevents long-running AI workflows from blocking REST requests.

---

# 🔌 22. Model Context Protocol — MCP Server

RepoPilot includes a standalone **read-only MCP server**.

The MCP server exposes repository information and analysis tools to MCP-compatible clients.

### Available MCP Tools

```text
repository_info(repo_id)

search_repository(repo_id, query, limit)

get_analysis_report(analysis_id)
```

---

## `repository_info`

Returns metadata about an imported repository.

Example:

```json
{
  "id": 12,
  "owner": "example",
  "name": "backend-service",
  "branch": "main",
  "status": "ready",
  "indexed_files": 143
}
```

---

## `search_repository`

Performs vector search against an indexed repository.

Example:

```text
search_repository(
    repo_id=12,
    query="Where is authentication implemented?",
    limit=6
)
```

Returns:

```text
Relevant file paths
Line ranges
Similarity scores
Code snippets
```

---

## `get_analysis_report`

Returns a previously generated RepoPilot multi-agent analysis.

---

### MCP Endpoint

When Docker Compose is running:

```text
http://localhost:9000/mcp
```

Transport:

```text
Streamable HTTP
```

---

# 🧠 Complete Multi-Agent Data Flow

```mermaid
flowchart TB

    U[User]

    U --> UI[React + TypeScript Frontend]

    UI -->|JWT REST Request| API[FastAPI]

    API --> DB[(PostgreSQL)]

    API --> CQ[Celery Queue]

    CQ --> W[Celery Worker]

    W --> LG[LangGraph]

    LG --> ROUTER[Router]

    ROUTER --> SEARCH[Repository Research]

    SEARCH --> VECTOR[(Qdrant)]

    VECTOR --> SEARCH

    SEARCH --> ORCH[Orchestrator]

    ORCH --> A1[Code / Logic Worker]
    ORCH --> A2[API / Integration Worker]
    ORCH --> A3[Database / State Worker]
    ORCH --> A4[Test / Edge Case Worker]

    A1 --> RED[Reducer / Fix Agent]
    A2 --> RED
    A3 --> RED
    A4 --> RED

    RED --> EVAL[Evaluator]

    EVAL -->|Needs More Evidence| SEARCH

    EVAL -->|Passed| FINAL[Final Engineering Report]

    FINAL --> DB

    LG --> PROGRESS[(Redis Progress Store)]

    PROGRESS --> WS[FastAPI WebSocket]

    WS --> UI

    LG --> LLM[OpenAI-Compatible LLM API]
```

---

# 🏛 System Architecture

```mermaid
flowchart LR

    subgraph Client["Frontend Layer"]
        React[React 18]
        TS[TypeScript]
        Redux[Redux Toolkit]
        Axios[Axios]
    end

    subgraph API["Application Layer"]
        FastAPI[FastAPI]
        JWT[JWT Authentication]
        WS[WebSocket Server]
    end

    subgraph Jobs["Async Processing"]
        Celery[Celery Worker]
        RedisQueue[(Redis)]
    end

    subgraph AI["AI Intelligence Layer"]
        LangGraph[LangGraph]
        Router[Router Agent]
        Research[RAG Research]
        Orchestrator[Orchestrator]
        Workers[Specialist Workers]
        Reducer[Reducer]
        Evaluator[Evaluator]
    end

    subgraph Storage["Data Layer"]
        PostgreSQL[(PostgreSQL)]
        Qdrant[(Qdrant)]
        Redis[(Redis)]
    end

    subgraph External["External Services"]
        GitHub[GitHub API]
        LLM[OpenAI-Compatible LLM API]
    end

    React --> TS
    TS --> Redux
    Redux --> Axios

    Axios --> FastAPI

    FastAPI --> JWT
    FastAPI --> PostgreSQL

    FastAPI --> Celery
    Celery --> RedisQueue

    Celery --> GitHub
    Celery --> Qdrant
    Celery --> LangGraph

    LangGraph --> Router
    Router --> Research
    Research --> Qdrant
    Research --> Orchestrator
    Orchestrator --> Workers
    Workers --> Reducer
    Reducer --> Evaluator

    Router --> LLM
    Orchestrator --> LLM
    Workers --> LLM
    Reducer --> LLM
    Evaluator --> LLM

    LangGraph --> Redis
    Redis --> WS
    WS --> React
```

---

# 📥 Repository Ingestion Pipeline

```mermaid
flowchart TD

    URL[GitHub Repository URL]

    URL --> PARSE[Parse Owner + Repository]

    PARSE --> META[GitHub Repository Metadata]

    META --> BRANCH[Determine Branch]

    BRANCH --> JOB[Celery Indexing Job]

    JOB --> TREE[Fetch Recursive File Tree]

    TREE --> FILTER[Filter Supported Files]

    FILTER --> LIMIT[Apply File Size / Repository Limits]

    LIMIT --> DOWNLOAD[Download Text Files]

    DOWNLOAD --> CHUNK[Line-Based Chunking]

    CHUNK --> VECTORIZE[Local Hashing Vectorizer]

    VECTORIZE --> UPSERT[Qdrant Upsert]

    UPSERT --> READY[Repository Status = Ready]
```

---

# 🗄 Data Architecture

RepoPilot uses different data stores for different responsibilities.

| Technology | Responsibility |
|---|---|
| **PostgreSQL** | Users, repositories, analyses, reports and history |
| **Qdrant** | Indexed repository chunks and vectors |
| **Redis DB 0** | Real-time analysis progress |
| **Redis DB 1** | Celery broker |
| **Redis DB 2** | Celery result backend |

---

# 🧱 Database Relationships

```mermaid
erDiagram

    USER ||--o{ REPOSITORY : owns
    USER ||--o{ ANALYSIS : creates
    REPOSITORY ||--o{ ANALYSIS : contains

    USER {
        int id
        string email
        string password_hash
        datetime created_at
    }

    REPOSITORY {
        int id
        int user_id
        string owner
        string name
        string url
        string branch
        string status
        int file_count
        text last_error
        datetime created_at
        datetime updated_at
    }

    ANALYSIS {
        int id
        int repo_id
        int user_id
        string kind
        text question
        string status
        int progress
        string current_step
        json result_json
        text error
        datetime created_at
        datetime updated_at
    }
```

---

# 🛠 Tech Stack

## Frontend

| Technology | Purpose |
|---|---|
| **React 18** | Component-based user interface |
| **TypeScript** | Type-safe frontend development |
| **Vite** | Frontend build and development server |
| **Redux Toolkit** | Authentication/client state |
| **React Redux** | Redux bindings |
| **React Router** | Client-side routing |
| **Axios** | HTTP API communication |
| **Native WebSocket API** | Live analysis progress |
| **Custom CSS** | Application styling |

---

## Backend

| Technology | Purpose |
|---|---|
| **Python** | Primary backend/AI language |
| **FastAPI** | REST API and WebSocket backend |
| **Pydantic** | Request/response validation |
| **SQLAlchemy 2** | Relational ORM |
| **Uvicorn** | ASGI server |
| **HTTPX** | GitHub and LLM HTTP communication |
| **python-jose** | JWT encoding/decoding |
| **Passlib + bcrypt** | Password hashing |

---

## AI & Agentic Architecture

| Technology | Purpose |
|---|---|
| **LangGraph** | Multi-agent workflow orchestration |
| **OpenAI-Compatible Chat API** | LLM reasoning |
| **Structured JSON Outputs** | Reliable agent communication |
| **RAG** | Repository-grounded context retrieval |
| **Qdrant** | Vector database |
| **Scikit-learn HashingVectorizer** | Local repository vectorization |
| **NumPy** | Vector processing |
| **MCP SDK** | Model Context Protocol tool server |

---

## Infrastructure

| Technology | Purpose |
|---|---|
| **PostgreSQL 16** | Persistent relational storage |
| **Redis 7** | Progress state + Celery infrastructure |
| **Celery** | Asynchronous repository/analysis jobs |
| **Docker** | Service containerization |
| **Docker Compose** | Multi-service orchestration |
| **Nginx** | Production frontend container |
| **GitHub Actions** | Continuous Integration |

---

# 🤖 Supported LLM Providers

RepoPilot communicates with an **OpenAI-compatible `/chat/completions` endpoint**.

That makes the LLM layer provider-flexible.

Examples include:

### Groq

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

### OpenRouter

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4.1-mini
```

### OpenAI

```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4.1-mini
```

The application accesses the provider through a small abstraction layer:

```text
RepoPilot Agent
      │
      ▼
LLM Service
      │
      ▼
OpenAI-Compatible API
```

This prevents the agent architecture from being tightly coupled to a single LLM provider.

---

# 🛡 LLM Fallback Behavior

An LLM API key is recommended for meaningful engineering analysis.

However, RepoPilot includes deterministic fallback behavior when no LLM key is configured.

Repository functionality such as:

```text
Repository Import
Repository Indexing
Vector Storage
Repository Retrieval
Authentication
Analysis Infrastructure
WebSocket Progress
MCP Repository Search
```

can still operate.

AI reasoning quality is intentionally limited without an LLM provider.

---

# 📂 Project Structure

```text
RepoPilot-AI/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py
│   │   │   └── state.py
│   │   │
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── repositories.py
│   │   │       ├── analyses.py
│   │   │       └── ws.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   │
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   │
│   │   ├── services/
│   │   │   ├── github.py
│   │   │   ├── llm.py
│   │   │   ├── progress.py
│   │   │   ├── repo_parser.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   │
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── mcp_server.py
│   │
│   ├── tests/
│   │   └── test_smoke.py
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── src/
│   │   │
│   │   ├── components/
│   │   │   ├── Nav.tsx
│   │   │   └── ProgressTimeline.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   │
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── RepositoryPage.tsx
│   │   │   └── AnalysisPage.tsx
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── store.ts
│   │   └── index.css
│   │
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
└── README.md
```

---

# 🌐 REST API

FastAPI automatically exposes interactive Swagger documentation.

After starting the backend:

```text
http://localhost:8000/docs
```

---

## Authentication

### Register User

```http
POST /api/auth/register
```

Request:

```json
{
  "email": "developer@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

---

### Login

```http
POST /api/auth/login
```

Request:

```json
{
  "email": "developer@example.com",
  "password": "password123"
}
```

---

### Current User

```http
GET /api/auth/me
```

Header:

```text
Authorization: Bearer <JWT>
```

---

# 📦 Repository APIs

### Import Repository

```http
POST /api/repositories
```

Request:

```json
{
  "url": "https://github.com/owner/repository",
  "branch": "main"
}
```

`branch` may be omitted.

---

### List User Repositories

```http
GET /api/repositories
```

---

### Get Repository

```http
GET /api/repositories/{repo_id}
```

---

### Re-index Repository

```http
POST /api/repositories/{repo_id}/reindex
```

---

# 🤖 Analysis APIs

### Start Analysis

```http
POST /api/analyses
```

Request:

```json
{
  "repo_id": 1,
  "kind": "bug",
  "question": "Why does payment verification succeed but credits are not updated?"
}
```

Supported `kind` values:

```text
ask
bug
code_review
architecture
tests
performance
```

---

### List Analyses

```http
GET /api/analyses
```

Optional repository filter:

```http
GET /api/analyses?repo_id=1
```

---

### Get Analysis

```http
GET /api/analyses/{analysis_id}
```

---

# 📡 WebSocket API

Real-time analysis progress is available through:

```text
/ws/analyses/{analysis_id}?token=<JWT>
```

Example:

```javascript
const socket = new WebSocket(
  `ws://localhost:8000/ws/analyses/25?token=${token}`
)

socket.onmessage = (event) => {
  const data = JSON.parse(event.data)

  console.log(data.progress)
  console.log(data.step)
}
```

Possible updates may represent:

```text
Starting multi-agent analysis

Router is classifying the engineering task

RAG research is retrieving relevant repository evidence

Orchestrator is decomposing the investigation

Specialist agents are analyzing repository evidence

Reducer is synthesizing specialist findings

Evaluator is checking grounding

Final engineering report is being assembled

Completed
```

---

# 🐳 Running With Docker

Docker Compose is the easiest way to run the complete project.

## Prerequisites

Install:

```text
Docker Desktop
Git
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/RepoPilot-AI.git
cd RepoPilot-AI
```

---

## 2. Create Environment File

### Linux / macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

---

## 3. Configure `.env`

At minimum, configure a secure secret:

```env
SECRET_KEY=replace-with-a-long-random-secret
```

For full AI analysis:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

---

## 4. Start All Services

```bash
docker compose up --build
```

Docker Compose starts:

```text
Frontend
FastAPI Backend
Celery Worker
MCP Server
PostgreSQL
Redis
Qdrant
```

---

# 🔌 Local Service URLs

| Service | URL |
|---|---|
| **RepoPilot Frontend** | `http://localhost:5173` |
| **FastAPI Backend** | `http://localhost:8000` |
| **Swagger API Docs** | `http://localhost:8000/docs` |
| **Health Check** | `http://localhost:8000/health` |
| **Qdrant Dashboard** | `http://localhost:6333/dashboard` |
| **MCP Server** | `http://localhost:9000/mcp` |
| **PostgreSQL** | `localhost:5432` |
| **Redis** | `localhost:6379` |

---

# 💻 Running Without Docker

You can also run each service manually.

You must have PostgreSQL, Redis and Qdrant available.

---

## Backend

```bash
cd backend
```

Create virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

# 👷 Start Celery Worker

From the backend directory:

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

---

# 🔌 Start MCP Server

From the backend directory:

```bash
python -m app.mcp_server
```

---

# ⚛️ Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🔐 Environment Variables

```env
# =========================================================
# APPLICATION
# =========================================================

APP_NAME=RepoPilot AI

SECRET_KEY=change-this-to-a-long-random-secret

ACCESS_TOKEN_EXPIRE_MINUTES=1440

CORS_ORIGINS=http://localhost:5173


# =========================================================
# POSTGRESQL / REDIS / QDRANT
# =========================================================

DATABASE_URL=postgresql+psycopg2://repopilot:repopilot@postgres:5432/repopilot

REDIS_URL=redis://redis:6379/0

QDRANT_URL=http://qdrant:6333

QDRANT_COLLECTION=repo_chunks


# =========================================================
# GITHUB
# =========================================================

# Optional for public repositories.
# Useful for authenticated requests and repositories
# accessible using the configured token.

GITHUB_TOKEN=


# =========================================================
# LLM
# =========================================================

LLM_API_KEY=

LLM_BASE_URL=https://api.groq.com/openai/v1

LLM_MODEL=llama-3.3-70b-versatile

LLM_TIMEOUT_SECONDS=90


# =========================================================
# REPOSITORY INGESTION LIMITS
# =========================================================

MAX_REPO_FILES=350

MAX_FILE_BYTES=180000

CHUNK_LINES=90

CHUNK_OVERLAP_LINES=15


# =========================================================
# CELERY
# =========================================================

CELERY_BROKER_URL=redis://redis:6379/1

CELERY_RESULT_BACKEND=redis://redis:6379/2


# =========================================================
# FRONTEND
# =========================================================

VITE_API_URL=http://localhost:8000/api

VITE_WS_URL=ws://localhost:8000/ws
```

---

# ⚠️ Environment Security

Never commit:

```text
.env
API keys
JWT secrets
GitHub access tokens
Database passwords
Production credentials
```

The repository should only contain:

```text
.env.example
```

with placeholder values.

---

# 🚀 How To Use RepoPilot

## Step 1 — Create Account

Open:

```text
http://localhost:5173
```

Register using email and password.

---

## Step 2 — Import Repository

Enter:

```text
https://github.com/owner/repository
```

Click:

```text
Import & Index
```

---

## Step 3 — Wait For Indexing

Repository status changes through states such as:

```text
queued
   ↓
indexing
   ↓
ready
```

If indexing fails:

```text
failed
```

and the repository stores an error message.

---

## Step 4 — Select Engineering Mode

Choose:

```text
Ask

Bug

Code Review

Architecture

Tests

Performance
```

---

## Step 5 — Enter Engineering Question

Example:

```text
Trace the authentication flow and determine
why refresh tokens may fail after expiration.
```

---

## Step 6 — Run Multi-Agent Analysis

RepoPilot displays the analysis progress.

Example:

```text
5%

Starting multi-agent analysis

        ↓

15%

Router is classifying the engineering task

        ↓

25%

RAG research is retrieving repository evidence

        ↓

38%

Orchestrator is decomposing the investigation

        ↓

Specialist Workers

        ↓

72%

Reducer is synthesizing findings

        ↓

86%

Evaluator is validating grounding

        ↓

96%

Final report is being assembled

        ↓

100%

Completed
```

---

## Step 7 — Inspect Final Report

The final interface displays:

```text
Summary

Evaluator Confidence

Root Cause / Conclusion

Suggested Fix

Optional Patch

Specialist Findings

Severity

Worker Confidence

Repository Evidence

File Paths

Line Numbers

Similarity Scores

Code Snippets
```

---

# 📑 Example Final Report Structure

```json
{
  "route": "bug_investigation",

  "question": "Why is authentication failing?",

  "summary": "The authentication failure is related to ...",

  "root_cause": "The refresh token is ...",

  "suggested_fix": "Update the token validation logic ...",

  "optional_patch": "...",

  "risk": "medium",

  "files_to_review": [
    "backend/auth/service.py",
    "backend/auth/middleware.py"
  ],

  "evaluation": {
    "passed": true,
    "confidence": 0.91,
    "reason": "The conclusion is supported by repository evidence."
  },

  "findings": [],

  "evidence": [],

  "attempts": 1
}
```

---

# 🧠 Key Engineering Decisions

## Why FastAPI?

RepoPilot's agentic backend is Python-based.

FastAPI provides:

- Native Python integration
- Pydantic validation
- Async-friendly architecture
- Automatic Swagger docs
- WebSocket support
- Clean REST API development
- Easy integration with AI/ML libraries

---

## Why LangGraph?

The problem is not well represented by one linear LLM request.

RepoPilot requires:

```text
Routing
     ↓
Repository Research
     ↓
Dynamic Task Decomposition
     ↓
Parallel Specialists
     ↓
Synthesis
     ↓
Validation
     ↓
Conditional Retry
```

LangGraph naturally models this as a stateful graph.

---

## Why PostgreSQL?

The application contains strongly related entities:

```text
User
   │
   └── Repository
          │
          └── Analysis
```

A relational database provides a natural persistence layer for:

- Ownership
- Analysis history
- Status tracking
- Structured metadata
- Reports

---

## Why Qdrant?

Repository RAG requires similarity search across large numbers of code chunks.

Qdrant provides:

```text
Vector Storage

Cosine Similarity Search

Metadata Payloads

Repository Filtering

Persistent Collections
```

---

## Why Redis?

Redis serves multiple roles:

```text
Real-Time Analysis Progress

Celery Message Broker

Celery Result Backend
```

---

## Why Celery?

Repository indexing and AI investigation can take significantly longer than normal HTTP requests.

Running them directly inside an API request would cause:

```text
Long response times
Request timeouts
Poor scalability
Blocked workers
```

Celery separates long-running tasks from the request lifecycle.

---

## Why WebSockets?

Polling every second creates unnecessary requests.

WebSockets provide a better experience for live agent progress:

```text
Backend Analysis
      │
      ▼
Redis State
      │
      ▼
WebSocket
      │
      ▼
Frontend Progress Timeline
```

---

# 🔒 Security Features

Current security measures include:

- bcrypt password hashing
- JWT authentication
- JWT expiration
- Protected repository endpoints
- Protected analysis endpoints
- Repository ownership validation
- Analysis ownership validation
- Authenticated WebSocket connections
- Configurable CORS
- Server-side environment variables
- No embedding-service credential requirement

---

# ⚠️ Current MVP Scope

RepoPilot is intentionally a **software-engineering portfolio MVP**, not a replacement for Cursor, GitHub Copilot, GitHub Advanced Security, or a production autonomous coding agent.

Current limitations include:

### Repository Limits

Default:

```text
Maximum repository files: 350

Maximum file size: 180 KB

Chunk size: 90 lines

Chunk overlap: 15 lines
```

These values are configurable.

---

### Static Repository Understanding

The current project analyzes repository source code and retrieved evidence.

It does not execute arbitrary imported repository code.

This is intentional because executing unknown repositories would require isolated sandboxing and considerably stronger security controls.

---

### Local Hashing Embeddings

The current MVP uses deterministic local vectors rather than a dedicated semantic code embedding model.

This keeps setup simple but may produce less accurate semantic retrieval than production embedding systems.

---

### No Automatic GitHub Pull Request Creation

RepoPilot currently produces suggested fixes/patches.

It does **not automatically modify repositories or create pull requests**.

This keeps repository access read-oriented and prevents uncontrolled AI-generated changes.

---

# 🧪 Testing

Backend smoke tests are included using:

```text
Pytest
```

Run tests:

```bash
cd backend
pytest
```

---

# 🔄 Continuous Integration

The repository contains:

```text
.github/workflows/ci.yml
```

GitHub Actions is used to validate the codebase during CI.

The project architecture is designed so additional checks can later include:

```text
Frontend Build
Backend Tests
Linting
Type Checking
Docker Build
Integration Tests
Security Scanning
```

---

# 🐳 Docker Architecture

Docker Compose currently manages:

```text
postgres
redis
qdrant
backend
worker
mcp
frontend
```

```mermaid
flowchart LR

    FE[Frontend Container<br/>React + Nginx]

    BE[Backend Container<br/>FastAPI]

    WORKER[Worker Container<br/>Celery]

    MCP[MCP Container]

    PG[(PostgreSQL Container)]

    REDIS[(Redis Container)]

    QD[(Qdrant Container)]

    FE --> BE

    BE --> PG
    BE --> REDIS

    BE --> WORKER

    WORKER --> REDIS
    WORKER --> PG
    WORKER --> QD

    MCP --> PG
    MCP --> QD
```

---

# 🩺 Health Check

Backend health endpoint:

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "app": "RepoPilot AI"
}
```

---

# 🔮 Future Roadmap

## V2 — Repository Intelligence

- [ ] GitHub OAuth
- [ ] Private repository authorization per user
- [ ] Tree-sitter AST parsing
- [ ] Function-level code chunks
- [ ] Class-level code chunks
- [ ] Symbol graph
- [ ] Import/dependency graph
- [ ] Cross-file call graph
- [ ] Semantic code embeddings
- [ ] Hybrid lexical + vector search
- [ ] Reranking

---

## V3 — Advanced Engineering Agents

- [ ] Dedicated Security Agent
- [ ] Dedicated Dependency Agent
- [ ] Dedicated DevOps Agent
- [ ] Database Query Analyzer
- [ ] API Contract Analyzer
- [ ] Docker / deployment diagnostics
- [ ] Static vulnerability analysis integration
- [ ] Repository health score
- [ ] Architecture scoring
- [ ] Technical debt analysis

---

## V4 — Autonomous Testing

- [ ] Generate test files
- [ ] Isolated sandbox execution
- [ ] Run generated tests
- [ ] Capture failures
- [ ] Feed failures back to agents
- [ ] Iterative fix verification
- [ ] Coverage analysis
- [ ] Regression-test generation

---

## V5 — GitHub Automation

- [ ] Commit suggestion preview
- [ ] User-approved code modifications
- [ ] Automatic branch creation
- [ ] Pull request generation
- [ ] PR summary generation
- [ ] AI code-review comments
- [ ] GitHub issue analysis

---

## V6 — Production AI Reliability

- [ ] LangGraph checkpoint persistence
- [ ] Human-in-the-loop approval
- [ ] Agent traces
- [ ] Cost tracking
- [ ] Token usage dashboard
- [ ] Prompt versioning
- [ ] LLM output evaluation
- [ ] Agent performance metrics
- [ ] Retrieval evaluation
- [ ] Hallucination monitoring

---

# 💡 Example Use Cases

## Bug Investigation

```text
"Payment verification is successful but credits
are not being persisted."
```

---

## Authentication Understanding

```text
"Explain the complete login flow from frontend
to database."
```

---

## Architecture Review

```text
"Explain the architecture of this application,
its services, databases, external integrations
and scaling risks."
```

---

## Code Review

```text
"Find the highest-impact correctness,
maintainability and performance problems."
```

---

## Testing

```text
"Identify the highest-risk backend flows and
generate an implementation-ready test plan."
```

---

## Performance

```text
"Find repeated database/API work, caching
opportunities and likely performance bottlenecks."
```

---

# 🎓 What This Project Demonstrates

RepoPilot AI combines multiple software-engineering disciplines in one system.

### Backend Engineering

```text
Python
FastAPI
REST APIs
Authentication
WebSockets
Background Jobs
Relational Databases
Caching / State
```

### AI Engineering

```text
LLM Integration
Agentic Workflows
LangGraph
RAG
Structured Outputs
Multi-Agent Systems
Evaluator Loops
Grounded Generation
Tool Integration
MCP
```

### Data / Retrieval

```text
Vectorization
Vector Databases
Similarity Search
Metadata Filtering
Repository Indexing
```

### Distributed Application Concepts

```text
Task Queues
Background Workers
Real-Time Communication
Service Separation
Persistent State
```

### DevOps

```text
Docker
Docker Compose
GitHub Actions
Multi-Container Architecture
Environment Configuration
```

---

# 📈 Engineering Highlights

RepoPilot is designed around several production-inspired ideas:

### 1. Retrieval Before Reasoning

Agents receive repository evidence before making engineering conclusions.

### 2. Specialized Agent Responsibilities

Different tasks investigate different aspects of the problem.

### 3. Structured Agent Communication

Agents exchange JSON-like structured results instead of relying entirely on free-form text.

### 4. Evidence Grounding

Reports contain repository paths, line ranges and snippets.

### 5. Evaluator Loop

The system validates whether a conclusion is actually supported.

### 6. Async Processing

Long-running AI and indexing workloads do not block API requests.

### 7. Real-Time User Feedback

Analysis progress is streamed through WebSockets.

### 8. Provider-Agnostic LLM Layer

Any compatible chat-completion provider can be configured.

### 9. Separation of Data Responsibilities

PostgreSQL, Redis and Qdrant each solve a different storage problem.

### 10. Read-Only MCP Tools

External MCP clients can query indexed repository knowledge without requiring write access.

---

# 🚧 Production Improvements

Before using RepoPilot in a production environment, recommended improvements include:

```text
GitHub OAuth

HTTP-only secure authentication cookies

Refresh-token rotation

Database migrations

Stronger rate limiting

Semantic code embeddings

AST-aware parsing

Sandboxed repository execution

Secret detection

File-level permission rules

Encrypted external tokens

Production reverse proxy

TLS / HTTPS

Centralized logging

Metrics and monitoring

OpenTelemetry tracing

Agent cost monitoring

LLM request retry strategy

Distributed Celery workers

Cloud object storage where required
```

---

# 🤝 Contributing

Contributions, feature suggestions and engineering improvements are welcome.

A typical contribution workflow:

```bash
git checkout -b feature/my-feature
```

Make your changes.

```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

Then create a Pull Request.

---

# ⭐ Support

If you find RepoPilot AI useful, consider giving the repository a ⭐.

It helps the project reach more developers interested in:

```text
AI-Native Software Engineering
Agentic AI
LangGraph
RAG
Python Backend Development
Developer Tools
Multi-Agent Systems
```

---

<div align="center">

## RepoPilot AI

### **Understand the codebase. Investigate with evidence. Engineer with AI.**

Built with **React • TypeScript • FastAPI • LangGraph • PostgreSQL • Redis • Qdrant • Celery • MCP • Docker**

</div>