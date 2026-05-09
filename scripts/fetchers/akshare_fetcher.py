from scripts.windowing import apply_recent_year_window

_SUFFIX_TO_MARKET = {
    "XSHE": "sz",
    "SZ": "sz",
    "XSHG": "sh",
    "SH": "sh",
    "XBSE": "bj",
    "BJ": "bj",
}

_HIST_COLUMN_MAP = {
    "date": "日期",
    "open": "开盘",
    "close": "收盘",
    "high": "最高",
    "low": "最低",
    "volume": "成交量",
    "amount": "成交额",
    "turnover": "换手率",
}


def fetch_akshare_stock_data(akshare_module, code: str, data_date: str) -> dict:
    symbol, _, suffix = code.partition(".")
    market = _SUFFIX_TO_MARKET.get(suffix.upper())
    record = {
        "source": "akshare",
        "code": code,
        "data_date": data_date,
        "missing_fields": [],
    }

    if market is None:
        endpoints: dict = {"hist": None, "individual_info": None, "fund_flow": None}
    else:
        sina_symbol = f"{market}{symbol}"
        xq_symbol = f"{market.upper()}{symbol}"
        endpoints = {
            "hist": lambda: _normalize_hist(
                akshare_module.stock_zh_a_daily(symbol=sina_symbol), symbol
            ),
            "individual_info": lambda: akshare_module.stock_individual_basic_info_xq(
                symbol=xq_symbol
            ).to_dict(orient="records"),
            "fund_flow": lambda: akshare_module.stock_individual_fund_flow(
                stock=symbol, market=market
            ).to_dict(orient="records"),
        }

    for field, fetch in endpoints.items():
        if fetch is None:
            record[field] = []
            record["missing_fields"].append(field)
            continue
        try:
            record[field] = fetch()
        except Exception:
            record[field] = []
            record["missing_fields"].append(field)
    record["hist"] = apply_recent_year_window(record["hist"], "日期", data_date)
    record["fund_flow"] = apply_recent_year_window(record["fund_flow"], "日期", data_date)
    return record


def _normalize_hist(df, symbol: str) -> list[dict]:
    df = df.rename(columns=_HIST_COLUMN_MAP)
    keep = [v for v in _HIST_COLUMN_MAP.values() if v in df.columns]
    df = df[keep].copy()
    if "日期" in df.columns:
        df["日期"] = df["日期"].astype(str)
    df["股票代码"] = symbol
    return df.to_dict(orient="records")
