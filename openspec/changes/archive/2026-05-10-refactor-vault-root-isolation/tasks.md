## 1. 路径配置入口

- [x] 1.1 在 `scripts/config.py` 新增 `get_vault_root(root, env=os.environ)` 函数：默认 `Path(root) / "vault"`，`STOCK_VAULT_ROOT` 环境变量可覆盖；附最小单测覆盖默认值与覆盖两条路径
- [x] 1.2 在 `.env.example` 增加 `# STOCK_VAULT_ROOT=vault` 注释行作为可选项说明

## 2. 脚本路径迁移

- [x] 2.1 改写 `scripts/init_daily_reports.py`：所有 `root / "companies"`、`root / "stock"` 改为基于 `get_vault_root(root)` 拼装，更新返回摘要中的相对路径字符串
- [x] 2.2 改写 `scripts/build_evidence_pack.py`、`scripts/fetch_stock_data.py`、`scripts/parse_stock_list.py`：所有产物输出路径统一通过 `get_vault_root` 取得；不再出现裸的 `companies/` 或 `stock/` 字面量
- [x] 2.3 在 `tests/` 内全量替换 `companies/`、`stock/<date>/`、`stock/2026-` 等路径字面量到 `vault/...` 形态；更新测试 fixture 与断言

## 3. 现有产物清理

- [x] 3.1 `git rm -r companies/ stock/` 并清理未跟踪旧产物目录；不在 apply 阶段自动提交 commit

## 4. spec 与文档同步

- [x] 4.1 修订主 spec：把 `openspec/specs/obsidian-report-scaffolding/spec.md` 与 `openspec/specs/structured-stock-data-draft/spec.md` 的路径字面量更新到 `vault/...`，与 change delta 一致
- [x] 4.2 修订 `CLAUDE.md` 的 Hard rules："Write outputs to `companies/` and `stock/YYYY-MM-DD/`" 改为 `vault/companies/` 与 `vault/stock/YYYY-MM-DD/`；同步 `AGENTS.md` 中对应描述
- [x] 4.3 修订 `.claude/skills/stock-analysis/SKILL.md` 与 `.agents/skills/stock-analysis/SKILL.md`：所有路径描述对齐 `vault/...`

## 5. 验证与收尾

- [x] 5.1 跑 `uv run pytest`，全量测试通过
- [x] 5.2 端到端跑一次工作流（`parse → init → fetch`）生成最小样本到 `vault/` 下，目视确认产物结构与 wikilink 解析无误
- [x] 5.3 自检：仓库根除 `vault/`、`templates/`、`scripts/`、`tests/`、`openspec/`、配置文件外，**无**遗留 `companies/`、`stock/<date>/` 目录
- [x] 5.4 自检：脚本对 vault 根的访问全部经过 `scripts/config.py` 的 `get_vault_root`，`grep -r '"companies"' scripts/` 与 `grep -r '"stock"' scripts/` 均无业务路径硬编码
- [x] 5.5 自检：wikilink 形态保持纯名称，未引入 `vault/` 或子目录前缀（`grep -r '\[\[vault/' vault/` 应无结果）
- [x] 5.6 跑 `openspec validate refactor-vault-root-isolation` 通过
