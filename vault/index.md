---
tags:
  - stock/vault-index
---

# A 股投研知识库

## 核心入口

- [[公司长期认知]]
- [[每日分析]]
- [[市场复盘与行情摘要]]
- [[来源证据与原始材料]]
- [[行业研究]]
- [[专题主题]]
- [[研究问题]]
- [[维护与健康检查]]

## 数据分层

- `vault/`：Obsidian/LLM 可读知识层，保存证据快照、摘要、索引、数据指针和研究结论。
- `vault/raw/`：文档型来源、小体量低频结构化证据、每日市场汇总快照。
- `data/runs/YYYY-MM-DD/<symbol>/`：本次分析生成的 Tushare/akshare 窗口型接口数据。

## 维护约定

- 新来源材料走 ingest，更新相关页面与 [[log|操作日志]]。
- 每日分析走 analysis，输出到 `vault/stock/YYYY-MM-DD/` 并保守更新公司长期认知。
- 有长期价值的问题沉淀到 [[questions/index|研究问题]] 或相关专题页。
- lint 定期检查孤儿页、缺失来源、过期结论和 raw/data 边界。
