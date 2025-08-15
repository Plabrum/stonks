"""scheduler

Revision ID: 12e0994850cc
Revises: 06057295e4ee
Create Date: 2025-08-10 22:01:03.961023

"""

import os
from typing import TYPE_CHECKING

import sqlalchemy as sa
from advanced_alchemy.types import (
    GUID,
    ORA_JSONB,
    DateTimeUTC,
    EncryptedString,
    EncryptedText,
    StoredObject,
)
from alembic import op
from sqlalchemy import Text  # noqa: F401

if TYPE_CHECKING:
    pass

__all__ = [
    "downgrade",
    "upgrade",
    "schema_upgrades",
    "schema_downgrades",
    "data_upgrades",
    "data_downgrades",
]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB
sa.EncryptedString = EncryptedString
sa.EncryptedText = EncryptedText
sa.StoredObject = StoredObject

# revision identifiers, used by Alembic.
revision = "12e0994850cc"
down_revision = "06057295e4ee"
branch_labels = None
depends_on = None

"""Enable pg_cron, create taskiq_enqueue wrapper, and cron_tasks table + triggers.

This migration:
- Ensures pg_cron is available.
- Creates a stable wrapper function taskiq_enqueue(task_name, args, kwargs, eta)
  that inserts into the TaskIQ Postgres broker queue and NOTIFY workers.
- Creates cron_tasks + triggers so that INSERT/UPDATE/DELETE auto-(un)schedule pg_cron jobs.

ENV VARS you can set before running Alembic (optional):
- TASKIQ_MESSAGES_TABLE  (default: 'taskiq_messages')
- TASKIQ_NOTIFY_CHANNEL  (default: 'taskiq_messages')

Adjust the INSERT columns in taskiq_enqueue() to match your taskiq-postgresql broker schema.
"""

TABLE = os.getenv("TASKIQ_MESSAGES_TABLE", "taskiq_messages")
CHANNEL = os.getenv("TASKIQ_NOTIFY_CHANNEL", "taskiq_messages")


def upgrade():
    # 1) pg_cron
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_cron;")

    # 2) stable enqueue wrapper (encapsulates broker internals)
    # NOTE: adjust columns if your taskiq-postgresql broker uses different names.
    op.execute(
        f"""
    CREATE OR REPLACE FUNCTION taskiq_enqueue(
        p_task_name text,
        p_args jsonb DEFAULT '[]'::jsonb,
        p_kwargs jsonb DEFAULT '{{}}'::jsonb,
        p_eta timestamptz DEFAULT NULL
    )
    RETURNS void
    LANGUAGE plpgsql
    AS $$
    DECLARE
      v_id bigint;
    BEGIN
      INSERT INTO {TABLE} (task_name, args, kwargs, created_at, eta)
      VALUES (p_task_name,
              COALESCE(p_args, '[]'::jsonb),
              COALESCE(p_kwargs, '{{}}'::jsonb),
              now(),
              p_eta)
      RETURNING id INTO v_id;

      PERFORM pg_notify('{CHANNEL}', v_id::text);
    END;
    $$;
    """
    )

    # 3) declarative cron table
    # op.execute(
    #     """
    # CREATE TABLE IF NOT EXISTS cron_tasks (
    #   id              BIGSERIAL PRIMARY KEY,
    #   name            TEXT NOT NULL UNIQUE,          -- human-friendly logical name
    #   task_name       TEXT NOT NULL,                 -- e.g. 'yourapp.tasks:reports_daily'
    #   args            JSONB NOT NULL DEFAULT '[]',   -- JSON array
    #   kwargs          JSONB NOT NULL DEFAULT '{}',   -- JSON object
    #   cron            TEXT NOT NULL,                 -- standard crontab expr
    #   enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    #   jobid           INTEGER,                       -- pg_cron job id
    #   last_synced_at  timestamptz,
    #   CHECK (jsonb_typeof(args) = 'array'),
    #   CHECK (jsonb_typeof(kwargs) = 'object')
    # );
    # """
    # )

    # 4) trigger function: on insert/update -> (re)schedule; on disable -> unschedule
    # We build the cron command to call the stable wrapper: SELECT taskiq_enqueue(...);
    op.execute(
        """
    CREATE OR REPLACE FUNCTION cron_tasks_sync()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
      v_jobid int;
      v_cmd   text;
    BEGIN
      -- If updating and substantial fields changed, drop prior job
      IF TG_OP = 'UPDATE' THEN
        IF OLD.jobid IS NOT NULL AND (OLD.cron IS DISTINCT FROM NEW.cron
                                      OR OLD.enabled IS DISTINCT FROM NEW.enabled
                                      OR OLD.task_name IS DISTINCT FROM NEW.task_name
                                      OR OLD.args IS DISTINCT FROM NEW.args
                                      OR OLD.kwargs IS DISTINCT FROM NEW.kwargs) THEN
          PERFORM cron.unschedule(OLD.jobid);
          NEW.jobid := NULL;
        END IF;
      END IF;

      IF NEW.enabled THEN
        -- Build command; pass JSON safely by %L-quoting text and casting back to jsonb.
        v_cmd := format(
          'SELECT taskiq_enqueue(%L, %L::jsonb, %L::jsonb);',
          NEW.task_name,
          NEW.args::text,
          NEW.kwargs::text
        );

        -- Schedule (in current DB). Returns jobid.
        SELECT cron.schedule(NEW.cron, v_cmd) INTO v_jobid;

        NEW.jobid := v_jobid;
        NEW.last_synced_at := now();
      ELSE
        -- Disabled: ensure unscheduled
        IF NEW.jobid IS NOT NULL THEN
          PERFORM cron.unschedule(NEW.jobid);
          NEW.jobid := NULL;
        END IF;
        NEW.last_synced_at := now();
      END IF;

      RETURN NEW;
    END;
    $$;
    """
    )

    # 5) unschedule on delete
    op.execute(
        """
    CREATE OR REPLACE FUNCTION cron_tasks_unschedule()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF OLD.jobid IS NOT NULL THEN
        PERFORM cron.unschedule(OLD.jobid);
      END IF;
      RETURN OLD;
    END;
    $$;
    """
    )

    # 6) attach triggers
    op.execute(
        """
    DROP TRIGGER IF EXISTS trg_cron_tasks_sync ON cron_tasks;
    CREATE TRIGGER trg_cron_tasks_sync
      BEFORE INSERT OR UPDATE OF name, task_name, args, kwargs, cron, enabled ON cron_tasks
      FOR EACH ROW
      EXECUTE FUNCTION cron_tasks_sync();

    DROP TRIGGER IF EXISTS trg_cron_tasks_unschedule ON cron_tasks;
    CREATE TRIGGER trg_cron_tasks_unschedule
      BEFORE DELETE ON cron_tasks
      FOR EACH ROW
      EXECUTE FUNCTION cron_tasks_unschedule();
    """
    )


def downgrade():
    op.execute(
        "DROP TRIGGER IF EXISTS trg_cron_tasks_unschedule ON cron_tasks;"
    )
    op.execute("DROP TRIGGER IF EXISTS trg_cron_tasks_sync ON cron_tasks;")
    op.execute("DROP FUNCTION IF EXISTS cron_tasks_unschedule();")
    op.execute("DROP FUNCTION IF EXISTS cron_tasks_sync();")
    op.execute("DROP TABLE IF EXISTS cron_tasks;")
    op.execute(
        "DROP FUNCTION IF EXISTS taskiq_enqueue(text, jsonb, jsonb, timestamptz);"
    )
    # You can keep pg_cron installed; dropping is optional.
    # op.execute("DROP EXTENSION IF EXISTS pg_cron;")
