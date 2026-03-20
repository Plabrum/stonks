#!/usr/bin/env bash
# Tears down a worktree's dev environment: drops database, removes .env.local.
# Non-interactive — safe to run from hooks.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
MAIN_ROOT=$(cd "$ROOT" && git rev-parse --git-common-dir | xargs -I{} dirname "$(readlink -f "{}")" 2>/dev/null || echo "$ROOT")

# Nothing to tear down if no .env.local
if [ ! -f "$ROOT/.env.local" ]; then
    echo "No .env.local found, nothing to tear down."
    exit 0
fi

# Parse database name from .env.local
DB_URL=$(grep -m1 '^DATABASE_URL=' "$ROOT/.env.local" | cut -d= -f2-)
if [ -n "$DB_URL" ]; then
    DB_NAME=$(echo "$DB_URL" | sed 's|.*/||')
    BASE_PREFIX=$(echo "$DB_URL" | sed 's|/[^/]*$||')
    ADMIN_URL="${BASE_PREFIX}/postgres"

    echo "Dropping database ${DB_NAME}..."
    psql "$ADMIN_URL" -c "DROP DATABASE IF EXISTS ${DB_NAME};" 2>/dev/null || echo "Warning: could not drop database ${DB_NAME}"
fi

rm -f "$ROOT/.env.local"
echo "Worktree teardown complete."
