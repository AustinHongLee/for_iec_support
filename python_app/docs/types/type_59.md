# TYPE-59 — Lug Plate Support for Shoe / Bare Pipe

| 項目 | 內容 |
|------|------|
| 圖號 | D-70 |
| 分類 | Lug plate side support |
| 適用範圍 | 2 1/2" & smaller, 3"~8", 10"~14" |
| 圖面頁數 | 1 |
| 狀態 | ✅ 已分析 |

---

## 系統本質

TYPE-59 是一個「兩側 lug plate 夾持」的支撐介面。

它有兩種使用情境：

- `FIG-A`: 用在 insulated pipe，圖面直接指定 `PIPE SHOE (D-63) (NOT FURNISHED)`
- `FIG-B`: 用在 bare pipe，改成 `U-BOLT (D-68 / M-26)`，並依 M-26 note 配 4 顆 finished hex nuts

也就是說，它不是獨立 shoe，而是：

- 左右兩塊 lug plate
- 中間搭配 shoe 或 U-bolt
- 依主管材質決定 lug plate 材料符號

---

## 編碼格式

```text
59-14B-A(S)
```

拆解如下：

- `59` = Type 編號
- `14B` = line size
- `A` = figure no.
- `(S)` = 材料符號，來自 `TABLE A`

圖面明確註記：

- `TABLE A` 的材料符號只在 `FIG.B` 使用

所以 calculator 端應該採這個規則：

- `FIG-A` 可不帶材料尾碼
- `FIG-B` 若有尾碼 `(A)/(S)/(R)`，則 lug plate 材料跟著切換

---

## 圖面構件

| 構件 | 來源 | 說明 |
|------|------|------|
| Lug Plate ×2 | 本圖 | 由 `A/B/C/D/T` 查表決定尺寸 |
| Pipe Shoe | `D-63` | 僅 `FIG-A`，且圖面標 `NOT FURNISHED` |
| U-bolt | `D-68 / M-26` | 僅 `FIG-B`，U-bolt 規格與 rod size 由 M-26 決定 |
| Finished hex nut | `M-26` | 僅 `FIG-B`，4 PCS |
| Shim | 現場調整 | `C/S SHIM IN FIELD (TYP.)` |

---

## 尺寸表

圖面尺寸表依 line size 分成 3 組：

| 管徑群組 | A | B | C | D | T |
|------|------|------|------|------|------|
| `2 1/2" & smaller` | 80 | 55 | 15 | — | 9 |
| `3"~8"` | 150 | 100 | 50 | — | 12 |
| `10"~14"` | 150 | 130 | 50 | 120 | 12 |

另外有一個 `FOR STAINLESS STEEL ONLY` 欄位，表示不鏽鋼情境下有額外尺寸或厚度要求。

如果 Claude 要先把 calculator 寫出來，建議第一版：

- 先完成 `A/B/C/D/T`
- `FOR STAINLESS STEEL ONLY` 先存在 table 中
- 若實作時還不確定如何影響 BOM，可先只保留為 metadata / remark

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
| `A` | Lug Plate ×2 + `D-63 shoe` reference (not furnished) |
| `B` | Lug Plate ×2 + U-bolt (`D-68 / M-26`) + finished hex nut ×4 |

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
- `FIG-A` / `FIG-B` 決定中間件是 `shoe` 或 `U-bolt + finished hex nut`
- `shoe` 在 BOM 是否計入，要跟專案既有「NOT FURNISHED」慣例一致
- `material_symbol` 只影響 lug plate material，不改幾何

---

## 與相近 Type 的差異

| Type | 本質 | 差異 |
|------|------|------|
| `52` | 梁上 shoe + lateral retaining | `59` 是兩側 lug plate 夾持介面，不是梁上導向框 |
| `58` | U-bolt + steel plate | `59` 有明確 lug plate 幾何與材質符號 |
| `60` | 大管 shoe support | `59` 支援範圍較小，且以 side plate / lug plate 為主 |

---

## 給 Claude 的一句話摘要

> TYPE-59 = 依 line size group 建 lug plate；`FIG-A` 配 `D-63 shoe`，`FIG-B` 配 `D-68 / M-26 U-bolt + finished hex nut x4`，材料尾碼只影響 plate material。
