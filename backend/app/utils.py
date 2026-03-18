from collections.abc import AsyncGenerator

from litestar.exceptions import ClientException
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import config


class Base(DeclarativeBase): ...


db_config = SQLAlchemyAsyncConfig(
    connection_string=config.DATABASE_URL,
    metadata=Base.metadata,
)


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
