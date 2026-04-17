"""
Config Loader - 讀取 configs/ 資料夾中的 JSON 設定檔
支援：
  - 讀取
  - 儲存 (自動更新 last_modified + change_log)
  - 列出所有可用 config
"""
import json
import os
from datetime import date
from typing import Optional

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")


def _config_path(type_id: str) -> str:
    """取得 config 檔案路徑"""
    filename = f"type_{type_id.lower().replace('t', '').zfill(2)}.json"
    return os.path.join(_CONFIG_DIR, filename)


def load_config(type_id: str) -> Optional[dict]:
    """讀取指定 Type 的 JSON config"""
    path = _config_path(type_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(type_id: str, config: dict, change_desc: str = ""):
    """儲存 config，自動更新 last_modified 和 change_log"""
    config["last_modified"] = date.today().isoformat()
    if change_desc:
        if "change_log" not in config:
            config["change_log"] = []
        config["change_log"].append({
            "date": date.today().isoformat(),
            "desc": change_desc,
        })
    path = _config_path(type_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def list_configs() -> list:
    """列出所有可用的 config 檔案"""
    if not os.path.exists(_CONFIG_DIR):
        return []
    configs = []
    for fn in sorted(os.listdir(_CONFIG_DIR)):
        if fn.endswith(".json") and fn.startswith("type_"):
            path = os.path.join(_CONFIG_DIR, fn)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            configs.append({
                "type_id": data.get("type_id", fn),
                "name": data.get("name", fn),
                "version": data.get("version", "?"),
                "last_modified": data.get("last_modified", "?"),
            })
    return configs


def get_type_table(type_id: str) -> list:
    """取得 Type 的查詢表 (table 欄位)"""
    config = load_config(type_id)
    if config and "table" in config:
        return config["table"]
    return []


def get_type_table_as_dict(type_id: str) -> dict:
    """將 table 轉為以 line_size 為 key 的 dict，方便查表"""
    table = get_type_table(type_id)
    return {row["line_size"]: row for row in table}
