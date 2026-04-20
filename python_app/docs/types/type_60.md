# TYPE-60 — Large Bore Shoe Side Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-71 |
| 分類 | Large bore shoe support |
| 適用範圍 | 16"~42" |
| 圖面頁數 | 1 |
| 狀態 | ✅ 已分析（待 calculator） |

---

## 系統本質

TYPE-60 是大口徑管線的 side support / shoe support。

圖面中心概念很清楚：

- `FIG-A` = insulated pipe
- `FIG-B` = bare pipe
- 中間引用 `PIPE SHOE (D-80, 80B) (NOT FURNISHED)`

也就是說 TYPE-60 本身不負責 shoe 幾何，而是負責：

- 左右側板 / lug-like plate
- 與 pipe shoe 的連接幾何
- 依 line size 與 figure 決定板件尺寸

---

## 編碼格式

```text
60-16B-A
```

拆解如下：

- `60` = Type 編號
- `16B` = line size
- `A` / `B` = figure no.

---

## 尺寸表結構

圖面表格欄位：

| 欄位 | 含義 |
|------|------|
| `SUPPORT NO.` | 完整支撐編號，例如 `60-16B-A` |
| `LINE SIZE` | 管徑 |
| `A/B/C/D/E/F/T` | plate 幾何尺寸 |

圖面已經把 `A` 與 `B` 兩組列分開，因此 calculator 最適合直接使用完整 key：

```python
TYPE60_TABLE = {
    "60-16B-A": {...},
    "60-16B-B": {...},
}
```

這樣 Claude 不用額外做 figure 合併判斷。

---

## 構件理解

### FIG-A

- 用於 insulated pipe
- 中間件為 `D-80 / 80B shoe`
- 幾何較對稱，表格中 `F` 為空

### FIG-B

- 用於 bare pipe
- 圖面多出 45° 與 `120°-120°` 幾何表現
- 表格中 `F` 有值，表示 FIG-B 比 FIG-A 多一個附加尺寸

---

## Calculator Handoff

### 最小輸入

```text
60-{size}B-{fig}
```

### 建議 BOM

第一版先保守做這 3 類：

| 構件 | 數量 | 說明 |
|------|------|------|
| Side Plate / Lug Plate | 2 | 尺寸由 `A/B/C/D/E/F/T` 推導或直接展開 |
| Shoe reference | 1 set | `D-80 / 80B`, not furnished |
| Weld remark | — | 視系統是否保留 remark 類構件 |

### 建議實作策略

- 不要試圖從圖形推導公式
- 直接把每一列 `SUPPORT NO.` 做成資料表
- `FIG-A` 與 `FIG-B` 的差異留在 table，不要在 calculator 端硬編碼

### 若要做 plate 展開

Claude 需要先判斷目前系統是：

- 接受「異形板 custom entry」
- 還是只能接受矩形 plate

若只能接受矩形 plate，第一版建議：

- 先用 `custom entry` 或 remark 表示 `TYPE-60 side plate`
- 等你人工確認後再細分成可製造板件

---

## 與相近 Type 的差異

| Type | 本質 | 差異 |
|------|------|------|
| `59` | 小中管徑 lug plate 支撐 | `60` 專注大口徑，且明確引用 `D-80/80B shoe` |
| `52` | 梁上 lateral retaining | `60` 是大管 side support，不是側向 guide frame |
| `66` | shoe 本體 | `60` 不是 shoe，自身只提供外圍支撐件 |

---

## 給 Claude 的一句話摘要

> TYPE-60 最適合做成「完整 support number 對完整尺寸列」的查表型 calculator；鞋座直接引用 `D-80/80B`，不要重算 shoe 幾何。
