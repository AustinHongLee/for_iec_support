# Type 36 — 夾持固定型支撐 (Restraint Clamp with Bolt + Lug Plate)

> **圖號**: 36 &nbsp;|&nbsp; **分類**: 支撐型式 &nbsp;|&nbsp; **狀態**: ✅ 已實作

焊接於 EXISTING STRUCTURE 的固定型支撐，透過 K Bolt + Lug Plate (M-34) 鎖固管線。
與 Type 35 (托條/resting) 差異在於本型為 **restraint** (限位固定)。

> ⚠️ **VBA 無此 Type**，完全依圖紙重新設計實作。

---

## 結構示意圖

```
     EXISTING STRUCTURE
     ═══════╤═══════════
             │
        ┌────┴────┐
        │ K BOLT  │  ← 螺栓鎖固管線
        │  ☀PIPE  │
        │         │
        └────┬────┘
             │
     ════════╧═══════════  ← MEMBER (型鋼)
             │
        ┌────┴────┐
        │LUG PLATE│  ← M-34 TYPE-C
        │ (M-34)  │
        └─────────┘
```

**力傳遞**：管線 → K Bolt 鎖固 → 型鋼(MEMBER) → Lug Plate(M-34) → 焊接至結構

---

## 編碼格式

**格式**: `36-{MEMBER}-{HH}`

| 段位 | 意義 | 說明 |
|:---:|------|------|
| 1 | Type 編號 | 固定 `36` |
| 2 | 型鋼代碼 | L50, L75, C100, C125, C150 |
| 3 | HH | 2 位數字, H = 長度 × 100mm |

**範例**: `36-C125-05` → C125 槽鋼, 長度 500mm

> ⚠️ 本型 H 代表「長度」而非「高度」，與 Type 35 相同。

---

## 支援型鋼與限制

| MEMBER | 規格 | H MAX (mm) | M-34 型號 |
|--------|------|:----------:|-----------|
| L50  | 50×50×6  | 600  | LGP-C-1 |
| L75  | 75×75×9  | 800  | LGP-C-3 |
| C100 | 100×50×5 | 1400 | LGP-C-4 |
| C125 | 125×65×6 | 1400 | LGP-C-6 |
| C150 | 150×75×9 | 1400 | LGP-C-7 |

> 不支援 H beam — 僅 Angle 和 Channel。

---

## BOM 組成 (3 筆)

| # | 項目 | 類別 | 規格/公式 | 數量 | 備註 |
|:-:|------|------|----------|:----:|------|
| 1 | MEMBER (型鋼) | 管路類 | H×100 mm | 1 | 主構件 |
| 2 | LUG PLATE TYPE-C | 鋼板類 | A × B × T (M-34 查表) | 1 | 見下方 M-34 對照 |
| 3 | K BOLT | 螺栓類 | 依 M-34 K 欄位 | 1 set | |

---

## M-34 Lug Plate 對照 (TYPE-C)

由 `data/m34_table.py` 中 `get_m34_by_member(code)` 自動查表：

| LGP 型號 | 對應 Member | A (板寬) | B (板高) | T (板厚) | K (bolt) |
|----------|------------|:-------:|:-------:|:-------:|----------|
| LGP-C-1 | L50  |  80 |  80 | 6  | M16×40  |
| LGP-C-3 | L75  | 100 | 100 | 9  | M20×50  |
| LGP-C-4 | C100 | 120 |  80 | 9  | M20×50  |
| LGP-C-6 | C125 | 150 | 100 | 12 | M22×65  |
| LGP-C-7 | C150 | 150 | 120 | 12 | M22×65  |

> Material: same as connected metal

---

## 運算邏輯

```
member_code = part2          # 如 "C125"
h_mm = int(part3) * 100     # 如 "05" → 500mm

① MEMBER:
   add_steel_section_entry(type, dim, h_mm)

② LUG PLATE:
   m34 = get_m34_by_member(member_code)
   add_plate_entry(A, B, T, material="")

③ K BOLT:
   add_custom_entry(name="K BOLT", spec=m34["K"], ...)
```

---

## 與相近 Type 比較

| Type | 本質 | 固定方式 | M-34 | K Bolt |
|------|------|---------|:----:|:------:|
| **35** | 托條 (resting) | 管坐在上面 | ❌ | ❌ |
| **36** | 固定 (restraint) | 螺栓鎖固 | ✅ | ✅ |

---

## 備註

- 無 M-42 底板（焊接於既有結構）
- VBA 中無 Type 36 程式碼，此為全新實作
- Lug Plate 材質跟隨母材 (same as connected metal)
