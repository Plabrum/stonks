from contextlib import asynccontextmanager
from typing import AsyncGenerator

import taskiq_litestar
from litestar import Litestar, get
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin

from app.company.routes import companies_router
from app.utils import broker, db_config, provide_transaction


@get("/health")
async def health_check() -> str:
    return "OK"


taskiq_litestar.init(
    broker,
    "app.app:app",
)


@asynccontextmanager
async def app_lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    """Lifespan generator."""
    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()


app = Litestar(
    route_handlers=[health_check, companies_router],
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config)],
    lifespan=[app_lifespan],
)
