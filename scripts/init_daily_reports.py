import argparse
import json
import sys
from pathlib import Path

from scripts.config import get_vault_root
from scripts.templates import render_template

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
_DAILY_DOCS = {
    "股票池排序.md": "stock_pool_ranking.md",
    "主题行业综述.md": "theme_industry_review.md",
    "研究日志.md": "research_log.md",
}
_KNOWLEDGE_DOCS = {
    "themes/index.md": "knowledge_themes_index.md",
    "events/index.md": "knowledge_events_index.md",
    "industries/index.md": "knowledge_industries_index.md",
    "catalysts/index.md": "knowledge_catalysts_index.md",
    "evidence/index.md": "knowledge_evidence_index.md",
    "reviews/index.md": "knowledge_reviews_index.md",
}


def init_daily_reports(
    stocks: list[dict[str, str]],
    date: str,
    root: Path | str = Path("."),
    industry_nodes: list[str] | None = None,
    catalyst_nodes: list[str] | None = None,
) -> dict:
    root = Path(root)
    vault = get_vault_root(root)
    companies_dir = vault / "companies"
    daily_dir = vault / "stock" / date
    data_dir = daily_dir / "data"
    companies_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    summary = {"date": date, "created": [], "skipped": []}
    _write_static(vault / "index.md", "vault_index.md", {}, summary, root)
    _write_knowledge_index(vault / "knowledge" / "index.md", summary, root)
    for filename, template in _KNOWLEDGE_DOCS.items():
        _write_static(vault / "knowledge" / filename, template, {}, summary, root)
    _write_nodes(vault / "knowledge" / "industries", industry_nodes or [], "industry_node.md", summary, root)
    _write_nodes(vault / "knowledge" / "catalysts", catalyst_nodes or [], "catalyst_node.md", summary, root)
    stock_links = []

    for stock in stocks:
        context = _context(stock, date)
        stock_links.append(f"- [[{context['daily_wikilink']}]]")
        skipped_files = []
        company_path = companies_dir / f"{context['company_wikilink']}.md"
        daily_path = daily_dir / f"{context['daily_wikilink']}.md"
        if _write_if_missing(company_path, "company_profile.md", context):
            summary["created"].append(str(company_path.relative_to(root)))
        else:
            skipped_files.append("company")
        if _write_if_missing(daily_path, "daily_stock_report.md", context):
            summary["created"].append(str(daily_path.relative_to(root)))
        else:
            skipped_files.append("daily")
        if skipped_files:
            summary["skipped"].append({"name": stock["name"], "code": stock["code"], "files": skipped_files})

    index_context = {"date": date, "stock_pool_links": "\n".join(stock_links)}
    _write_static(daily_dir / "index.md", "daily_index.md", index_context, summary, root)
    for filename, template in _DAILY_DOCS.items():
        _write_static(daily_dir / filename, template, {"date": date}, summary, root)
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
        "comparison_scope": "待人工填写",
        "industry_catalyst_links": "[[行业研究入口]] / [[催化研究入口]]",
    }


def _write_static(path: Path, template_name: str, context: dict[str, str], summary: dict, root: Path) -> None:
    if _write_if_missing(path, template_name, context):
        summary["created"].append(str(path.relative_to(root)))
    else:
        summary["skipped"].append({"file": path.name})


def _write_nodes(directory: Path, node_names: list[str], template_name: str, summary: dict, root: Path) -> None:
    for node_name in node_names:
        path = directory / f"{node_name}.md"
        if _write_if_missing(path, template_name, {"node_name": node_name}):
            summary["created"].append(str(path.relative_to(root)))
        else:
            summary["skipped"].append({"file": str(path.relative_to(root))})


def _write_knowledge_index(path: Path, summary: dict, root: Path) -> None:
    if _write_if_missing(path, "knowledge_index.md", {}):
        summary["created"].append(str(path.relative_to(root)))
        return

    relative_path = str(path.relative_to(get_vault_root(root)))
    content = path.read_text(encoding="utf-8")
    missing_links = [link for link in ["[[行业研究入口]]", "[[催化研究入口]]"] if link not in content]
    if not missing_links:
        summary["skipped"].append({"file": relative_path})
        return
    if "## 长期沉淀层" not in content:
        summary["skipped"].append({"file": relative_path, "append_skipped": missing_links})
        return

    insertion = "".join(f"- {link}\n" for link in missing_links)
    if content.endswith("\n"):
        content = f"{content}{insertion}"
    else:
        content = f"{content}\n{insertion}"
    path.write_text(content, encoding="utf-8")
    summary["skipped"].append({"file": relative_path, "appended": missing_links})


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
