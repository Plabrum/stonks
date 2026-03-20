---
name: worktree
description: Set up or tear down a Claude Code worktree for parallel development. Handles port assignment, database creation, dependency installation, and cleanup. Use after `claude --worktree` or when asked to work in a worktree.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: <setup|teardown|list>
---

# Worktree Dev Environment

This skill manages the **dev environment** (ports, database, deps) for worktrees. Worktree creation itself is handled by Claude Code natively (`claude --worktree <name>` or `claude -w`).

Native worktrees live at `.claude/worktrees/<name>/` with branches named `worktree-<name>`.

## Commands

### `/worktree setup`

Set up the current worktree for development. Run this after entering a worktree.

Steps:

1. **Create database + assign unique ports:**
   ```bash
   bash scripts/worktree-setup.sh
   ```
   This creates a dedicated postgres database (e.g. `finance_worktree_feature_auth`), scans for free ports, and writes `.env.local` with `BACKEND_PORT`, `FRONTEND_PORT`, and `DATABASE_URL`.

2. **Install dependencies:**
   ```bash
   just install
   ```

3. **Run migrations:**
   ```bash
   just db-upgrade
   ```

4. **Report** the database name, assigned ports, and remind the user they can run `just dev` to start.

### `/worktree teardown [name]`

Clean up a worktree's dev environment and remove it.

Steps:

1. If no name provided, **list worktrees** and ask which to remove:
   ```bash
   git worktree list
   ```

2. **Read the worktree's `.env.local`** to find its database name. Parse `DATABASE_URL` to extract the db name (the last path segment).

3. **Drop the worktree database:**
   ```bash
   # Parse base connection info from the main repo's .env
   # Connect to the 'postgres' admin db to drop the worktree db
   psql postgresql://user:pass@host:port/postgres -c "DROP DATABASE IF EXISTS <db_name>;"
   ```
   Confirm with the user before dropping.

4. **Remove the worktree:**
   ```bash
   git worktree remove .claude/worktrees/<name>
   ```
   If it has uncommitted changes, warn the user and ask for confirmation before using `--force`.

5. **Optionally delete the branch** — ask the user:
   ```bash
   git branch -d worktree-<name>
   ```
   Use `-d` (safe delete). If it warns about unmerged changes, tell the user and let them decide.

6. **Prune** stale references:
   ```bash
   git worktree prune
   ```

### `/worktree list`

List all active worktrees with their ports and databases:

```bash
git worktree list
```

For each worktree, read its `.env.local` and show the port assignments and database name. If a worktree has no `.env.local`, note that it needs `/worktree setup`.

## Resource Scheme

- **Database**: Each worktree gets its own postgres database named `finance_<sanitized_worktree_name>` on the same server as the main `finance` db. Created during setup, dropped during teardown.
- **Ports**: Main repo uses defaults (backend `8000`, frontend `5173`). Worktrees get ports starting at `8001`/`5174`, incrementing to avoid conflicts.
- **Config**: Everything is stored in `.env.local` at the worktree root, picked up automatically by `just` and the backend.

## Development in a Worktree

```bash
claude --worktree feature-auth   # create worktree (native)
# then inside the session:
/worktree setup                  # create db, assign ports, install deps, run migrations
just dev                         # start backend + frontend
```
