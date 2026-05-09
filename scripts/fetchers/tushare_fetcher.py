from scripts.parse_stock_list import to_tushare_code


def fetch_tushare_stock_data(client, code: str, data_date: str) -> dict:
    ts_code = to_tushare_code(code)
    record = {
        "source": "tushare",
        "code": code,
        "data_date": data_date,
        "missing_fields": [],
    }
    endpoints = {
        "stock_basic": lambda: client.stock_basic(ts_code=ts_code),
        "daily": lambda: client.daily(ts_code=ts_code),
        "daily_basic": lambda: client.daily_basic(ts_code=ts_code),
        "fina_indicator": lambda: client.fina_indicator(ts_code=ts_code),
    }
    for field, fetch in endpoints.items():
        try:
            record[field] = fetch().to_dict(orient="records")
        except Exception:
            record[field] = []
            record["missing_fields"].append(field)
    return record
