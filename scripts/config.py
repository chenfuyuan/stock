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
