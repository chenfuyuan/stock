import json
import subprocess
import sys

from scripts.parse_stock_list import normalize_code, parse_stock_list, to_tushare_code


def test_parse_numbered_stock_pool_with_parentheses():
    records = parse_stock_list("1. 炼石航空(000697.XSHE)\n2. 甘肃能源(000791.XSHE)")

    assert records == [
        {"name": "炼石航空", "code": "000697.XSHE"},
        {"name": "甘肃能源", "code": "000791.XSHE"},
    ]


def test_parse_skips_lines_without_supported_stock_code():
    records = parse_stock_list("股票池\n注释：重点关注\n炼石航空(000697.XSHE)")

    assert records == [{"name": "炼石航空", "code": "000697.XSHE"}]


def test_normalize_tushare_suffixes_to_canonical_suffixes():
    assert normalize_code("000697.SZ") == "000697.XSHE"
    assert normalize_code("600000.SH") == "600000.XSHG"
    assert normalize_code("430489.BJ") == "430489.XBSE"


def test_parse_deduplicates_by_normalized_code():
    records = parse_stock_list("炼石航空(000697.XSHE)\n炼石航空 000697.SZ")

    assert records == [{"name": "炼石航空", "code": "000697.XSHE"}]


def test_to_tushare_code_converts_canonical_suffixes():
    assert to_tushare_code("000697.XSHE") == "000697.SZ"
    assert to_tushare_code("600000.XSHG") == "600000.SH"
    assert to_tushare_code("430489.XBSE") == "430489.BJ"


def test_parse_stock_list_cli_reads_stdin_and_writes_json():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.parse_stock_list"],
        input="炼石航空(000697.XSHE)\n",
        text=True,
        capture_output=True,
        check=True,
    )

    assert json.loads(result.stdout) == [{"name": "炼石航空", "code": "000697.XSHE"}]
