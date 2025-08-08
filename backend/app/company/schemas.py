from datetime import datetime
from typing import Dict, List, Literal, Optional

from msgspec import Struct


class FilingSchema(Struct, kw_only=True):
    id: str
    cik: str
    company_id: str
    type: Literal["10-Q", "10-K"]
    period_end: datetime
    filing_date: datetime

    # Income statement
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None
    shares_outstanding: Optional[float] = None

    # Balance sheet
    cash: Optional[float] = None
    debt: Optional[float] = None

    # Metadata
    document_url: Optional[str] = None
    source: Optional[Literal["EDGAR", "Manual", "Other"]] = None

    created_at: datetime
    updated_at: datetime


class CompanyStatsSchema(Struct, kw_only=True):
    ltm_revenue: Optional[float] = None
    ltm_revenue_growth: Optional[float] = None
    ltm_net_income: Optional[float] = None
    ltm_ebitda: Optional[float] = None

    share_price: Optional[float] = None
    shares_outstanding: Optional[float] = None
    equity_value: Optional[float] = None
    cash: Optional[float] = None
    debt: Optional[float] = None
    enterprise_value: Optional[float] = None

    multiple_ev_to_revenue: Optional[float] = None
    multiple_ev_to_ebitda: Optional[float] = None
    price_to_earnings: Optional[float] = None

    # fund
    median_fund_investment_percentage_change: Optional[float] = None


class CompanyComparablesSchema(Struct, kw_only=True):
    median_ev_to_revenue: Optional[float] = None
    median_ev_to_ebitda: Optional[float] = None
    median_pe_ratio: Optional[float] = None


class CompanyPredictionsSchema(Struct, kw_only=True):
    projected_5y_share_price: Optional[float] = None


class CompanySchema(Struct, kw_only=True):
    id: str
    name: str
    ticker: str
    industry: Optional[str] = None

    filings: List[FilingSchema]
    latest_filing: Optional[FilingSchema] = None

    stats: Optional[CompanyStatsSchema] = None
    comparables: Optional[CompanyComparablesSchema] = None
    predictions: Optional[CompanyPredictionsSchema] = None

    created_at: datetime
    updated_at: datetime


class SortCriterion(Struct, kw_only=True):
    field: str
    direction: Literal["asc", "desc"]


class NumericRange(Struct, kw_only=True):
    min: Optional[float] = None
    max: Optional[float] = None


class CompanySearchFilters(Struct, kw_only=True):
    industries: Optional[List[str]] = None
    subIndustries: Optional[List[str]] = None
    numericRanges: Optional[Dict[str, NumericRange]] = None


class Pagination(Struct, kw_only=True):
    offset: Optional[int] = None
    limit: Optional[int] = None


class CompanySearchSchema(Struct, kw_only=True):
    search: Optional[str] = None
    filters: Optional[CompanySearchFilters] = None
    sorting: Optional[List[SortCriterion]] = None
    pagination: Optional[Pagination] = None


class CompanySearchResultSchema(Struct, kw_only=True):
    id: str
    name: str
    ticker: str
    industry: Optional[str] = None
    equity_value: Optional[float] = None
    ltm_revenue: Optional[float] = None
    multiple_ev_to_revenue: Optional[float] = None
    created_at: datetime
    updated_at: datetime
