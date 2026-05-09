from scripts.templates import render_template


def test_render_template_replaces_known_variables_and_keeps_unknown_placeholders():
    rendered = render_template("{{stock_name}} {{stock_code}} {{unknown}}", {"stock_name": "炼石航空", "stock_code": "000697.XSHE"})

    assert rendered == "炼石航空 000697.XSHE {{unknown}}"
