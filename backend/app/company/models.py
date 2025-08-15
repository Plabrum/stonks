# # models/business.py
# from sqlalchemy import String, Text
# from sqlalchemy.orm import Mapped, mapped_column
#
# from app.utils import Base
#
#
# class Company(Base):
#     __tablename__ = "businesses"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     ticker: Mapped[str] = mapped_column(
#         String(16),
#         unique=True,
#         index=True,
#         nullable=False,
#     )
#     description: Mapped[str] = mapped_column(Text, nullable=True)
#     sector: Mapped[str] = mapped_column(String(100), nullable=True)
#     exchange: Mapped[str] = mapped_column(String(50), nullable=True)
