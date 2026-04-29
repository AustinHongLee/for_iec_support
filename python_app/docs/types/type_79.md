# Type 79 — U-Band Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-94 |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | U-band support |
| 適用範圍 | 5"~24" |
| 狀態 | 已實作 calculator；M-55 已接線，重量仍為估算 |

---

## 系統本質

Type 79 是 U-band 型支撐，圖面標註：

- `U-BAND SEE M-55`
- `IF USED AS ANCHOR`

目前 repo 已建立 `data/m55_table.py` component table，calculator 會從 M-55 查 `PUBD1-{line_size}B` 尺寸。  
但 M-55 圖面沒有 source unit-weight 欄位，因此重量仍以 U-band blank `B×E×T` 幾何估算。

---

## 編碼格式

```text
79-{line_size}B[(anchor_type)]
```

範例：

```text
79-8B(A)
```

---

## 尺寸表欄位

`data/m55_table.py` 轉錄：

```text
PIPE SIZE / A / B / C / D / F / H / J / T / E / R
```

---

## Calculator Handoff

目前輸出單一 `U-BAND` item，designation 來自 M-55，例如 `PUBD1-8B`。重量使用：

```text
weight = B * E * T * steel_density
```

這是 M-55 已接線後的保守估算，不是 source unit-weight。

---

## 殘留風險

- M-55 已 component table 化，但 source PDF 無重量欄，因此 Type 79 仍不是重量精算
- PDF 無文字層，M-55 尺寸表由 rendered bitmap AI visual transcription 建立，需要 reviewer spot-check
- Anchor type 目前只視為 weld/detail note，不新增 BOM item
