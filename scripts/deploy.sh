#!/bin/bash
set -euo pipefail

# === Config ===
STACK_NAME="litestar_stack"
SERVICE_NAME="${STACK_NAME}_litestar-app"
IMAGE_NAME="litestar-app-image"

# === Load env ===
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# === Validate WORKDIR ===
if [ -z "${WORKDIR:-}" ]; then
  echo "❌ Error: WORKDIR not set. Please specify in .env or environment."
  exit 1
fi

BACKEND_DIR="${WORKDIR}/backend"
cd "$BACKEND_DIR"

# === Git Pull ===
echo "🔄 Pulling latest changes from main..."
git pull origin main

# === Build image ===
echo "🔨 Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

# === Confirm image is referenced in docker-compose.yml ===
if ! grep -q "$IMAGE_NAME" docker-compose.yml; then
  echo "⚠️ Warning: '$IMAGE_NAME' not found in docker-compose.yml. Make sure it's set under 'image:' for litestar-app."
fi

# === Deploy stack ===
echo "📦 Deploying stack '$STACK_NAME' to Docker Swarm..."
docker stack deploy -c docker-compose.yml -c docker-compose.override.prod.yml "$STACK_NAME"

# === Wait for replicas to be healthy ===
echo "⏳ Waiting for service '$SERVICE_NAME' to be healthy..."

# Get desired replica count
REPLICAS=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' "$SERVICE_NAME")

until [ "$(docker service ps --filter 'desired-state=running' --format '{{.CurrentState}}' "$SERVICE_NAME" | grep -c 'Running')" -eq "$REPLICAS" ]; do
  echo "⏳ $SERVICE_NAME: Waiting for $REPLICAS replicas to be running..."
  sleep 5
done

# Optional: Wait for health to be 'healthy' (if healthcheck is in place)
ALL_HEALTHY=false
for i in {1..10}; do
  if docker service ps "$SERVICE_NAME" --no-trunc --format '{{.CurrentState}}' | grep -q "Running.*(healthy)"; then
    ALL_HEALTHY=true
    break
  fi
  echo "💤 Waiting for container health checks to report 'healthy'..."
  sleep 5
done

if [ "$ALL_HEALTHY" = false ]; then
  echo "⚠️ Warning: Health checks not fully passed yet. Proceeding anyway."
fi

# === Tailscale HTTPS ===
echo "🌐 Configuring Tailscale HTTPS tunnel to port 8000..."
tailscale serve --https 443 localhost:8000

echo "✅ Deployment complete!"
