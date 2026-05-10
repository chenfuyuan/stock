# Pre-Design: refactor-vault-root-isolation

## 1. Problem & Goals

- 真实问题：当前仓库根目录同时承载 Obsidian 文档（`companies/`、`stock/<date>/`）与代码工程（`scripts/`、`tests/`、`openspec/`、`.venv/` 等）。把仓库根设为 Obsidian 库根时，库内会出现大量非文档项目；不设为库根则文档无法被 Obsidian 直接索引。
- Goals：
  - 将 Obsidian 库根从仓库根抽出到仓库内子目录 `vault/`，库内只看到文档。
  - 所有研究产物（公司档案、每日股票池目录、入口页、综合文档、证据缓存等）默认落到 `vault/` 下。
  - 脚本、specs、skill 文档的路径描述同步更新到新位置，保持单一事实来源。
- Non-goals：
  - 不引入「行业 / 题材对标」相关的内容增强（拆为后续独立 change）。
  - 不改动模板章节结构、日评/档案 schema、wikilink 命名规则。
  - 不调整 OpenSpec 工作流目录（`openspec/` 仍位于仓库根）。
  - 不为兼容旧路径做双写、软链接或迁移脚本。

## 2. Constraints / Invariants

- 库根采用仓库内子目录 `vault/`，文档与代码同仓共版本，统一进 git。
- 现有 `companies/`、`stock/2026-05-10/` 产物清空重生，不做内容迁移。
- wikilink 形态保持纯名称引用（如 `[[000697.XSHE-炼石航空]]`），不带路径前缀，依赖 Obsidian 名称解析。
- `templates/` 留在仓库根（代码资产），渲染产出只进 `vault/`。
- 路径来源单一：脚本通过 `scripts/config.py` 暴露 vault 根，其他脚本不重复推断。
- Obsidian 库根之外（`scripts/`、`tests/`、`templates/`、`openspec/`、`.venv/` 等）不被纳入 `vault/`。

## 3. Direction & Key decisions

- 推荐路线：「集中化路径配置 + 一次性物理迁移」——通过 `scripts/config.py` 暴露 vault 根，脚本统一从此读，配合 specs/skill 文档同步改写，旧产物 git rm 后重生。
- 放弃路线：「仓库根即库根，代码藏入 tooling/ 子目录」——理由：`.venv/`、`uv.lock`、`pyproject.toml`、`openspec/` 等顶层项无法搬入 tooling/，Obsidian 仍会看到非文档项；需要依赖 `.obsidian` 排除规则维持纯净，护栏脆弱。
- 放弃路线：「仓库外独立 vault 路径」——理由：文档脱离仓库版本控制，多机环境需额外同步配置；与「文档与代码同仓共版本」的偏好不符。
- 关键决策：
  - vault 子目录命名为 `vault/`：理由：中性、Obsidian 社区常用术语，不绑定具体主题。
  - 路径配置入口集中在 `scripts/config.py`：理由：现有 config 模块已是脚本配置事实来源，沿用避免另起新模块。
  - 现有产物 git rm 重生：理由：用户确认现存内容是调试样本，无保留价值；避免迁移期双路径混乱。
  - specs 与 skill 文档随本 change 一并修订：理由：路径出现在 `obsidian-report-scaffolding`、`stock-analysis-workflow`、`structured-stock-data-draft` 三个 spec 与 `stock-analysis` skill；不同步会造成事实分裂。
  - 模板文件位置不动：理由：模板属代码资产、需被脚本读取，与 vault 文档形态分离；只改渲染目标。

## 4. Guardrails for downstream

- Must follow：
  - 脚本对 vault 根的访问统一通过 `scripts/config.py` 的入口取得，不在多处重复推断或硬编码。
  - 渲染产物（公司档案、日评、入口页、综合文档、证据缓存等）只写入 `vault/` 下；模板与脚本仍在仓库根。
  - wikilink 保持纯名称引用，不携带 `vault/` 或子目录前缀。
  - `vault/` 与代码一并进入仓库 git 历史，不在 `vault/` 内单独初始化 git。
  - 同步修订涉及的 specs：`obsidian-report-scaffolding`、`stock-analysis-workflow`、`structured-stock-data-draft`；同步修订 `CLAUDE.md` 的 Hard rules 与 `stock-analysis` skill 文档中的路径描述。
- Forbidden to invent：
  - 不引入仓库外路径（如 `~/obsidian-vault/` 或绝对路径默认值）。
  - 不为兼容旧路径加双写、软链接、迁移脚本或回退分支。
  - 不在 `vault/` 内放置 `scripts/`、`tests/`、`__pycache__/` 等非文档资产。
  - 不改动模板章节结构、日评/档案 schema 或 wikilink 命名规则。
  - 不引入新外部依赖、不新增能力（capability）。

## Next step

- 建议下一步：`/opsx:ff`
- 复杂度信号：路径与文档同步是机械改动，无新模型、无新外部依赖、无跨能力架构判断；影响 3 个现有 spec 的修订属 delta，proposal + specs + tasks 一把过即可，无需独立 design.md。
