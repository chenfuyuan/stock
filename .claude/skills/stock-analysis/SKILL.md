# stock-analysis

Use this skill when the user provides an A-share stock pool, asks to analyze A-share stocks, or asks to generate daily stock analysis documents.

## Inputs

Users usually provide stock names and A-share codes such as `炼石航空(000697.XSHE)`. Treat the pasted stock pool as the source input.

## Execution sequence

1. Parse the stock pool first:
   `python -m scripts.parse_stock_list`
   - Read the user's pasted text from stdin.
   - If the JSON list is empty, stop and ask the user to confirm the input instead of generating empty reports.
2. Determine the analysis date. Use the user's requested date, otherwise today's date.
3. Initialize Obsidian files:
   `python -m scripts.init_daily_reports --date <YYYY-MM-DD>`
   - Pipe the parsed JSON list into stdin.
   - Preserve existing files; do not overwrite user-edited company profiles, daily reports, or daily summary files.
4. Fetch structured data draft:
   `python -m scripts.fetch_stock_data --date <YYYY-MM-DD>`
   - Pipe the same parsed JSON list into stdin.
   - Tushare is preferred when `TUSHARE_TOKEN` is available; akshare is always supplemental.
   - The script writes raw JSON under `vault/stock/<date>/data/<code>.json` and a derived Evidence Pack under `vault/stock/<date>/evidence/<code>.json`. Raw JSON is for audit, recalculation, and necessary deep checks only — do not pipe it into prompts by default.
   - Evidence Pack regeneration without re-fetching: `python -m scripts.build_evidence_pack --date <YYYY-MM-DD>`.
   - Structured data is a draft only and never replaces current web research.
5. Read existing company profiles, daily report files, summary files, and `vault/stock/<date>/evidence/<code>.json` (the default Evidence Pack input). Open `vault/stock/<date>/data/<code>.json` only when an audit, recalculation, or deeper verification is required.
6. Perform current web research for announcements, exchange filings, regulator/government policy, company IR, mainstream financial media, reliable data platforms, and industry context.
7. Classify every source and current fact before using it in conclusions.
8. Write each stock daily report with conclusions first and a clear source list.
9. Conservatively update company profiles only with A/B-level long-lived facts. Put short-term catalysts, uncertain details, and proposed profile changes in the daily report's `建议写入公司档案的信息` section.
10. Write the daily stock-pool ranking, theme/industry review, research log, and update the daily index page.
11. Run the quality gates before reporting completion.

## Source grading and fact boundaries

- A-level sources: company announcements, exchange disclosures, CNINFO, regulator/government sites, company IR, official filings.
- B-level sources: mainstream financial media, reputable data platforms, broker/public industry research with clear dates.
- C-level sources: forums, social media, community discussions, unsourced summaries, market rumors.
- Unconfirmed: any claim that lacks a retrievable source or is only supported by C-level sources.
- Every current fact about announcements, news, policy, market data, valuation, finance, or industry context must include a data date or retrieval time.
- C-level or unconfirmed material must not independently support a core conclusion; label it as unconfirmed or insufficient.
- Prefer Tavily MCP tools for web search/extraction. If Tavily is unavailable or unsuitable, fall back to built-in `WebSearch` and record the fallback in the research log.

## Daily stock report structure

Each stock daily report must keep the 14-section structure:

1. 投研结论摘要
2. 关注等级
3. 核心变化
4. 公司与业务背景
5. 行情与估值
6. 财务质量
7. 资金与筹码
8. 公告与事件
9. 行业与政策
10. 竞争格局
11. 风险因素
12. 需继续核验的问题
13. 来源清单
14. 建议写入公司档案的信息

Use one of five attention levels: `高关注`、`中高关注`、`中性跟踪`、`低关注`、`暂不跟踪`. Explain the level using sourced research, not price targets.

## Investment-output boundaries

Reports are research opinions only. Do not provide specific buy prices, sell prices, take-profit levels, stop-loss levels, or position sizing advice. Do not imply an executable trading instruction through exact price bands or allocation percentages.

## Quality gates

Before completion, verify:

- File completeness: every stock has a company profile and daily report; the daily directory has `index.md`, `股票池排序.md`, `主题行业综述.md`, `研究日志.md`, raw JSON drafts under `data/`, and Evidence Packs under `evidence/`.
- Source completeness: every current fact has a source grade and data date or retrieval time; every daily report has a source list.
- Conclusion boundary: no core conclusion relies only on C-level or unconfirmed sources.
- Investment boundary: no specific buy/sell price, take-profit/stop-loss level, or position sizing advice appears in reports or summaries.
- Obsidian compatibility: YAML frontmatter, tags, wikilinks, backlinks, and conclusion-first headings remain intact.
- Company profile maintenance: only A/B-level long-lived facts are written into company profiles; uncertain or short-term items remain in daily reports.
