## Why

当前仓库根目录同时承载 Obsidian 文档（`companies/`、`stock/<date>/`）与代码工程（`scripts/`、`tests/`、`openspec/`、`.venv/` 等）。把仓库根设为 Obsidian 库根时，库内会被 `.venv/`、`pyproject.toml`、`uv.lock`、`scripts/` 等淹没；不设为库根则文档无法被 Obsidian 直接索引。需要在仓库内划出一个只包含文档的子目录作为 Obsidian 库根。

## What Changes

- 新增统一的 Obsidian 库根 `vault/`，作为所有研究产物的物理位置
- 修改公司档案、每日股票池目录、入口页、综合文档与证据缓存的输出路径，从 `companies/`、`stock/<date>/` 迁至 `vault/companies/`、`vault/stock/<date>/`
- 修改脚本对 vault 根的访问路径，集中于 `scripts/config.py` 暴露的单一入口
- 移除当前已生成的 `companies/`、`stock/2026-05-10/` 旧产物，新产物从 `vault/` 重新生成
- 修改 `CLAUDE.md` Hard rules 与 `stock-analysis` skill 中的输出路径描述，与新结构对齐

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `obsidian-report-scaffolding`：研究产物的物理输出路径调整为 `vault/` 子目录下，目录初始化与模板渲染需写入新位置
- `structured-stock-data-draft`：结构化数据缓存目录从 `stock/<date>/data/` 调整为 `vault/stock/<date>/data/`

## Impact

- 代码：`scripts/config.py`（新增 vault 根入口）、`scripts/init_daily_reports.py`、`scripts/build_evidence_pack.py`、`scripts/fetch_stock_data.py`、`scripts/parse_stock_list.py` 中所有路径引用统一改为读取该入口
- 测试：`tests/` 内涉及输出路径的断言需要更新到新路径
- 文档：`CLAUDE.md`、`AGENTS.md`、`.claude/skills/stock-analysis/SKILL.md` 中路径描述同步
- 产物：现有 `companies/`、`stock/2026-05-10/` 目录从仓库移除（git rm），不做内容迁移
- 不影响：模板章节结构、日评/档案 schema、wikilink 命名规则、OpenSpec 工作流目录（`openspec/` 仍位于仓库根）
