import argparse
import json
import sys
from pathlib import Path

from scripts.templates import render_template

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
_DAILY_DOCS = {
    "股票池排序.md": "stock_pool_ranking.md",
    "主题行业综述.md": "theme_industry_review.md",
    "研究日志.md": "research_log.md",
}


def init_daily_reports(stocks: list[dict[str, str]], date: str, root: Path | str = Path(".")) -> dict:
    root = Path(root)
    companies_dir = root / "companies"
    daily_dir = root / "stock" / date
    data_dir = daily_dir / "data"
    companies_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    summary = {"date": date, "created": [], "skipped": []}
    stock_links = []

    for stock in stocks:
        context = _context(stock, date)
        stock_links.append(f"- [[{context['daily_wikilink']}]]")
        skipped_files = []
        if _write_if_missing(companies_dir / f"{context['company_wikilink']}.md", "company_profile.md", context):
            summary["created"].append(str(Path("companies") / f"{context['company_wikilink']}.md"))
        else:
            skipped_files.append("company")
        if _write_if_missing(daily_dir / f"{context['daily_wikilink']}.md", "daily_stock_report.md", context):
            summary["created"].append(str(Path("stock") / date / f"{context['daily_wikilink']}.md"))
        else:
            skipped_files.append("daily")
        if skipped_files:
            summary["skipped"].append({"name": stock["name"], "code": stock["code"], "files": skipped_files})

    index_context = {"date": date, "stock_pool_links": "\n".join(stock_links)}
    _write_static(daily_dir / "index.md", "daily_index.md", index_context, summary, date)
    for filename, template in _DAILY_DOCS.items():
        _write_static(daily_dir / filename, template, {"date": date}, summary, date)
    return summary


def _context(stock: dict[str, str], date: str) -> dict[str, str]:
    company_wikilink = f"{stock['code']}-{stock['name']}"
    daily_wikilink = f"{stock['code']}-{stock['name']}-日评"
    return {
        "date": date,
        "stock_code": stock["code"],
        "stock_name": stock["name"],
        "company_wikilink": company_wikilink,
        "daily_wikilink": daily_wikilink,
    }


def _write_static(path: Path, template_name: str, context: dict[str, str], summary: dict, date: str) -> None:
    if _write_if_missing(path, template_name, context):
        summary["created"].append(str(Path("stock") / date / path.name))
    else:
        summary["skipped"].append({"file": path.name})


def _write_if_missing(path: Path, template_name: str, context: dict[str, str]) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    template = (_TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    path.write_text(render_template(template, context), encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    stocks = json.loads(sys.stdin.read() or "[]")
    summary = init_daily_reports(stocks, args.date, Path(args.root))
    json.dump(summary, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
