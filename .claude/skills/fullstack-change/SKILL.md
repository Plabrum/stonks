---
name: fullstack-change
description: >
  Guides through the full stack of changes needed when modifying a SQLAlchemy model
  in the stonks project: model edit → Alembic migration → migration apply → codegen
  → frontend TypeScript types. Use this skill whenever a backend model change needs
  to be reflected end-to-end — including adding/removing columns or tables, renaming
  fields, changing types or constraints, or any schema change that touches the API
  contract. Trigger on phrases like "add a field to the model", "update the schema",
  "new column", "change the model", "add a table", "fullstack change", "update the
  types", or whenever someone makes a backend model change and needs the frontend
  to reflect it. Always invoke this skill instead of doing just the migration or
  just the codegen in isolation — it's easy to forget a step and end up with type
  drift between backend and frontend.
---

# Fullstack Change

A backend model change ripples through four layers. This skill walks you through all of them in order so nothing gets out of sync.

```
SQLAlchemy model
    ↓  (autogenerate)
Alembic migration
    ↓  (apply)
Litestar OpenAPI schema (live at /schema/openapi.json)
    ↓  (orval codegen)
frontend/src/openapi/  ← TypeScript types + React Query hooks
```

Run the full flow. Only stop if something looks genuinely wrong — don't ask for confirmation at each step unless there's a decision to make.

---

## Step 1: Edit the model

Models live in `backend/app/*/models.py`. Each model file exports one or more SQLAlchemy `MappedColumn` classes that inherit from `BaseDBModel` (and optionally `TimestampMixin`).

If the user hasn't made the model change yet, help them make it. If they've already changed the model, move on.

**Common patterns:**

```python
# Add a nullable column
market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

# Add a non-nullable column with a server default
is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

# Add an indexed column
isin: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
```

After editing the model, verify the file has no syntax errors:
```bash
cd backend && uv run python -c "from app.company.models import *"
```
(Adjust the import path for the model you changed.)

---

## Step 2: Create and apply the migration

Use the `create-migration` skill to handle this step. It will:
1. Inspect the model diff
2. Derive a descriptive migration message
3. Run `just db-migrate <message>` to autogenerate the migration file
4. Validate the generated file for correctness
5. Run `just db-upgrade` to apply it

**Invoke it now.** Don't proceed to codegen until the migration has been applied successfully.

---

## Step 3: Ensure the backend is running and up to date

Codegen fetches the live OpenAPI schema from the running backend. The backend must be running on the correct port.

Check if it's already running:
```bash
curl -s http://localhost:${BACKEND_PORT:-8000}/schema/openapi.json | head -c 100
```

If it's not running (connection refused), start it:
```bash
just dev-backend
```

If the backend was already running but may not have picked up the model change (hot reload sometimes misses structural changes), check its output or restart it.

---

## Step 4: Run codegen

```bash
just codegen
```

This fetches `http://localhost:${BACKEND_PORT:-8000}/schema/openapi.json` and runs Orval to regenerate two things:

- **`frontend/src/openapi/litestarAPI.schemas.ts`** — all TypeScript interfaces and types (one per Litestar `Schema`)
- **`frontend/src/openapi/<tag>/<tag>.ts`** — React Query hooks per API tag (e.g., `company/company.ts`)

**If codegen fails:**
- `ECONNREFUSED` → backend isn't running; go back to step 3
- Schema parse error → the model or route may have a type annotation Litestar can't serialize; check the backend logs
- Orval type error → look at the generated schema diff — sometimes a type change breaks an existing hook signature

---

## Step 5: Verify the frontend types

After codegen, check that the generated types match what you expected:

```bash
git diff frontend/src/openapi/
```

Look for:
- The new/changed field appearing in `litestarAPI.schemas.ts`
- Any updated response shapes in the hook files
- No unexpected deletions (a missing field in the schema means it wasn't included in the Litestar response DTO)

If the field doesn't appear in the generated types, the issue is usually one of:
1. The field is on the SQLAlchemy model but not on the Litestar `Schema` (dataclass/DTO) used as the route's return type — add it there
2. The route returns the wrong schema type
3. Litestar is excluding the field (check for `exclude` in the DTO config)

Once the types look right, run a frontend type-check to confirm nothing broke:
```bash
cd frontend && npm run type-check
```

---

## Step 6: Update frontend usage (if needed)

If the field rename or type change affects existing frontend code that used the old field name, TypeScript will surface these as type errors after the codegen. Fix them before moving on.

Generated files in `frontend/src/openapi/` are always overwritten by `just codegen` — never edit them manually.

---

## Checklist

- [ ] Model change is in place and imports cleanly
- [ ] Migration autogenerated and reviewed
- [ ] Migration applied (`just db-upgrade`)
- [ ] Backend running with updated schema
- [ ] `just codegen` ran successfully
- [ ] Generated types reviewed (`git diff frontend/src/openapi/`)
- [ ] `npm run type-check` passes
