from datetime import date, datetime, timedelta

_RECENT_WINDOW_DAYS = 365


def apply_recent_year_window(
    records: list[dict],
    date_field: str,
    data_date: str,
) -> list[dict]:
    if not records or date_field not in records[0]:
        return records
    cutoff = _parse_date(data_date) - timedelta(days=_RECENT_WINDOW_DAYS)
    kept: list[dict] = []
    for row in records:
        value = row.get(date_field)
        if value is None:
            kept.append(row)
            continue
        try:
            row_date = _parse_date(str(value))
        except ValueError:
            kept.append(row)
            continue
        if row_date >= cutoff:
            kept.append(row)
    return kept


def _parse_date(value: str) -> date:
    text = value.strip()
    if "-" in text:
        return datetime.strptime(text, "%Y-%m-%d").date()
    return datetime.strptime(text, "%Y%m%d").date()
