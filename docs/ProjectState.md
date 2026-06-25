# Project State

## Engineering Intelligence Hub - Current Status

**Project Repository**: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub.git

**Last Updated**: 25 June 2026 (Phase 2 complete + bug fixes)

**Current Phase**: Phase 2 - Complete & Tested

**Documentation**: All `.md` files live in [`docs/`](../docs/). Start with [`docs/README.md`](../docs/README.md).

---

## Project Overview

Engineering Intelligence Hub is an AI-powered engineering knowledge platform that enables software teams to upload technical documents, search engineering knowledge, chat with project documentation, analyze GitHub repositories, and evaluate AI quality—all in one monolithic SaaS application optimized for portfolio demonstration.

**Target**: 80% production-level AI SaaS suitable as flagship portfolio project for AI Engineer / GenAI Engineer roles

**Architecture**: Monolithic (FastAPI + Next.js + PostgreSQL + Ollama)

---

## Repository Structure (22-06-2026)

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
│   ├── setup.md              # Setup & manual testing
│   ├── TESTING.md            # Comprehensive testing guide
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

### Phase 1: Foundation — Complete (19-06-2026)

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

### Phase 2: Workspace Management — Complete (22-06-2026)

#### Backend (Tasks 2.1–2.2)

- [x] `Workspace` and `WorkspaceMember` models with Owner/Member roles
- [x] Alembic migration `002_create_workspaces.py`
- [x] Workspace service with access control
- [x] Workspace API: CRUD, member invite/remove
- [x] Workspace access dependencies in `dependencies.py`
- [x] `WorkspaceInvitation` model with status tracking
- [x] Invitation API: send, accept, decline, cancel, list
- [x] Alembic migration `003_workspace_invitations_oauth.py`

#### Frontend (Task 2.3)

- [x] `WorkspaceContext` with workspace switching (localStorage)
- [x] Dashboard shell with nav and workspace switcher
- [x] `/workspaces` page: list, create, edit, delete
- [x] Member manager: invite by email, remove members (owner only)
- [x] Role-based UI (owner vs member actions)
- [x] `DeleteWorkspaceDialog` with confirmation modal
- [x] `PendingInvitations` component with accept/decline buttons

#### OAuth Integration (Phase 2 Extension)

- [x] Google OAuth 2.0 login flow
- [x] GitHub OAuth login flow
- [x] OAuth service with state validation
- [x] User model OAuth fields (`oauth_provider`, `oauth_subject`)
- [x] OAuth endpoints and callbacks
- [x] Frontend OAuth buttons with provider detection
- [x] OAuth callback page for token handling
- [x] Account linking (email-based user merge)

---

## Pending — Phase 1 wrap-up

- [x] Docker stack running (postgres, backend, frontend)
- [x] Alembic migration applied (`001_create_users`)
- [x] API smoke test: register + login working
- [x] Manual UI test — register/login in browser
- [x] First commit and push to GitHub

### Recent Updates (25-06-2026)

**Phase 2 Complete + Bug Fixes**:
1. ✅ **Workspace Management** — Full CRUD with role-based access
2. ✅ **Workspace Invitations** — Send, accept, decline, cancel workflow
3. ✅ **OAuth Integration** — Google and GitHub social login working
4. ✅ **Delete Confirmation** — Modal with workspace name typing requirement (GitHub-style)
5. ✅ **Bug Fix** — Screen glitching (infinite re-render loop) **RESOLVED**
   - **Root cause**: Three components had infinite loops from function dependencies in React hooks
   - **Fixed files**: 
     - `WorkspaceContext.tsx` - Removed circular dependency in acceptInvitation
     - `WorkspaceList.tsx` - Removed redundant refreshWorkspaces calls
     - `MemberManager.tsx` - Fixed useEffect dependencies and removed refresh call (main culprit)
   - **Solution**: Never use callback functions in dependency arrays, only primitive values
6. ✅ **Automated Tests** — Backend unit tests passing (4/4)

**Testing**:
- Automated backend tests: ✅ 4/4 unit tests passing
- Screen glitching bug: ✅ **FULLY FIXED** after finding all three sources
- Integration tests: Deferred to Phase 9

**Documentation**:
- Consolidated into docs/ folder
- Removed unnecessary PHASE2_SUMMARY.md
- Moved OAuth setup to docs/oauth-setup.md
- All information in ProjectState.md and CHANGELOG.md

### Issues fixed (19-06-2026)

1. **`.env` list parsing** — `ALLOWED_HOSTS` comma-separated values crashed Pydantic; now stored as strings
2. **Stale `import jwt`** in `dependencies.py` — removed unused import
3. **DB auto-create on startup** — broke in Docker (wrong `postgres` role); skipped for Docker dev
4. **Frontend `npm ci`** — lock file sync fixed; Docker uses `npm install`

---

## Next Up — Phase 3: Document Ingestion

**Ready to Start**: After Phase 2 testing complete

**What's Coming**:
- [ ] Document model and file storage
- [ ] Upload API (PDF, DOCX, TXT, Markdown)
- [ ] Text extraction pipeline
- [ ] Chunking algorithm (512 tokens, 50 overlap)
- [ ] Embedding generation (BAAI/bge-small-en-v1.5)
- [ ] Background processing
- [ ] Document list UI per workspace

See [`docs/specs/tasks.md`](./specs/tasks.md) for full task list.

---

## Completed — Phase 2 (reference)

- [x] Workspace and WorkspaceMember models
- [x] CRUD API with Owner/Member roles
- [x] Workspace management UI

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

## How to Test

See [`docs/TESTING.md`](./TESTING.md) for comprehensive testing guide.

**Quick Test**:
```powershell
# Automated tests
docker compose exec backend pytest tests/unit -v

# Manual tests
Start-Process http://localhost:3000/workspaces
```

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
