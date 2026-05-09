import json
import re
import sys

_SUFFIX_TO_CANONICAL = {
    "XSHE": "XSHE",
    "XSHG": "XSHG",
    "XBSE": "XBSE",
    "SZ": "XSHE",
    "SH": "XSHG",
    "BJ": "XBSE",
}

_CANONICAL_TO_TUSHARE = {
    "XSHE": "SZ",
    "XSHG": "SH",
    "XBSE": "BJ",
}

_CODE_PATTERN = re.compile(r"(?P<code>\d{6})\.(?P<suffix>XSHE|XSHG|XBSE|SZ|SH|BJ)\b", re.IGNORECASE)


def normalize_code(code: str) -> str:
    match = _CODE_PATTERN.search(code.strip())
    if not match:
        raise ValueError(f"unsupported stock code: {code}")
    suffix = _SUFFIX_TO_CANONICAL[match.group("suffix").upper()]
    return f"{match.group('code')}.{suffix}"


def to_tushare_code(code: str) -> str:
    canonical = normalize_code(code)
    number, suffix = canonical.split(".", 1)
    return f"{number}.{_CANONICAL_TO_TUSHARE[suffix]}"


def parse_stock_list(text: str) -> list[dict[str, str]]:
    records = []
    seen_codes = set()
    for line in text.splitlines():
        match = _CODE_PATTERN.search(line)
        if not match:
            continue
        code = normalize_code(match.group(0))
        if code in seen_codes:
            continue
        name = _extract_name(line[: match.start()])
        records.append({"name": name, "code": code})
        seen_codes.add(code)
    return records


def _extract_name(prefix: str) -> str:
    cleaned = prefix.strip()
    cleaned = re.sub(r"^\s*\d+[.、]\s*", "", cleaned)
    cleaned = cleaned.rstrip("（(").strip()
    return cleaned


def main() -> None:
    records = parse_stock_list(sys.stdin.read())
    json.dump(records, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
