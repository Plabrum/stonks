import asyncio

from app.utils import broker


@broker.task()
async def ingest_company_data(ticker: str) -> str:
    """
    Simulates fetching and ingesting data for a given company ticker.
    In a real application, this is where you'd fetch data from an external API,
    process it, and save it to your database.
    """
    print(f"Starting data ingestion for ticker: {ticker}")
    # Simulate network and processing time
    await asyncio.sleep(5)
    message = f"Successfully ingested data for {ticker}"
    print(message)
    return message


@broker.task(schedule=[{"cron": "* * * * *"}])  # Runs every minute
async def update_all_companies() -> None:
    """
    A scheduled task to update data for all companies.
    This is a placeholder. In a real app, you would fetch the list of tickers
    from your database.
    """
    print("Executing daily task: `update_all_companies`")
    # Placeholder tickers.
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    for ticker in tickers:
        # Queue the ingestion task for each ticker.
        await ingest_company_data.kiq(ticker)
    print(f"Finished queuing ingestion tasks for {len(tickers)} companies.")
