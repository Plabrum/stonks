# =========
# Example: build an OPTIONS payload in-code
# =========


def example_options_companies() -> OptionsResponse:
    return OptionsResponse(
        resource="companies",
        columns=[
            TextColumnSpec(name="name", filterOps=[op.value for op in OpText]),
            TextColumnSpec(
                name="ticker", filterOps=[OpText.equals.value, OpText._in.value]
            ),
            EnumColumnSpec(
                name="sector",
                values=["Technology", "Energy", "Healthcare", "Financials"],
                filterOps=[OpEnum._in.value, OpEnum.notIn.value],
            ),
            CurrencyColumnSpec(
                name="share_price",
                unit="USD",
                filterOps=[
                    OpNum.lt.value,
                    OpNum.lte.value,
                    OpNum.eq.value,
                    OpNum.gte.value,
                    OpNum.gt.value,
                    OpNum.between.value,
                ],
            ),
            TextColumnSpec(
                name="website",
                sortable=False,
                filterOps=[OpText.contains.value, OpText.equals.value],
            ),
            DateTimeColumnSpec(
                name="as_of",
                grains=["1d", "1w", "1m"],
                filterOps=[
                    OpDate.on.value,
                    OpDate.before.value,
                    OpDate.after.value,
                    OpDate.between.value,
                ],
            ),
        ],
        supports=SupportsSpec(),
        constraints=ConstraintsSpec(),
    )


# =========
# Example: decode/encode
# =========

# Encode to JSON bytes for a response:
# msgspec.json.encode(OptionsResponse(...))

# Decode a request body (bytes) into a DataQuery:
# query = msgspec.json.decode(body_bytes, type=DataQuery)
