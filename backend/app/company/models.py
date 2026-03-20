from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.base.mixins import TimestampMixin
from app.base.models import BaseDBModel


class Company(TimestampMixin, BaseDBModel):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ticker: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=True)
    exchange: Mapped[str] = mapped_column(String(50), nullable=True)
