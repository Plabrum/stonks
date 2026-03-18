# Stonks Justfile — https://just.systems

# List available commands
default:
    @just --list

# ─── Install ──────────────────────────────────────────────────────────────────

# Install all dependencies
install:
    cd backend && uv sync --dev
    cd frontend && npm install

# ─── Database ─────────────────────────────────────────────────────────────────

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
    cd backend && uv run litestar --app app.index:app run -r -d -p 8000

# Start Vite frontend dev server
dev-frontend:
    cd frontend && npm run dev

# Start SAQ worker
dev-worker:
    cd backend && uv run litestar --app app.index:app workers run

# ─── Codegen ──────────────────────────────────────────────────────────────────

# Generate API client from live backend schema (requires backend on :8000)
codegen:
    cd frontend && npx orval

# ─── Build ────────────────────────────────────────────────────────────────────

# Build frontend for production
build:
    cd frontend && npm run build
