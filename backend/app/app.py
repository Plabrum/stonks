import os

from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from litestar.response import Response
from litestar_saq import SAQPlugin
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.routes import companies_router
from app.company.tasks import is_healthy
from app.utils import db_config, provide_transaction, saq_config


@get("/health")
async def health_check(
    session: AsyncSession, include_in_schema: bool = False
) -> str:
    print("Health check endpoint called")
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    print(f"✅ Database connected successfully, test value: {value}")
    msg = await is_healthy.kiq("Litestar is running")
    print(f"📨 Enqueued is_healthy task: {msg}")
    return "OK"


# SAQ_DSN = os.getenv("SAQ_DSN", "postgres://user:pass@localhost:5432/saq")


@get("/metrics", sync_to_thread=True, include_in_schema=False)
def metrics_handler() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


allowed_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

app = Litestar(
    route_handlers=[metrics_handler, health_check, companies_router],
    dependencies={"session": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config), SAQPlugin(saq_config)],
    cors_config=CORSConfig(allow_origins=allowed_origins),
)
