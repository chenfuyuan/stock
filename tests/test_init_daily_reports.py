import json
import subprocess
import sys
from pathlib import Path

from scripts.init_daily_reports import init_daily_reports
from scripts.templates import render_template


STOCKS = [
    {"name": "炼石航空", "code": "000697.XSHE"},
    {"name": "甘肃能源", "code": "000791.XSHE"},
]


def test_init_daily_reports_creates_expected_structure(tmp_path):
    summary = init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    assert (tmp_path / "vault" / "index.md").exists()
    assert "[[市场复盘与行情摘要]]" in (tmp_path / "vault" / "index.md").read_text(encoding="utf-8")
    assert "data/runs/YYYY-MM-DD/<symbol>/" in (tmp_path / "vault" / "index.md").read_text(encoding="utf-8")
    assert (tmp_path / "vault" / "knowledge" / "index.md").exists()
    assert (tmp_path / "vault" / "knowledge" / "themes" / "index.md").exists()
    assert (tmp_path / "vault" / "knowledge" / "events" / "index.md").exists()
    assert (tmp_path / "vault" / "knowledge" / "industries" / "index.md").exists()
    assert (tmp_path / "vault" / "knowledge" / "catalysts" / "index.md").exists()
    assert (tmp_path / "vault" / "knowledge" / "industries").is_dir()
    assert (tmp_path / "vault" / "knowledge" / "catalysts").is_dir()
    assert (tmp_path / "vault" / "knowledge" / "evidence" / "index.md").exists()
    assert (tmp_path / "vault" / "knowledge" / "reviews" / "index.md").exists()
    assert (tmp_path / "vault" / "companies" / "000697.XSHE-炼石航空.md").exists()
    assert (tmp_path / "vault" / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md").exists()
    assert (tmp_path / "vault" / "stock" / "2026-05-10" / "index.md").exists()
    assert (tmp_path / "vault" / "stock" / "2026-05-10" / "股票池排序.md").exists()
    assert (tmp_path / "vault" / "stock" / "2026-05-10" / "主题行业综述.md").exists()
    assert (tmp_path / "vault" / "stock" / "2026-05-10" / "研究日志.md").exists()
    assert not (tmp_path / "vault" / "stock" / "2026-05-10" / "data").exists()
    assert summary["created"]


def test_init_daily_reports_keeps_existing_files_and_reports_skipped(tmp_path):
    existing_files = {
        tmp_path / "vault" / "index.md": "用户全库入口",
        tmp_path / "vault" / "knowledge" / "index.md": "用户知识库入口",
        tmp_path / "vault" / "knowledge" / "themes" / "index.md": "用户主题入口",
        tmp_path / "vault" / "companies" / "000697.XSHE-炼石航空.md": "用户内容",
        tmp_path / "vault" / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md": "用户日评",
        tmp_path / "vault" / "stock" / "2026-05-10" / "index.md": "用户每日入口",
        tmp_path / "vault" / "stock" / "2026-05-10" / "研究日志.md": "用户研究日志",
    }
    for path, content in existing_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    summary = init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    for path, content in existing_files.items():
        assert path.read_text(encoding="utf-8") == content
    assert {"name": "炼石航空", "code": "000697.XSHE", "files": ["company", "daily"]} in summary["skipped"]


def test_company_profile_links_long_term_tracking_entries(tmp_path):
    init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    content = (tmp_path / "vault" / "companies" / "000697.XSHE-炼石航空.md").read_text(encoding="utf-8")

    assert "## 长期跟踪要点" in content
    assert "[[主题研究入口]]" in content
    assert "[[事件跟踪入口]]" in content
    assert "[[复盘入口]]" in content


def test_existing_knowledge_index_is_safely_appended_once(tmp_path):
    path = tmp_path / "vault" / "knowledge" / "index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntags:\n  - stock/knowledge-index\n---\n\n# 知识库入口\n\n## 长期沉淀层\n\n- [[主题研究入口]]\n- [[事件跟踪入口]]\n", encoding="utf-8")

    first_summary = init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)
    second_summary = init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)
    content = path.read_text(encoding="utf-8")

    assert content.count("[[行业研究入口]]") == 1
    assert content.count("[[催化研究入口]]") == 1
    assert any(item["file"] == "knowledge/index.md" and "appended" in item for item in first_summary["skipped"])
    assert not any(item.get("file") == "knowledge/index.md" and item.get("appended") for item in second_summary["skipped"])


def test_existing_knowledge_index_reports_when_append_point_is_missing(tmp_path):
    path = tmp_path / "vault" / "knowledge" / "index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("用户知识库入口", encoding="utf-8")

    summary = init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    assert path.read_text(encoding="utf-8") == "用户知识库入口"
    assert {"file": "knowledge/index.md", "append_skipped": ["[[行业研究入口]]", "[[催化研究入口]]"]} in summary["skipped"]


def test_industry_and_catalyst_node_templates_have_required_fields():
    templates = [
        (Path("templates/industry_node.md"), "stock/industry", "行业逻辑"),
        (Path("templates/catalyst_node.md"), "stock/catalyst", "关键催化"),
    ]

    for path, tag, driver_section in templates:
        content = render_template(path.read_text(encoding="utf-8"), {"node_name": "低空经济"})
        assert content.startswith("---\ntags:")
        assert tag in content
        assert "# 低空经济" in content
        for section in ["核心结论", "相关股票", driver_section, "风险因素", "更新记录", "来源清单"]:
            assert f"## {section}" in content
        for field in ["来源", "发布日期或检索时间", "数据日期", "证据说明", "相关日评"]:
            assert field in content


def test_init_daily_reports_can_create_and_preserve_industry_and_catalyst_nodes(tmp_path):
    existing = tmp_path / "vault" / "knowledge" / "industries" / "低空经济.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("用户行业研究结论", encoding="utf-8")

    summary = init_daily_reports(
        [STOCKS[0]],
        "2026-05-10",
        tmp_path,
        industry_nodes=["低空经济", "航空制造"],
        catalyst_nodes=["低空经济政策"],
    )

    assert existing.read_text(encoding="utf-8") == "用户行业研究结论"
    assert (tmp_path / "vault" / "knowledge" / "industries" / "航空制造.md").exists()
    catalyst_content = (tmp_path / "vault" / "knowledge" / "catalysts" / "低空经济政策.md").read_text(encoding="utf-8")
    assert "# 低空经济政策" in catalyst_content
    assert "## 更新记录" in catalyst_content
    assert "## 来源清单" in catalyst_content
    assert str(Path("vault/knowledge/industries/航空制造.md")) in summary["created"]
    assert {"file": "vault/knowledge/industries/低空经济.md"} in summary["skipped"]


def test_daily_report_template_replaces_core_variables_and_has_sections(tmp_path):
    init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    content = (tmp_path / "vault" / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md").read_text(encoding="utf-8")

    assert "炼石航空" in content
    assert "000697.XSHE" in content
    assert "2026-05-10" in content
    assert "[[000697.XSHE-炼石航空]]" in content
    assert "[[行业研究入口]]" in content
    assert "[[催化研究入口]]" in content
    assert "{{stock_name}}" not in content
    assert "{{stock_code}}" not in content
    assert "{{date}}" not in content
    assert "{{comparison_scope}}" not in content
    assert "{{industry_catalyst_links}}" not in content
    assert "## 投研结论摘要" in content
    assert "## 行业/催化横向比较" in content
    assert "## 数据依据" in content
    assert "data/runs/2026-05-10/000697.XSHE/" in content
    assert "## 建议写入公司档案的信息" in content
    assert "[[证据库入口]]" in content
    assert "[[复盘入口]]" in content
    assert "## 后续验证点" in content
    assert "不构成具体买卖价位、止盈止损或仓位建议" in content


def test_long_term_entry_templates_have_obsidian_metadata_and_purpose(tmp_path):
    init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    entries = [
        ("knowledge/index.md", "# 知识库入口", "[[主题研究入口]]"),
        ("knowledge/themes/index.md", "# 主题研究入口", "## 可追加材料"),
        ("knowledge/events/index.md", "# 事件跟踪入口", "## 可追加材料"),
        ("knowledge/industries/index.md", "# 行业研究入口", "## 行业索引"),
        ("knowledge/catalysts/index.md", "# 催化研究入口", "## 催化索引"),
        ("knowledge/evidence/index.md", "# 证据库入口", "## 记录字段"),
        ("knowledge/reviews/index.md", "# 复盘入口", "## 验证结果"),
    ]
    for relative_path, title, purpose in entries:
        content = (tmp_path / "vault" / relative_path).read_text(encoding="utf-8")
        assert content.startswith("---\ntags:")
        assert title in content
        assert purpose in content


def test_research_log_template_tracks_follow_up_questions(tmp_path):
    init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    content = (tmp_path / "vault" / "stock" / "2026-05-10" / "研究日志.md").read_text(encoding="utf-8")

    assert "## 当日验证点汇总" in content
    assert "## 后续观察事项" in content
    assert "[[复盘入口]]" in content


def test_index_contains_stock_and_daily_document_links(tmp_path):
    init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    content = (tmp_path / "vault" / "stock" / "2026-05-10" / "index.md").read_text(encoding="utf-8")

    assert "[[000697.XSHE-炼石航空-日评]]" in content
    assert "[[000791.XSHE-甘肃能源-日评]]" in content
    assert "[[股票池排序]]" in content
    assert "[[主题行业综述]]" in content
    assert "[[研究日志]]" in content
    assert "[[知识库入口]]" in content


def test_generated_wikilinks_do_not_carry_path_prefix(tmp_path):
    init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    files = [
        tmp_path / "vault" / "index.md",
        tmp_path / "vault" / "knowledge" / "index.md",
        tmp_path / "vault" / "stock" / "2026-05-10" / "index.md",
        tmp_path / "vault" / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md",
        tmp_path / "vault" / "companies" / "000697.XSHE-炼石航空.md",
    ]
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert "[[vault/" not in content
        assert "[[stock/" not in content
        assert "[[companies/" not in content
        assert "[[knowledge/" not in content


def test_generated_templates_do_not_include_trading_advice_fields(tmp_path):
    init_daily_reports(STOCKS, "2026-05-10", tmp_path)

    files = [
        tmp_path / "vault" / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md",
        tmp_path / "vault" / "companies" / "000697.XSHE-炼石航空.md",
        tmp_path / "vault" / "knowledge" / "index.md",
        tmp_path / "vault" / "knowledge" / "industries" / "index.md",
        tmp_path / "vault" / "knowledge" / "catalysts" / "index.md",
        tmp_path / "vault" / "knowledge" / "reviews" / "index.md",
    ]
    forbidden = ["评分：", "排名：", "买入价：", "卖出价：", "买入价格：", "卖出价格：", "止盈：", "止损：", "止盈价：", "止损价：", "仓位建议："]
    for path in files:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in content


def test_daily_report_cross_comparison_and_deposition_fields(tmp_path):
    init_daily_reports([STOCKS[0]], "2026-05-10", tmp_path)

    content = (tmp_path / "vault" / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md").read_text(encoding="utf-8")

    assert content.index("## 行业与政策") < content.index("## 行业/催化横向比较") < content.index("## 竞争格局")
    for field in ["比较口径", "关联节点", "对比对象", "共同驱动", "共同催化说明", "行业逻辑说明", "相对差异", "共同风险", "证据来源"]:
        assert field in content
    assert "建议写入行业/催化节点的信息" in content
    assert "当日证据" in content
    assert "长期复用证据" in content


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
