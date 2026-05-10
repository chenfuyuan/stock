import json
from pathlib import Path

import pytest

from scripts.build_evidence_pack import build_evidence_pack, write_evidence_pack

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "evidence_pack"


@pytest.fixture()
def raw_payload():
    return {
        "stock": {"name": "炼石航空", "code": "000697.XSHE"},
        "fetched_at": "2026-05-10T03:00:00+00:00",
        "tushare_status": "ok",
        "tushare": {
            "source": "tushare",
            "code": "000697.XSHE",
            "data_date": "2026-05-10",
            "missing_fields": [],
            "stock_basic": [{"ts_code": "000697.SZ", "name": "炼石航空"}],
            "daily": [
                {"ts_code": "000697.SZ", "trade_date": "20240101", "close": 9.0},
                {"ts_code": "000697.SZ", "trade_date": "20250601", "close": 10.0},
                {"ts_code": "000697.SZ", "trade_date": "20260101", "close": 11.0},
            ],
            "daily_basic": [{"ts_code": "000697.SZ", "pe": 20.0}],
            "fina_indicator": [
                {"ts_code": "000697.SZ", "end_date": "20220331", "roe": 1.0},
                {"ts_code": "000697.SZ", "end_date": "20230331", "roe": 2.0},
                {"ts_code": "000697.SZ", "end_date": "20230630", "roe": 2.5},
                {"ts_code": "000697.SZ", "end_date": "20231231", "roe": 3.0},
                {"ts_code": "000697.SZ", "end_date": "20240630", "roe": 4.0},
                {"ts_code": "000697.SZ", "end_date": "20241231", "roe": 4.5},
                {"ts_code": "000697.SZ", "end_date": "20250331", "roe": 5.0},
            ],
        },
        "akshare": {
            "source": "akshare",
            "code": "000697.XSHE",
            "data_date": "2026-05-10",
            "missing_fields": [],
            "hist": [
                {"代码": "000697", "日期": "2024-01-01", "收盘": 9.0},
                {"代码": "000697", "日期": "2025-06-01", "收盘": 10.0},
                {"代码": "000697", "日期": "2026-01-01", "收盘": 11.0},
            ],
            "individual_info": [{"item": "股票简称", "value": "炼石航空"}],
            "fund_flow": [
                {"代码": "000697", "日期": "2024-01-01", "主力净流入": -50},
                {"代码": "000697", "日期": "2025-06-01", "主力净流入": 100},
                {"代码": "000697", "日期": "2026-01-01", "主力净流入": 200},
            ],
        },
        "missing_fields": [],
    }


def _write_raw(tmp_path: Path, payload: dict) -> Path:
    raw_path = tmp_path / "stock" / "2026-05-10" / "data" / "000697.XSHE.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return raw_path


def test_build_evidence_pack_produces_metadata_from_raw_without_network(tmp_path, raw_payload):
    raw_path = _write_raw(tmp_path, raw_payload)

    pack = build_evidence_pack(raw_path)

    assert pack["raw_path"] == str(raw_path)
    assert pack["generated_at"]
    assert pack["data_date"] == "2026-05-10"
    assert pack["fetched_at"] == "2026-05-10T03:00:00+00:00"
    assert pack["tushare_status"] == "ok"
    assert pack["stock"] == {"name": "炼石航空", "code": "000697.XSHE"}
    assert pack["missing_fields"] == []


def test_build_evidence_pack_windows_high_frequency_data_to_recent_year(tmp_path, raw_payload):
    raw_path = _write_raw(tmp_path, raw_payload)

    pack = build_evidence_pack(raw_path)

    daily_dates = [row["trade_date"] for row in pack["tushare"]["daily"]]
    assert "20240101" not in daily_dates
    assert "20250601" in daily_dates
    assert "20260101" in daily_dates

    hist_dates = [row["日期"] for row in pack["akshare"]["hist"]]
    assert hist_dates == ["2025-06-01", "2026-01-01"]

    fund_dates = [row["日期"] for row in pack["akshare"]["fund_flow"]]
    assert fund_dates == ["2025-06-01", "2026-01-01"]


def test_build_evidence_pack_selects_recent_fina_periods_not_full_history(tmp_path, raw_payload):
    raw_path = _write_raw(tmp_path, raw_payload)

    pack = build_evidence_pack(raw_path)

    fina = pack["tushare"]["fina_indicator_recent"]
    assert "fina_indicator" not in pack["tushare"]
    end_dates = [row["end_date"] for row in fina]
    assert end_dates == ["20250331", "20241231", "20240630", "20231231"]
    assert len(fina) <= 4


def test_build_evidence_pack_exposes_missing_field_status(tmp_path):
    raw = {
        "stock": {"name": "X", "code": "111111.XSHE"},
        "fetched_at": "2026-05-10T03:00:00+00:00",
        "tushare_status": "skipped:no_token",
        "tushare": None,
        "akshare": {
            "source": "akshare",
            "code": "111111.XSHE",
            "data_date": "2026-05-10",
            "missing_fields": ["fund_flow"],
            "hist": [],
            "individual_info": [],
            "fund_flow": [],
        },
        "missing_fields": ["akshare:fund_flow"],
    }
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")

    pack = build_evidence_pack(raw_path)

    assert pack["tushare"] is None
    assert pack["tushare_status"] == "skipped:no_token"
    assert pack["missing_fields"] == ["akshare:fund_flow"]
    assert pack["akshare"]["missing_fields"] == ["fund_flow"]


def test_build_evidence_pack_matches_shape_for_full_fixture(tmp_path):
    raw_path = tmp_path / "000697.XSHE.json"
    raw_path.write_text((FIXTURES / "raw_input.json").read_text(encoding="utf-8"), encoding="utf-8")

    pack = build_evidence_pack(raw_path)

    shape = json.loads((FIXTURES / "evidence_pack_shape.json").read_text(encoding="utf-8"))
    assert set(pack.keys()) == set(shape.keys())
    assert set(pack["tushare"].keys()) == set(shape["tushare"].keys())
    assert set(pack["akshare"].keys()) == set(shape["akshare"].keys())
    daily_dates = [row["trade_date"] for row in pack["tushare"]["daily"]]
    assert "20240101" not in daily_dates
    assert len(pack["tushare"]["fina_indicator_recent"]) <= 4


def test_build_evidence_pack_matches_shape_for_missing_fixture(tmp_path):
    raw_path = tmp_path / "000791.XSHE.json"
    raw_path.write_text(
        (FIXTURES / "raw_input_missing.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    pack = build_evidence_pack(raw_path)

    assert pack["tushare"] is None
    assert pack["tushare_status"] == "skipped:no_token"
    assert pack["akshare"]["missing_fields"] == ["fund_flow"]
    assert pack["missing_fields"] == ["akshare:fund_flow"]


def test_write_evidence_pack_writes_to_evidence_directory(tmp_path, raw_payload):
    raw_path = _write_raw(tmp_path, raw_payload)
    evidence_dir = tmp_path / "stock" / "2026-05-10" / "evidence"

    out_path = write_evidence_pack(raw_path, evidence_dir)

    assert out_path == evidence_dir / "000697.XSHE.json"
    text = out_path.read_text(encoding="utf-8")
    pack = json.loads(text)
    assert pack["raw_path"] == str(raw_path)
    assert pack["tushare"]["fina_indicator_recent"]


def test_build_evidence_pack_cli_reads_run_directories(tmp_path, raw_payload):
    raw_path = tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "structured_data.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(raw_payload, ensure_ascii=False), encoding="utf-8")

    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "scripts.build_evidence_pack", "--date", "2026-05-10", "--root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=True,
    )

    summary = json.loads(result.stdout)
    out_path = tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "evidence_pack.json"
    assert summary["evidence"] == [str(out_path)]
    assert json.loads(out_path.read_text(encoding="utf-8"))["raw_path"] == str(raw_path)
