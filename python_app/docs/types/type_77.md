# Type 77 — Saddle Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-92 |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | Large-pipe saddle support |
| 適用範圍 | 26"~40" |
| 狀態 | 已實作 calculator；重量為估算 |

---

## 系統本質

Type 77 是大管徑 saddle support。圖面 note 指定 saddle material 與 pipe material identical or similar，並可帶 anchor type 註記。

---

## 編碼格式

```text
77-{line_size}B[(anchor_type)]
77-{line_size}B-(anchor_type)
```

範例：

```text
77-26B-(A)
```

---

## 尺寸表

| Line size | A | B | C | T | H |
|-----------|---:|---:|---:|---:|---:|
| 26" | 200 | 35 | 600 | 12 | 650 |
| 28" | 200 | 35 | 600 | 12 | 650 |
| 30" | 250 | 40 | 650 | 12 | 700 |
| 32" | 250 | 40 | 650 | 12 | 700 |
| 34" | 250 | 45 | 750 | 12 | 750 |
| 36" | 250 | 45 | 750 | 12 | 750 |
| 40" | 300 | 50 | 850 | 16 | 800 |

---

## Calculator Handoff

目前輸出單一 `SADDLE` item。重量使用 bounding geometry 估算：

```text
weight = (C*H + A*B) * T * steel_density
```

---

## 殘留風險

- PDF 無文字層，尺寸表由 rendered bitmap AI visual transcription 建立
- 圖面沒有 unit-weight 欄位；目前重量是 bounding estimate
- Anchor type 只做 warning 註記，實際 anchor detail 需查 D-80A table B
