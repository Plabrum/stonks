from __future__ import annotations

import enum
from typing import Any, Dict, Literal, Optional, Sequence, Tuple, Union

import msgspec


# --- Shared bits
class Dir(str, enum.Enum):
    asc = "asc"
    desc = "desc"


TimeGrain = Literal["1h", "1d", "1w", "1m"]


# Filters (same as before; trimmed here)
class FilterText(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: Literal["contains", "startsWith", "equals", "in"]
    value: Union[str, Sequence[str]]
    caseSensitive: bool = False


class FilterEnum(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: Literal["in", "notIn"]
    value: Sequence[str]


class FilterNum(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: Literal["<", "<=", "=", ">=", ">", "between"]
    value: Union[float, int, Tuple[float, float], Tuple[int, int]]


class FilterDate(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: Literal["on", "before", "after", "between"]
    value: Union[str, Tuple[str, str]]


Filter = Union[FilterText, FilterEnum, FilterNum, FilterDate]


class SortKey(msgspec.Struct, frozen=True):
    # Sort by the alias of a projection (recommended) or by a raw column name.
    by: str
    dir: Dir = Dir.asc


class Page(msgspec.Struct, kw_only=True, frozen=True):
    limit: int = 50
    cursor: Optional[str] = None


# --- Projection expressions (the important part) ---


# 1) Raw column reference -> projects as its own name unless "as" provided
class Col(msgspec.Struct, tag=True, frozen=True):
    expr: Literal["col"] = "col"
    name: str
    as_: Optional[str] = msgspec.field(name="as", default=None)


# 2) Time bucket expression -> groups timestamps into grains; also acts like a group key
class TimeBucket(msgspec.Struct, tag=True, frozen=True):
    expr: Literal["time_bucket"] = "time_bucket"
    column: str
    grain: TimeGrain
    as_: Optional[str] = msgspec.field(name="as", default=None)


# 3) Aggregation over a column. Two scopes:
#    - "group": standard GROUP BY (non-agg projections become group keys)
#    - "window": SQL window function with a window spec (no GROUP BY)
class WindowFrame(msgspec.Struct, kw_only=True, frozen=True):
    # rows-based frame; keep it simple
    type: Literal["rows"] = "rows"
    preceding: int = 0
    following: int = 0


class WindowSpec(msgspec.Struct, kw_only=True, frozen=True):
    partitionBy: Sequence[str]  # aliases or column names
    orderBy: Sequence[str]  # aliases or column names
    frame: WindowFrame = WindowFrame()


class Agg(msgspec.Struct, tag=True, frozen=True):
    expr: Literal["agg"] = "agg"
    fn: Literal[
        "count",
        "distinct_count",
        "sum",
        "avg",
        "min",
        "max",
        "median",
        "percentile",
    ]
    column: Optional[str] = None  # column-less when fn=="count"
    p: Optional[float] = None  # for percentile
    scope: Literal["group", "window"] = "group"
    window: Optional[WindowSpec] = None  # required if scope=="window"
    as_: Optional[str] = msgspec.field(name="as", default=None)


# A projection is any of the above
Projection = Union[Col, TimeBucket, Agg]


# --- Discriminated union by data_source (Option A: no discovery)
class BaseQuery(msgspec.Struct, kw_only=True, frozen=True):
    select: Sequence[Projection]  # unified list (raw + computed)
    filters: Optional[Sequence[Filter]] = None
    sort: Optional[Sequence[SortKey]] = None
    page: Optional[Page] = None


class CompaniesQuery(BaseQuery, tag=True, frozen=True):
    data_source: Literal["companies"] = "companies"


class StockPricesQuery(BaseQuery, tag=True, frozen=True):
    data_source: Literal["stock_prices"] = "stock_prices"


DataQuery = Union[CompaniesQuery, StockPricesQuery]

# --- Response
Row = Dict[str, Any]


class Meta(msgspec.Struct, kw_only=True, frozen=True):
    nextCursor: Optional[str] = None


class DataResponse(msgspec.Struct, frozen=True):
    data: Sequence[Row]
    meta: Meta
