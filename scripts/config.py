import os
from pathlib import Path

from dotenv import dotenv_values


def get_tushare_token(root: Path | str = Path(".")) -> str | None:
    env_path = Path(root) / ".env"
    if env_path.exists():
        value = dotenv_values(env_path).get("TUSHARE_TOKEN")
        if value:
            return value
    return os.environ.get("TUSHARE_TOKEN") or None


def get_vault_root(root: Path | str = Path("."), env: dict | None = None) -> Path:
    env = env if env is not None else os.environ
    override = env.get("STOCK_VAULT_ROOT")
    if override:
        return Path(override)
    return Path(root) / "vault"
