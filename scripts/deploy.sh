#!/bin/bash
set -e

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "$WORKDIR" ]; then
  echo "Error: WORKDIR not set. Please specify in .env or environment."
  exit 1
fi

BACKEND_DIR="${WORKDIR}/backend"

cd "$BACKEND_DIR"

echo "Pulling latest changes..."
git pull origin main

echo "Rebuilding and restarting..."
docker compose build
docker compose up -d
