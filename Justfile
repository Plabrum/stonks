# Stonks Justfile — https://just.systems

set dotenv-filename := ".env.local"
set dotenv-load := true
set dotenv-required := false

# Configurable ports (override via .env.local or env vars for worktree dev)
export BACKEND_PORT := env("BACKEND_PORT", "8000")
export FRONTEND_PORT := env("FRONTEND_PORT", "5173")

# List available commands
default:
    @just --list

# ─── Install ──────────────────────────────────────────────────────────────────

# Install all dependencies
install:
    cd backend && uv sync --dev
    cd frontend && npm install

# ─── Database ─────────────────────────────────────────────────────────────────

# Start dev postgres
db-start:
    docker compose -f docker-compose.dev.yml up -d

# Stop dev postgres
db-stop:
    docker compose -f docker-compose.dev.yml down

# Create a new migration from model changes
db-migrate +message:
    cd backend && uv run alembic revision --autogenerate -m "{{message}}"

# Apply all pending migrations
db-upgrade:
    cd backend && uv run alembic upgrade head

# Downgrade by one revision
db-downgrade:
    cd backend && uv run alembic downgrade -1

# ─── Development ──────────────────────────────────────────────────────────────

# Run backend + frontend dev servers in parallel
dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    just dev-backend &
    just dev-frontend &
    wait

# Start Litestar backend with hot reload
dev-backend:
    cd backend && uv run litestar --app app.index:app run -r -d -p ${BACKEND_PORT}

# Start Vite frontend dev server
dev-frontend:
    cd frontend && npm run dev -- --port ${FRONTEND_PORT}

# Start SAQ worker
dev-worker:
    cd backend && uv run litestar --app app.index:app workers run

# ─── Codegen ──────────────────────────────────────────────────────────────────

# Generate API client from live backend schema (requires backend running)
codegen:
    cd frontend && OPENAPI_URL="http://localhost:${BACKEND_PORT}/schema/openapi.json" npx orval

# ─── Code Quality ─────────────────────────────────────────────────────────

# Lint backend code
lint:
    cd backend && uv run ruff check .

# Lint frontend code
lint-frontend:
    cd frontend && npm run lint

# Format backend code
fmt:
    cd backend && uv run ruff format .

# Type-check backend code
typecheck:
    cd backend && uv run basedpyright

# ─── Build ────────────────────────────────────────────────────────────────────

# Build frontend for production
build:
    cd frontend && npm run build
