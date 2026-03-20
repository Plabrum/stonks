from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adds created_at, updated_at, deleted_at audit columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        index=True,
    )

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(tz=UTC)

    def restore(self) -> None:
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
