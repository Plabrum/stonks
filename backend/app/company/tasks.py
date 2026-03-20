import asyncio

from app.queue.enums import TaskName
from app.queue.registry import task
from app.queue.types import AppContext


@task(TaskName.INGEST_COMPANY_DATA)
async def ingest_company_data(ctx: AppContext, *, ticker: str) -> str:
    """Fetch and ingest data for a given company ticker."""
    print(f"Starting data ingestion for ticker: {ticker}")
    await asyncio.sleep(5)
    message = f"Successfully ingested data for {ticker}"
    print(message)
    return message
