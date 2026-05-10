import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.build_evidence_pack import write_evidence_pack
from scripts.config import get_tushare_token
from scripts.fetchers.akshare_fetcher import fetch_akshare_stock_data
from scripts.fetchers.tushare_fetcher import fetch_tushare_stock_data


def fetch_stock_data(
    stocks: list[dict[str, str]],
    date: str,
    root: Path | str = Path("."),
    token: str | None = None,
    tushare_fetcher=None,
    akshare_fetcher=None,
) -> dict:
    root = Path(root)
    summary = {"date": date, "written": [], "evidence": [], "metadata": []}

    for stock in stocks:
        tushare_record = None
        akshare_record = None
        missing_fields = []
        tushare_status = "skipped:no_token"

        if token:
            try:
                tushare_record = (tushare_fetcher or _default_tushare_fetcher)(stock["code"], date, token)
                tushare_status = "ok"
                missing_fields.extend(f"tushare:{field}" for field in tushare_record.get("missing_fields", []))
            except Exception as exc:
                tushare_status = f"unavailable:{type(exc).__name__}"
                missing_fields.append("tushare:unavailable")

        try:
            akshare_record = (akshare_fetcher or _default_akshare_fetcher)(stock["code"], date)
            missing_fields.extend(f"akshare:{field}" for field in akshare_record.get("missing_fields", []))
        except Exception as exc:
            akshare_record = None
            missing_fields.append(f"akshare:unavailable:{type(exc).__name__}")

        payload = {
            "stock": stock,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tushare_status": tushare_status,
            "tushare": tushare_record,
            "akshare": akshare_record,
            "missing_fields": missing_fields,
        }
        run_dir = root / "data" / "runs" / date / stock["code"]
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "structured_data.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        summary["written"].append(str(path))
        evidence_path = write_evidence_pack(path, run_dir, output_name="evidence_pack.json")
        summary["evidence"].append(str(evidence_path))
        metadata_path = _write_run_metadata(run_dir, stock, date, payload, evidence_path)
        summary["metadata"].append(str(metadata_path))
    return summary


def _write_run_metadata(run_dir: Path, stock: dict[str, str], date: str, payload: dict, evidence_path: Path) -> Path:
    sources = []
    if payload.get("tushare"):
        sources.append("tushare")
    if payload.get("akshare"):
        sources.append("akshare")
    metadata = {
        "stock": stock,
        "analysis_date": date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query_window": {"type": "recent_year", "end_date": date},
        "data_sources": sources,
        "files": ["structured_data.json", evidence_path.name],
        "missing_fields": list(payload.get("missing_fields") or []),
        "tushare_status": payload.get("tushare_status"),
    }
    path = run_dir / "metadata.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def _default_tushare_fetcher(code: str, date: str, token: str) -> dict:
    import tushare as ts

    client = ts.pro_api(token)
    return fetch_tushare_stock_data(client, code, date)


def _default_akshare_fetcher(code: str, date: str) -> dict:
    import akshare as ak

    return fetch_akshare_stock_data(ak, code, date)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    stocks = json.loads(sys.stdin.read() or "[]")
    summary = fetch_stock_data(stocks, args.date, root, token=get_tushare_token(root))
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
