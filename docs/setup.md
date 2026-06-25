# Setup & Manual Testing Guide

**Last updated**: 22 June 2026

Step-by-step instructions to run the project locally, test Phase 1 (authentication), and verify everything before committing and pushing to GitHub.

---

## Prerequisites

Install and verify:

| Tool | Version | Check command |
|------|---------|---------------|
| Docker Desktop | Latest | `docker --version` |
| Git | Any recent | `git --version` |
| Node.js (optional, for local frontend) | 20+ | `node --version` |
| Python (optional, for local backend tests) | 3.11+ | `python --version` |

**Important**: Start **Docker Desktop** and wait until it shows "Running" before any `docker compose` commands.

---

## Part 1 — One-time setup

### Step 1: Clone (if not already)

```powershell
git clone git@github.com:Jishmitha-sia/Engineering-Intelligence-Hub.git
cd Engineering-Intelligence-Hub
```

### Step 2: Create environment files

```powershell
# Root .env (backend / Docker)
Copy-Item .env.example .env

# Frontend API URL
Set-Content -Path frontend\.env.local -Value "NEXT_PUBLIC_API_URL=http://localhost:8000"
```

Edit `.env` if needed. Minimum for local dev:

- `JWT_SECRET_KEY` — at least 32 characters
- `DATABASE_URL` — default works with Docker Compose postgres service

**Optional - OAuth Social Login** (Phase 2 feature):
- To enable Google/GitHub login, add OAuth credentials to `.env`
- See [oauth-quick-start.md](./oauth-quick-start.md) for 5-minute setup
- Skip this if you only need email/password login

### Step 3: Build and start services

```powershell
docker compose up -d --build
```

Wait 1–2 minutes, then check status:

```powershell
docker compose ps
```

Expected: `postgres`, `backend`, `frontend` running. `ollama` may also be up (not required for Phase 1 auth).

### Step 4: Run database migrations

```powershell
docker compose exec backend alembic upgrade head
```

Expected output includes `Running upgrade  -> 001`.

---

## Part 2 — Manual testing (Phases 1 & 2)

### Authentication Tests (Phase 1)

### Test 1: Backend health check

Open in browser or run:

```powershell
curl http://localhost:8000/health
```

**Pass criteria**: JSON with `"status": "healthy"`.

### Test 2: API documentation

Open: http://localhost:8000/docs

**Pass criteria**: Swagger UI loads; you see `/api/v1/auth/register`, `/api/v1/auth/login`, etc.

### Test 3: Register via API (optional)

In Swagger UI:

1. Expand `POST /api/v1/auth/register`
2. Try it out with:

```json
{
  "email": "manual-test@example.com",
  "password": "SecurePass123!",
  "full_name": "Manual Tester"
}
```

**Pass criteria**: `201` response with `access_token` and user object.

### Test 4: Frontend landing page

Open: http://localhost:3000

**Pass criteria**: Landing page with "Get started" and "Sign in" buttons.

### Test 5: User registration (UI)

1. Go to http://localhost:3000/register
2. Fill in:
   - Full name: `Manual Tester`
   - Email: `ui-test@example.com`
   - Password: `SecurePass123!` (uppercase, lowercase, digit, special char)
3. Click **Create account**

**Pass criteria**: Redirect to `/dashboard` with welcome message and your email shown.

### Test 6: Sign out and sign in

1. Click **Sign out** → should go to `/login`
2. Sign in with the same email/password

**Pass criteria**: Redirect back to `/dashboard`.

### Test 7: Protected route

1. Sign out
2. Try opening http://localhost:3000/dashboard directly

**Pass criteria**: Redirect to `/login`.

### Test 8: Invalid login

1. On login page, use wrong password

**Pass criteria**: Error message shown (no crash).

### Test 9: Duplicate registration

1. Try registering again with the same email

**Pass criteria**: Error like "Email already registered".

### Test 10: Backend unit tests (optional, no Docker DB needed)

```powershell
cd backend
pip install fastapi uvicorn sqlalchemy asyncpg alembic python-jose passlib bcrypt pydantic pydantic-settings email-validator httpx pytest pytest-asyncio
$env:PYTHONPATH="app"
pytest tests/unit -v --no-cov
```

**Pass criteria**: 4 tests passed.

### Workspace & OAuth Tests (Phase 2)

**Test 11: Create Workspace**

1. Go to http://localhost:3000/workspaces
2. Click **Create workspace**
3. Enter name and description
4. Click **Create**

**Pass criteria**: Workspace appears in list.

**Test 12: OAuth Provider Detection**

```powershell
curl http://localhost:8000/api/v1/auth/oauth/providers
```

**Pass criteria**: Returns `{"google":false,"github":false}` (or `true` if configured)

**For full Phase 2 testing** (workspaces, invitations, OAuth):
- See [phase2-testing.md](./phase2-testing.md) for comprehensive test suite
- See [oauth-quick-start.md](./oauth-quick-start.md) to enable OAuth (optional)

---

## Part 3 — Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker compose` fails with pipe error | Start Docker Desktop |
| Backend won't start | `docker compose logs backend` — check DB connection |
| Frontend can't reach API | Confirm `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| Migration error | `docker compose exec backend alembic upgrade head` |
| Port already in use | Stop other apps on 3000, 8000, or 5432 |
| CORS errors | Ensure `ALLOWED_HOSTS` in `.env` includes `http://localhost:3000` |

View logs:

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

Stop everything:

```powershell
docker compose down
```

---

## Part 4 — Commit and push to GitHub

Run these **only after** manual tests pass.

### Step 1: Review what will be committed

```powershell
git status
```

**Must NOT appear** (secrets / build artifacts):

- `.env`
- `frontend/.env.local`
- `node_modules/`
- `frontend/.next/`
- `backend/.pytest_cache/`

**Should appear**:

- `backend/`, `frontend/`, `docs/`, `docker/`
- `.env.example`, `.gitignore`, `README.md`, `docker-compose.yml`

### Step 2: Stage files

```powershell
git add .
git status
```

Double-check `.env` is **not** staged.

### Step 3: Commit

```powershell
git commit -m "feat: Phase 1 foundation — auth, frontend, docs structure

- FastAPI backend with JWT auth and Alembic migrations
- Next.js frontend with login/register and dashboard
- Docker Compose for postgres, backend, frontend
- Documentation moved to docs/ with setup guide"
```

### Step 4: Push

```powershell
git push -u origin main
```

If your default branch is `master`, use that instead. If the remote has existing history:

```powershell
git pull origin main --rebase
git push -u origin main
```

### Step 5: Verify on GitHub

Open: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub

Confirm:

- `docs/` folder with all markdown files
- `README.md` at root
- No `.env` file visible in the repo

---

## Part 5 — Local development without full Docker (alternative)

**Backend only** (requires postgres running via Docker):

```powershell
docker compose up postgres -d
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH="app"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend only** (separate terminal):

```powershell
cd frontend
npm install
npm run dev
```

---

## Next development step

After Phase 1 & 2 are verified and pushed:
- ✅ Phase 1 complete: Authentication
- ✅ Phase 2 complete: Workspaces, Invitations, OAuth
- 🚀 Continue with **Phase 3: Document Ingestion** — see [specs/tasks.md](./specs/tasks.md) and [ProjectState.md](./ProjectState.md)

**Phase 2 Summary**: See [PHASE2_COMPLETE.md](./PHASE2_COMPLETE.md) for full feature list and testing procedures.
