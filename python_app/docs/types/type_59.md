# TYPE-59 — D-70 Detail Z 翼形角板

| 項目 | 內容 |
|------|------|
| 圖號 | D-70 |
| 分類 | Lug plate side support |
| 適用範圍 | 2 1/2" & smaller, 3"~8", 10"~14" |
| 圖面頁數 | 1 |
| 狀態 | ✅ 已分析 |
| 資料日 | 2026-05-29 |

---

## 系統本質

TYPE-59 是一個以 D-70 Detail Z 翼形角板作為側向固定件的支撐介面。

現行計算規則收斂為一件事：

- BOM 永遠只產生 `TYPE 59 翼形角板`
- `FIG-A` / `FIG-B` 只保留為既有編碼欄位，不會追加 `D-63 shoe`、`D-68 / M-26 U-bolt` 或 `finished hex nut`
- 依 line size group 建立 lug plate；`10"~14"` 為 2 片，其餘為 1 片
- 依材料尾碼決定 lug plate 材質

---

## 編碼格式

```text
59-14B-A(S)
```

拆解如下：

- `59` = Type 編號
- `14B` = line size
- `A` = figure no.，保留在輸入格式中，但不影響 BOM 項目
- `(S)` = 材料符號，來自 `TABLE A`

calculator 端採這個規則：

- `FIG-A` / `FIG-B` 都只會產生翼形角板
- 若有尾碼 `(A)/(S)/(R)`，則 lug plate 材料跟著切換

---

## 圖面構件

| 構件 | 來源 | 說明 |
|------|------|------|
| Lug Plate | 本圖 | 由 `A/B/C/D/T` 查表決定尺寸；顯示規格為 `A x B x P25 x C x t` |
| FIG A/B | 編碼欄位 | 保留輸入相容性，不產生 BOM 差異 |
| Shim | 現場調整 | `C/S SHIM IN FIELD (TYP.)` |

---

## 尺寸表

圖面尺寸表依 line size 分成 3 組：

| 管徑群組 | A | B | C | D | T |
|------|------|------|------|------|------|
| `2 1/2" & smaller` | 80 | 55 | 15 | — | 9 |
| `3"~8"` | 150 | 100 | 50 | — | 12 |
| `10"~14"` | 150 | 130 | 50 | 120 | 12 |

另外有一個 `FOR STAINLESS STEEL ONLY` 欄位，現行 calculator 將其作為不鏽鋼板厚 `S_T`：

| 管徑群組 | 一般 T | 不鏽鋼 T | 片數 |
|------|------|------|------|
| `2 1/2" & smaller` | 9 | 6 | 1 |
| `3"~8"` | 12 | 9 | 1 |
| `10"~14"` | 12 | — | 2 |

---

## Detail Z 淨面積算重模型

Detail Z 不是單純 `A x B x t` 矩形板，而是外接矩形扣掉右上缺角三角形：

```text
毛面積 = A * B
缺角三角形 = (B - C) * (A - 25) / 2
淨面積 = A * B - (B - C) * (A - 25) / 2
重量 = 淨面積 * t * density / 1,000,000
```

缺角斜邊同時保留在計算說明：

```text
斜邊 = sqrt((B - C)^2 + (A - 25)^2)
```

---

## TABLE A — 材料符號

| Main Pipe Material | Lug Plate Material | Symbol |
|------|------|------|
| Carbon Steel | A-283-C | NONE |
| Alloy Steel | A387-22 | `(A)` |
| Stainless Steel | A240-304 | `(S)` |
| Carbon Steel (A516-60) | A516-60 | `(R)` |

calculator 可以直接把 `(A)/(S)/(R)` 映射成 plate material。

---

## Calculator Handoff

### 最小輸入

```text
59-{size}B-{fig}{material_symbol?}
```

### BOM 建議

| FIG | 構件 |
|------|------|
| `A` | `TYPE 59 翼形角板` × plate_qty |
| `B` | `TYPE 59 翼形角板` × plate_qty |

### 建議資料表

```python
TYPE59_TABLE = {
    "2_5_and_smaller": {"A": 80, "B": 55, "C": 15, "D": None, "T": 9},
    "3_to_8": {"A": 150, "B": 100, "C": 50, "D": None, "T": 12},
    "10_to_14": {"A": 150, "B": 130, "C": 50, "D": 120, "T": 12},
}
```

### 實作重點

- `line size` 不是逐一列尺寸，而是先落到 3 個 group
- `FIG-A` / `FIG-B` 不決定中間件，Type 59 不產生 shoe / U-bolt / nut
- `material_symbol` 影響 lug plate material；不鏽鋼 small/medium 同時改用 `S_T`
- lug plate 重量採 Detail Z 淨面積，不再用外接矩形重量

---

## 與相近 Type 的差異

| Type | 本質 | 差異 |
|------|------|------|
| `52` | 梁上 shoe + lateral retaining | `59` 是兩側 lug plate 夾持介面，不是梁上導向框 |
| `58` | U-bolt + steel plate | `59` 有明確 lug plate 幾何與材質符號 |
| `60` | 大管 shoe support | `59` 支援範圍較小，且以 side plate / lug plate 為主 |

---

## 給 Claude 的一句話摘要

> TYPE-59 = 依 line size group 建 Detail Z 翼形角板；規格顯示 `A x B x P25 x C x t`，重量以 `A*B - (B-C)*(A-25)/2` 淨面積計；BOM 永遠只有 `TYPE 59 翼形角板`，不追加 U-bolt 或 finished hex nut。
