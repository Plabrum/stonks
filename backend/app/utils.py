import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from litestar.exceptions import ClientException
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig
from litestar.status_codes import HTTP_409_CONFLICT
from litestar_saq import QueueConfig, SAQConfig
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Load the .env file
load_dotenv()


# Define base model
class Base(DeclarativeBase): ...


BASE_DSN = os.getenv("DATABASE_URL")
if not BASE_DSN:
    raise RuntimeError("DATABASE_URL is not set.")

# Convert for SQLAlchemy
SQLALCHEMY_DSN = BASE_DSN.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemy config using PostgreSQL
db_config = SQLAlchemyAsyncConfig(
    connection_string=SQLALCHEMY_DSN,
    metadata=Base.metadata,
    create_all=True,
)

saq_config = SAQConfig(
    queue_configs=[QueueConfig(dsn=BASE_DSN, name="samples")],
)


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
