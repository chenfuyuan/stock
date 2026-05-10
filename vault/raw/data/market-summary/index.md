---
tags:
  - stock/raw
  - stock/market-summary
---

# 每日市场汇总 raw

用于保存小体量复盘证据快照，例如指数、总成交额、涨跌家数、涨跌停统计、行业/概念汇总。

## 目录约定

```text
vault/raw/data/market-summary/YYYY-MM-DD/
  indices.csv
  breadth.csv
  turnover.csv
  sector-summary.csv
  metadata.md
```

## metadata 必填项

- 交易日
- 数据源
- 采集时间
- 字段口径
- 缺失或异常说明

## 禁止内容

- 全 A 逐股票行情明细
- 全市场资金流明细
- 分钟线
- 逐笔数据
