"""益高設定檔載入器（讀 companies/eko/configs/<code>.json）。

與 core.config_loader 分離：益高資料放在延展套件內，核心不受影響。
"""
import json
import os
from functools import lru_cache

_CFG_DIR = os.path.join(os.path.dirname(__file__), "configs")


@lru_cache(maxsize=None)
def load_eko_config(code):
    path = os.path.join(_CFG_DIR, f"{str(code).lower()}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_codes():
    if not os.path.isdir(_CFG_DIR):
        return []
    return sorted(fn[:-5].upper() for fn in os.listdir(_CFG_DIR)
                  if fn.endswith(".json"))
