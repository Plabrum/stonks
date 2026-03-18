# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python app
FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Configure uv behaviour for reproducible builds
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_INSTALLER_METADATA=1
ENV UV_LINK_MODE=copy

# Install project dependencies into a managed virtualenv
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=backend/uv.lock,target=uv.lock \
  --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-dev

# Copy application source
COPY backend/ /app

# Copy built frontend assets
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Make scripts executable
RUN chmod +x /app/scripts/start.sh /app/scripts/start-worker.sh /app/scripts/migrate.py

# Ensure the project venv is preferred at runtime
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["./scripts/start.sh"]
