# -*- coding: utf-8 -*-
"""益高(E-KO)支撐判讀 — 試用 CLI。

用法（在 repo 根或任何位置皆可）:
  python python_app/companies/eko_cli.py                 # 互動模式(輸入編號看BOM)
  python python_app/companies/eko_cli.py FS12W-2-1300H-400L
  python python_app/companies/eko_cli.py --codes         # 列出目前支援的編號
  python python_app/companies/eko_cli.py --excel out.xlsx FS12W-2-1300H-400L UB1-6"
  python python_app/companies/eko_cli.py --file list.txt --excel out.xlsx

list.txt 每行一筆，可用逗號在編號後加數量：  FS12W-2-1300H-400L, 3
本工具只呼叫延展套件 companies.api，不修改原始核心。
"""
import os
import sys

# 讓本檔在任何 cwd 下都能 import core/companies（python_app 加入 path）
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

from companies import api                      # noqa: E402
from companies.eko import dispatch as _dispatch  # noqa: E402
from companies.eko.config_loader import load_eko_config  # noqa: E402


def supported():
    rows = []
    for code in _dispatch.supported_codes():
        cfg = load_eko_config(code) or {}
        rows.append((code, cfg.get("name", ""),
                     (cfg.get("designation_format", {}) or {}).get("example", "")))
    return rows


def print_codes():
    print("目前支援的益高編號（Phase 2 建置中，會持續增加）：")
    print("-" * 64)
    for code, name, ex in supported():
        print(f"  {code:6s} {name:28s} 例: {ex}")
    print("-" * 64)


def _fmt_result(desig, r):
    out = [f"\n■ {desig}"]
    if r.error:
        out.append(f"  ✗ 錯誤：{r.error}")
        return "\n".join(out)
    hdr = f"  {'品名':<10}{'規格':<20}{'材質':<14}{'長x寬':<14}{'數量':>4} {'單重kg':>8} {'總重kg':>8}"
    out.append(hdr)
    out.append("  " + "-" * (len(hdr)))
    for e in r.entries:
        lw = f"{int(e.length) if e.length else '-'}x{int(e.width) if e.width else '-'}"
        out.append(f"  {e.name:<10}{str(e.spec)[:19]:<20}{str(e.material)[:13]:<14}"
                   f"{lw:<14}{e.quantity:>4} {e.unit_weight:>8} {e.total_weight:>8}")
    out.append(f"  {'單組總重':<10}{'':<48}{round(r.total_weight, 2):>8} kg")
    for w in r.warnings:
        out.append(f"  ⚠ {w}")
    return "\n".join(out)


def analyze_one(desig):
    r = api.analyze(desig, company="EKO")
    print(_fmt_result(desig, r))
    return r


def _parse_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "," in line:
        d, q = line.split(",", 1)
        try:
            return d.strip(), max(1, int(q.strip()))
        except ValueError:
            return d.strip(), 1
    return line, 1


def export_excel(pairs, path):
    from core.project_aggregation import ProjectInputRow
    rows = [ProjectInputRow(designation=d, quantity=q, serial=f"S-{i+1:03d}")
            for i, (d, q) in enumerate(pairs)]
    project = api.export_project(rows, path, company="EKO")
    print(f"\n✓ 已輸出 10 分頁 Excel：{path}")
    print(f"  支撐 {project.total_support_count} 組，全案總重 {round(project.total_weight, 2)} kg，"
          f"錯誤 {len([e for e in project.errors])} 項")


def interactive():
    print("=" * 64)
    print(" 益高(E-KO)支撐判讀 — 試用（互動模式）")
    print("=" * 64)
    print_codes()
    print("輸入一個編號看材料清單；輸入 codes 重列支援清單；輸入 quit 離開。\n")
    while True:
        try:
            line = input("益高編號> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            break
        if line.lower() in ("codes", "?", "help"):
            print_codes(); continue
        analyze_one(line)


def main(argv):
    args = list(argv)
    if "--codes" in args:
        print_codes(); return
    excel_path = None
    if "--excel" in args:
        i = args.index("--excel")
        excel_path = args[i + 1]
        del args[i:i + 2]
    file_path = None
    if "--file" in args:
        i = args.index("--file")
        file_path = args[i + 1]
        del args[i:i + 2]

    pairs = []
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            for ln in f:
                p = _parse_line(ln)
                if p:
                    pairs.append(p)
    for a in args:
        pairs.append((a, 1))

    if not pairs:
        interactive(); return

    if excel_path:
        export_excel(pairs, excel_path)
    else:
        for d, _q in pairs:
            analyze_one(d)


if __name__ == "__main__":
    main(sys.argv[1:])
