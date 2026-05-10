import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.build_evidence_pack import write_evidence_pack
from scripts.config import get_tushare_token, get_vault_root
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
    vault = get_vault_root(root)
    data_dir = vault / "stock" / date / "data"
    evidence_dir = vault / "stock" / date / "evidence"
    data_dir.mkdir(parents=True, exist_ok=True)
    summary = {"date": date, "written": [], "evidence": []}

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
        path = data_dir / f"{stock['code']}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        summary["written"].append(str(path))
        evidence_path = write_evidence_pack(path, evidence_dir)
        summary["evidence"].append(str(evidence_path))
    return summary


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
