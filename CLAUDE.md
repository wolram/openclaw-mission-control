# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

OpenClaw Mission Control is an operations and governance platform for running AI agents across teams. It provides work orchestration (orgs → board groups → boards → tasks), agent lifecycle management, human-in-the-loop approval workflows, gateway integration for distributed execution, and activity audit trails.

## Commands

### Setup
```bash
make setup            # Install backend (uv) + frontend (npm) dependencies
cp .env.example .env  # Configure LOCAL_AUTH_TOKEN (min 50 chars) for local auth
```

### Development (fast local loop)
```bash
docker compose -f compose.yml --env-file .env up -d db   # Start DB + Redis only
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

### Full Docker stack
```bash
make docker-up       # Build and start full stack
make docker-watch    # Start with auto-rebuild on file changes
make docker-down     # Stop
```

### Testing
```bash
make test                  # All tests
make backend-test          # pytest only
make backend-coverage      # pytest with coverage gates
make frontend-test         # vitest only
cd backend && uv run pytest tests/path/to/test_file.py::test_name  # Single test
```

### Code Quality
```bash
make format          # Format backend (black + isort) + frontend (prettier)
make format-check    # Check without modifying
make lint            # flake8 + eslint + docs
make typecheck       # mypy --strict + tsc
make check           # Full CI gate: lint + typecheck + tests + coverage + build
```

### Database Migrations
```bash
make backend-migrate           # Apply Alembic migrations
make backend-migration-check   # Validate migration graph and reversibility
# Policy: exactly one migration per PR; CI enforces forward + backward compatibility
```

### API Client Generation
```bash
make api-gen   # Regenerate frontend/src/api/generated/ from OpenAPI spec
               # Backend must be running on 127.0.0.1:8000
```

## Architecture

### Services
- **Frontend** (port 3000): Next.js 16 / React 19 / TypeScript / Tailwind CSS / Radix UI. TanStack Query for data fetching. TanStack Table for data tables.
- **Backend** (port 8000): FastAPI / Python 3.12 / SQLModel (async SQLAlchemy 2). OpenAPI spec auto-generated.
- **Database**: PostgreSQL 16 (async via psycopg 3)
- **Queue**: Redis 7 + RQ for background jobs (webhooks, notifications)

### Backend Structure (`backend/app/`)
- `api/` — 26+ FastAPI routers, one file per resource (e.g. `tasks.py`, `agents.py`, `boards.py`)
- `models/` — SQLModel ORM models (~30 files)
- `schemas/` — Pydantic request/response schemas (separate from models)
- `services/` — Business logic; `services/openclaw/` for agent-specific ops, `services/webhooks/` for webhook handling
- `core/` — Config (`config.py`), error handling (`error_handling.py`), logging, security headers
- `db/` — Async database session management
- `migrations/versions/` — Alembic migration files

### Frontend Structure (`frontend/src/`)
- `app/` — Next.js App Router pages (dashboard, boards, agents, approvals, gateways, activity, skills, etc.)
- `components/` — Atomic design: `atoms/`, `molecules/`, `organisms/`, `ui/` (Radix wrappers), `tables/`, `charts/`
- `api/generated/` — **Auto-generated** TypeScript API client via Orval; never edit directly
- `hooks/` — Custom React hooks
- `lib/` — Utilities and helpers

### Domain Model
Hierarchy: **Organizations** → **Board Groups** → **Boards** → **Tasks**. **Agents** operate within boards. **Gateways** connect to remote execution environments. **Approvals** are human-in-the-loop gates on workflows. **Activity** provides an immutable audit log.

### Authentication
Two modes (set via `AUTH_MODE` env var):
- `local` (default): shared bearer token (`LOCAL_AUTH_TOKEN`, min 50 chars)
- `clerk`: Clerk JWT integration

## Code Conventions

### Python
- Black + isort + flake8 + mypy `--strict`. Max line length: 100.
- `snake_case` throughout.
- **100% test coverage enforced** on `app.core.error_handling` and `app.services.mentions`.

### TypeScript / React
- ESLint + Prettier. Components: `PascalCase`. Variables/functions: `camelCase`.
- Prefix unused destructured variables with `_`.

### Commits
Conventional Commits format: `feat:`, `fix:`, `docs:`, `test(core):`, etc.
