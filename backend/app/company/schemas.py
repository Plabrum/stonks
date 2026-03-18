from datetime import datetime
from typing import Literal

from msgspec import Struct


class FilingSchema(Struct, kw_only=True):
    id: str
    cik: str
    company_id: str
    type: Literal["10-Q", "10-K"]
    period_end: datetime
    filing_date: datetime

    # Income statement
    revenue: float | None = None
    net_income: float | None = None
    ebitda: float | None = None
    shares_outstanding: float | None = None

    # Balance sheet
    cash: float | None = None
    debt: float | None = None

    # Metadata
    document_url: str | None = None
    source: Literal["EDGAR", "Manual", "Other"] | None = None

    created_at: datetime
    updated_at: datetime


class CompanyStatsSchema(Struct, kw_only=True):
    ltm_revenue: float | None = None
    ltm_revenue_growth: float | None = None
    ltm_net_income: float | None = None
    ltm_ebitda: float | None = None

    share_price: float | None = None
    shares_outstanding: float | None = None
    equity_value: float | None = None
    cash: float | None = None
    debt: float | None = None
    enterprise_value: float | None = None

    multiple_ev_to_revenue: float | None = None
    multiple_ev_to_ebitda: float | None = None
    price_to_earnings: float | None = None

    # fund
    median_fund_investment_percentage_change: float | None = None


class CompanyComparablesSchema(Struct, kw_only=True):
    median_ev_to_revenue: float | None = None
    median_ev_to_ebitda: float | None = None
    median_pe_ratio: float | None = None


class CompanyPredictionsSchema(Struct, kw_only=True):
    projected_5y_share_price: float | None = None


class CompanySchema(Struct, kw_only=True):
    id: str
    name: str
    ticker: str
    industry: str | None = None

    filings: list[FilingSchema]
    latest_filing: FilingSchema | None = None

    stats: CompanyStatsSchema | None = None
    comparables: CompanyComparablesSchema | None = None
    predictions: CompanyPredictionsSchema | None = None

    created_at: datetime
    updated_at: datetime


class SortCriterion(Struct, kw_only=True):
    field: str
    direction: Literal["asc", "desc"]


class NumericRange(Struct, kw_only=True):
    min: float | None = None
    max: float | None = None


class CompanySearchFilters(Struct, kw_only=True):
    industries: list[str] | None = None
    subIndustries: list[str] | None = None  # TODO: rename to sub_industries (update frontend too)
    numericRanges: dict[str, NumericRange] | None = None  # TODO: rename to numeric_ranges (update frontend too)


class Pagination(Struct, kw_only=True):
    offset: int | None = None
    limit: int | None = None


class CompanySearchSchema(Struct, kw_only=True):
    search: str | None = None
    filters: CompanySearchFilters | None = None
    sorting: list[SortCriterion] | None = None
    pagination: Pagination | None = None


class CompanySearchResultSchema(Struct, kw_only=True):
    id: str
    name: str
    ticker: str
    industry: str | None = None
    equity_value: float | None = None
    ltm_revenue: float | None = None
    multiple_ev_to_revenue: float | None = None
    created_at: datetime
    updated_at: datetime
