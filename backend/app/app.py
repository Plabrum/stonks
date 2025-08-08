import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import taskiq_litestar
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from litestar.response import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.company.routes import companies_router
from app.utils import broker, db_config, provide_transaction


@get("/health")
async def health_check(include_in_schema: bool = False) -> str:
    return "OK"


@get("/metrics", sync_to_thread=True, include_in_schema=False)
def metrics_handler() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


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


allowed_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")
cors_config = CORSConfig(allow_origins=allowed_origins)

app = Litestar(
    route_handlers=[metrics_handler, health_check, companies_router],
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config)],
    cors_config=cors_config,
    lifespan=[app_lifespan],
)
