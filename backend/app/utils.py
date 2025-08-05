import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from litestar.exceptions import ClientException
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.serializers.json_serializer import JSONSerializer
from taskiq_pg import AsyncpgBroker, AsyncpgResultBackend

# Load the .env file
load_dotenv()


# Define base model
class Base(DeclarativeBase): ...


# Get database URL from environment variable
# Get minimal DSN from .env
BASE_DSN = os.getenv("DATABASE_URL")
if not BASE_DSN:
    raise RuntimeError("DATABASE_URL is not set.")

# Convert for SQLAlchemy
SQLALCHEMY_DSN = BASE_DSN.replace("postgresql://", "postgresql+asyncpg://")

# raise RuntimeError(f"Using SQLAlchemy DSN: {SQLALCHEMY_DSN}")
# SQLAlchemy config using PostgreSQL
db_config = SQLAlchemyAsyncConfig(
    connection_string=SQLALCHEMY_DSN,
    metadata=Base.metadata,
    create_all=True,
)

asyncpg_result_backend = AsyncpgResultBackend(
    dsn=BASE_DSN,
    serializer=JSONSerializer(),
)

broker = AsyncpgBroker(
    dsn=BASE_DSN,
).with_result_backend(asyncpg_result_backend)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
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
