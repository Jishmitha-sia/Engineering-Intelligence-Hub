# Engineering Intelligence Hub

> AI-powered engineering knowledge platform for software teams

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

## Overview

Engineering Intelligence Hub helps software teams upload technical documents, search knowledge semantically, chat with documentation via RAG, analyze GitHub repos, and measure AI quality — in one monolithic SaaS platform.

**Status (19 June 2026)**: Phase 1 (authentication & foundation) ~95% complete.

## Quick start

```powershell
# 1. Environment
Copy-Item .env.example .env

# 2. Start services (Docker Desktop must be running)
docker compose up -d --build

# 3. Database migrations
docker compose exec backend alembic upgrade head
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

**Full setup & manual testing**: see [`docs/setup.md`](docs/setup.md)

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/README.md`](docs/README.md) | Documentation index |
| [`docs/ProjectState.md`](docs/ProjectState.md) | Current status — **read this to continue work** |
| [`docs/setup.md`](docs/setup.md) | Setup, manual testing, commit/push guide |
| [`docs/CHANGELOG.md`](docs/CHANGELOG.md) | Version history |
| [`docs/specs/tasks.md`](docs/specs/tasks.md) | 10-phase implementation plan |
| [`docs/specs/requirements.md`](docs/specs/requirements.md) | Requirements |
| [`docs/specs/design.md`](docs/specs/design.md) | Technical design |
| [`docs/ArchitectureDecisionRecords.md`](docs/ArchitectureDecisionRecords.md) | ADRs |

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│  Next.js    │───▶│   FastAPI   │───▶│  PostgreSQL      │
│  Frontend   │    │   Backend   │    │  + pgvector      │
└─────────────┘    └──────┬──────┘    └──────────────────┘
                          │
                   ┌──────▼──────┐
                   │   Ollama    │  (Phase 4+)
                   └─────────────┘
```

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.11+, Pydantic V2 |
| Database | PostgreSQL 15 + pgvector |
| Auth | JWT + bcrypt |
| AI (planned) | BGE embeddings, Ollama LLM, LangGraph |
| Deploy | Docker Compose |

## Project structure

```
Engineering-Intelligence-Hub/
├── README.md              # This file
├── .env.example           # Environment template (commit)
├── .env                   # Local secrets (do not commit)
├── backend/               # FastAPI application
├── frontend/              # Next.js application
├── docker/                # Postgres init scripts
├── docs/                  # All documentation
├── docker-compose.yml
└── docker-compose.dev.yml
```

## Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Authentication & foundation | ~95% |
| 2 | Workspace management | Planned |
| 3 | Document ingestion | Planned |
| 4 | RAG chat | Planned |
| 5 | GitHub integration | Planned |
| 6–10 | Self-healing RAG, eval, monitoring, prod | Planned |

## Contributing

1. Read [`docs/ProjectState.md`](docs/ProjectState.md) and [`docs/specs/tasks.md`](docs/specs/tasks.md)
2. Follow [`docs/setup.md`](docs/setup.md) for local testing
3. Update `docs/CHANGELOG.md` and `docs/ProjectState.md` with your changes

## License

MIT — see [LICENSE](LICENSE) (to be added).

---

**Repository**: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub
