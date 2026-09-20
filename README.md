# NEXORA — Personal AI Work OS

NEXORA is a modular personal AI work operating system designed to research, plan, execute, evaluate and automate complex work through specialist agents, tools, workflows, memory, media intelligence, integrations and approval gates.

## Phase 1

Phase 1 establishes the real application foundation: FastAPI API, PostgreSQL persistence, Redis readiness, worker runtime, policy/approval contracts, agent/intelligence contracts, Next.js dashboard, Docker and CI.

## Architecture

```
USER → WEB → API → APPLICATION SERVICES → DOMAIN → REPOSITORIES → POSTGRES
                         │
                         ├── POLICY / APPROVAL
                         ├── EVENTS
                         ├── AGENT / CAPABILITY CONTRACTS
                         └── WORKER → REDIS
```

Future phases add intelligence execution, MCP, memory/RAG, media, social, integrations, evaluation and durable workflows.

## Local development

Backend:
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --reload
```

Frontend:
```powershell
cd apps/web
npm.cmd install
npm.cmd run dev
```

Database migrations:
```powershell
alembic upgrade head
```

Tests:
```powershell
.\.venv\Scripts\python.exe -m pytest
```

Docker:
```powershell
docker compose up --build
```

No AI provider credentials are required for Phase 1.
