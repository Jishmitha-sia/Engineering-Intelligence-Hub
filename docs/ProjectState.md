# Project State

## Engineering Intelligence Hub - Current Status

**Project Repository**: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub.git

**Last Updated**: 19 June 2026 (Docker verified working)

**Current Phase**: Phase 1 - Foundation (~98% complete)

**Documentation**: All `.md` files live in [`docs/`](../docs/). Start with [`docs/README.md`](../docs/README.md).

---

## Project Overview

Engineering Intelligence Hub is an AI-powered engineering knowledge platform that enables software teams to upload technical documents, search engineering knowledge, chat with project documentation, analyze GitHub repositories, and evaluate AI quality—all in one monolithic SaaS application optimized for portfolio demonstration.

**Target**: 80% production-level AI SaaS suitable as flagship portfolio project for AI Engineer / GenAI Engineer roles

**Architecture**: Monolithic (FastAPI + Next.js + PostgreSQL + Ollama)

---

## Repository Structure (19-06-2026)

```
Engineering-Intelligence-Hub/
├── README.md                 # Root overview only
├── .env.example              # Committed template
├── .env                      # Local secrets (gitignored)
├── .gitignore
├── backend/                  # FastAPI + Alembic + tests
├── frontend/                 # Next.js 14 + auth UI
├── docker/                   # Postgres init scripts
├── docs/                     # All documentation
│   ├── ProjectState.md       # This file
│   ├── setup.md              # Manual test & commit guide
│   ├── CHANGELOG.md
│   ├── ArchitectureDecisionRecords.md
│   └── specs/
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
├── docker-compose.yml
└── docker-compose.dev.yml
```

---

## Completed Work

### Phase 0: Requirements & Design — Complete (18-06-2026)

- [x] Requirements document (`docs/specs/requirements.md`)
- [x] Technical design (`docs/specs/design.md`)
- [x] Task breakdown (`docs/specs/tasks.md`)
- [x] Architecture Decision Records (`docs/ArchitectureDecisionRecords.md`)

### Phase 1: Foundation — In Progress (19-06-2026)

#### Backend (Tasks 1.1–1.3)

- [x] FastAPI project structure with `/health`
- [x] Pydantic Settings configuration
- [x] PostgreSQL + async SQLAlchemy
- [x] Alembic migration `001_create_users.py`
- [x] User model, schemas, auth service
- [x] JWT (python-jose) + bcrypt password hashing
- [x] Auth API: register, login, logout, me, change-password
- [x] Unit tests for security (4 passing)
- [ ] Integration tests (needs PostgreSQL running)

#### Frontend (Tasks 1.4–1.5)

- [x] Next.js 14 + TypeScript + TailwindCSS
- [x] UI components (Button, Input, Card, Label)
- [x] Login and register pages
- [x] AuthContext + JWT localStorage
- [x] Protected `/dashboard` route
- [x] API client (`src/lib/api.ts`)

#### Infrastructure (Task 1.6)

- [x] Docker Compose (postgres, backend, frontend, ollama)
- [x] `docker-compose.dev.yml`
- [x] `.env.example` + `.gitignore`
- [x] Docs reorganized into `docs/`
- [x] Manual testing guide (`docs/setup.md`)

---

## Pending — Phase 1 wrap-up

- [x] Docker stack running (postgres, backend, frontend)
- [x] Alembic migration applied (`001_create_users`)
- [x] API smoke test: register + login working
- [ ] **Your manual UI test** — register/login in browser at http://localhost:3000
- [ ] First commit and push to GitHub

### Issues fixed (19-06-2026)

1. **`.env` list parsing** — `ALLOWED_HOSTS` comma-separated values crashed Pydantic; now stored as strings
2. **Stale `import jwt`** in `dependencies.py` — removed unused import
3. **DB auto-create on startup** — broke in Docker (wrong `postgres` role); skipped for Docker dev
4. **Frontend `npm ci`** — lock file sync fixed; Docker uses `npm install`

---

## Next Up — Phase 2: Workspace Management

- [ ] Workspace and WorkspaceMember models
- [ ] CRUD API with Owner/Member roles
- [ ] Workspace management UI

See [`docs/specs/tasks.md`](./specs/tasks.md) for full task list.

---

## Technology Stack Status

| Layer | Technology | Status |
|-------|-----------|--------|
| Frontend | Next.js 14, TypeScript, TailwindCSS | Implemented |
| Backend | FastAPI, Python 3.11+, Pydantic V2 | Implemented |
| Database | PostgreSQL 15 + pgvector | Configured |
| Auth | JWT (python-jose), bcrypt | Implemented |
| Embeddings | BAAI/bge-small-en-v1.5 | Not started |
| LLM | Ollama (qwen3:8b, llama3.1:8b) | Docker ready |
| Testing | Pytest unit tests | Partial |
| Deployment | Docker Compose | Configured |

---

## How to Run

See [`docs/setup.md`](./setup.md) for full instructions.

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

---

## Notes for continuing work

1. Read this file and `docs/specs/tasks.md` first
2. Update this file and `docs/CHANGELOG.md` after each phase
3. Never commit `.env` or `frontend/.env.local`
4. Ollama models only needed from Phase 4 onward
