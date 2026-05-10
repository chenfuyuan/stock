## 1. 知识库目录与入口

- [x] 1.1 建立或更新 `vault/index.md`，覆盖公司、行业、专题、raw、market、stock、questions、maintenance 入口
- [x] 1.2 建立或更新 `vault/log.md`，支持记录 ingest、analysis、query、lint 动作
- [x] 1.3 建立 `vault/market/` 相关入口，承载市场日报、个股行情摘要和数据指针
- [x] 1.4 建立 `vault/raw/data/market-summary/` 约定，保存每日市场汇总快照和 metadata

## 2. 结构化数据输出路径

- [x] 2.1 定位所有 `vault/stock/<date>/data/<code>.json` 生成、读取和引用点
- [x] 2.2 将结构化接口数据输出改为 `data/runs/<date>/<symbol>/`，同一 run 内窗口型数据覆盖刷新
- [x] 2.3 为 `data/runs/<date>/<symbol>/` 生成 metadata，记录来源、获取时间、查询区间、字段口径和缺失字段
- [x] 2.4 移除旧路径新增逻辑，不做双写、不保留兼容 shim

## 3. 数据分层规则落地

- [x] 3.1 将文档型来源和低频小体量结构化证据归档到 `vault/raw/` 或 `vault/raw/data/`
- [x] 3.2 将每日市场汇总保存到 `vault/raw/data/market-summary/<date>/`，并排除逐股票明细
- [x] 3.3 将近一年日线、近一年资金流和近 N 日对比数据限定为本次 `data/runs/` 输出
- [x] 3.4 限定每日逐股票明细采集范围为目标股票池或分析中明确需要补充的股票

## 4. 报告与 LLM 维护流程

- [x] 4.1 更新每日研究报告模板，加入固定 `数据依据` 小节
- [x] 4.2 在分析流程中记录数据源、获取时间、查询区间、run 路径和 Obsidian 来源页面
- [x] 4.3 在 analysis 流程中更新相关公司页、市场页、`vault/index.md` 和 `vault/log.md`，避免全库大扫除
- [x] 4.4 在 ingest、query、lint 流程说明中明确各自更新页面范围和 backlinks 规则

## 5. 验证与收尾

- [x] 5.1 运行 `uv run pytest`，确认现有测试基线通过
- [x] 5.2 运行 `openspec validate docs-obsidian-stock-wiki`，确认 change artifacts 有效
- [x] 5.3 自检未将全市场逐股票行情、全市场资金流、分钟线或逐笔写入 `vault/raw/` 或 `vault/stock/<date>/`
- [x] 5.4 自检未默认采集全 A 每只股票明细，且未扫描本地长期全量行情或资金流文件
- [x] 5.5 自检所有新报告引用 `data/runs/<date>/<symbol>/`，不再新增 `vault/stock/<date>/data/<code>.json`
