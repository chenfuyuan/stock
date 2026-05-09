import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.windowing import apply_recent_year_window

_FINA_LATEST_PERIODS = 4
_FINA_PERIOD_KEYS = ("end_date", "ann_date", "report_date")


def build_evidence_pack(raw_path: Path | str) -> dict:
    raw_path = Path(raw_path)
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    data_date = _extract_data_date(raw)
    return {
        "raw_path": str(raw_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stock": raw.get("stock"),
        "data_date": data_date,
        "fetched_at": raw.get("fetched_at"),
        "tushare_status": raw.get("tushare_status"),
        "missing_fields": list(raw.get("missing_fields") or []),
        "tushare": _evidence_from_tushare(raw.get("tushare"), data_date),
        "akshare": _evidence_from_akshare(raw.get("akshare"), data_date),
    }


def write_evidence_pack(raw_path: Path | str, evidence_dir: Path | str) -> Path:
    raw_path = Path(raw_path)
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    pack = build_evidence_pack(raw_path)
    out_path = evidence_dir / raw_path.name
    out_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return out_path


def _extract_data_date(raw: dict) -> str | None:
    for key in ("tushare", "akshare"):
        block = raw.get(key) or {}
        date = block.get("data_date")
        if date:
            return date
    return None


def _evidence_from_tushare(record: dict | None, data_date: str | None) -> dict | None:
    if not record:
        return None
    cutoff = data_date or record.get("data_date") or ""
    return {
        "source": record.get("source"),
        "code": record.get("code"),
        "data_date": record.get("data_date"),
        "missing_fields": list(record.get("missing_fields") or []),
        "stock_basic": record.get("stock_basic", []),
        "daily_basic": record.get("daily_basic", []),
        "daily": apply_recent_year_window(record.get("daily", []), "trade_date", cutoff),
        "fina_indicator_recent": _select_latest_periods(
            record.get("fina_indicator", []), _FINA_LATEST_PERIODS
        ),
    }


def _evidence_from_akshare(record: dict | None, data_date: str | None) -> dict | None:
    if not record:
        return None
    cutoff = data_date or record.get("data_date") or ""
    return {
        "source": record.get("source"),
        "code": record.get("code"),
        "data_date": record.get("data_date"),
        "missing_fields": list(record.get("missing_fields") or []),
        "individual_info": record.get("individual_info", []),
        "hist": apply_recent_year_window(record.get("hist", []), "日期", cutoff),
        "fund_flow": apply_recent_year_window(record.get("fund_flow", []), "日期", cutoff),
    }


def _select_latest_periods(records: list[dict], n: int) -> list[dict]:
    if not records:
        return []
    period_key = next((k for k in _FINA_PERIOD_KEYS if k in records[0]), None)
    if period_key is None:
        return list(records[:n])
    sorted_records = sorted(records, key=lambda r: str(r.get(period_key) or ""), reverse=True)
    return sorted_records[:n]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    raw_dir = root / "stock" / args.date / "data"
    evidence_dir = root / "stock" / args.date / "evidence"
    summary = {"date": args.date, "evidence": []}
    for raw_path in sorted(raw_dir.glob("*.json")):
        out_path = write_evidence_pack(raw_path, evidence_dir)
        summary["evidence"].append(str(out_path))
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
