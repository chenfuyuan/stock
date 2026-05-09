def fetch_akshare_stock_data(akshare_module, code: str, data_date: str) -> dict:
    symbol = code.split(".", 1)[0]
    record = {
        "source": "akshare",
        "code": code,
        "data_date": data_date,
        "missing_fields": [],
    }
    endpoints = {
        "hist": lambda: akshare_module.stock_zh_a_hist(symbol=symbol),
        "individual_info": lambda: akshare_module.stock_individual_info_em(symbol=symbol),
        "fund_flow": lambda: akshare_module.stock_individual_fund_flow(stock=symbol),
    }
    for field, fetch in endpoints.items():
        try:
            record[field] = fetch().to_dict(orient="records")
        except Exception:
            record[field] = []
            record["missing_fields"].append(field)
    return record
