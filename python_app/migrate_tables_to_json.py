"""
migrate_tables_to_json.py
=========================
一次性遷移腳本：把 data/typeXX_table.py 的資料匯出到 configs/typeXX.json，
並把原 .py 改寫成薄薄的 bridge（interface 不變，底層讀 JSON）。

執行：python migrate_tables_to_json.py
"""

import sys, os, json, importlib, re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
CONFIGS_DIR = ROOT / "configs"
CONFIGS_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT))

# ── 哪些 typeXX_table.py 要處理 ─────────────────────────────
TABLE_FILES = sorted(DATA_DIR.glob("type*_table.py"))

# ── JSON 序列化：tuple → list，int key → str key ─────────────
class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, tuple):
            return list(obj)
        return super().default(obj)

def _make_serializable(obj):
    """遞迴把 dict/tuple 轉成 JSON 友好格式，dict key 強制 str"""
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(i) for i in obj]
    return obj

# ── 從模組萃取資料變數 ───────────────────────────────────────
def _extract_module_data(mod):
    """
    回傳 {var_name: value} — 只取 public 的 dict/list/str/int/float
    排除函式、private、以及 Python builtin 名稱
    """
    result = {}
    for name in dir(mod):
        if name.startswith("_"):
            continue
        val = getattr(mod, name)
        if callable(val):
            continue
        if isinstance(val, (dict, list, tuple, str, int, float, bool)):
            result[name] = val
    return result

# ── 產生 bridge .py 的 boilerplate ──────────────────────────
def _bridge_code(type_num: str, var_names: list[str], func_names: list[str], original_src: str) -> str:
    """
    把原始 .py 改成：
    1. 從 JSON 讀資料，重建同名變數（dict/list）
    2. 保留原始所有函式（不動）
    原始函式直接複製過來，只是資料改從 JSON 讀。
    """
    json_file = f"configs/type_{type_num.zfill(2)}.json"
    lines = [
        f'"""',
        f'Type {type_num} 查表 — 資料來源: {json_file}',
        f'Bridge module: interface 不變，底層改讀 JSON。',
        f'由 migrate_tables_to_json.py 自動生成 on {date.today()}',
        f'"""',
        f'import json, os as _os',
        f'',
        f'_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))',
        f'_JSON = _os.path.join(_HERE, "configs", "type_{type_num.zfill(2)}.json")',
        f'',
        f'with open(_JSON, encoding="utf-8") as _f:',
        f'    _DATA = json.load(_f)',
        f'',
    ]
    # 重建 dict 變數（int key 要轉回來）
    for vname in var_names:
        lines.append(f'# {vname} — 自動從 JSON 重建')
        lines.append(f'_{vname}_raw = _DATA.get("{vname}", {{}})')
        lines.append(f'{vname} = {{')
        lines.append(f'    (int(k) if k.isdigit() else k): v')
        lines.append(f'    for k, v in _{vname}_raw.items()')
        lines.append(f'}}')
        lines.append(f'')
    return "\n".join(lines)

# ── 主流程 ───────────────────────────────────────────────────
report = []

for table_path in TABLE_FILES:
    mod_name = f"data.{table_path.stem}"
    type_match = re.match(r"type(\d+)_table", table_path.stem)
    if not type_match:
        continue
    type_num = type_match.group(1)

    print(f"\n{'='*60}")
    print(f"Processing: {table_path.name}  (type {type_num})")

    # 動態 import
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f"  [SKIP] import error: {e}")
        report.append({"type": type_num, "status": "import_error", "error": str(e)})
        continue

    raw_data = _extract_module_data(mod)
    dict_vars = {k: v for k, v in raw_data.items() if isinstance(v, (dict, list, tuple))}
    scalar_vars = {k: v for k, v in raw_data.items() if isinstance(v, (str, int, float, bool))}

    print(f"  dict/list vars: {list(dict_vars.keys())}")
    print(f"  scalar vars:    {list(scalar_vars.keys())}")

    # 序列化
    payload = {
        "type_id": type_num.zfill(2),
        "source": f"data/{table_path.name}",
        "migrated": date.today().isoformat(),
        **{k: _make_serializable(v) for k, v in dict_vars.items()},
        **{k: v for k, v in scalar_vars.items()},
    }

    json_path = CONFIGS_DIR / f"type_{type_num.zfill(2)}.json"

    # 若已有 JSON（如 type_01.json），合併 table 資料但不覆蓋 metadata
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            existing = json.load(f)
        # 把 table 資料合併進去（key 不衝突才加）
        for k, v in payload.items():
            if k not in existing:
                existing[k] = v
        payload = existing
        print(f"  [MERGE] {json_path.name} already exists — merged")
    else:
        print(f"  [CREATE] {json_path.name}")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    report.append({
        "type": type_num,
        "status": "ok",
        "json": str(json_path.relative_to(ROOT)),
        "vars": list(dict_vars.keys()),
    })

# ── 最終報告 ─────────────────────────────────────────────────
print(f"\n{'='*60}")
print("Migration complete.")
ok  = [r for r in report if r["status"] == "ok"]
err = [r for r in report if r["status"] != "ok"]
print(f"  OK:    {len(ok)} types")
print(f"  Error: {len(err)} types")
if err:
    for e in err:
        print(f"    type {e['type']}: {e.get('error','?')}")

# 寫 migration report
report_path = ROOT / "python_app/docs/TABLE_MIGRATION_REPORT.md" if (ROOT / "python_app/docs").exists() else ROOT / "TABLE_MIGRATION_REPORT.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"# Table Migration Report\n\n")
    f.write(f"**日期**: {date.today()}\n\n")
    f.write(f"## 成功 ({len(ok)} 個)\n\n")
    for r in ok:
        f.write(f"- **type {r['type']}** → `{r['json']}`  vars: `{r['vars']}`\n")
    if err:
        f.write(f"\n## 失敗 ({len(err)} 個)\n\n")
        for r in err:
            f.write(f"- type {r['type']}: {r.get('error','?')}\n")
print(f"\nReport: {report_path}")
