import json
import subprocess
import sys
from pathlib import Path

from scripts.init_daily_reports import init_daily_reports


STOCKS = [
    {"name": "炼石航空", "code": "000697.XSHE"},
    {"name": "甘肃能源", "code": "000791.XSHE"},
]


def test_init_daily_reports_creates_expected_structure(tmp_path):
    summary = init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    assert (tmp_path / "companies" / "000697.XSHE-炼石航空.md").exists()
    assert (tmp_path / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md").exists()
    assert (tmp_path / "stock" / "2026-05-10" / "index.md").exists()
    assert (tmp_path / "stock" / "2026-05-10" / "股票池排序.md").exists()
    assert (tmp_path / "stock" / "2026-05-10" / "主题行业综述.md").exists()
    assert (tmp_path / "stock" / "2026-05-10" / "研究日志.md").exists()
    assert (tmp_path / "stock" / "2026-05-10" / "data").is_dir()
    assert summary["created"]


def test_init_daily_reports_keeps_existing_files_and_reports_skipped(tmp_path):
    company = tmp_path / "companies" / "000697.XSHE-炼石航空.md"
    daily = tmp_path / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md"
    company.parent.mkdir(parents=True)
    daily.parent.mkdir(parents=True)
    company.write_text("用户内容", encoding="utf-8")
    daily.write_text("用户日评", encoding="utf-8")

    summary = init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    assert company.read_text(encoding="utf-8") == "用户内容"
    assert daily.read_text(encoding="utf-8") == "用户日评"
    assert {"name": "炼石航空", "code": "000697.XSHE", "files": ["company", "daily"]} in summary["skipped"]


def test_daily_report_template_replaces_core_variables_and_has_sections(tmp_path):
    init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    content = (tmp_path / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md").read_text(encoding="utf-8")

    assert "炼石航空" in content
    assert "000697.XSHE" in content
    assert "2026-05-10" in content
    assert "[[000697.XSHE-炼石航空]]" in content
    assert "{{stock_name}}" not in content
    assert "## 投研结论摘要" in content
    assert "## 建议写入公司档案的信息" in content
    assert "不构成具体买卖价位、止盈止损或仓位建议" in content


def test_index_contains_stock_and_daily_document_links(tmp_path):
    init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    content = (tmp_path / "stock" / "2026-05-10" / "index.md").read_text(encoding="utf-8")

    assert "[[000697.XSHE-炼石航空-日评]]" in content
    assert "[[000791.XSHE-甘肃能源-日评]]" in content
    assert "[[股票池排序]]" in content
    assert "[[主题行业综述]]" in content
    assert "[[研究日志]]" in content


def test_init_daily_reports_cli_reads_json_and_outputs_summary(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "scripts.init_daily_reports", "--date", "2026-05-10", "--root", str(tmp_path)],
        input=json.dumps([STOCKS[0]], ensure_ascii=False),
        text=True,
        capture_output=True,
        check=True,
    )

    summary = json.loads(result.stdout)
    assert summary["date"] == "2026-05-10"
    assert summary["created"]
    assert summary["skipped"] == []
