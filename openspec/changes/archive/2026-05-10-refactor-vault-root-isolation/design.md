## Context

仓库根目录当前同时承载 Obsidian 文档与代码工程。文档分布在 `companies/`、`stock/<date>/`，代码分布在 `scripts/`、`tests/`、`templates/`、`openspec/`、`.venv/` 等。Obsidian 直接以仓库根为库根时，会被代码工程项淹没；现有 `scripts/init_daily_reports.py:18` 处硬编码 `root / "companies"`，路径推断也分散在多个脚本中。

本次重构在仓库内划出 `vault/` 子目录作为 Obsidian 库根，统一路径配置入口，并清空重生现有产物。

## Goals / Non-Goals

**Goals:**

- 把 Obsidian 库根从仓库根抽出到 `vault/`，库内只看到文档
- 所有研究产物默认落到 `vault/companies/`、`vault/stock/<date>/`
- 路径来源单一：脚本通过 `scripts/config.py` 暴露 vault 根，其他脚本不重复推断
- specs 与 skill 文档与新结构对齐

**Non-Goals:**

- 不引入「行业 / 题材对标」相关的内容增强（已拆为后续独立 change）
- 不改动模板章节结构、日评/档案 schema、wikilink 命名规则
- 不调整 OpenSpec 工作流目录（`openspec/` 仍位于仓库根）
- 不为兼容旧路径做双写、软链接、迁移脚本

## Decisions

**vault 子目录命名为 `vault/`**：相比 `docs/`（语义偏向静态文档）、`research/`（领域化命名局限性强），`vault/` 是 Obsidian 社区通用术语，中性、向未来扩展友好。

**路径配置入口集中在 `scripts/config.py`**：现有 `scripts/config.py` 已是脚本配置事实来源（读取 Tushare token），沿用避免另起新模块。新增 `get_vault_root(root: Path | str = Path(".")) -> Path` 函数，所有脚本通过此函数获取 vault 根。环境变量 `STOCK_VAULT_ROOT` 可覆盖默认值，便于测试隔离。

**模板留在仓库根 `templates/`，渲染产出进 `vault/`**：模板属代码资产、需被脚本读取，不应混入 Obsidian 库；只改 `init_daily_reports.py` 中渲染目标路径，不动模板加载路径。

**wikilink 形态保持纯名称**：`[[000697.XSHE-炼石航空]]` 不带任何路径前缀。Obsidian 通过库内文件名自动解析，不依赖路径——这意味着 `companies/` 和 `stock/<date>/` 同位移到 `vault/` 下后，wikilink 不需要任何改写。

**现有产物 git rm 清空重生**：用户确认现存内容是调试样本，无保留价值。避免迁移期双路径混乱、避免软链接 / 双写带来的脚本复杂度。

**stock-analysis-workflow 不做 spec delta**：该 capability 的 Requirements 都是流程性约束（执行序列、来源分级、输出边界、检索优先级），不出现路径字面量；路径变化只反映在 `stock-analysis` skill 文档与 `CLAUDE.md`，作为文档同步任务进入 tasks.md。

## Risks / Trade-offs

- **风险**：Obsidian 已有用户笔记或链接指向旧路径（如外部笔记中的 `[[../companies/...]]`） → **Mitigation**：当前仓库为单人项目，已确认现有产物清空重生；外部引用风险不存在。
- **风险**：测试中可能存在硬编码 `companies/`、`stock/` 字符串 → **Mitigation**：tasks 阶段全量 grep `tests/` 下所有路径字面量并改至 `vault/...`，跑 `uv run pytest` 验证。
- **风险**：`vault/` 进入 git 后，未来产物提交噪声大 → **Trade-off**：与代码同仓共版本是已确认偏好，接受这个代价；如未来想剔除，可加入 `.gitignore`，但当前不做。
- **风险**：环境变量 `STOCK_VAULT_ROOT` 若未文档化，外部用户可能困惑 → **Mitigation**：在 `CLAUDE.md` 与 `.env.example`（如有需要）记录其用途，缺省值为 `vault/`。

## Migration Plan

1. 在 `scripts/config.py` 增加 `get_vault_root` 函数，默认 `Path(root) / "vault"`，支持 `STOCK_VAULT_ROOT` 覆盖
2. 改写所有脚本对 `companies/`、`stock/` 的路径引用，统一通过 `get_vault_root` 拼装
3. 同步修订 `tests/` 内涉及输出路径的断言
4. `git rm -r companies/ stock/`，确认已清理
5. 修订 specs（`obsidian-report-scaffolding`、`structured-stock-data-draft` 的 spec.md）、`CLAUDE.md`、`AGENTS.md`、`.claude/skills/stock-analysis/SKILL.md` 中的路径字面量
6. 跑一遍完整工作流（`parse → init → fetch → ...`）生成新样本到 `vault/` 下，确认 Obsidian 中将 `vault/` 设为库根后界面干净
7. **回滚策略**：本次为重构，回滚通过 `git revert` 单一 commit 完成；不需要数据迁移回滚

## Open Questions

无。
