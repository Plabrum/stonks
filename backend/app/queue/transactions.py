import asyncio
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

from litestar import Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.queue.exceptions import CommittableTaskError
from app.queue.enums import TaskName


@asynccontextmanager
async def task_transaction(
    db_sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    """Async context manager that begins a transaction and commits or rolls back.

    Commits on success or on CommittableTaskError (then re-raises).
    Rolls back on all other exceptions.
    """
    async with db_sessionmaker() as session:
        await session.begin()
        try:
            yield session
            await session.commit()
        except CommittableTaskError:
            await session.commit()
            raise
        except Exception:
            await session.rollback()
            raise


def with_transaction(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that injects `transaction: AsyncSession` as a keyword argument."""

    @wraps(fn)
    async def wrapper(ctx: Any, **kwargs: Any) -> Any:
        if "transaction" in kwargs:
            return await fn(ctx, **kwargs)
        async with task_transaction(ctx["db_sessionmaker"]) as session:
            return await fn(ctx, transaction=session, **kwargs)

    return wrapper


async def dispatch_task(
    transaction: AsyncSession,
    request: Request,
    task_name: TaskName,
    *,
    queue: str = "default",
    **kwargs: Any,
) -> None:
    """Enqueue a task after the current session commits."""

    def _listener(_session: Any) -> None:
        asyncio.ensure_future(request.app.state.task_queues.get(queue).enqueue(task_name, **kwargs))

    event.listen(transaction.sync_session, "after_commit", _listener, once=True)
