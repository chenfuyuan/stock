# Project Instructions

This project is an A-share deep research and Obsidian knowledge base workflow.

## Hard rules

- Users usually provide stock names and A-share codes, such as `炼石航空(000697.XSHE)`.
- When a user provides an A-share stock pool, asks to analyze A-share stocks, or asks to generate daily stock analysis documents, invoke the `stock-analysis` skill before doing the work.
- Every analysis must use current data and web search. Do not use model training data as the basis for current facts.
- Prefer A/B-level sources: company announcements, exchanges, CNINFO, regulator/government sites, company IR, mainstream financial media, reliable data platforms, Tushare, and akshare.
- Tushare/akshare data is a structured draft only; it does not replace current web search for announcements, news, policy, industry context, or market narratives.
- All current facts must include a data date or retrieval time.
- Reports are research opinions only. Do not provide specific buy prices, sell prices, take-profit/stop-loss levels, or position sizing advice.
- Write outputs to `companies/` and `stock/YYYY-MM-DD/`.
- Reports must be Obsidian-friendly: YAML frontmatter, tags, wikilinks, backlinks, clear headings, and conclusions first.
- Never commit tokens, `.env`, or local configuration.

## Python commands

- This project uses `uv` and the checked-in `uv.lock`; do not rely on globally installed `python`, `pip`, or `pytest`.
- Run Python commands with `uv run python ...`.
- Run tests with `uv run pytest`.
- Manage dependencies with `uv add ...`, `uv add --dev ...`, and `uv sync`.
