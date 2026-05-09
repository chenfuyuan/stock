# A-Share Deep Research Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first iteration of a Claude Code-driven A-share daily research workflow: deterministic Python helper scripts (parsing, scaffolding, Tushare/akshare data fetching), Obsidian-friendly markdown templates, and a `stock-analysis` skill that orchestrates the end-to-end flow.

**Architecture:** Three layers. (1) `scripts/` runs all deterministic work — parsing pasted stock pools, creating dated directories, fetching structured data from Tushare with akshare as fallback. (2) `templates/` holds static markdown templates (frontmatter + section skeletons) so every Obsidian note has the same shape. (3) `.claude/skills/stock-analysis/SKILL.md` is the workflow Claude executes: parse → init → fetch → web search → write per-stock reports → write three daily summaries → check quality gates.

**Tech Stack:** Python 3.10+, `tushare`, `akshare`, `python-dotenv`, `pytest` (dev), Markdown templates with YAML frontmatter. No web framework, no MCP, no multi-agent orchestration in v1.

**Spec source:** `docs/superpowers/specs/2026-05-09-stock-analysis-workflow-design.md`

---

## File Structure

Files this plan creates or modifies:

```text
pyproject.toml                              [create] Python project + deps
.env.example                                [create] Tushare token template
.gitignore                                  [modify] add tests caches if missing
companies/.gitkeep                          [create] long-term archive root
stock/.gitkeep                              [create] daily output root

scripts/__init__.py                         [create] package marker
scripts/config.py                           [create] load TUSHARE_TOKEN
scripts/parse_stock_list.py                 [create] parse pasted pool, code conversion
scripts/utils.py                            [create] template rendering helper
scripts/init_daily_reports.py               [create] scaffold dated dirs + files
scripts/fetch_stock_data.py                 [create] orchestrate fetchers, write JSON
scripts/fetchers/__init__.py                [create] package marker
scripts/fetchers/tushare_fetcher.py         [create] Tushare client wrapper
scripts/fetchers/akshare_fetcher.py         [create] akshare wrapper

templates/company_archive.md                [create] long-term company archive
templates/stock_report.md                   [create] per-stock daily report
templates/daily_index.md                    [create] daily MOC
templates/pool_ranking.md                   [create] daily pool ranking
templates/theme_industry.md                 [create] daily theme/industry
templates/research_log.md                   [create] daily research log

tests/__init__.py                           [create] package marker
tests/test_config.py                        [create]
tests/test_parse_stock_list.py              [create]
tests/test_utils.py                         [create]
tests/test_init_daily_reports.py            [create]
tests/fetchers/__init__.py                  [create]
tests/fetchers/test_tushare_fetcher.py      [create]
tests/fetchers/test_akshare_fetcher.py      [create]
tests/test_fetch_stock_data.py              [create]

.claude/skills/stock-analysis/SKILL.md      [create] workflow skill
```

**Decomposition rationale:** Each script has one responsibility. Fetchers are split per data source so Tushare and akshare can evolve independently and one failing doesn't break the other. Templates are split per document type so Claude can render any one of them in isolation. Tests live next to the structure they cover.

---

## Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Modify: `.gitignore`
- Create: `scripts/__init__.py`, `scripts/fetchers/__init__.py`
- Create: `tests/__init__.py`, `tests/fetchers/__init__.py`
- Create: `companies/.gitkeep`, `stock/.gitkeep`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "stock-research"
version = "0.1.0"
description = "A-share deep research workflow for Obsidian"
requires-python = ">=3.10"
dependencies = [
    "tushare>=1.4.0",
    "akshare>=1.13.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
pythonpath = ["."]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["scripts*"]
```

- [ ] **Step 2: Create `.env.example`**

```text
# Copy to .env and fill in. .env is gitignored.
TUSHARE_TOKEN=your_tushare_token_here
```

- [ ] **Step 3: Verify `.gitignore` excludes the right things**

The existing `.gitignore` already excludes `.env`, `.env.*`, `.claude/settings.local.json`, `__pycache__/`, `*.py[cod]`, `.DS_Store`. Append pytest cache and editor leftovers if missing:

```text
.pytest_cache/
.coverage
*.egg-info/
build/
dist/
```

- [ ] **Step 4: Create empty package and placeholder files**

Create empty files:
- `scripts/__init__.py` (empty)
- `scripts/fetchers/__init__.py` (empty)
- `tests/__init__.py` (empty)
- `tests/fetchers/__init__.py` (empty)
- `companies/.gitkeep` (empty)
- `stock/.gitkeep` (empty)

- [ ] **Step 5: Install deps and verify pytest runs**

Run:
```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
pytest --version
```
Expected: pytest version printed without error. The venv path is gitignored via the existing `.env*` rule? No — add `.venv/` to `.gitignore` if not present.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .env.example .gitignore scripts/ tests/ companies/ stock/
git commit -m "chore: scaffold stock-research project"
```

---

## Task 2: Config loader (TDD)

**Files:**
- Test: `tests/test_config.py`
- Create: `scripts/config.py`

Loads the Tushare token from (1) a `.env` file in the project root, then (2) the `TUSHARE_TOKEN` environment variable. Returns `None` if neither is set — callers decide whether that is fatal. Token must never leak into logs or written reports.

- [ ] **Step 1: Write the failing test**

Create `tests/test_config.py`:
```python
from pathlib import Path

import pytest

from scripts import config


def test_load_tushare_token_from_env_var(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TUSHARE_TOKEN", "from-env-var")
    assert config.load_tushare_token() == "from-env-var"


def test_load_tushare_token_from_dotenv(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    (tmp_path / ".env").write_text("TUSHARE_TOKEN=from-dotenv\n", encoding="utf-8")
    assert config.load_tushare_token() == "from-dotenv"


def test_dotenv_overrides_env_var_when_explicit(monkeypatch, tmp_path):
    # .env should win when both are set, so that switching local config
    # without unsetting a stale shell var still works.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TUSHARE_TOKEN", "from-env-var")
    (tmp_path / ".env").write_text("TUSHARE_TOKEN=from-dotenv\n", encoding="utf-8")
    assert config.load_tushare_token() == "from-dotenv"


def test_returns_none_when_missing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    assert config.load_tushare_token() is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError` for `scripts.config` or similar.

- [ ] **Step 3: Implement `scripts/config.py`**

```python
"""Local config loader. Reads Tushare token from .env then env var."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


def project_root() -> Path:
    return Path.cwd()


def load_tushare_token() -> str | None:
    """Return the Tushare token or None.

    Resolution order: project-root .env (wins if set), then TUSHARE_TOKEN env var.
    Never log or print the token.
    """
    env_file = project_root() / ".env"
    if env_file.exists():
        values = dotenv_values(env_file)
        token = values.get("TUSHARE_TOKEN")
        if token:
            return token
    return os.environ.get("TUSHARE_TOKEN")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/config.py tests/test_config.py
git commit -m "feat(config): load Tushare token from .env or env var"
```

---

## Task 3: Stock list parser and code conversion (TDD)

**Files:**
- Test: `tests/test_parse_stock_list.py`
- Create: `scripts/parse_stock_list.py`

Parses the pasted stock pool (multi-line free text) into a list of `{name, code}` dicts. Normalizes the exchange suffix to the spec form (`.XSHE` / `.XSHG` / `.XBSE`). Provides a converter to Tushare's suffix form (`.SZ` / `.SH` / `.BJ`). Also exposes a CLI: read text from stdin, print JSON to stdout.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_parse_stock_list.py`:
```python
import json
import subprocess
import sys

import pytest

from scripts.parse_stock_list import (
    normalize_code,
    parse_stock_list,
    to_tushare_code,
)


class TestNormalizeCode:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("000697.XSHE", "000697.XSHE"),
            ("000697.xshe", "000697.XSHE"),
            ("000697.SZ", "000697.XSHE"),
            ("600000.SH", "600000.XSHG"),
            ("600000.XSHG", "600000.XSHG"),
            ("430489.BJ", "430489.XBSE"),
            ("430489.XBSE", "430489.XBSE"),
        ],
    )
    def test_normalizes_to_spec_suffix(self, raw, expected):
        assert normalize_code(raw) == expected


class TestToTushareCode:
    @pytest.mark.parametrize(
        "spec_code,tushare_code",
        [
            ("000697.XSHE", "000697.SZ"),
            ("600000.XSHG", "600000.SH"),
            ("430489.XBSE", "430489.BJ"),
        ],
    )
    def test_converts_for_tushare(self, spec_code, tushare_code):
        assert to_tushare_code(spec_code) == tushare_code


class TestParseStockList:
    def test_numbered_list_with_parens(self):
        text = """
        1. 炼石航空(000697.XSHE)
        2. 甘肃能源(000791.XSHE)
        3. 云南锗业(002428.XSHE)
        """
        assert parse_stock_list(text) == [
            {"name": "炼石航空", "code": "000697.XSHE"},
            {"name": "甘肃能源", "code": "000791.XSHE"},
            {"name": "云南锗业", "code": "002428.XSHE"},
        ]

    def test_space_separated(self):
        text = "炼石航空 000697.XSHE\n甘肃能源 000791.XSHE\n"
        assert parse_stock_list(text) == [
            {"name": "炼石航空", "code": "000697.XSHE"},
            {"name": "甘肃能源", "code": "000791.XSHE"},
        ]

    def test_code_only_line(self):
        assert parse_stock_list("000697.XSHE\n") == [
            {"name": "", "code": "000697.XSHE"}
        ]

    def test_normalizes_tushare_suffix_input(self):
        assert parse_stock_list("浦发银行 600000.SH\n") == [
            {"name": "浦发银行", "code": "600000.XSHG"}
        ]

    def test_dedupes_by_code(self):
        text = "炼石航空(000697.XSHE)\n炼石航空 000697.SZ\n"
        assert parse_stock_list(text) == [
            {"name": "炼石航空", "code": "000697.XSHE"}
        ]

    def test_skips_lines_without_a_code(self):
        text = "标题: 今日股票池\n炼石航空(000697.XSHE)\n# 注释\n"
        assert parse_stock_list(text) == [
            {"name": "炼石航空", "code": "000697.XSHE"}
        ]

    def test_empty_input(self):
        assert parse_stock_list("") == []


class TestCli:
    def test_cli_reads_stdin_writes_json(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "scripts.parse_stock_list"],
            input="炼石航空(000697.XSHE)\n甘肃能源(000791.XSHE)\n",
            capture_output=True,
            text=True,
            check=True,
        )
        assert json.loads(result.stdout) == [
            {"name": "炼石航空", "code": "000697.XSHE"},
            {"name": "甘肃能源", "code": "000791.XSHE"},
        ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_parse_stock_list.py -v`
Expected: FAIL with `ModuleNotFoundError` for `scripts.parse_stock_list`.

- [ ] **Step 3: Implement `scripts/parse_stock_list.py`**

```python
"""Parse pasted A-share stock pools into structured records."""
from __future__ import annotations

import json
import re
import sys

# Matches a 6-digit code with one of the recognized exchange suffixes.
_CODE_RE = re.compile(
    r"(?P<digits>\d{6})\.(?P<suffix>XSHE|XSHG|XBSE|SZ|SH|BJ)",
    re.IGNORECASE,
)
# CJK run, allowing internal middle dot (·) and ASCII letters/digits seen in tickers.
_NAME_RE = re.compile(r"[一-鿿][一-鿿\w·]*")

_SPEC_SUFFIX = {
    "XSHE": "XSHE",
    "XSHG": "XSHG",
    "XBSE": "XBSE",
    "SZ": "XSHE",
    "SH": "XSHG",
    "BJ": "XBSE",
}

_TUSHARE_SUFFIX = {
    "XSHE": "SZ",
    "XSHG": "SH",
    "XBSE": "BJ",
}


def normalize_code(code: str) -> str:
    """Normalize an A-share code to the spec form (.XSHE / .XSHG / .XBSE)."""
    match = _CODE_RE.fullmatch(code.strip())
    if not match:
        raise ValueError(f"not an A-share code: {code!r}")
    return f"{match.group('digits')}.{_SPEC_SUFFIX[match.group('suffix').upper()]}"


def to_tushare_code(spec_code: str) -> str:
    """Convert a spec code (.XSHE etc.) to Tushare's suffix (.SZ etc.)."""
    digits, _, suffix = spec_code.partition(".")
    if suffix not in _TUSHARE_SUFFIX:
        raise ValueError(f"not a normalized spec code: {spec_code!r}")
    return f"{digits}.{_TUSHARE_SUFFIX[suffix]}"


def parse_stock_list(text: str) -> list[dict]:
    """Parse pasted stock-pool text into a deduplicated list of {name, code}."""
    out: list[dict] = []
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        code_match = _CODE_RE.search(line)
        if not code_match:
            continue
        code = f"{code_match.group('digits')}.{_SPEC_SUFFIX[code_match.group('suffix').upper()]}"
        if code in seen:
            continue
        seen.add(code)
        before = line[: code_match.start()]
        after = line[code_match.end():]
        name_match = _NAME_RE.search(before) or _NAME_RE.search(after)
        name = name_match.group(0) if name_match else ""
        out.append({"name": name, "code": code})
    return out


def main() -> None:
    text = sys.stdin.read()
    json.dump(parse_stock_list(text), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_parse_stock_list.py -v`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/parse_stock_list.py tests/test_parse_stock_list.py
git commit -m "feat(parser): parse stock pool input and convert codes"
```

---

## Task 4: Template — company long-term archive

**Files:**
- Create: `templates/company_archive.md`

Static template; no code, no test. Variables: `{{stock_code}}`, `{{stock_name}}`, `{{date}}`. Frontmatter is YAML; tags use Obsidian style. The `相关日评` section uses a wikilink to today's report, and the daily report will backlink to this archive — that two-way link is what makes Obsidian backlinks light up.

- [ ] **Step 1: Create the template**

Write `templates/company_archive.md`:
```markdown
---
type: company-archive
stock_code: {{stock_code}}
stock_name: {{stock_name}}
created: {{date}}
last_updated: {{date}}
tags:
  - company-archive
  - {{stock_code}}
---

# {{stock_name}}（{{stock_code}}）公司长期档案

> 本档案只沉淀稳定、长期有效的信息。中短期信息放在每日日评，由用户确认后再回填这里。

## 主营业务

（待填写：业务条线、主要产品/服务、收入结构）

## 股权结构与治理

（待填写：实控人、主要股东、董事会与管理层、关联交易）

## 核心资产、项目、产能

（待填写：关键资产、在建项目、产能与利用率）

## 产业链位置

（待填写：上游供应、下游客户、议价能力、可比公司）

## 长期财务特征

（待填写：营收/利润长期趋势、毛利率区间、现金流特征、资本开支节奏、负债结构）

## 长期风险

（待填写：行业周期、监管、技术替代、客户/供应商集中、治理）

## 历史重大事项

（待填写：并购重组、定增、违规处罚、重大诉讼、关键管理层变动）

## 相关日评

- [[{{date}}/{{stock_code}}-{{stock_name}}-日评]]
```

- [ ] **Step 2: Commit**

```bash
git add templates/company_archive.md
git commit -m "feat(templates): add company long-term archive template"
```

---

## Task 5: Template — per-stock daily report

**Files:**
- Create: `templates/stock_report.md`

Long template — covers all 14 sections from the spec. Conclusions first, sources at the end. Frontmatter holds `attention_level` so the daily ranking can pick it up by reading frontmatter only. The wikilink to the company archive is required so backlinks work.

- [ ] **Step 1: Create the template**

Write `templates/stock_report.md`:
```markdown
---
type: stock-daily-report
date: {{date}}
stock_code: {{stock_code}}
stock_name: {{stock_name}}
attention_level:
tags:
  - stock-analysis
  - {{date}}
  - {{stock_code}}
related_company: "[[{{stock_code}}-{{stock_name}}]]"
---

# {{stock_name}}（{{stock_code}}） {{date}} 日评

> 报告仅为研究观点，不构成具体买卖价位、止盈止损或仓位建议。
> 关联公司档案：[[{{stock_code}}-{{stock_name}}]]

## 1. 投研结论摘要

（一句话核心结论 + 简明判断；至多 3 行）

## 2. 关注等级

- 等级：（1 重点关注 / 2 积极关注 / 3 谨慎关注 / 4 观察跟踪 / 5 暂不关注）
- 一句话说明为何选择该等级

## 3. 核心逻辑

- 关键支持因素 1（来源 / 数据日期）
- 关键支持因素 2（来源 / 数据日期）
- 关键支持因素 3（来源 / 数据日期）

## 4. 最大风险

- 风险点 1（来源 / 数据日期）
- 风险点 2（来源 / 数据日期）
- 风险点 3（来源 / 数据日期）

## 5. 需要继续跟踪的变量

- 跟踪变量 1（信号 / 阈值 / 数据来源）
- 跟踪变量 2

## 6. 公司与业务概况

- 主营业务、主要产品 / 服务
- 客户结构、收入构成
- 产业链位置与议价能力

## 7. 行业与政策背景

- 当前行业景气度（数据日期：YYYY-MM-DD）
- 主要政策与监管动向
- 竞争格局

## 8. 财务与经营质量

- 营收、净利润、毛利率（数据日期 / 来源）
- 经营性现金流
- 资产负债与杠杆
- 关键经营指标（应收周转、存货周转、ROE 等）

## 9. 估值与同业比较

- PE / PB / 股息率（数据日期）
- 与可比公司对比
- 估值结论（不给出具体买卖价位）

## 10. 技术面与资金情绪

- 近期股价走势
- 量价配合
- 北向资金 / 主力资金（如有，注明数据日期）
- 龙虎榜（如有）

## 11. 最新公告、新闻与事件催化

- 公告 1（日期 / 来源）
- 新闻 1（日期 / 来源）
- 待跟踪催化（含潜在时间窗口）

## 12. 信息来源与可信度分级

### A 级（公司公告、交易所、巨潮、监管 / 政府、定期报告）

- 

### B 级（公司官网、IR、主流财经媒体、Tushare、akshare）

- 

### C 级（财经门户二次报道、互动平台、社区讨论、市场传闻）

- 

## 13. 无法确认或证据不足事项

- 

## 14. 建议写入公司档案的信息

> 仅列出长期稳定、来源 A/B 级的信息。用户确认后再回填到 `companies/{{stock_code}}-{{stock_name}}.md`。

- 
```

- [ ] **Step 2: Commit**

```bash
git add templates/stock_report.md
git commit -m "feat(templates): add per-stock daily report template"
```

---

## Task 6: Templates — daily index, pool ranking, theme/industry, research log

**Files:**
- Create: `templates/daily_index.md`
- Create: `templates/pool_ranking.md`
- Create: `templates/theme_industry.md`
- Create: `templates/research_log.md`

The daily index is the MOC (map of content). The other three are summary documents. All four use `{{date}}` and the index also uses `{{stock_pool_links}}` (multi-line markdown).

- [ ] **Step 1: Create `templates/daily_index.md`**

```markdown
---
type: daily-index
date: {{date}}
tags:
  - daily-index
  - {{date}}
---

# {{date}} 股票池研究入口

## 当日股票池

{{stock_pool_links}}

## 综合文档

- [[当日股票池排序]]
- [[当日主题与行业综述]]
- [[当日研究日志]]

## 共同主题与行业标签

（待填写）

## 今日核心结论

（待填写：3-5 条）

## 后续待跟踪

（待填写）
```

- [ ] **Step 2: Create `templates/pool_ranking.md`**

```markdown
---
type: pool-ranking
date: {{date}}
tags:
  - pool-ranking
  - {{date}}
---

# {{date}} 当日股票池排序

## 排序汇总

| 排名 | 股票 | 关注等级 | 一句话核心理由 | 主要风险 |
|------|------|----------|----------------|----------|
|      |      |          |                |          |

## 排序逻辑说明

（说明本次排序的依据：基本面权重、催化预期、估值、风险偏好等）

## 重点关注与积极关注

（链接到对应日评，简述核心理由与边界条件）

## 谨慎关注 / 观察跟踪 / 暂不关注

（说明判断依据与转向条件）
```

- [ ] **Step 3: Create `templates/theme_industry.md`**

```markdown
---
type: theme-industry
date: {{date}}
tags:
  - theme-industry
  - {{date}}
---

# {{date}} 主题与行业综述

## 共同主题

（识别股票池背后的共同投资主题）

## 涉及行业链条

（上下游、横向竞争、关联板块）

## 政策与监管催化

（最新政策、监管文件、行业指导意见，注明日期与来源）

## 市场叙事与情绪

（近期市场对该主题的叙事和情绪倾向，注明信息来源等级）

## 行业层面的风险

（与个股层面区分开的、行业共同面对的风险）
```

- [ ] **Step 4: Create `templates/research_log.md`**

```markdown
---
type: research-log
date: {{date}}
tags:
  - research-log
  - {{date}}
---

# {{date}} 研究日志

## 检索来源汇总

- A 级：
- B 级：
- C 级：

## 数据可用性与限制

- Tushare：
- akshare：
- 其他来源：

## 无法确认事项

- 

## 后续跟踪问题

- 

## 流程异常与改进建议

- 
```

- [ ] **Step 5: Commit**

```bash
git add templates/daily_index.md templates/pool_ranking.md templates/theme_industry.md templates/research_log.md
git commit -m "feat(templates): add daily index, ranking, theme, and log templates"
```

---

## Task 7: Template rendering helper (TDD)

**Files:**
- Test: `tests/test_utils.py`
- Create: `scripts/utils.py`

Tiny `{{var}}` substituter — no Jinja dependency. Reads from the project's `templates/` directory by default. Raises if a placeholder remains unfilled, but only for placeholders the caller asked to substitute (so the template can keep `{{待填写}}`-style human placeholders if any). Behavior: literal `str.replace` over `(key, value)` pairs from the context dict.

- [ ] **Step 1: Write the failing test**

Create `tests/test_utils.py`:
```python
from pathlib import Path

import pytest

from scripts import utils


def test_render_template_substitutes_variables(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "hello.md").write_text(
        "# Hi {{name}}, code {{code}}\nbody {{name}}\n",
        encoding="utf-8",
    )
    out = utils.render_template(
        "hello.md",
        {"name": "炼石航空", "code": "000697.XSHE"},
        template_dir=template_dir,
    )
    assert out == "# Hi 炼石航空, code 000697.XSHE\nbody 炼石航空\n"


def test_render_template_leaves_unknown_placeholders_alone(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "x.md").write_text("{{a}} and {{b}}\n", encoding="utf-8")
    out = utils.render_template("x.md", {"a": "1"}, template_dir=template_dir)
    assert out == "1 and {{b}}\n"


def test_render_template_default_dir(monkeypatch, tmp_path):
    project = tmp_path / "proj"
    (project / "templates").mkdir(parents=True)
    (project / "templates" / "t.md").write_text("hi {{x}}\n", encoding="utf-8")
    monkeypatch.chdir(project)
    assert utils.render_template("t.md", {"x": "y"}) == "hi y\n"


def test_render_template_missing_file(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        utils.render_template("no.md", {}, template_dir=template_dir)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_utils.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `scripts/utils.py`**

```python
"""Shared helpers for the stock-research scripts."""
from __future__ import annotations

from pathlib import Path
from typing import Mapping


def render_template(
    name: str,
    context: Mapping[str, str],
    template_dir: Path | None = None,
) -> str:
    """Render `templates/{name}` by literal `{{key}}` substitution.

    Unknown placeholders are left as-is so templates can keep human-facing
    placeholders that the engineer is meant to fill in later.
    """
    if template_dir is None:
        template_dir = Path.cwd() / "templates"
    text = (template_dir / name).read_text(encoding="utf-8")
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    return text
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_utils.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/utils.py tests/test_utils.py
git commit -m "feat(utils): add template rendering helper"
```

---

## Task 8: Daily reports initializer (TDD)

**Files:**
- Test: `tests/test_init_daily_reports.py`
- Create: `scripts/init_daily_reports.py`

Given a date (default: today) and a list of stocks, create:
- `companies/<code>-<name>.md` (only if missing)
- `stock/<date>/<code>-<name>-日评.md`
- `stock/<date>/index.md`
- `stock/<date>/当日股票池排序.md`
- `stock/<date>/当日主题与行业综述.md`
- `stock/<date>/当日研究日志.md`
- `stock/<date>/data/` (empty, for fetch_stock_data output)

Idempotent: re-running with the same input must not overwrite existing per-stock or company files. The script returns a summary (created vs skipped). CLI: read the JSON list (from `parse_stock_list`) on stdin, optional `--date YYYY-MM-DD` flag.

- [ ] **Step 1: Write the failing test**

Create `tests/test_init_daily_reports.py`:
```python
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import init_daily_reports


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Create a project layout with the templates directory copied in."""
    repo_root = Path(__file__).resolve().parents[1]
    templates_src = repo_root / "templates"
    templates_dst = tmp_path / "templates"
    templates_dst.mkdir()
    for f in templates_src.iterdir():
        if f.is_file():
            (templates_dst / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_creates_full_layout(project):
    stocks = [
        {"name": "炼石航空", "code": "000697.XSHE"},
        {"name": "甘肃能源", "code": "000791.XSHE"},
    ]
    result = init_daily_reports.init(stocks, date="2026-05-10")

    assert (project / "companies" / "000697.XSHE-炼石航空.md").exists()
    assert (project / "companies" / "000791.XSHE-甘肃能源.md").exists()

    daily = project / "stock" / "2026-05-10"
    assert (daily / "index.md").exists()
    assert (daily / "当日股票池排序.md").exists()
    assert (daily / "当日主题与行业综述.md").exists()
    assert (daily / "当日研究日志.md").exists()
    assert (daily / "000697.XSHE-炼石航空-日评.md").exists()
    assert (daily / "000791.XSHE-甘肃能源-日评.md").exists()
    assert (daily / "data").is_dir()

    assert set(result["created_companies"]) == {"000697.XSHE", "000791.XSHE"}
    assert set(result["created_reports"]) == {"000697.XSHE", "000791.XSHE"}


def test_substitutes_template_variables(project):
    init_daily_reports.init(
        [{"name": "炼石航空", "code": "000697.XSHE"}], date="2026-05-10"
    )
    report = (
        project / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md"
    ).read_text(encoding="utf-8")
    assert "炼石航空" in report
    assert "000697.XSHE" in report
    assert "2026-05-10" in report
    assert "{{stock_name}}" not in report
    assert "{{stock_code}}" not in report
    assert "{{date}}" not in report


def test_index_lists_all_stocks(project):
    init_daily_reports.init(
        [
            {"name": "炼石航空", "code": "000697.XSHE"},
            {"name": "甘肃能源", "code": "000791.XSHE"},
        ],
        date="2026-05-10",
    )
    index = (project / "stock" / "2026-05-10" / "index.md").read_text(encoding="utf-8")
    assert "[[000697.XSHE-炼石航空-日评]]" in index
    assert "[[000791.XSHE-甘肃能源-日评]]" in index


def test_idempotent_does_not_overwrite_existing(project):
    init_daily_reports.init(
        [{"name": "炼石航空", "code": "000697.XSHE"}], date="2026-05-10"
    )
    company_file = project / "companies" / "000697.XSHE-炼石航空.md"
    company_file.write_text("CUSTOM USER CONTENT", encoding="utf-8")
    report_file = (
        project / "stock" / "2026-05-10" / "000697.XSHE-炼石航空-日评.md"
    )
    report_file.write_text("REPORT IN PROGRESS", encoding="utf-8")

    result = init_daily_reports.init(
        [{"name": "炼石航空", "code": "000697.XSHE"}], date="2026-05-10"
    )

    assert company_file.read_text(encoding="utf-8") == "CUSTOM USER CONTENT"
    assert report_file.read_text(encoding="utf-8") == "REPORT IN PROGRESS"
    assert result["created_companies"] == []
    assert result["created_reports"] == []
    assert "000697.XSHE" in result["skipped_companies"]
    assert "000697.XSHE" in result["skipped_reports"]


def test_default_date_is_today(project, monkeypatch):
    import datetime as dt

    class FakeDate(dt.date):
        @classmethod
        def today(cls):
            return cls(2026, 5, 10)

    monkeypatch.setattr(init_daily_reports, "_date", FakeDate)
    init_daily_reports.init([{"name": "炼石航空", "code": "000697.XSHE"}])
    assert (project / "stock" / "2026-05-10").is_dir()


def test_cli_reads_stdin(project):
    payload = json.dumps([{"name": "炼石航空", "code": "000697.XSHE"}])
    result = subprocess.run(
        [sys.executable, "-m", "scripts.init_daily_reports", "--date", "2026-05-10"],
        input=payload,
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(result.stdout)
    assert out["date"] == "2026-05-10"
    assert (project / "stock" / "2026-05-10" / "index.md").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_init_daily_reports.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `scripts/init_daily_reports.py`**

```python
"""Initialize the daily directory layout and template files."""
from __future__ import annotations

import argparse
import datetime as _date_module
import json
import sys
from pathlib import Path
from typing import Iterable

from scripts.utils import render_template

# Indirection so tests can patch `init_daily_reports._date` without touching
# the stdlib module itself.
_date = _date_module.date


def _today_str() -> str:
    return _date.today().isoformat()


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _stock_pool_links(stocks: Iterable[dict]) -> str:
    return "\n".join(
        f"- [[{s['code']}-{s['name']}-日评]] —— 关注等级：（待填）"
        for s in stocks
    )


def init(stocks: list[dict], date: str | None = None) -> dict:
    """Create the dated layout and template files. Idempotent."""
    date = date or _today_str()
    project = Path.cwd()

    companies_dir = project / "companies"
    daily_dir = project / "stock" / date
    data_dir = daily_dir / "data"
    _ensure_dir(companies_dir)
    _ensure_dir(daily_dir)
    _ensure_dir(data_dir)

    created_companies: list[str] = []
    skipped_companies: list[str] = []
    created_reports: list[str] = []
    skipped_reports: list[str] = []

    for s in stocks:
        ctx = {"stock_name": s["name"], "stock_code": s["code"], "date": date}

        company_file = companies_dir / f"{s['code']}-{s['name']}.md"
        if _write_if_missing(company_file, render_template("company_archive.md", ctx)):
            created_companies.append(s["code"])
        else:
            skipped_companies.append(s["code"])

        report_file = daily_dir / f"{s['code']}-{s['name']}-日评.md"
        if _write_if_missing(report_file, render_template("stock_report.md", ctx)):
            created_reports.append(s["code"])
        else:
            skipped_reports.append(s["code"])

    pool_ctx = {"date": date, "stock_pool_links": _stock_pool_links(stocks)}
    _write_if_missing(daily_dir / "index.md", render_template("daily_index.md", pool_ctx))
    _write_if_missing(daily_dir / "当日股票池排序.md", render_template("pool_ranking.md", {"date": date}))
    _write_if_missing(daily_dir / "当日主题与行业综述.md", render_template("theme_industry.md", {"date": date}))
    _write_if_missing(daily_dir / "当日研究日志.md", render_template("research_log.md", {"date": date}))

    return {
        "date": date,
        "daily_dir": str(daily_dir),
        "created_companies": created_companies,
        "skipped_companies": skipped_companies,
        "created_reports": created_reports,
        "skipped_reports": skipped_reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize daily stock reports.")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to today")
    args = parser.parse_args()
    stocks = json.load(sys.stdin)
    result = init(stocks, date=args.date)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_init_daily_reports.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/init_daily_reports.py tests/test_init_daily_reports.py
git commit -m "feat(init): scaffold daily directory and template files"
```

---

## Task 9: Tushare fetcher (TDD with mocks)

**Files:**
- Test: `tests/fetchers/test_tushare_fetcher.py`
- Create: `scripts/fetchers/tushare_fetcher.py`

Wraps the Tushare pro client. Each fetch returns a small dict shaped for the eventual JSON output. Network is always mocked in tests. The fetcher accepts the spec code (e.g. `000697.XSHE`) and converts internally. If a single endpoint fails, log it as a missing field and continue — one bad endpoint must not lose the whole record.

Field set for v1 (kept modest, expand later):
- `basic`: from `pro.stock_basic` (name, area, industry, list_date)
- `recent_quotes`: last ~20 trading days from `pro.daily`
- `daily_basic`: most recent `pro.daily_basic` (PE, PB, turnover_rate, total_mv, circ_mv)
- `fina_indicator`: most recent `pro.fina_indicator` (gross_margin, netprofit_yoy, roe)

- [ ] **Step 1: Write the failing test**

Create `tests/fetchers/test_tushare_fetcher.py`:
```python
from unittest.mock import MagicMock

import pandas as pd
import pytest

from scripts.fetchers import tushare_fetcher


@pytest.fixture
def fake_pro():
    pro = MagicMock()
    pro.stock_basic.return_value = pd.DataFrame(
        [{"ts_code": "000697.SZ", "name": "炼石航空", "industry": "航空装备",
          "area": "陕西", "list_date": "19960827"}]
    )
    pro.daily.return_value = pd.DataFrame(
        [
            {"trade_date": "20260508", "open": 10.0, "high": 10.5, "low": 9.9,
             "close": 10.3, "vol": 12345.0, "amount": 12345678.0, "pct_chg": 1.2},
        ]
    )
    pro.daily_basic.return_value = pd.DataFrame(
        [{"trade_date": "20260508", "pe": 35.6, "pe_ttm": 30.1, "pb": 4.2,
          "turnover_rate": 5.8, "total_mv": 1.2e10, "circ_mv": 9.0e9}]
    )
    pro.fina_indicator.return_value = pd.DataFrame(
        [{"end_date": "20260331", "grossprofit_margin": 22.5,
          "netprofit_yoy": -8.4, "roe": 3.1}]
    )
    return pro


def test_fetch_returns_combined_record(fake_pro):
    record = tushare_fetcher.fetch("000697.XSHE", pro=fake_pro)
    assert record["code"] == "000697.XSHE"
    assert record["source"] == "tushare"
    assert record["data_date"]
    assert record["basic"]["name"] == "炼石航空"
    assert record["basic"]["industry"] == "航空装备"
    assert record["recent_quotes"][0]["close"] == 10.3
    assert record["daily_basic"]["pe_ttm"] == 30.1
    assert record["fina_indicator"]["roe"] == 3.1
    assert record["missing_fields"] == []


def test_fetch_uses_tushare_suffix(fake_pro):
    tushare_fetcher.fetch("000697.XSHE", pro=fake_pro)
    args, kwargs = fake_pro.stock_basic.call_args
    assert kwargs.get("ts_code") == "000697.SZ"


def test_fetch_records_missing_fields_when_endpoint_fails(fake_pro):
    fake_pro.fina_indicator.side_effect = RuntimeError("api timeout")
    record = tushare_fetcher.fetch("000697.XSHE", pro=fake_pro)
    assert record["fina_indicator"] is None
    assert "fina_indicator" in record["missing_fields"]
    # Other fields still populate.
    assert record["basic"]["name"] == "炼石航空"


def test_fetch_handles_empty_dataframe(fake_pro):
    fake_pro.daily.return_value = pd.DataFrame()
    record = tushare_fetcher.fetch("000697.XSHE", pro=fake_pro)
    assert record["recent_quotes"] == []
    assert "recent_quotes" in record["missing_fields"]


def test_make_pro_uses_token(monkeypatch):
    captured = {}

    def fake_set_token(t):
        captured["token"] = t

    fake_pro = object()

    def fake_pro_api():
        return fake_pro

    monkeypatch.setattr(tushare_fetcher.ts, "set_token", fake_set_token)
    monkeypatch.setattr(tushare_fetcher.ts, "pro_api", fake_pro_api)
    pro = tushare_fetcher.make_pro("THE_TOKEN")
    assert captured["token"] == "THE_TOKEN"
    assert pro is fake_pro
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/fetchers/test_tushare_fetcher.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `scripts/fetchers/tushare_fetcher.py`**

```python
"""Tushare fetcher. Wraps `pro.*` endpoints with a stable record shape."""
from __future__ import annotations

import datetime as dt
from typing import Any

import pandas as pd
import tushare as ts

from scripts.parse_stock_list import to_tushare_code

QUOTES_LOOKBACK_DAYS = 30  # we then keep at most ~20 rows in the record


def make_pro(token: str):
    ts.set_token(token)
    return ts.pro_api()


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")


def _safe(call, missing: list[str], field: str) -> Any:
    try:
        return call()
    except Exception:  # noqa: BLE001 — fetcher must not propagate one endpoint's failure
        missing.append(field)
        return None


def fetch(spec_code: str, pro) -> dict:
    """Fetch basic + quotes + valuation + financial indicator for one stock."""
    ts_code = to_tushare_code(spec_code)
    today = dt.date.today()
    start = (today - dt.timedelta(days=QUOTES_LOOKBACK_DAYS)).strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")

    missing: list[str] = []

    basic_df = _safe(lambda: pro.stock_basic(ts_code=ts_code), missing, "basic")
    basic = None
    if basic_df is not None:
        rows = _df_to_records(basic_df)
        basic = rows[0] if rows else None
        if basic is None:
            missing.append("basic")

    daily_df = _safe(
        lambda: pro.daily(ts_code=ts_code, start_date=start, end_date=end),
        missing,
        "recent_quotes",
    )
    recent_quotes: list[dict] = []
    if daily_df is not None:
        rows = _df_to_records(daily_df)
        if not rows:
            missing.append("recent_quotes")
        else:
            recent_quotes = rows[:20]

    db_df = _safe(
        lambda: pro.daily_basic(ts_code=ts_code, start_date=start, end_date=end),
        missing,
        "daily_basic",
    )
    daily_basic = None
    if db_df is not None:
        rows = _df_to_records(db_df)
        if rows:
            daily_basic = rows[0]
        else:
            missing.append("daily_basic")

    fi_df = _safe(lambda: pro.fina_indicator(ts_code=ts_code), missing, "fina_indicator")
    fina_indicator = None
    if fi_df is not None:
        rows = _df_to_records(fi_df)
        if rows:
            fina_indicator = rows[0]
        else:
            missing.append("fina_indicator")

    return {
        "code": spec_code,
        "source": "tushare",
        "data_date": today.isoformat(),
        "basic": basic,
        "recent_quotes": recent_quotes,
        "daily_basic": daily_basic,
        "fina_indicator": fina_indicator,
        "missing_fields": missing,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/fetchers/test_tushare_fetcher.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetchers/tushare_fetcher.py tests/fetchers/test_tushare_fetcher.py
git commit -m "feat(fetchers): add tushare fetcher with per-endpoint isolation"
```

---

## Task 10: akshare fetcher (TDD with mocks)

**Files:**
- Test: `tests/fetchers/test_akshare_fetcher.py`
- Create: `scripts/fetchers/akshare_fetcher.py`

akshare uses bare 6-digit codes for most stock APIs (no exchange suffix), so the fetcher strips the suffix internally. Field set for v1:
- `recent_quotes`: `stock_zh_a_hist(symbol=code, period="daily")` — last ~20 rows.
- `individual_info`: `stock_individual_info_em(symbol=code)` — name, industry, market cap, etc.
- `fund_flow`: `stock_individual_fund_flow(stock=code)` — most recent row.

Same per-endpoint isolation as the Tushare fetcher.

- [ ] **Step 1: Write the failing test**

Create `tests/fetchers/test_akshare_fetcher.py`:
```python
from unittest.mock import patch

import pandas as pd
import pytest

from scripts.fetchers import akshare_fetcher


@pytest.fixture
def hist_df():
    return pd.DataFrame(
        [
            {"日期": "2026-05-07", "开盘": 10.1, "收盘": 10.3, "最高": 10.5,
             "最低": 9.9, "成交量": 12345, "成交额": 1.2e7, "涨跌幅": 1.2},
            {"日期": "2026-05-08", "开盘": 10.3, "收盘": 10.4, "最高": 10.6,
             "最低": 10.1, "成交量": 11000, "成交额": 1.1e7, "涨跌幅": 0.97},
        ]
    )


@pytest.fixture
def info_df():
    return pd.DataFrame(
        [
            {"item": "股票简称", "value": "炼石航空"},
            {"item": "行业", "value": "航空装备"},
            {"item": "总市值", "value": 1.2e10},
        ]
    )


@pytest.fixture
def flow_df():
    return pd.DataFrame(
        [
            {"日期": "2026-05-08", "主力净流入-净额": 1.5e7,
             "主力净流入-净占比": 5.2, "收盘价": 10.4, "涨跌幅": 0.97},
        ]
    )


def test_fetch_combined_record(hist_df, info_df, flow_df):
    with patch.object(akshare_fetcher.ak, "stock_zh_a_hist", return_value=hist_df), \
         patch.object(akshare_fetcher.ak, "stock_individual_info_em", return_value=info_df), \
         patch.object(akshare_fetcher.ak, "stock_individual_fund_flow", return_value=flow_df):
        record = akshare_fetcher.fetch("000697.XSHE")

    assert record["code"] == "000697.XSHE"
    assert record["source"] == "akshare"
    assert record["data_date"]
    assert len(record["recent_quotes"]) == 2
    assert record["recent_quotes"][-1]["收盘"] == 10.4
    assert record["individual_info"]["行业"] == "航空装备"
    assert record["individual_info"]["股票简称"] == "炼石航空"
    assert record["fund_flow"]["主力净流入-净额"] == 1.5e7
    assert record["missing_fields"] == []


def test_fetch_isolates_endpoint_failure(hist_df, info_df):
    def boom(*a, **kw):
        raise RuntimeError("blocked")
    with patch.object(akshare_fetcher.ak, "stock_zh_a_hist", return_value=hist_df), \
         patch.object(akshare_fetcher.ak, "stock_individual_info_em", return_value=info_df), \
         patch.object(akshare_fetcher.ak, "stock_individual_fund_flow", side_effect=boom):
        record = akshare_fetcher.fetch("000697.XSHE")

    assert record["fund_flow"] is None
    assert "fund_flow" in record["missing_fields"]
    assert record["individual_info"]["股票简称"] == "炼石航空"


def test_fetch_strips_exchange_suffix(hist_df, info_df, flow_df):
    captured = {}

    def capture_hist(symbol, **kwargs):
        captured["hist"] = symbol
        return hist_df

    with patch.object(akshare_fetcher.ak, "stock_zh_a_hist", side_effect=capture_hist), \
         patch.object(akshare_fetcher.ak, "stock_individual_info_em", return_value=info_df), \
         patch.object(akshare_fetcher.ak, "stock_individual_fund_flow", return_value=flow_df):
        akshare_fetcher.fetch("000697.XSHE")

    assert captured["hist"] == "000697"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/fetchers/test_akshare_fetcher.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `scripts/fetchers/akshare_fetcher.py`**

```python
"""akshare fetcher. Strips the exchange suffix internally."""
from __future__ import annotations

import datetime as dt
from typing import Any

import akshare as ak
import pandas as pd


def _bare(spec_code: str) -> str:
    return spec_code.split(".", 1)[0]


def _safe(call, missing: list[str], field: str) -> Any:
    try:
        return call()
    except Exception:  # noqa: BLE001
        missing.append(field)
        return None


def _df_records(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")


def fetch(spec_code: str) -> dict:
    bare = _bare(spec_code)
    today = dt.date.today()
    missing: list[str] = []

    hist = _safe(
        lambda: ak.stock_zh_a_hist(symbol=bare, period="daily"),
        missing,
        "recent_quotes",
    )
    recent_quotes: list[dict] = []
    if hist is not None:
        records = _df_records(hist)
        if not records:
            missing.append("recent_quotes")
        else:
            recent_quotes = records[-20:]

    info = _safe(lambda: ak.stock_individual_info_em(symbol=bare), missing, "individual_info")
    individual_info = None
    if info is not None:
        records = _df_records(info)
        if not records:
            missing.append("individual_info")
        else:
            # akshare returns a long-format (item, value) table; flatten.
            individual_info = {row["item"]: row["value"] for row in records}

    flow = _safe(lambda: ak.stock_individual_fund_flow(stock=bare), missing, "fund_flow")
    fund_flow = None
    if flow is not None:
        records = _df_records(flow)
        if not records:
            missing.append("fund_flow")
        else:
            fund_flow = records[-1]

    return {
        "code": spec_code,
        "source": "akshare",
        "data_date": today.isoformat(),
        "recent_quotes": recent_quotes,
        "individual_info": individual_info,
        "fund_flow": fund_flow,
        "missing_fields": missing,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/fetchers/test_akshare_fetcher.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetchers/akshare_fetcher.py tests/fetchers/test_akshare_fetcher.py
git commit -m "feat(fetchers): add akshare fetcher with per-endpoint isolation"
```

---

## Task 11: Fetch orchestration with fallback (TDD)

**Files:**
- Test: `tests/test_fetch_stock_data.py`
- Create: `scripts/fetch_stock_data.py`

Drives both fetchers and writes one JSON per stock to `stock/<date>/data/<code>.json`. Behavior:

- If `TUSHARE_TOKEN` present, run Tushare first.
- Always also run akshare (it's the cross-check + provides fields Tushare doesn't, like fund flow). Errors in akshare don't block.
- If Tushare token missing, log it in `tushare_status` and skip Tushare.
- Output structure has top-level `code`, `data_date`, `tushare`, `akshare`, `missing_fields` (union of both fetchers' missing fields, plus a marker if a whole fetcher was unavailable).
- Each JSON also records the actual exchange suffix used and Tushare token presence (presence only — never the token itself).

CLI: read JSON list on stdin, accept `--date` and `--out-dir`. Defaults to `stock/<today>/data/`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_fetch_stock_data.py`:
```python
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import fetch_stock_data


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_fetch_one_writes_combined_record(project):
    tushare_record = {
        "code": "000697.XSHE", "source": "tushare", "data_date": "2026-05-10",
        "basic": {"name": "炼石航空"}, "recent_quotes": [{"close": 10.3}],
        "daily_basic": None, "fina_indicator": None,
        "missing_fields": ["daily_basic", "fina_indicator"],
    }
    akshare_record = {
        "code": "000697.XSHE", "source": "akshare", "data_date": "2026-05-10",
        "recent_quotes": [{"收盘": 10.4}],
        "individual_info": {"行业": "航空装备"},
        "fund_flow": {"主力净流入-净额": 1.5e7},
        "missing_fields": [],
    }
    with patch.object(fetch_stock_data, "_run_tushare", return_value=tushare_record), \
         patch.object(fetch_stock_data, "_run_akshare", return_value=akshare_record):
        out = fetch_stock_data.fetch_one(
            {"name": "炼石航空", "code": "000697.XSHE"},
            tushare_token="t",
            out_dir=project / "out",
        )

    written = json.loads((project / "out" / "000697.XSHE.json").read_text("utf-8"))
    assert written["code"] == "000697.XSHE"
    assert written["name"] == "炼石航空"
    assert written["tushare_status"] == "ok"
    assert written["tushare"]["basic"]["name"] == "炼石航空"
    assert written["akshare"]["fund_flow"]["主力净流入-净额"] == 1.5e7
    assert "tushare:daily_basic" in written["missing_fields"]
    assert "tushare:fina_indicator" in written["missing_fields"]
    assert out["written"] == str(project / "out" / "000697.XSHE.json")


def test_fetch_one_skips_tushare_when_token_missing(project):
    akshare_record = {
        "code": "000697.XSHE", "source": "akshare", "data_date": "2026-05-10",
        "recent_quotes": [], "individual_info": None, "fund_flow": None,
        "missing_fields": ["recent_quotes", "individual_info", "fund_flow"],
    }
    with patch.object(fetch_stock_data, "_run_akshare", return_value=akshare_record):
        fetch_stock_data.fetch_one(
            {"name": "炼石航空", "code": "000697.XSHE"},
            tushare_token=None,
            out_dir=project / "out",
        )

    written = json.loads((project / "out" / "000697.XSHE.json").read_text("utf-8"))
    assert written["tushare_status"] == "skipped:no_token"
    assert written["tushare"] is None
    assert written["akshare"]["recent_quotes"] == []


def test_fetch_one_records_tushare_failure(project):
    akshare_record = {
        "code": "000697.XSHE", "source": "akshare", "data_date": "2026-05-10",
        "recent_quotes": [], "individual_info": None, "fund_flow": None,
        "missing_fields": [],
    }
    def boom(*a, **kw):
        raise RuntimeError("network down")
    with patch.object(fetch_stock_data, "_run_tushare", side_effect=boom), \
         patch.object(fetch_stock_data, "_run_akshare", return_value=akshare_record):
        fetch_stock_data.fetch_one(
            {"name": "炼石航空", "code": "000697.XSHE"},
            tushare_token="t",
            out_dir=project / "out",
        )
    written = json.loads((project / "out" / "000697.XSHE.json").read_text("utf-8"))
    assert written["tushare_status"].startswith("error:")
    assert written["tushare"] is None
    assert "tushare:unavailable" in written["missing_fields"]


def test_fetch_all_iterates(project):
    fake_record = {
        "code": "ANY", "source": "tushare", "data_date": "2026-05-10",
        "basic": None, "recent_quotes": [], "daily_basic": None,
        "fina_indicator": None, "missing_fields": [],
    }
    fake_ak = {
        "code": "ANY", "source": "akshare", "data_date": "2026-05-10",
        "recent_quotes": [], "individual_info": None, "fund_flow": None,
        "missing_fields": [],
    }
    with patch.object(fetch_stock_data, "_run_tushare", return_value=fake_record), \
         patch.object(fetch_stock_data, "_run_akshare", return_value=fake_ak):
        result = fetch_stock_data.fetch_all(
            [{"name": "A", "code": "000001.XSHE"},
             {"name": "B", "code": "000002.XSHE"}],
            tushare_token="t",
            out_dir=project / "out",
        )
    assert (project / "out" / "000001.XSHE.json").exists()
    assert (project / "out" / "000002.XSHE.json").exists()
    assert len(result["written"]) == 2


def test_token_never_appears_in_output(project):
    akshare_record = {
        "code": "000697.XSHE", "source": "akshare", "data_date": "2026-05-10",
        "recent_quotes": [], "individual_info": None, "fund_flow": None,
        "missing_fields": [],
    }
    secret = "SHOULD_NOT_LEAK_TOKEN_xyz123"
    with patch.object(fetch_stock_data, "_run_akshare", return_value=akshare_record), \
         patch.object(fetch_stock_data, "_run_tushare", side_effect=RuntimeError(secret)):
        fetch_stock_data.fetch_one(
            {"name": "x", "code": "000697.XSHE"},
            tushare_token=secret,
            out_dir=project / "out",
        )
    blob = (project / "out" / "000697.XSHE.json").read_text("utf-8")
    assert secret not in blob
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_fetch_stock_data.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Implement `scripts/fetch_stock_data.py`**

```python
"""Orchestrate Tushare + akshare fetchers and write per-stock JSON drafts."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from scripts.config import load_tushare_token
from scripts.fetchers import akshare_fetcher, tushare_fetcher


def _today() -> str:
    return dt.date.today().isoformat()


def _run_tushare(spec_code: str, token: str) -> dict:
    pro = tushare_fetcher.make_pro(token)
    return tushare_fetcher.fetch(spec_code, pro=pro)


def _run_akshare(spec_code: str) -> dict:
    return akshare_fetcher.fetch(spec_code)


def fetch_one(stock: dict, tushare_token: str | None, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    code = stock["code"]
    name = stock["name"]
    record: dict = {
        "code": code,
        "name": name,
        "fetched_at": dt.datetime.now().isoformat(timespec="seconds"),
        "tushare_status": "skipped:no_token",
        "tushare": None,
        "akshare": None,
        "missing_fields": [],
    }

    if tushare_token:
        try:
            ts_record = _run_tushare(code, tushare_token)
            record["tushare"] = ts_record
            record["tushare_status"] = "ok"
            for f in ts_record.get("missing_fields", []):
                record["missing_fields"].append(f"tushare:{f}")
        except Exception as exc:  # noqa: BLE001
            # Strip the message: it could echo the token in some libraries' errors.
            record["tushare_status"] = f"error:{type(exc).__name__}"
            record["missing_fields"].append("tushare:unavailable")

    try:
        ak_record = _run_akshare(code)
        record["akshare"] = ak_record
        for f in ak_record.get("missing_fields", []):
            record["missing_fields"].append(f"akshare:{f}")
    except Exception as exc:  # noqa: BLE001
        record["akshare_status"] = f"error:{type(exc).__name__}"
        record["missing_fields"].append("akshare:unavailable")

    out_path = out_dir / f"{code}.json"
    out_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"code": code, "written": str(out_path)}


def fetch_all(stocks: list[dict], tushare_token: str | None, out_dir: Path) -> dict:
    results = [fetch_one(s, tushare_token, out_dir) for s in stocks]
    return {"out_dir": str(out_dir), "written": [r["written"] for r in results]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Tushare + akshare drafts.")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD; defaults to today")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Override output dir; defaults to stock/<date>/data",
    )
    args = parser.parse_args()
    date = args.date or _today()
    out_dir = Path(args.out_dir) if args.out_dir else Path("stock") / date / "data"
    stocks = json.load(sys.stdin)
    token = load_tushare_token()
    result = fetch_all(stocks, tushare_token=token, out_dir=out_dir)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_fetch_stock_data.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_stock_data.py tests/test_fetch_stock_data.py
git commit -m "feat(fetch): orchestrate tushare+akshare with fallback and JSON output"
```

---

## Task 12: stock-analysis skill — workflow

**Files:**
- Create: `.claude/skills/stock-analysis/SKILL.md`

The skill is the runbook Claude follows when a user pastes a stock pool. It must:
- Tell Claude exactly which scripts to run, in order, with the expected I/O.
- Enforce the source grading (A/B/C/unconfirmed) and the data-date requirement.
- Enforce the no-buy/sell-price rule and the 5-tier attention level.
- Specify the per-stock report structure and the three daily summaries.
- End with quality gates Claude must self-check before reporting success.
- Reference Tavily MCP search first, with WebSearch as fallback.

The skill content is long but it is one logical unit; we keep it as a single file. The skill activates when the user provides A-share stock names+codes, asks to analyze A-share stocks, or asks for daily stock analysis docs.

- [ ] **Step 1: Create the skill file**

Write `.claude/skills/stock-analysis/SKILL.md`:
```markdown
---
name: stock-analysis
description: Use when the user pastes an A-share stock pool, asks to analyze A-share stocks, or asks for daily stock analysis documents. Drives the full pipeline — parse pool, scaffold dated dirs and templates, fetch Tushare+akshare drafts, web-search for current facts, write per-stock long-form reports and three daily summary docs, run quality gates.
---

# Stock-Analysis Workflow

## When to use

Trigger this skill whenever the user:
- pastes a list of A-share names+codes (e.g. `炼石航空(000697.XSHE)`),
- asks to analyze one or more A-share stocks,
- asks to generate daily stock analysis docs for a given date.

## Hard rules

- **Current data only.** Never use model-training knowledge as a current fact. Every current fact (price, valuation, announcement, news, policy) must come from a search done in this conversation, with a retrieval timestamp or data date.
- **No price/position advice.** Do not output specific buy/sell prices, take-profit/stop-loss levels, or position sizing. Output research opinions only.
- **Source grading is mandatory.**
  - **A:** company announcements, exchanges (SSE/SZSE/BSE), CNINFO, regulators/government, official periodic reports.
  - **B:** company website / IR, mainstream financial media, reliable data platforms, Tushare, akshare.
  - **C:** secondary financial portals, interactive Q&A platforms, communities, rumors.
  - **Unconfirmed:** only one non-authoritative source, or no cross-verification.
  - C-grade and Unconfirmed sources may not solo-support a core conclusion.
  - On conflict, A wins; flag the conflict in the report.
  - Long-term company archive only absorbs A/B-grade and long-term-stable info.
- **Tushare/akshare are drafts, not facts.** They never replace web search for announcements, news, policy, industry context, or market narrative.
- **No tokens or local config in any output.** Token presence may be reported (`ok` / `skipped:no_token`); the value never leaves the script.

## Execution sequence

Run these in order. Stop and ask the user only if step 1 produces zero stocks.

1. **Parse the stock pool.** Pipe the user's pasted list into `python -m scripts.parse_stock_list` and capture the JSON.
2. **Pick the date.** Default to today (`YYYY-MM-DD`). Use the user's date if explicitly provided.
3. **Scaffold templates.** Pipe the JSON from step 1 into `python -m scripts.init_daily_reports --date YYYY-MM-DD`. This creates `companies/`, `stock/<date>/`, the daily summary files, and per-stock report stubs. Idempotent — safe to re-run.
4. **Fetch the structured drafts.** Pipe the same JSON into `python -m scripts.fetch_stock_data --date YYYY-MM-DD`. This writes `stock/<date>/data/<code>.json` per stock. If `TUSHARE_TOKEN` is missing, akshare-only data is acceptable; note this in the daily research log.
5. **Read existing company archives.** For each stock, read `companies/<code>-<name>.md` if it already has user-confirmed content beyond the template; use it as background, do not overwrite.
6. **Web-search for current facts.** For each stock, run searches focused on:
   - latest announcements (CNINFO / 巨潮 / exchange disclosures),
   - company news in the last 30 days,
   - relevant policy / regulatory changes,
   - industry context and recent narrative,
   - any recent share-price catalyst.
   Prefer Tavily MCP (`mcp__tavily-remote-mcp__tavily_search`, `mcp__tavily-remote-mcp__tavily_extract`) when available; fall back to built-in `WebSearch` only if Tavily is unavailable, and note the fallback. Record retrieval timestamps for each citation.
7. **Grade every source** (A/B/C/Unconfirmed) at the moment you cite it.
8. **Write per-stock reports.** Edit `stock/<date>/<code>-<name>-日评.md` in place. Fill every section of the template. Conclusions first — sections 1-5 must be readable on their own. Mark each current fact with its source and data date. Set `attention_level` in the frontmatter to one of: `重点关注`, `积极关注`, `谨慎关注`, `观察跟踪`, `暂不关注`.
9. **Update company archives — conservatively.** Only write A/B-grade, long-term-stable info. Borderline or short-term info goes into the daily report's `建议写入公司档案的信息` section for the user to confirm later. Append a backlink in the archive to the new daily report.
10. **Write the three daily summaries.**
    - `当日股票池排序.md`: ranking table, ranking logic, per-tier explanation. Read each report's frontmatter `attention_level` to populate.
    - `当日主题与行业综述.md`: shared themes, industry chain, policy catalysts, market narrative.
    - `当日研究日志.md`: source list, data limits, unconfirmed items, follow-up questions, any flow anomalies.
11. **Update the daily index.** Edit `stock/<date>/index.md` so each stock pool entry shows its attention level, plus the day's core conclusions and follow-ups.
12. **Run the quality gates** (next section). If any fail, fix before reporting success.

## Per-stock report structure (must match the template)

1. 投研结论摘要
2. 关注等级
3. 核心逻辑
4. 最大风险
5. 需要继续跟踪的变量
6. 公司与业务概况
7. 行业与政策背景
8. 财务与经营质量
9. 估值与同业比较
10. 技术面与资金情绪
11. 最新公告、新闻与事件催化
12. 信息来源与可信度分级
13. 无法确认或证据不足事项
14. 建议写入公司档案的信息

Conclusions live at the top (1-5). Detail and evidence below. Sources go inline at the citation point and are also collected in section 12.

## Quality gates

Before claiming completion, verify all of these:

**File completeness**
- [ ] Each stock in the pool has a daily report at `stock/<date>/<code>-<name>-日评.md`.
- [ ] Each first-time stock has a company archive at `companies/<code>-<name>.md`.
- [ ] The daily directory has `index.md`.
- [ ] The daily directory has all three summary docs.

**Source completeness**
- [ ] Every daily report has a populated section 12 with sources by tier.
- [ ] Every current fact has either an inline source or a data date.
- [ ] Every unconfirmable item is listed in section 13.
- [ ] No core conclusion rests on a C-grade or Unconfirmed source alone.

**Conclusion bounds**
- [ ] Each daily report has one of the 5 attention levels in its frontmatter and section 2.
- [ ] No specific buy or sell price.
- [ ] No position size advice.
- [ ] No stop-loss / take-profit levels.

**Obsidian compatibility**
- [ ] Every output has YAML frontmatter and tags.
- [ ] Every daily report links to its company archive (`[[<code>-<name>]]`).
- [ ] The daily index links to every per-stock report and all three summaries.

**Long-term archive discipline**
- [ ] Only stable, long-term info in `companies/`.
- [ ] Volatile/short-term info in the daily report's section 14.
- [ ] Each updated archive backlinks to the new daily report.

## Common pitfalls

- Pasting Tushare numbers without an explicit data date — always include the date that came back from the API.
- Citing a Weibo / Xueqiu post as if it were B-grade — it is C-grade unless a regulator or company source confirms it.
- Writing a "买入" or "目标价 X 元" — strip these on review.
- Forgetting to update `attention_level` in the frontmatter, which then breaks the ranking summary.
- Over-writing a user-edited company archive — the init script is idempotent for a reason; re-running it does not overwrite, and Claude must not either.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/stock-analysis/SKILL.md
git commit -m "feat(skill): add stock-analysis workflow skill"
```

---

## Task 13: Final verification — full pipeline smoke test

**Files:**
- No new files. Verifies everything works end-to-end on a small sample.

This is the single end-to-end check. We don't write a CI job for it — the goal is for the human (or Claude in a future session) to run these commands once and confirm the whole stack moves data through correctly.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: every test from tasks 2, 3, 7, 8, 9, 10, 11 passes. No skips, no errors.

- [ ] **Step 2: Verify token leak protection**

Run:
```bash
TUSHARE_TOKEN=fake-token-xyz123 python -c "
from scripts.config import load_tushare_token
t = load_tushare_token()
assert t == 'fake-token-xyz123'
print('config OK')
"
```
Expected: `config OK`. Then ensure `.env` is gitignored:
```bash
echo TUSHARE_TOKEN=should_not_commit > .env
git status --short | grep -E '^\?\? \.env$' && echo "gitignore OK: .env not tracked" || echo "FAIL: .env appears tracked"
rm .env
```
Expected: `gitignore OK: .env not tracked`.

- [ ] **Step 3: Smoke-test the parse → init pipeline**

Run:
```bash
echo "1. 炼石航空(000697.XSHE)
2. 甘肃能源(000791.XSHE)" | python -m scripts.parse_stock_list | \
  python -m scripts.init_daily_reports --date 2026-05-10
```
Expected: JSON summary printed to stdout listing both `created_companies` and `created_reports`. Then verify the layout:
```bash
ls stock/2026-05-10/
ls companies/
```
Expected: see `index.md`, `当日股票池排序.md`, `当日主题与行业综述.md`, `当日研究日志.md`, `000697.XSHE-炼石航空-日评.md`, `000791.XSHE-甘肃能源-日评.md`, `data/`. Both company archives present.

- [ ] **Step 4: Confirm template variables resolved**

Run:
```bash
grep -l '{{stock_name}}\|{{stock_code}}\|{{date}}' stock/2026-05-10/*.md companies/*.md && echo "FAIL: unresolved placeholders" || echo "OK: all variables substituted"
```
Expected: `OK: all variables substituted`.

- [ ] **Step 5: Run init a second time and confirm idempotency**

Run:
```bash
echo "TEST USER EDIT" > companies/000697.XSHE-炼石航空.md
echo "1. 炼石航空(000697.XSHE)" | python -m scripts.parse_stock_list | \
  python -m scripts.init_daily_reports --date 2026-05-10
cat companies/000697.XSHE-炼石航空.md
```
Expected: file still contains `TEST USER EDIT`. Then restore:
```bash
rm companies/000697.XSHE-炼石航空.md
echo "1. 炼石航空(000697.XSHE)" | python -m scripts.parse_stock_list | \
  python -m scripts.init_daily_reports --date 2026-05-10
```

- [ ] **Step 6: (Optional, requires real token) Smoke-test fetcher**

Only if the user has set up `TUSHARE_TOKEN` in `.env`. Otherwise skip — akshare alone may rate-limit on first run.

Run:
```bash
echo "1. 炼石航空(000697.XSHE)" | python -m scripts.parse_stock_list | \
  python -m scripts.fetch_stock_data --date 2026-05-10
cat stock/2026-05-10/data/000697.XSHE.json | python -m json.tool | head -40
```
Expected: JSON containing `tushare_status` and `akshare` fields. If Tushare token is absent, `tushare_status` reads `skipped:no_token` and only `akshare` is populated.

- [ ] **Step 7: Clean up smoke-test artifacts and commit nothing**

The smoke-test outputs (`stock/2026-05-10/...`, `companies/000697.XSHE-炼石航空.md`, etc.) are real workflow data and should be tracked. Decide whether to keep them as a sample or delete:
```bash
# To keep as a tracked sample (preferred for first run):
git add stock/2026-05-10 companies/
git status

# Or to delete:
# rm -rf stock/2026-05-10 companies/000697.XSHE-炼石航空.md companies/000791.XSHE-甘肃能源.md
```
Ask the user which to do — do not commit the sample data without confirmation.

- [ ] **Step 8: Final commit (only if keeping sample data)**

```bash
git commit -m "chore: add 2026-05-10 sample data from smoke test"
```

---

## Self-Review Checklist (post-write)

Spec coverage:
- 项目级硬规则与边界 → CLAUDE.md already exists and the skill restates them. ✓
- `stock-analysis` skill → Task 12. ✓
- `scripts/` (parse, init, fetch) → Tasks 3, 8, 11. ✓
- `templates/` → Tasks 4, 5, 6. ✓
- `companies/` and `stock/` directories → Task 1 creates with `.gitkeep`; Task 8 populates. ✓
- 输出目录与文件结构 (index + 4 reports + 3 summaries + per-stock reports + data dir) → Task 8 + Task 11. ✓
- 个股日评结构 14 sections → Task 5 template + Task 12 skill. ✓
- 关注等级 5 档 → Task 5 frontmatter, Task 12 skill enforces. ✓
- 公司长期档案保守维护 → Task 4 template, Task 8 idempotency, Task 12 skill. ✓
- 三份每日综合文档 → Tasks 6, 12. ✓
- 来源分级 A/B/C/未确认 → Task 12 skill enforces. ✓
- 默认分析流程 1-12 → Task 12 skill execution sequence mirrors. ✓
- 本地配置 (.env, gitignore) → Tasks 1, 2. ✓
- parse_stock_list / init_daily_reports / fetch_stock_data → Tasks 3, 8, 11. ✓
- Tushare 优先 + akshare fallback → Task 11. ✓
- JSON 字段来源、数据日期、缺失项 → Tasks 9, 10, 11. ✓
- 质量控制四组检查 → Task 12 quality gates. ✓
- 技术验证项 → Task 13. ✓

Placeholder scan: no "TBD", no "implement later", no "similar to Task N" without code. Each test step shows the assertion; each implementation step shows the code. ✓

Type consistency: `parse_stock_list` returns `list[dict]` with keys `name`, `code` — used identically in tasks 8 and 11. `fetch` returns dicts with consistent keys (`code`, `source`, `data_date`, `recent_quotes`, `missing_fields`) used in task 11's orchestration tests. `render_template(name, context, template_dir=None)` signature is consistent across task 7 and task 8 callers. `init(stocks, date=None)` signature consistent across task 8 tests and task 11 plan. ✓

No missing references found.
