import json
import subprocess
import sys

from scripts.fetch_stock_data import fetch_stock_data


STOCK = {"name": "炼石航空", "code": "000697.XSHE"}
TOKEN = "real-secret-token"


def test_fetch_stock_data_writes_combined_json_to_run_directory(tmp_path):
    def tushare_fetcher(code, date, token):
        assert token == TOKEN
        return {"source": "tushare", "code": code, "data_date": date, "missing_fields": ["fina_indicator"]}

    def akshare_fetcher(code, date):
        return {"source": "akshare", "code": code, "data_date": date, "missing_fields": ["fund_flow"]}

    summary = fetch_stock_data([STOCK], "2026-05-10", tmp_path, token=TOKEN, tushare_fetcher=tushare_fetcher, akshare_fetcher=akshare_fetcher)

    output_path = tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "structured_data.json"
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["stock"] == STOCK
    assert payload["tushare_status"] == "ok"
    assert payload["tushare"]["source"] == "tushare"
    assert payload["akshare"]["source"] == "akshare"
    assert payload["missing_fields"] == ["tushare:fina_indicator", "akshare:fund_flow"]
    assert summary["written"] == [str(output_path)]
    assert not (tmp_path / "vault" / "stock" / "2026-05-10" / "data").exists()


def test_fetch_stock_data_writes_run_metadata(tmp_path):
    def akshare_fetcher(code, date):
        return {"source": "akshare", "code": code, "data_date": date, "missing_fields": ["fund_flow"]}

    fetch_stock_data([STOCK], "2026-05-10", tmp_path, token=None, tushare_fetcher=None, akshare_fetcher=akshare_fetcher)

    metadata_path = tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["stock"] == STOCK
    assert metadata["analysis_date"] == "2026-05-10"
    assert metadata["data_sources"] == ["akshare"]
    assert metadata["query_window"] == {"type": "recent_year", "end_date": "2026-05-10"}
    assert metadata["missing_fields"] == ["akshare:fund_flow"]
    assert metadata["files"] == ["structured_data.json", "evidence_pack.json"]


def test_fetch_stock_data_skips_tushare_without_token_and_still_runs_akshare(tmp_path):
    def akshare_fetcher(code, date):
        return {"source": "akshare", "code": code, "data_date": date, "missing_fields": []}

    fetch_stock_data([STOCK], "2026-05-10", tmp_path, token=None, tushare_fetcher=None, akshare_fetcher=akshare_fetcher)

    payload = json.loads((tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "structured_data.json").read_text(encoding="utf-8"))
    assert payload["tushare_status"] == "skipped:no_token"
    assert payload["tushare"] is None
    assert payload["akshare"]["source"] == "akshare"


def test_fetch_stock_data_does_not_write_token_from_exception_text(tmp_path):
    def tushare_fetcher(code, date, token):
        raise RuntimeError(f"failed with {token}")

    def akshare_fetcher(code, date):
        return {"source": "akshare", "code": code, "data_date": date, "missing_fields": []}

    fetch_stock_data([STOCK], "2026-05-10", tmp_path, token=TOKEN, tushare_fetcher=tushare_fetcher, akshare_fetcher=akshare_fetcher)

    text = (tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "structured_data.json").read_text(encoding="utf-8")
    assert TOKEN not in text
    assert "failed with" not in text
    assert "RuntimeError" in text


def test_fetch_stock_data_also_writes_evidence_pack_in_run_directory(tmp_path):
    def akshare_fetcher(code, date):
        return {"source": "akshare", "code": code, "data_date": date, "missing_fields": []}

    summary = fetch_stock_data(
        [STOCK],
        "2026-05-10",
        tmp_path,
        token=None,
        tushare_fetcher=None,
        akshare_fetcher=akshare_fetcher,
    )

    raw_path = tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "structured_data.json"
    evidence_path = tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "evidence_pack.json"
    assert evidence_path.exists()
    assert summary["evidence"] == [str(evidence_path)]
    pack = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert pack["raw_path"] == str(raw_path)
    assert pack["data_date"] == "2026-05-10"


def test_fetch_stock_data_cli_reads_stdin_and_writes_summary(tmp_path, monkeypatch):
    monkeypatch.setenv("TUSHARE_TOKEN", "")
    result = subprocess.run(
        [sys.executable, "-m", "scripts.fetch_stock_data", "--date", "2026-05-10", "--root", str(tmp_path)],
        input=json.dumps([STOCK], ensure_ascii=False),
        text=True,
        capture_output=True,
        check=True,
    )

    summary = json.loads(result.stdout)
    assert summary["date"] == "2026-05-10"
    assert summary["written"] == [str(tmp_path / "data" / "runs" / "2026-05-10" / "000697.XSHE" / "structured_data.json")]
