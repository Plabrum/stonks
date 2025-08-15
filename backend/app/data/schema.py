from __future__ import annotations

import enum
from typing import Any, Dict, Literal, Optional, Sequence, Tuple, Union

import msgspec

# =========
# Enums
# =========


class Dir(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class ColumnType(str, enum.Enum):
    text = "text"
    enum = "enum"
    number = "number"
    currency = "currency"
    date = "date"
    datetime = "datetime"


class OpText(str, enum.Enum):
    contains = "contains"
    startsWith = "startsWith"
    equals = "equals"
    _in = "in"  # "in" is a keyword in Python; map during I/O if you prefer


class OpEnum(str, enum.Enum):
    _in = "in"
    notIn = "notIn"


class OpNum(str, enum.Enum):
    lt = "<"
    lte = "<="
    eq = "="
    gte = ">="
    gt = ">"
    between = "between"


class OpDate(str, enum.Enum):
    on = "on"
    before = "before"
    after = "after"
    between = "between"


TimeGrain = Literal["1h", "1d", "1w", "1m"]


# =========
# OPTIONS /data/{resource}
# =========


class ColumnBase(msgspec.Struct, kw_only=True, frozen=True):
    name: str
    type: ColumnType
    sortable: bool = True
    filterOps: Optional[Sequence[str]] = None  # advertised ops; optional


class TextColumnSpec(ColumnBase, frozen=True):
    type: Literal[ColumnType.text] = ColumnType.text


class EnumColumnSpec(ColumnBase, frozen=True):
    type: Literal[ColumnType.enum] = ColumnType.enum
    values: Sequence[str] = ()


class NumberColumnSpec(ColumnBase, frozen=True):
    type: Literal[ColumnType.number] = ColumnType.number
    unit: Optional[str] = None  # e.g., "units"


class CurrencyColumnSpec(ColumnBase, frozen=True):
    type: Literal[ColumnType.currency] = ColumnType.currency
    unit: str = "USD"


class DateColumnSpec(ColumnBase, frozen=True):
    type: Literal[ColumnType.date] = ColumnType.date
    grains: Sequence[TimeGrain] = ()


class DateTimeColumnSpec(ColumnBase, frozen=True):
    type: Literal[ColumnType.datetime] = ColumnType.datetime
    grains: Sequence[TimeGrain] = ()


ColumnSpec = Union[
    TextColumnSpec,
    EnumColumnSpec,
    NumberColumnSpec,
    CurrencyColumnSpec,
    DateColumnSpec,
    DateTimeColumnSpec,
]


class SupportsSpec(msgspec.Struct, kw_only=True, frozen=True):
    sorting: bool = True
    multiSort: bool = True
    pagination: Dict[str, Any] = msgspec.field(
        default_factory=lambda: {"mode": "cursor", "maxPageSize": 500}
    )
    aggregations: Sequence[str] = (
        "count",
        "sum",
        "avg",
        "min",
        "max",
        "median",
        "percentile",
        "distinct_count",
    )
    groupBy: bool = True
    timeBucketing: bool = True


class ConstraintsSpec(msgspec.Struct, kw_only=True, frozen=True):
    maxSelect: int = 50
    maxGroupBy: int = 4
    maxAggregates: int = 8


class OptionsResponse(msgspec.Struct, kw_only=True, frozen=True):
    resource: str
    columns: Sequence[ColumnSpec]
    supports: SupportsSpec = SupportsSpec()
    constraints: ConstraintsSpec = ConstraintsSpec()


# =========
# POST /data/{resource} request (Query DSL)
# =========


class Sort(msgspec.Struct, frozen=True):
    column: str
    dir: Dir = Dir.asc


# --- Filters ---


class FilterText(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: OpText
    value: Union[str, Sequence[str]]
    caseSensitive: bool = False


class FilterEnum(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: OpEnum
    value: Sequence[str]


class FilterNum(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: OpNum
    # value can be a single number or a [min, max] tuple for "between"
    value: Union[float, int, Tuple[float, float], Tuple[int, int]]


class FilterDate(msgspec.Struct, kw_only=True, frozen=True):
    column: str
    op: OpDate
    # ISO8601 string or [start, end] for "between"
    value: Union[str, Tuple[str, str]]


Filter = Union[FilterText, FilterEnum, FilterNum, FilterDate]

# --- Grouping ---


class TimeGroup(msgspec.Struct, frozen=True):
    column: str
    grain: TimeGrain


class GroupByColumn(msgspec.Struct, frozen=True):
    column: str


class GroupByTime(msgspec.Struct, frozen=True):
    time: TimeGroup


GroupBy = Union[GroupByColumn, GroupByTime]

# --- Aggregates ---


class AggCount(msgspec.Struct, frozen=True):
    fn: Literal["count"] = "count"
    as_: Optional[str] = msgspec.field(name="as", default=None)


class AggDistinctCount(msgspec.Struct, frozen=True):
    fn: Literal["distinct_count"] = "distinct_count"
    column: str
    as_: Optional[str] = msgspec.field(name="as", default=None)


class AggBasic(msgspec.Struct, frozen=True):
    fn: Literal["sum", "avg", "min", "max", "median"]
    column: str
    as_: Optional[str] = msgspec.field(name="as", default=None)


class AggPercentile(msgspec.Struct, frozen=True):
    fn: Literal["percentile"] = "percentile"
    column: str
    p: float  # 0..100 or 0..1 (decide server-side; document expectation)
    as_: Optional[str] = msgspec.field(name="as", default=None)


Aggregate = Union[AggCount, AggDistinctCount, AggBasic, AggPercentile]

# --- Pagination ---


class Page(msgspec.Struct, kw_only=True, frozen=True):
    limit: int = 50
    cursor: Optional[str] = None  # opaque server-issued token


# --- The Query itself ---


class DataQuery(msgspec.Struct, kw_only=True, frozen=True):
    # If aggregates are omitted/null → tabular mode.
    select: Optional[Sequence[str]] = None
    filters: Optional[Sequence[Filter]] = None
    sort: Optional[Sequence[Sort]] = None
    page: Optional[Page] = None

    # Aggregation-specific
    groupBy: Optional[Sequence[GroupBy]] = None
    aggregates: Optional[Sequence[Aggregate]] = None


# =========
# Responses
# =========


class MetaBase(msgspec.Struct, kw_only=True, frozen=True):
    resource: Optional[str] = None
    nextCursor: Optional[str] = None


class TabularMeta(MetaBase, frozen=True):
    columns: Optional[Sequence[str]] = None
    totalApprox: Optional[int] = None


class AggregatedMeta(MetaBase, frozen=True):
    groupBy: Optional[Sequence[Any]] = (
        None  # echo of request groupBy; leave Any for simplicity
    )
    aggregates: Optional[Sequence[str]] = None


Row = Dict[str, Any]


class TabularResponse(msgspec.Struct, frozen=True):
    data: Sequence[Row]
    meta: TabularMeta


class AggregatedResponse(msgspec.Struct, frozen=True):
    data: Sequence[Row]
    meta: AggregatedMeta


# Unified success envelope if you prefer one type
DataResponse = Union[TabularResponse, AggregatedResponse]

# =========
# Error model
# =========


class ErrorBody(msgspec.Struct, frozen=True):
    code: str
    message: str


class ErrorResponse(msgspec.Struct, frozen=True):
    error: ErrorBody
