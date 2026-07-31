"""Load drawing-backed DES-M15172 support configurations."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


_CONFIG_DIR = Path(__file__).with_name("configs")


@lru_cache(maxsize=None)
def load_config(code: str) -> dict | None:
    path = _CONFIG_DIR / f"{str(code).lower()}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def list_codes() -> list[str]:
    return sorted(path.stem.upper() for path in _CONFIG_DIR.glob("*.json"))
