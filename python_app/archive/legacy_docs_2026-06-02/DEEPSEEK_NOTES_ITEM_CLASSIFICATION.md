# Deepseek Notes - Item Classification

> 依據：`component_roles.py`、`models.py`、`material_summary.py`、`type_59.py`、`plate.py`、`summary_export.py` 程式碼 + `STEEL_PLATE_NAMING_PLAN.md` 討論文件。
> 標記：[程式] = 程式碼中已有 / [文件] = 討論文件中 / [推測] = 我的判斷。

---

## 你認為目前概念是否清楚

**概念層次清楚，實作層正在收斂。** 四層分類的邊界已經定義得很乾淨：

| 層級 | 來源 | 用途 | 變更頻率 |
|------|------|------|---------|
| `category`（屬性） | `entry.category`，BOM 材料類別 | UI 分組顏色、採購大類 | 幾乎不變 |
| `role`（語意角色） | `ComponentRole` enum | CAD 圖庫對應、程式邏輯分支 | 新增 type 時才擴充 |
| `item_class`（物件類別） | `ItemClass` enum，從 role 自動推導 | 採購/製造分流 | 不變 |
| `manufacturing_type`（製造方式） | `ManufacturingType` enum，從 role + shape_kind 推導 | 工單、備料、外購單 | shape_kind 觸發 |

Type 59 已經是完整參考實作：[程式] `part_key`、`stock_id`、`shape_kind="wing"`、`item_class`、`manufacturing_type`、`gross_area / cutout_area / net_area` 全部到位。其他 type 的落差是遷移進度問題，不是設計問題。

---

## 建議分類規則

以下分類整合現有 [程式] 定義與 [推測] 建議：

### 物件類別（item_class）

| role / category | 建議 item_class | 理由 |
|-----------------|----------------|------|
| pipe, column, top_beam, diagonal_brace, trunnion, angle, channel, h_section | `primary_structure` | [程式] 已定義。承載骨架，不可省略 |
| base_plate, lug_plate, shim_plate, cover_plate, wing_plate, stopper_plate, side_plate, top_plate, saddle_plate, reinforcement_pad, generic_plate, flat_bar | `fabricated_part` | [程式] 已定義。需切割/鑽孔/放樣 |
| expansion_bolt, machine_bolt, k_bolt, nut, washer, u_bolt | `accessory` | [程式] 已定義。外購標準件 |
| gasket, pu_block, clamp | `accessory` | [程式] 已定義 |
| spring（目前歸在 category="彈簧類"） | `accessory` | [推測] ComponentRole 尚無 SPRING，建議補上 |
| D-63 shoe（Type 59 FIG-A，NOT FURNISHED） | `reference_only` | [推測] 圖面參照但不供貨，需明確標記 |

### 製造方式（manufacturing_type）

| role | shape_kind | 建議 manufacturing_type | 理由 |
|------|-----------|------------------------|------|
| pipe, column, top_beam, diagonal_brace, trunnion, angle, channel, h_section | — | `raw_cut` | [程式] 已定義。原料裁切 |
| flat_bar | — | `raw_cut` | [程式] 已定義。扁鋼本質是型鋼裁切，非板件 |
| base_plate, shim_plate, cover_plate, side_plate, top_plate, generic_plate | 空白 | `plate_cut` | [程式] 已定義。矩形板切割 |
| lug_plate（Type 59 Detail Z） | `wing` | `shaped_plate` | [程式] 已實作。L 型缺角需放樣 |
| lug_plate（Type 25/26/36/39/43/45/47，M-34 TYPE-C） | 空白（目前） | `plate_cut` → 應改 `shaped_plate` | [推測] M-34 Lug Plate TYPE-C 有斜角/缺角，非純矩形。但 [程式] 目前未傳 shape_kind |
| saddle_plate（Type 56/80 SADDLE_ARC） | 空白（目前） | `plate_cut` → 應改 `shaped_plate` | [推測] 弧形板必須放樣 |
| reinforcement_pad（Type 61/76/80） | 空白（目前） | `plate_cut` → 應改 `shaped_plate` | [推測] 120° 弧形墊板 |
| stopper_plate, wing_plate | `rect`（預設） | `plate_cut` | [程式] 四方板，不需 shape_kind |
| 所有 bolt/nut/washer/clamp/gasket/pu_block | — | `purchased` | [程式] 已定義 |

---

## 風險與矛盾

### 風險 1：`MACHINED` 有定義但無使用

[程式] `ManufacturingType.MACHINED` 存在，但 `ROLE_MANUFACTURING_TYPE` 和 `CATEGORY_MANUFACTURING_TYPE` 沒有任何 role 對應到它。這意味著：
- 有鑽孔的板（M42 b/c/d 型）目前仍被標為 `plate_cut`，不是 `machined`
- 若未來需要區分「純切割」和「切割+鑽孔」，MACHINED 應啟用
- [推測] 建議：保持現狀，等 CAD/CAM 端回報需要區分時再補

### 風險 2：`shape_kind` 未傳遞會導致異形板誤標

[程式] `manufacturing_type_for()` 依賴 `shape_kind` 來判斷是否為 `shaped_plate`。目前只有 Type 59 傳了 `shape_kind="wing"`。其他異形板：

| Type | role | 現有 shape_kind | 結果 | 應該 |
|------|------|----------------|------|------|
| 25/26/36 | lug_plate | 無 | `plate_cut` ❌ | `shaped_plate` |
| 39/43/45/47 | lug_plate | 無 | `plate_cut` ❌ | `shaped_plate` |
| 56 | saddle_plate | 無 | `plate_cut` ❌ | `shaped_plate` |
| 61 | reinforcement_pad | 無 | `plate_cut` ❌ | `shaped_plate` |
| 76 | reinforcement_pad | 無 | `plate_cut` ❌ | `shaped_plate` |
| 77 | saddle_plate | 無 | `plate_cut` ❌ | `shaped_plate` |
| 80 | saddle_plate | 無 | `plate_cut` ❌ | `shaped_plate` |

> [程式] 這不是 bug（功能正常，只是分類不精確），但在採購/工單分流時，CAD 師傅會拿到標記為 plate_cut 但實際需要放樣的板。

### 風險 3：`flat_bar` 的 item_class 和 manufacturing_type 不一致

[程式] `flat_bar` → `item_class=FABRICATED_PART` 但 `manufacturing_type=RAW_CUT`。

這在邏輯上是正確的（扁鋼是型鋼裁切，但用途是加工件），但在採購單上：
- `item_class=fabricated_part` → 採購認為要發包加工
- `manufacturing_type=raw_cut` → 工單認為只是裁切

[推測] 建議保持現狀，但 `RAW_CUT` 的扁鋼和 `RAW_CUT` 的管路如果出現在同一張工單，需要靠 `role=flat_bar` vs `role=pipe` 來區分語意。

### 風險 4：category fallback 的雙路徑

[程式] `item_class_for()` 和 `manufacturing_type_for()` 有兩層 fallback：
1. role → enum lookup
2. category → enum lookup

問題在於 `CATEGORY_ITEM_CLASS` 把所有 `鋼板類` 都對應到 `FABRICATED_PART`，而 `ROLE_ITEM_CLASS` 把 `FLAT_BAR` 也對應到 `FABRICATED_PART`。目前兩條路結果一致。但如果未來某個 category 被拆分（例如「鋼板類」拆成「標準鋼板」和「異形鋼板」），而 role mapping 沒跟上，就會出現同一塊板兩種分類。

[推測] 這是 Phase 3 遷移期的過渡設計，短期 OK。

### 風險 5：`_PLATE_NAMES = {"Plate"}` 的舊 fallback 可能誤判

[程式] `material_summary.py` 第 27 行：`_PLATE_NAMES = {"Plate"}` 和第 48 行的 `base.startswith("Plate")`。

改名後的新 name（如 `59_lug_plate_wing_a150_...` 或 `TYPE 59 翼形角板`）不會觸發這個 fallback。但如果有任何 legacy code 仍然產出 `Plate_*` 開頭的名字，`_classify_entry` 的 `entry.role` 為空時就會走這個路徑。改名計畫完成後應移除這個 fallback。

---

## 對 Type 59 的建議

### 1. 命名三層分離 — ✅ 已正確

[程式] Type 59 是目前唯一正確示範三層分離的 type：

| 層級 | 值 | 用途 |
|------|-----|------|
| `entry.name` | `TYPE 59 翼形角板` | 人類讀的品名 |
| `entry.part_key` | `59_lug_plate_wing_a150_b130_p25_c50_t12` | 程式/機器識別 |
| `entry.stock_id` | `PL-XXXXXXXX` | 庫存/PDM 主鍵 |

[推測] 這比 STEEL_PLATE_NAMING_PLAN.md 討論的「把什麼都塞進 name」更乾淨。name 保持人類友善，part_key 保持可解析，stock_id 保持穩定。

### 2. shape_spec 人類格式 — ✅ 非常清楚

[程式] `lug_shape_spec = "A150 x B130 x P25 x C50 x t12"` — 帶前綴標籤，CAD 師傅不必查表就能對照圖面。

[推測] 其他異形板應該跟進這個格式，而非純數字串。

### 3. 顯示名稱 — ⚠️ 小建議

[程式] `_LUG_DISPLAY_NAME = "TYPE 59 翼形角板"` — 清楚，但若未來要查「所有翼形板」，搜「翼形」會命中，搜 `wing` 不會。

[推測] 中英文並存更好：`TYPE 59 翼形角板 (Lug Plate)`。不影響程式邏輯，純 UI 友善。

### 4. 重量計算 — ✅ 正確

[程式] `gross_area = A×B`、`cutout_area = (B-C)×(A-25)/2`、`net_area = gross - cutout`。重量用 `net_area` 計算，比舊版外框矩形更精確。

---

## 建議採納

1. **[程式] 已實作** — `item_class_for()` / `manufacturing_type_for()` 的 role-first + category-fallback 雙路徑設計 → 不需改動
2. **[程式] 已實作** — `analysis_result.add_entry()` 自動呼叫 `item_class_for()` 和 `manufacturing_type_for()` 填入 → 不需改動
3. **[程式] 已實作** — `summary_export.py` 已輸出 `item_class` 和 `manufacturing_type` 兩欄 → 不需改動
4. **[程式] 已實作** — Type 59 的 `part_key`、`stock_id`、`shape_kind`、`gross_area/cutout_area/net_area` 模式 → 作為其他 type 遷移的範本
5. **[推測]** `shape_kind` 應補上白名單定義（`rect` / `wing` / `arc` / `lugz` / `saddle`），放在 `GeometryHints` 的 docstring 或 `plate_shape_reference.md` 中

---

## 需要人工確認

1. **Lug Plate 的 shape_kind**：[程式] Type 59 用 `"wing"`，但 STEEL_PLATE_NAMING_PLAN.md 討論用 `"lugz"`。需統一。我建議用 `"lugz"`（避免和 wing_plate role 混淆），但最終由你決定。
2. **M-34 Lug Plate TYPE-C**：[程式] Type 25/26/36/39 等也產出 LUG PLATE，但走 M-34 標準件表，形狀可能和 Type 59 不同。M-34 的 shape_kind 應該是什麼？需看 M-34 圖面。
3. **弧形板的 shape_spec 參數順序**：弦長 / 弧高 / 板寬 → 需定義順序並寫進 `plate_shape_reference.md`。
4. **ComponentRole 補 SPRING**：目前 `category="彈簧類"` 存在但沒有對應的 `ComponentRole.SPRING`。是刻意不補，還是遷移中？

---

## 不建議採納

1. **不建議把 `item_class` / `manufacturing_type` 塞進 `entry.name`**。Type 59 已經示範了正確做法：name = 人類品名，分類資訊走獨立欄位。塞進 name 只會讓 regex 更複雜、未來改 enum 時被迫改 name。

2. **不建議現在啟動 `MACHINED`**。`MACHINED` enum 已定義但無使用。等有實際需求（例如 CAM 端需要區分「純切割板」和「切割+鑽孔板」）再啟用。提前啟用只會讓所有有孔的 M42 板都跳成 `machined`，反而模糊 `plate_cut` vs `shaped_plate` 的界線。

3. **不建議把 STEEL_PLATE_NAMING_PLAN.md 的命名格式直接當成 `entry.name`**。那份文件討論的格式比較適合 `part_key`（程式可解析），不適合 `name`（人類讀）。Type 59 的 `part_key` 寫法（`59_lug_plate_wing_a150_b130_p25_c50_t12`）已經同時滿足可讀和可解析，建議其他 type 跟進這個格式，而非 §十二 的純數字串。

---

*Deepseek Notes — 2026-06-03 | 依據程式碼盤點 + 分類設計審查*
