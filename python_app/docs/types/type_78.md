# Type 78 — Small-Pipe Strap Anchor / Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-93 |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | Small-pipe strap anchor/support |
| 適用範圍 | 3/4"~4" |
| 狀態 | 已實作 calculator，M-54 Fig.1 table-backed |

---

## 系統本質

Type 78 是小管徑 strap 型支撐，圖面標註：

- `STRAP FIG. 1 SEE M-54`
- `IF USED AS ANCHOR`

因此 calculator 直接呼叫 `build_m54_item(line_size, fig_no=1)`。

---

## 編碼格式

```text
78-{line_size}B[(anchor_type)]
```

範例：

```text
78-2B(A)
```

---

## Calculator Handoff

| 構件 | 來源 | 精度 |
|------|------|------|
| STRAP | M-54 FIG.1 | table-backed calculated weight |

Fig.1 不扣除 Fig.2 的兩個 Ø11 bolt holes。

---

## 殘留風險

- Type 78 / M-54 PDF 都是 vector drawing；尺寸表由 rendered bitmap AI visual transcription 建立
- Anchor type 目前只視為 weld/detail note，不新增 BOM item
