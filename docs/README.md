# Documentation

**Last updated**: 19 June 2026

Central documentation for the Engineering Intelligence Hub project. Use this folder to pick up work after a break or a new chat session.

## Quick links

| Document | Purpose |
|----------|---------|
| [ProjectState.md](./ProjectState.md) | **Start here** — current phase, what's done, what's next |
| [setup.md](./setup.md) | Local setup and **manual testing** before commit/push |
| [CHANGELOG.md](./CHANGELOG.md) | Version history and notable changes |
| [ArchitectureDecisionRecords.md](./ArchitectureDecisionRecords.md) | ADRs — why we chose each technology |
| [specs/tasks.md](./specs/tasks.md) | Full 10-phase implementation task list |
| [specs/requirements.md](./specs/requirements.md) | Functional & non-functional requirements |
| [specs/design.md](./specs/design.md) | Technical design, schema, API architecture |

## Project status snapshot (19-06-2026)

- **Phase 0** (Planning): Complete
- **Phase 1** (Auth & foundation): ~95% — backend auth, frontend login/register, Docker Compose
- **Phase 2** (Workspaces): Next
- **Phases 3–10**: Not started

## Repository layout

```
Engineering-Intelligence-Hub/
├── README.md                 # Project overview (root only)
├── .env.example              # Environment template (commit this)
├── .env                      # Local secrets (never commit)
├── backend/                  # FastAPI application
├── frontend/                 # Next.js application
├── docker/                   # PostgreSQL init scripts
├── docs/                     # All project documentation (this folder)
│   ├── ProjectState.md
│   ├── setup.md
│   ├── CHANGELOG.md
│   ├── ArchitectureDecisionRecords.md
│   └── specs/
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
├── docker-compose.yml
└── docker-compose.dev.yml
```

## Maintenance rule

When completing a phase or significant task:

1. Update `ProjectState.md` with date and checklist
2. Add an entry under `[Unreleased]` in `CHANGELOG.md`
3. Mark tasks complete in `specs/tasks.md` if applicable
