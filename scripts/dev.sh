#!/usr/bin/env bash
set -e

echo "Starting dockerized Postgres..."
docker compose -f docker-compose.yaml up -d

echo "Starting backend and frontend..."

# Kill everything on Ctrl+C or script exit
trap 'echo "Stopping..."; kill 0; docker compose -f docker-compose-development.yaml down' SIGINT SIGTERM EXIT

# Start backend (Litestar)
(
  cd backend
  uv run litestar run --reload
) &

# Start frontend (Next.js)
(
  cd frontend
  yarn dev
) &

wait
