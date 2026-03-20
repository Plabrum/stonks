"""Database utility helpers."""

from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig
from msgspec import structs
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.models import BaseDBModel
from app.base.schemas import BaseSchema
from app.config import config

db_config = SQLAlchemyAsyncConfig(
    connection_string=config.DATABASE_URL,
    metadata=BaseDBModel.metadata,
)


async def update_model[T: BaseDBModel](
    session: AsyncSession,
    model_instance: T,
    update_vals: BaseSchema,
) -> T:
    """Apply fields from a schema struct onto a model instance.

    Only sets fields that exist on the model. Handles nested objects by
    detecting the ``{field}_id`` foreign-key convention: if a ``{field}_id``
    attribute exists the field is treated as a relationship.

    - Nested field is ``None``  → clears the FK (``{field}_id = None``)
    - Nested field is a dict   → updates the existing related object in-place
    - Regular field            → set directly

    After applying all fields ``session.flush()`` is called so the changes
    are written to the transaction without committing.
    """
    update_dict = structs.asdict(update_vals)

    for field, value in update_dict.items():
        if not hasattr(model_instance, field):
            continue

        nested_id_field = f"{field}_id"
        if hasattr(model_instance, nested_id_field):
            if value is None:
                setattr(model_instance, nested_id_field, None)
            elif isinstance(value, dict):
                existing = getattr(model_instance, field, None)
                if existing:
                    for nested_field, nested_value in value.items():
                        if hasattr(existing, nested_field):
                            setattr(existing, nested_field, nested_value)
        else:
            setattr(model_instance, field, value)

    await session.flush()
    return model_instance
