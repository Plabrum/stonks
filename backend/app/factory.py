from pathlib import Path

from litestar import Litestar, Router, get
from litestar.config.cors import CORSConfig
from litestar.enums import MediaType
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
from litestar.response import Response
from litestar.static_files import StaticFilesConfig
from litestar_saq import QueueConfig, SAQConfig, SAQPlugin

from app.company.routes import companies_router
from app.company.tasks import ingest_company_data
from app.config import config
from app.queue.config import shutdown, startup
from app.utils import db_config, provide_transaction


@get("/health", include_in_schema=False)
async def health_check() -> str:
    return "OK"


def create_app() -> Litestar:
    cors_config = CORSConfig(
        allow_origins=[config.FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    queue_config = QueueConfig(
        dsn=config.REDIS_URL,
        name="stonks",
        tasks=[ingest_company_data],
        startup=startup,
        shutdown=shutdown,
    )
    saq_config = SAQConfig(queue_configs=[queue_config])
    saq_plugin = SAQPlugin(config=saq_config)

    api_router = Router(path="/api", route_handlers=[companies_router])
    route_handlers: list = [health_check, api_router]
    static_configs: list[StaticFilesConfig] = []

    if not config.IS_DEV:
        static_dir = Path(config.STATIC_DIR)
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            static_configs.append(
                StaticFilesConfig(
                    path="/assets",
                    directories=[str(assets_dir)],
                )
            )

        index_path = static_dir / "index.html"

        @get("/{path:path}", include_in_schema=False)
        async def spa_handler(path: str) -> Response:
            return Response(
                content=index_path.read_text(),
                media_type=MediaType.HTML,
            )

        route_handlers.append(spa_handler)

    return Litestar(
        route_handlers=route_handlers,
        dependencies={"transaction": provide_transaction},
        plugins=[SQLAlchemyPlugin(db_config), saq_plugin],
        cors_config=cors_config,
        static_files_config=static_configs,
    )
