#!/usr/bin/env bash
# Sets up a worktree for development: unique ports + dedicated database.
# Idempotent — safe to run multiple times.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
MAIN_ROOT=$(cd "$ROOT" && git rev-parse --git-common-dir | xargs -I{} dirname "$(readlink -f "{}")" 2>/dev/null || echo "$ROOT")

# If .env.local already exists with ports, we're done
if [ -f "$ROOT/.env.local" ] && grep -q BACKEND_PORT "$ROOT/.env.local" 2>/dev/null; then
    echo "Worktree already configured:"
    cat "$ROOT/.env.local"
    exit 0
fi

# ─── Database ────────────────────────────────────────────────────────────────

# Read the base DATABASE_URL from the main repo's .env
BASE_DB_URL=$(grep -m1 '^DATABASE_URL=' "$MAIN_ROOT/.env" 2>/dev/null | cut -d= -f2-)
if [ -z "$BASE_DB_URL" ]; then
    echo "Error: no DATABASE_URL found in $MAIN_ROOT/.env"
    exit 1
fi

# Derive worktree name from directory
WORKTREE_NAME=$(basename "$ROOT")
# Sanitize for use as a postgres db name (lowercase, hyphens to underscores)
DB_SUFFIX=$(echo "$WORKTREE_NAME" | tr '[:upper:]' '[:lower:]' | tr '-' '_')

# Parse base URL to swap the database name
# Format: postgresql://user:pass@host:port/dbname
BASE_PREFIX=$(echo "$BASE_DB_URL" | sed 's|/[^/]*$||')  # everything before /dbname
DB_NAME="finance_${DB_SUFFIX}"
WORKTREE_DB_URL="${BASE_PREFIX}/${DB_NAME}"

# Create the database if it doesn't exist
echo "Creating database ${DB_NAME}..."
ADMIN_URL="${BASE_PREFIX}/postgres"
psql "$ADMIN_URL" -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || \
    psql "$ADMIN_URL" -c "CREATE DATABASE ${DB_NAME};"
echo "Database ${DB_NAME} ready."

# ─── Ports ───────────────────────────────────────────────────────────────────

find_free_port() {
    local port=$1
    local varname=$2
    while true; do
        if ss -tlnH "sport = :$port" 2>/dev/null | grep -q ":$port"; then
            port=$((port + 1)); continue
        fi
        if grep -rq "${varname}=$port" "$MAIN_ROOT/.claude/worktrees/"*/".env.local" 2>/dev/null; then
            port=$((port + 1)); continue
        fi
        if [ -f "$MAIN_ROOT/.env.local" ] && grep -q "${varname}=$port" "$MAIN_ROOT/.env.local" 2>/dev/null; then
            port=$((port + 1)); continue
        fi
        break
    done
    echo "$port"
}

BACKEND_PORT=$(find_free_port 8001 BACKEND_PORT)
FRONTEND_PORT=$(find_free_port 5174 FRONTEND_PORT)

# ─── Write config ────────────────────────────────────────────────────────────

cat > "$ROOT/.env.local" <<EOF
BACKEND_PORT=$BACKEND_PORT
FRONTEND_PORT=$FRONTEND_PORT
DATABASE_URL=$WORKTREE_DB_URL
EOF

echo ""
echo "Worktree configured:"
echo "  Database: $DB_NAME"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo ""
echo "Run 'just db-upgrade' to apply migrations, then 'just dev' to start."
