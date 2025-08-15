# # services/company_service.py
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.company.models import Company
#
#
# async def get_company_by_ticker(ticker: str, session: AsyncSession) -> Company:
#     result = await session.execute(
#         select(Company).where(Company.ticker == ticker)
#     )
#     company = result.scalars().first()
#
#     if not company:
#         raise ValueError(f"Company with ticker '{ticker}' not found.")
#
#     return company
