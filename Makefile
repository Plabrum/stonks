# Monorepo Makefile using uv + yarn

FRONTEND_DIR=frontend
BACKEND_DIR=backend
DEPLOY_SCRIPT=scripts/deploy.sh
DEV_SCRIPT=scripts/dev.sh

.PHONY: dev
dev:
	bash $(DEV_SCRIPT)

.PHONY: build
build:
	@echo "Building frontend..."
	cd $(FRONTEND_DIR) && yarn build
	@echo "Building backend Docker image..."
	cd $(BACKEND_DIR) && docker build -t my-backend .

.PHONY: server
server:
	@echo "Running deploy script locally..."
	bash $(DEPLOY_SCRIPT)

.PHONY: dc-up
dc-up:
	@echo "Starting Docker Compose services..."
	cd $(BACKEND_DIR) && docker compose up -d

.PHONY: dc-down
dc-down:
	@echo "Stopping Docker Compose services..."
	cd $(BACKEND_DIR) && docker compose down

.PHONY: dc-build
dc-build:
	@echo "Building Docker Compose services..."
	cd $(BACKEND_DIR) && docker compose build
