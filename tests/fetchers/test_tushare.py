import pandas as pd

from scripts.fetchers.tushare_fetcher import fetch_tushare_stock_data


class FakeTushareClient:
    def __init__(self, failures=None):
        self.failures = failures or set()

    def stock_basic(self, ts_code):
        return self._frame("stock_basic", {"ts_code": ts_code, "name": "炼石航空"})

    def daily(self, ts_code):
        return self._frame("daily", {"ts_code": ts_code, "close": 10.5})

    def daily_basic(self, ts_code):
        return self._frame("daily_basic", {"ts_code": ts_code, "pe": 20.0})

    def fina_indicator(self, ts_code):
        return self._frame("fina_indicator", {"ts_code": ts_code, "roe": 5.0})

    def _frame(self, field, row):
        if field in self.failures:
            raise RuntimeError("boom secret-token")
        return pd.DataFrame([row])


def test_fetch_tushare_stock_data_collects_all_fields():
    record = fetch_tushare_stock_data(FakeTushareClient(), "000697.XSHE", "2026-05-10")

    assert record["source"] == "tushare"
    assert record["code"] == "000697.XSHE"
    assert record["data_date"] == "2026-05-10"
    assert record["stock_basic"][0]["ts_code"] == "000697.SZ"
    assert record["daily"][0]["close"] == 10.5
    assert record["daily_basic"][0]["pe"] == 20.0
    assert record["fina_indicator"][0]["roe"] == 5.0
    assert record["missing_fields"] == []


def test_fetch_tushare_stock_data_isolates_field_failures_without_exception_text():
    record = fetch_tushare_stock_data(FakeTushareClient({"fina_indicator"}), "000697.XSHE", "2026-05-10")

    assert record["fina_indicator"] == []
    assert record["missing_fields"] == ["fina_indicator"]
    assert "secret-token" not in str(record)
