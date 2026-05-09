import pandas as pd

from scripts.fetchers.akshare_fetcher import fetch_akshare_stock_data


class FakeAkshare:
    def __init__(self, failures=None):
        self.failures = failures or set()

    def stock_zh_a_hist(self, symbol):
        return self._frame("hist", {"代码": symbol, "收盘": 10.5})

    def stock_individual_info_em(self, symbol):
        return self._frame("individual_info", {"item": "股票简称", "value": "炼石航空"})

    def stock_individual_fund_flow(self, stock):
        return self._frame("fund_flow", {"代码": stock, "主力净流入": 100})

    def _frame(self, field, row):
        if field in self.failures:
            raise RuntimeError("boom")
        return pd.DataFrame([row])


def test_fetch_akshare_stock_data_collects_all_fields():
    record = fetch_akshare_stock_data(FakeAkshare(), "000697.XSHE", "2026-05-10")

    assert record["source"] == "akshare"
    assert record["code"] == "000697.XSHE"
    assert record["data_date"] == "2026-05-10"
    assert record["hist"][0]["代码"] == "000697"
    assert record["individual_info"][0]["value"] == "炼石航空"
    assert record["fund_flow"][0]["主力净流入"] == 100
    assert record["missing_fields"] == []


def test_fetch_akshare_stock_data_isolates_field_failures():
    record = fetch_akshare_stock_data(FakeAkshare({"fund_flow"}), "000697.XSHE", "2026-05-10")

    assert record["fund_flow"] == []
    assert record["missing_fields"] == ["fund_flow"]


def test_fetch_akshare_stock_data_limits_hist_and_fund_flow_to_recent_year():
    class WindowedAkshare(FakeAkshare):
        def stock_zh_a_hist(self, symbol):
            return pd.DataFrame(
                [
                    {"代码": symbol, "日期": "2024-01-01", "收盘": 9.0},
                    {"代码": symbol, "日期": "2025-06-01", "收盘": 10.0},
                    {"代码": symbol, "日期": "2026-01-01", "收盘": 11.0},
                ]
            )

        def stock_individual_fund_flow(self, stock):
            return pd.DataFrame(
                [
                    {"代码": stock, "日期": "2024-01-01", "主力净流入": -50},
                    {"代码": stock, "日期": "2025-06-01", "主力净流入": 100},
                    {"代码": stock, "日期": "2026-01-01", "主力净流入": 200},
                ]
            )

    record = fetch_akshare_stock_data(WindowedAkshare(), "000697.XSHE", "2026-05-10")

    hist_dates = [row["日期"] for row in record["hist"]]
    assert hist_dates == ["2025-06-01", "2026-01-01"]

    fund_dates = [row["日期"] for row in record["fund_flow"]]
    assert fund_dates == ["2025-06-01", "2026-01-01"]
