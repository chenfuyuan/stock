import pandas as pd

from scripts.fetchers.akshare_fetcher import fetch_akshare_stock_data


class FakeAkshare:
    def __init__(self, failures=None):
        self.failures = failures or set()
        self.daily_calls: list[dict] = []
        self.basic_info_calls: list[dict] = []
        self.fund_flow_calls: list[dict] = []

    def stock_zh_a_daily(self, symbol):
        self.daily_calls.append({"symbol": symbol})
        return self._frame(
            "hist",
            {"date": "2026-05-08", "open": 11.77, "close": 12.58, "high": 12.94, "low": 11.58, "volume": 5.0, "amount": 6.0, "turnover": 0.08},
        )

    def stock_individual_basic_info_xq(self, symbol):
        self.basic_info_calls.append({"symbol": symbol})
        return self._frame("individual_info", {"item": "org_short_name_cn", "value": "炼石航空"})

    def stock_individual_fund_flow(self, stock, market):
        self.fund_flow_calls.append({"stock": stock, "market": market})
        return self._frame("fund_flow", {"代码": stock, "市场": market, "主力净流入": 100})

    def _frame(self, field, row):
        if field in self.failures:
            raise RuntimeError("boom")
        return pd.DataFrame([row])


def test_fetch_akshare_stock_data_collects_all_fields():
    fake = FakeAkshare()
    record = fetch_akshare_stock_data(fake, "000697.XSHE", "2026-05-10")

    assert record["source"] == "akshare"
    assert record["code"] == "000697.XSHE"
    assert record["data_date"] == "2026-05-10"
    assert record["hist"][0]["日期"] == "2026-05-08"
    assert record["hist"][0]["收盘"] == 12.58
    assert record["hist"][0]["股票代码"] == "000697"
    assert record["individual_info"][0]["value"] == "炼石航空"
    assert record["fund_flow"][0]["主力净流入"] == 100
    assert record["fund_flow"][0]["市场"] == "sz"
    assert fake.daily_calls == [{"symbol": "sz000697"}]
    assert fake.basic_info_calls == [{"symbol": "SZ000697"}]
    assert fake.fund_flow_calls == [{"stock": "000697", "market": "sz"}]
    assert record["missing_fields"] == []


def test_fetch_akshare_stock_data_isolates_field_failures():
    record = fetch_akshare_stock_data(FakeAkshare({"fund_flow"}), "000697.XSHE", "2026-05-10")

    assert record["fund_flow"] == []
    assert record["missing_fields"] == ["fund_flow"]


def test_fetch_akshare_stock_data_maps_suffix_to_market():
    cases = [
        ("000697.XSHE", "sz", "sz000697", "SZ000697"),
        ("000697.SZ", "sz", "sz000697", "SZ000697"),
        ("600000.XSHG", "sh", "sh600000", "SH600000"),
        ("600000.SH", "sh", "sh600000", "SH600000"),
        ("835174.XBSE", "bj", "bj835174", "BJ835174"),
        ("835174.BJ", "bj", "bj835174", "BJ835174"),
    ]
    for code, expected_market, expected_sina, expected_xq in cases:
        fake = FakeAkshare()
        fetch_akshare_stock_data(fake, code, "2026-05-10")
        assert fake.fund_flow_calls == [{"stock": code.split(".")[0], "market": expected_market}], code
        assert fake.daily_calls == [{"symbol": expected_sina}], code
        assert fake.basic_info_calls == [{"symbol": expected_xq}], code


def test_fetch_akshare_stock_data_skips_all_fields_for_unknown_suffix():
    fake = FakeAkshare()
    record = fetch_akshare_stock_data(fake, "000697.UNKNOWN", "2026-05-10")

    assert record["hist"] == []
    assert record["individual_info"] == []
    assert record["fund_flow"] == []
    assert set(record["missing_fields"]) == {"hist", "individual_info", "fund_flow"}
    assert fake.daily_calls == []
    assert fake.basic_info_calls == []
    assert fake.fund_flow_calls == []


def test_fetch_akshare_stock_data_limits_hist_and_fund_flow_to_recent_year():
    class WindowedAkshare(FakeAkshare):
        def stock_zh_a_daily(self, symbol):
            self.daily_calls.append({"symbol": symbol})
            return pd.DataFrame(
                [
                    {"date": "2024-01-01", "open": 9.0, "close": 9.0, "high": 9.0, "low": 9.0, "volume": 1, "amount": 1, "turnover": 0.01},
                    {"date": "2025-06-01", "open": 10.0, "close": 10.0, "high": 10.0, "low": 10.0, "volume": 1, "amount": 1, "turnover": 0.01},
                    {"date": "2026-01-01", "open": 11.0, "close": 11.0, "high": 11.0, "low": 11.0, "volume": 1, "amount": 1, "turnover": 0.01},
                ]
            )

        def stock_individual_fund_flow(self, stock, market):
            self.fund_flow_calls.append({"stock": stock, "market": market})
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


def test_fetch_akshare_stock_data_normalizes_date_objects_to_strings():
    import datetime

    class DateObjectAkshare(FakeAkshare):
        def stock_zh_a_daily(self, symbol):
            self.daily_calls.append({"symbol": symbol})
            return pd.DataFrame(
                [{"date": datetime.date(2026, 5, 8), "open": 11.77, "close": 12.58, "high": 12.94, "low": 11.58, "volume": 5, "amount": 6, "turnover": 0.08}]
            )

    record = fetch_akshare_stock_data(DateObjectAkshare(), "000697.XSHE", "2026-05-10")
    assert record["hist"][0]["日期"] == "2026-05-08"
    assert isinstance(record["hist"][0]["日期"], str)
