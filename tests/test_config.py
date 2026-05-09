from scripts.config import get_tushare_token


def test_get_tushare_token_prefers_dotenv_file_over_environment(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("TUSHARE_TOKEN=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("TUSHARE_TOKEN", "from-env-var")

    assert get_tushare_token(tmp_path) == "from-dotenv"


def test_get_tushare_token_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)

    assert get_tushare_token(tmp_path) is None
