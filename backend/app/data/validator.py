from __future__ import annotations

import enum
from typing import Dict, List, Literal, Optional, Sequence, Set, Tuple, Union

import msgspec

# ---------------------------
# Reuse your query/DSL types
# ---------------------------

Dir = Literal["asc", "desc"]
TimeGrain = Literal["1h", "1d", "1w", "1m"]


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
    by: str
    dir: Dir = "asc"


class Page(msgspec.Struct, kw_only=True, frozen=True):
    limit: int = 50
    cursor: Optional[str] = None


# Projections
class Col(msgspec.Struct, tag=True, frozen=True):
    expr: Literal["col"] = "col"
    name: str
    as_: Optional[str] = msgspec.field(name="as", default=None)


class TimeBucket(msgspec.Struct, tag=True, frozen=True):
    expr: Literal["time_bucket"] = "time_bucket"
    column: str
    grain: TimeGrain
    as_: Optional[str] = msgspec.field(name="as", default=None)


class WindowFrame(msgspec.Struct, kw_only=True, frozen=True):
    type: Literal["rows"] = "rows"
    preceding: int = 0
    following: int = 0


class WindowSpec(msgspec.Struct, kw_only=True, frozen=True):
    partitionBy: Sequence[str]
    orderBy: Sequence[str]
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
    column: Optional[str] = None
    p: Optional[float] = None
    scope: Literal["group", "window"] = "group"
    window: Optional[WindowSpec] = None
    as_: Optional[str] = msgspec.field(name="as", default=None)


Projection = Union[Col, TimeBucket, Agg]


class BaseQuery(msgspec.Struct, kw_only=True, frozen=True):
    select: Sequence[Projection]
    filters: Optional[Sequence[Filter]] = None
    sort: Optional[Sequence[SortKey]] = None
    page: Optional[Page] = None


class CompaniesQuery(BaseQuery, tag=True, frozen=True):
    data_source: Literal["companies"] = "companies"


class StockPricesQuery(BaseQuery, tag=True, frozen=True):
    data_source: Literal["stock_prices"] = "stock_prices"


DataQuery = Union[CompaniesQuery, StockPricesQuery]


# ---------------------------
# Registry (server-internal)
# ---------------------------


class ColType(str, enum.Enum):
    text = "text"
    enum = "enum"
    number = "number"
    currency = "currency"
    date = "date"
    datetime = "datetime"


class ColumnInfo(msgspec.Struct, frozen=True):
    type: ColType
    aggregatable: bool = (
        True  # text/enum are aggregatable via count/distinct_count only
    )


ResourceRegistry = Dict[str, Dict[str, ColumnInfo]]

REGISTRY: ResourceRegistry = {
    "companies": {
        "name": ColumnInfo(ColType.text, aggregatable=False),
        "ticker": ColumnInfo(ColType.text, aggregatable=False),
        "sector": ColumnInfo(ColType.enum, aggregatable=False),
        "share_price": ColumnInfo(ColType.currency, aggregatable=True),
        "website": ColumnInfo(ColType.text, aggregatable=False),
        "as_of": ColumnInfo(ColType.datetime, aggregatable=False),
    },
    "stock_prices": {
        "ticker": ColumnInfo(ColType.text, aggregatable=False),
        "open": ColumnInfo(ColType.currency, aggregatable=True),
        "close": ColumnInfo(ColType.currency, aggregatable=True),
        "max": ColumnInfo(ColType.currency, aggregatable=True),
        "min": ColumnInfo(ColType.currency, aggregatable=True),
        "volume": ColumnInfo(ColType.number, aggregatable=True),
        "as_of": ColumnInfo(ColType.datetime, aggregatable=False),
    },
}

# Allowed filter ops per type
FILTER_OPS: Dict[ColType, Set[str]] = {
    ColType.text: {"contains", "startsWith", "equals", "in"},
    ColType.enum: {"in", "notIn"},
    ColType.number: {"<", "<=", "=", ">=", ">", "between"},
    ColType.currency: {"<", "<=", "=", ">=", ">", "between"},
    ColType.date: {"on", "before", "after", "between"},
    ColType.datetime: {"on", "before", "after", "between"},
}

NUMERIC_TYPES = {ColType.number, ColType.currency}


# ---------------------------
# Validation outputs
# ---------------------------


class Plan(msgspec.Struct, frozen=True):
    data_source: str
    group: bool  # whether grouped aggregates exist
    group_keys: Sequence[str]  # aliases to GROUP BY
    time_buckets: Sequence[str]  # aliases of time buckets
    agg_aliases: Sequence[str]  # aliases of all aggs
    window_agg_aliases: Sequence[str]  # aliases of window aggs
    projection_aliases: Sequence[str]  # all aliases exposed
    order_by: Sequence[SortKey]
    page_limit: int


class ErrorItem(msgspec.Struct, frozen=True):
    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(msgspec.Struct, frozen=True):
    error: Sequence[ErrorItem]


# ---------------------------
# Validator
# ---------------------------

MAX_PAGE_LIMIT = 1000


def _alias_of(p: Projection) -> str:
    if isinstance(p, Col):
        return p.as_ or p.name
    if isinstance(p, TimeBucket):
        return p.as_ or f"{p.column}@{p.grain}"
    if isinstance(p, Agg):
        return p.as_ or (f"{p.fn}_{p.column}" if p.column else p.fn)


def _validate_filters(
    filters: Sequence[Filter],
    cols: Dict[str, ColumnInfo],
    errors: List[ErrorItem],
) -> None:
    for f in filters:
        col = getattr(f, "column", None)
        if col not in cols:
            errors.append(
                ErrorItem(
                    "BAD_COLUMN", f"Unknown column '{col}' in filter", "filters"
                )
            )
            continue
        t = cols[col].type
        allowed = FILTER_OPS[t]
        op = getattr(f, "op")
        if op not in allowed:
            errors.append(
                ErrorItem(
                    "INVALID_FILTER",
                    f"Op '{op}' not allowed for type '{t.value}' on '{col}'",
                    "filters",
                )
            )


def _validate_timebucket(
    tb: TimeBucket, cols: Dict[str, ColumnInfo], errors: List[ErrorItem]
) -> None:
    if tb.column not in cols:
        errors.append(
            ErrorItem(
                "BAD_COLUMN",
                f"Unknown column '{tb.column}' in time_bucket",
                "select",
            )
        )
        return
    if cols[tb.column].type not in {ColType.datetime, ColType.date}:
        errors.append(
            ErrorItem(
                "BAD_TIME_COLUMN",
                f"time_bucket requires date/datetime column, got '{tb.column}'",
                "select",
            )
        )


def _validate_agg(
    ag: Agg, cols: Dict[str, ColumnInfo], errors: List[ErrorItem]
) -> None:
    if ag.fn == "count":
        pass
    elif ag.fn == "distinct_count":
        if not ag.column:
            errors.append(
                ErrorItem(
                    "BAD_AGG", "distinct_count requires 'column'", "select"
                )
            )
        elif ag.column not in cols:
            errors.append(
                ErrorItem(
                    "BAD_COLUMN",
                    f"Unknown column '{ag.column}' in aggregate",
                    "select",
                )
            )
    else:
        if not ag.column:
            errors.append(
                ErrorItem("BAD_AGG", f"{ag.fn} requires 'column'", "select")
            )
            return
        if ag.column not in cols:
            errors.append(
                ErrorItem(
                    "BAD_COLUMN",
                    f"Unknown column '{ag.column}' in aggregate",
                    "select",
                )
            )
            return
        if cols[ag.column].type not in NUMERIC_TYPES:
            errors.append(
                ErrorItem(
                    "AGG_TYPE",
                    f"{ag.fn} requires numeric column, got '{ag.column}'",
                    "select",
                )
            )
        if ag.fn == "percentile":
            if ag.p is None:
                errors.append(
                    ErrorItem("BAD_AGG", "percentile requires 'p'", "select")
                )
            else:
                if not (0 < ag.p <= 100 or 0 < ag.p <= 1):
                    errors.append(
                        ErrorItem(
                            "BAD_AGG",
                            "percentile 'p' should be in (0,1] or (0,100]",
                            "select",
                        )
                    )
    # window validation
    if ag.scope == "window":
        if not ag.window:
            errors.append(
                ErrorItem(
                    "BAD_WINDOW",
                    "window scope requires 'window' spec",
                    "select",
                )
            )
        else:
            if not ag.window.partitionBy:
                errors.append(
                    ErrorItem(
                        "BAD_WINDOW",
                        "window.partitionBy must not be empty",
                        "select",
                    )
                )
            if not ag.window.orderBy:
                errors.append(
                    ErrorItem(
                        "BAD_WINDOW",
                        "window.orderBy must not be empty",
                        "select",
                    )
                )


def validate_query(
    q: DataQuery, registry: ResourceRegistry = REGISTRY
) -> Union[Plan, ErrorResponse]:
    ds = q.data_source
    if ds not in registry:
        return ErrorResponse(
            [ErrorItem("UNKNOWN_RESOURCE", f"Unknown data_source '{ds}'")]
        )
    cols = registry[ds]

    errors: List[ErrorItem] = []

    # 1) Projections
    if not q.select or len(q.select) == 0:
        errors.append(
            ErrorItem(
                "EMPTY_SELECT", "At least one projection is required", "select"
            )
        )
        return ErrorResponse(errors)

    has_group_aggs = any(
        isinstance(p, Agg) and p.scope == "group" for p in q.select
    )

    group_keys: List[str] = []
    time_buckets: List[str] = []
    agg_aliases: List[str] = []
    window_aliases: List[str] = []
    projection_aliases: List[str] = []

    seen_aliases: Set[str] = set()

    for p in q.select:
        # Validate each projection & collect aliases
        if isinstance(p, Col):
            if p.name not in cols:
                errors.append(
                    ErrorItem(
                        "BAD_COLUMN", f"Unknown column '{p.name}'", "select"
                    )
                )
            alias = _alias_of(p)
            if alias in seen_aliases:
                errors.append(
                    ErrorItem(
                        "DUP_ALIAS", f"Duplicate alias '{alias}'", "select"
                    )
                )
            seen_aliases.add(alias)
            projection_aliases.append(alias)
            if has_group_aggs:
                group_keys.append(alias)

        elif isinstance(p, TimeBucket):
            _validate_timebucket(p, cols, errors)
            alias = _alias_of(p)
            if alias in seen_aliases:
                errors.append(
                    ErrorItem(
                        "DUP_ALIAS", f"Duplicate alias '{alias}'", "select"
                    )
                )
            seen_aliases.add(alias)
            projection_aliases.append(alias)
            time_buckets.append(alias)
            if has_group_aggs:
                group_keys.append(alias)

        elif isinstance(p, Agg):
            _validate_agg(p, cols, errors)
            alias = _alias_of(p)
            if alias in seen_aliases:
                errors.append(
                    ErrorItem(
                        "DUP_ALIAS", f"Duplicate alias '{alias}'", "select"
                    )
                )
            seen_aliases.add(alias)
            projection_aliases.append(alias)
            agg_aliases.append(alias)
            if p.scope == "window":
                window_aliases.append(alias)

    # 2) Filters
    if q.filters:
        _validate_filters(q.filters, cols, errors)

    # 3) Sort (must reference a projected alias or raw column name in select)
    if q.sort:
        valid_sort_targets = set(projection_aliases) | {
            getattr(p, "name", None) for p in q.select if isinstance(p, Col)
        }
        valid_sort_targets |= set(group_keys) | set(agg_aliases)
        valid_sort_targets.discard(None)
        for s in q.sort:
            if s.by not in valid_sort_targets:
                errors.append(
                    ErrorItem(
                        "BAD_SORT",
                        f"Sort 'by' must reference a selected alias/column, got '{s.by}'",
                        "sort",
                    )
                )

    # 4) Page size
    lim = q.page.limit if q.page else 50
    if lim <= 0 or lim > MAX_PAGE_LIMIT:
        errors.append(
            ErrorItem("BAD_LIMIT", f"limit must be 1..{MAX_PAGE_LIMIT}", "page")
        )

    # 5) Grouping sanity: if grouped aggregates exist, ensure no accidental non-key numerics leak through.
    # (In this unified model, bare Cols become keys so this is already safe. You might still want to
    #  ban selecting raw numerics that weren't intended as keys; keep as optional rule.)
    # Example optional rule:
    if has_group_aggs:
        # nothing to do; group keys already inferred from Col/TimeBucket
        pass

    if errors:
        return ErrorResponse(errors)

    # Build a minimal execution plan to hand to your compiler
    order_by = q.sort or []
    plan = Plan(
        data_source=ds,
        group=has_group_aggs,
        group_keys=group_keys,
        time_buckets=time_buckets,
        agg_aliases=agg_aliases,
        window_agg_aliases=window_aliases,
        projection_aliases=projection_aliases,
        order_by=order_by,
        page_limit=lim,
    )
    return plan


# ---------------------------
# Example usage in your handler
# ---------------------------


def run_query(q: DataQuery) -> Union[Plan, ErrorResponse]:
    plan_or_err = validate_query(q)
    if isinstance(plan_or_err, ErrorResponse):
        return plan_or_err
    # else: pass `plan_or_err` + `q` to your SQL builder
    return plan_or_err
