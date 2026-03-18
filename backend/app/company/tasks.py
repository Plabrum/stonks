import asyncio

from saq.types import Context


async def ingest_company_data(ctx: Context, *, ticker: str) -> str:
    """
    Simulates fetching and ingesting data for a given company ticker.
    In a real application, this is where you'd fetch data from an external API,
    process it, and save it to your database.
    """
    print(f"Starting data ingestion for ticker: {ticker}")
    await asyncio.sleep(5)
    message = f"Successfully ingested data for {ticker}"
    print(message)
    return message
