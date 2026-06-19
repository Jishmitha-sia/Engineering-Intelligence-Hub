# What to Commit to GitHub

**Last updated**: 19 June 2026

This project follows standard open-source hygiene. **Never commit secrets or generated artifacts.**

## Commit these

| Path | Why |
|------|-----|
| `README.md` | Root project overview |
| `LICENSE` | MIT license |
| `.gitignore` | Ignore rules |
| `.env.example` | Environment template (no secrets) |
| `backend/` | FastAPI source, Alembic, tests, `requirements-*.txt` |
| `frontend/` | Next.js source, `package.json`, `package-lock.json` |
| `docker/` | Postgres init scripts |
| `docs/` | All documentation and specs |
| `docker-compose.yml` | Service orchestration |
| `docker-compose.dev.yml` | Dev overrides |

## Never commit these

| Path | Why |
|------|-----|
| `.env` | Contains JWT secret and local config |
| `frontend/.env.local` | API URL / local frontend secrets |
| `node_modules/` | Installed dependencies |
| `frontend/.next/` | Next.js build output |
| `backend/.pytest_cache/` | Test cache |
| `backend/htmlcov/` | Coverage reports |
| `uploads/`, `logs/`, `tmp/` | Runtime data |
| `.kiro/` | Local AI workspace metadata |

## Verify before every commit

```powershell
git status
git check-ignore -v .env frontend/.env.local
```

If `.env` appears in `git status` as staged, run `git reset HEAD .env` immediately.

## When to test vs when to commit

| Stage | Who | What |
|-------|-----|------|
| **Automated tests** | Agent / CI | Unit tests, Docker health, API smoke tests |
| **Manual UI test** | **You** | Register, login, logout in browser — 5 min checklist in `setup.md` |
| **Commit** | **You** (after manual test passes) | Stage, commit, push |
| **Push** | **You** | Only after commit; verify GitHub has no `.env` |

The agent runs automated checks; **you** confirm the UI works in the browser before the first push.
