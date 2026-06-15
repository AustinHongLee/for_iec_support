"""測試材料合計 + 下料計算"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.calculator import analyze_batch
from core.material_summary import aggregate
from core.cutting_optimizer import optimize_from_summary

# ── 模擬一批支撐編碼 ──
codes = [
    "01-4B-05A",
    "01-4B-05A",
    "01-4B-08A",
    "01-8B-05A",
    "01-2B-05A",
    "03-4B-05",
    "05-4B-05",
    "07-4B-05",
]

print(f"=== 分析 {len(codes)} 筆編碼 ===\n")

# 1. 批次分析
results = analyze_batch(codes)
for r in results:
    if r.error:
        print(f"  {r.fullstring}: ERROR - {r.error}")
    else:
        print(f"  {r.fullstring}: {len(r.entries)} entries, {r.total_weight:.2f} kg")

# 2. 材料合計
print(f"\n=== 材料合計表 ===\n")
summary = aggregate(results)

print(f"{'品名':<10} {'規格':<18} {'材質':<12} {'類型':<8} "
      f"{'需求總長':>10} {'件數':>5} {'總重(kg)':>9} {'採購':>6} {'單位':<4}")
print("-" * 100)

for ln in summary.lines:
    length_str = f"{ln.total_length_mm:.0f}mm" if ln.total_length_mm else "-"
    qty_str = str(ln.piece_count) if ln.aggregate_type == "linear" else str(ln.total_qty)
    print(f"{ln.name:<10} {ln.spec:<18} {ln.material:<12} {ln.aggregate_type:<8} "
          f"{length_str:>10} {qty_str:>5} {ln.total_weight:>9.2f} {ln.purchase_qty:>6} {ln.purchase_unit:<4}")

print(f"\n合計總重: {summary.total_weight:.2f} kg")

# 3. 下料計算 (僅線性材料)
linear_lines = summary.get_linear_lines()
if linear_lines:
    print(f"\n=== 下料計算 ({len(linear_lines)} 種線性材料) ===")

    for ln in linear_lines:
        plan = optimize_from_summary(ln)
        if not plan:
            continue

        print(f"\n── {plan.name} {plan.spec} ({plan.material}) ──")
        print(f"  需求: {plan.total_pieces} 段, 總長 {plan.total_demand_length:.0f}mm")
        print(f"  原料: {plan.total_bars} 根 × {plan.stock_length:.0f}mm")
        print(f"  平均使用率: {plan.avg_utilization:.1f}%")
        print(f"  總餘料: {plan.total_remnant:.0f}mm, 廢料: {plan.total_waste:.0f}mm")
        print()

        for i, bar in enumerate(plan.bars):
            pieces_str = " + ".join(
                f"{p.demand_length:.0f}({p.source})" for p in bar.pieces
            )
            print(f"  原料 #{i+1}: [{pieces_str}]  "
                  f"用={bar.used_length:.0f}mm  "
                  f"餘={bar.remnant:.0f}mm  "
                  f"率={bar.utilization:.1f}%")

# 4. 匯出 Excel
print(f"\n=== 匯出 Excel ===")
from export.summary_export import export_summary_and_cutting
out_path = os.path.join(os.path.dirname(__file__), "output", "test_summary_cutting.xlsx")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
export_summary_and_cutting(summary, out_path)
print(f"已匯出: {out_path}")
