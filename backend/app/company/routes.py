from datetime import datetime
from typing import List

from litestar import Router, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.schemas import (
    CompanyComparablesSchema,
    CompanyPredictionsSchema,
    CompanySchema,
    CompanySearchResultSchema,
    CompanySearchSchema,
    CompanyStatsSchema,
    FilingSchema,
)


@get("/{ticker:str}")
async def get_company(ticker: str, transaction: AsyncSession) -> CompanySchema:
    # Logic to retrieve company data based on the slug
    return CompanySchema(
        id="company_001",
        name="Example Corporation",
        ticker="EXM",
        industry="Technology",
        filings=[
            FilingSchema(
                id="filing_123",
                cik="0000123456",
                company_id="company_001",
                type="10-K",
                period_end=datetime.fromisoformat("2024-12-31T00:00:00Z"),
                filing_date=datetime.fromisoformat("2025-02-15T00:00:00Z"),
                revenue=50000000.0,
                net_income=7000000.0,
                ebitda=9000000.0,
                shares_outstanding=10000000.0,
                cash=12000000.0,
                debt=5000000.0,
                document_url="https://example.com/filing.pdf",
                source="EDGAR",
                created_at=datetime.fromisoformat("2025-02-15T10:00:00Z"),
                updated_at=datetime.fromisoformat("2025-02-15T10:00:00Z"),
            ),
        ],
        latest_filing=FilingSchema(
            id="filing_123",
            cik="0000123456",
            company_id="company_001",
            type="10-K",
            period_end=datetime.fromisoformat("2024-12-31T00:00:00Z"),
            filing_date=datetime.fromisoformat("2025-02-15T00:00:00Z"),
            revenue=50000000.0,
            net_income=7000000.0,
            ebitda=9000000.0,
            shares_outstanding=10000000.0,
            cash=12000000.0,
            debt=5000000.0,
            document_url="https://example.com/filing.pdf",
            source="EDGAR",
            created_at=datetime.fromisoformat("2025-02-15T10:00:00Z"),
            updated_at=datetime.fromisoformat("2025-02-15T10:00:00Z"),
        ),
        stats=CompanyStatsSchema(
            ltm_revenue=49000000.0,
            ltm_revenue_growth=12.5,
            ltm_net_income=6800000.0,
            ltm_ebitda=8800000.0,
            share_price=25.5,
            shares_outstanding=10000000.0,
            equity_value=255000000.0,
            cash=12000000.0,
            debt=5000000.0,
            enterprise_value=248000000.0,
            multiple_ev_to_revenue=5.06,
            multiple_ev_to_ebitda=28.18,
            price_to_earnings=37.5,
            median_fund_investment_percentage_change=2.5,
        ),
        comparables=CompanyComparablesSchema(
            median_ev_to_revenue=4.2,
            median_ev_to_ebitda=22.5,
            median_pe_ratio=28.3,
        ),
        predictions=CompanyPredictionsSchema(
            projected_5y_share_price=75.0,
        ),
        created_at=datetime.fromisoformat("2025-02-15T10:00:00Z"),
        updated_at=datetime.fromisoformat("2025-08-01T15:45:00Z"),
    )


@post("/search")
async def search_companies(
    data: CompanySearchSchema, transaction: AsyncSession
) -> List[CompanySearchResultSchema]:
    # In a real application, you would use the data from the `data` argument
    # to filter and sort the companies from the database.
    # For now, we'll just return a mock list of companies.

    return [
        CompanySearchResultSchema(
            id="company_001",
            name="Example Corporation",
            ticker="EXM",
            industry="Technology",
            equity_value=255000000.0,
            ltm_revenue=49000000.0,
            multiple_ev_to_revenue=5.06,
            created_at=datetime.fromisoformat("2025-02-15T10:00:00Z"),
            updated_at=datetime.fromisoformat("2025-08-01T15:45:00Z"),
        ),
        CompanySearchResultSchema(
            id="company_002",
            name="Innovate Inc.",
            ticker="INVT",
            industry="Technology",
            equity_value=500000000.0,
            ltm_revenue=120000000.0,
            multiple_ev_to_revenue=4.17,
            created_at=datetime.fromisoformat("2025-03-20T12:00:00Z"),
            updated_at=datetime.fromisoformat("2025-08-01T16:00:00Z"),
        ),
        CompanySearchResultSchema(
            id="company_003",
            name="GreenTech Solutions",
            ticker="GTS",
            industry="Renewable Energy",
            equity_value=750000000.0,
            ltm_revenue=180000000.0,
            multiple_ev_to_revenue=4.17,
            created_at=datetime.fromisoformat("2025-03-25T10:30:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:10:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_004",
            name="MediCore Health",
            ticker="MCH",
            industry="Healthcare",
            equity_value=1250000000.0,
            ltm_revenue=450000000.0,
            multiple_ev_to_revenue=2.78,
            created_at=datetime.fromisoformat("2025-04-10T09:00:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:12:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_005",
            name="Quantum Dynamics",
            ticker="QDY",
            industry="Technology",
            equity_value=960000000.0,
            ltm_revenue=300000000.0,
            multiple_ev_to_revenue=3.20,
            created_at=datetime.fromisoformat("2025-04-18T14:45:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:13:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_006",
            name="AgriCorp Ltd.",
            ticker="AGR",
            industry="Agriculture",
            equity_value=350000000.0,
            ltm_revenue=90000000.0,
            multiple_ev_to_revenue=3.89,
            created_at=datetime.fromisoformat("2025-05-01T11:00:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:14:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_007",
            name="Urban Mobility Co.",
            ticker="UMC",
            industry="Transportation",
            equity_value=620000000.0,
            ltm_revenue=150000000.0,
            multiple_ev_to_revenue=4.13,
            created_at=datetime.fromisoformat("2025-05-12T08:30:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:15:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_008",
            name="Finlytics AI",
            ticker="FAI",
            industry="Finance",
            equity_value=810000000.0,
            ltm_revenue=200000000.0,
            multiple_ev_to_revenue=4.05,
            created_at=datetime.fromisoformat("2025-05-25T13:15:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:16:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_009",
            name="NeuroVerse Labs",
            ticker="NVL",
            industry="Biotechnology",
            equity_value=690000000.0,
            ltm_revenue=120000000.0,
            multiple_ev_to_revenue=5.75,
            created_at=datetime.fromisoformat("2025-06-02T15:20:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:17:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_010",
            name="Oceanix Marine",
            ticker="OCM",
            industry="Shipping",
            equity_value=410000000.0,
            ltm_revenue=140000000.0,
            multiple_ev_to_revenue=2.93,
            created_at=datetime.fromisoformat("2025-06-15T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:18:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_011",
            name="Helix Robotics",
            ticker="HLX",
            industry="Industrial Automation",
            equity_value=980000000.0,
            ltm_revenue=310000000.0,
            multiple_ev_to_revenue=3.16,
            created_at=datetime.fromisoformat("2025-06-28T17:10:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:19:00+00:00"),
        ),
        CompanySearchResultSchema(
            id="company_012",
            name="Lumina Solar",
            ticker="LSR",
            industry="Energy",
            equity_value=720000000.0,
            ltm_revenue=240000000.0,
            multiple_ev_to_revenue=3.00,
            created_at=datetime.fromisoformat("2025-07-10T12:00:00+00:00"),
            updated_at=datetime.fromisoformat("2025-08-01T16:20:00+00:00"),
        ),
    ]


companies_router = Router(
    path="/company", route_handlers=[get_company, search_companies]
)
