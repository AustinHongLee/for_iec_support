"""
Config Loader - 讀取 configs/ 資料夾中的 JSON 設定檔
支援：
  - 讀取
  - 儲存 (自動更新 last_modified + change_log)
  - 列出所有可用 config
"""
import getpass
import json
import os
from copy import deepcopy
from datetime import date
from typing import Optional

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")
_ANCHOR_INDEX = os.path.join(_CONFIG_DIR, "type_anchor_index.json")

_METADATA_KEYS = {
    "type_id",
    "name",
    "source",
    "migrated",
    "version",
    "last_modified",
    "change_log",
    "data_updated_at",
    "data_update_note",
}


def _normalize_type_id(type_id: str) -> str:
    value = str(type_id or "").strip().upper().replace("TYPE-", "").replace("TYPE_", "")
    if value.endswith(("C", "T")) and value[:-1].isdigit():
        return f"{int(value[:-1]):02d}{value[-1]}"
    return f"{int(value):02d}" if value.isdigit() else value


def _load_anchor_index() -> dict:
    if not os.path.exists(_ANCHOR_INDEX):
        return {"types": {}}
    with open(_ANCHOR_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)


def _anchor_entry(type_id: str) -> dict | None:
    return _load_anchor_index().get("types", {}).get(type_id)


def _direct_config_path(type_id: str, *, must_exist: bool) -> str | None:
    if not type_id.isdigit():
        return None
    path = os.path.join(_CONFIG_DIR, f"type_{int(type_id):02d}.json")
    if must_exist and not os.path.exists(path):
        return None
    return path


def _config_path(type_id: str, *, must_exist: bool = True) -> str | None:
    """取得 config 檔案路徑；不猜測含字母的外部代碼。"""
    normalized = _normalize_type_id(type_id)
    entry = _anchor_entry(normalized)
    if entry and entry.get("anchor_kind") == "storage_alias":
        return _direct_config_path(str(entry.get("storage_id", "")), must_exist=must_exist)
    if entry and entry.get("anchor_kind") == "shared_spec":
        return None
    return _direct_config_path(normalized, must_exist=must_exist)


def validate_config(config: dict) -> list[str]:
    """Return compatibility-schema issues for existing Type config files."""
    issues: list[str] = []
    if not isinstance(config, dict):
        return ["config must be a JSON object"]

    type_id = config.get("type_id")
    if not isinstance(type_id, str) or not type_id.strip():
        issues.append("type_id must be a non-empty string")

    payload_keys = [key for key in config if key not in _METADATA_KEYS]
    if not payload_keys:
        issues.append("config must contain at least one calculation payload key")

    if "table" in config:
        table = config["table"]
        if not isinstance(table, list):
            issues.append("table must be a list")
        else:
            bad_rows = [index for index, row in enumerate(table, 1) if not isinstance(row, dict)]
            if bad_rows:
                issues.append(f"table rows must be objects: {bad_rows}")

    for key, value in config.items():
        if key.endswith("_TABLE") and not isinstance(value, (dict, list)):
            issues.append(f"{key} must be an object or list")

    designation_format = config.get("designation_format")
    if designation_format is not None:
        if not isinstance(designation_format, dict):
            issues.append("designation_format must be an object")
        elif not designation_format.get("pattern"):
            issues.append("designation_format.pattern is required when designation_format exists")

    type_spec = config.get("TYPE_SPEC")
    if type_spec is not None:
        if not isinstance(type_spec, dict):
            issues.append("TYPE_SPEC must be an object")
        elif not isinstance(type_spec.get("engine"), str) or not type_spec.get("engine"):
            issues.append("TYPE_SPEC.engine must be a non-empty string")

    return issues


def load_config(
    type_id: str, *, strict: bool = False, variant: str | None = None
) -> Optional[dict]:
    """讀取指定 Type 的 JSON config"""
    if variant is not None:
        raise NotImplementedError("variant overlay 尚未實作;規格見 configs/variants/README.md")
    path = _config_path(type_id)
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if strict:
        issues = validate_config(config)
        if issues:
            raise ValueError(f"Invalid config for Type {_normalize_type_id(type_id)}: {'; '.join(issues)}")
    return config


def save_config(type_id: str, config: dict, change_desc: str = ""):
    """儲存 config，自動更新 last_modified 和 change_log"""
    config["last_modified"] = date.today().isoformat()
    if change_desc:
        if "change_log" not in config:
            config["change_log"] = []
        try:
            changed_by = getpass.getuser()
        except Exception:
            changed_by = "unknown"
        config["change_log"].append({
            "date": date.today().isoformat(),
            "desc": change_desc,
            "by": changed_by,
        })
    path = _config_path(type_id, must_exist=False)
    if not path:
        raise ValueError(f"Cannot resolve config path for Type {type_id!r}")
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


def get_variation_axes(type_id: str, *, config: dict | None = None) -> dict:
    """Return a detached copy of a Type's declarative override axes."""
    loaded = config if config is not None else load_config(type_id)
    axes = loaded.get("variation_axes", {}) if isinstance(loaded, dict) else {}
    return deepcopy(axes) if isinstance(axes, dict) else {}
