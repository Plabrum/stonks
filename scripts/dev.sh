#!/usr/bin/env bash
set -e

echo "Starting backend and frontend..."

# Kill both processes on exit or Ctrl+C
trap 'kill 0' SIGINT SIGTERM EXIT

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
