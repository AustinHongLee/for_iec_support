# Type 76 — Large-Pipe Pad Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-91 |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | Large-pipe pad support |
| 適用範圍 | 26"~42" |
| 狀態 | 已實作 calculator；重量由圖面幾何計算 |

---

## 系統本質

Type 76 是大管徑用的 120 度 pad support。圖面沒有尺寸表，只有固定幾何：

- `FOR PIPE SIZE 26" ~ 42"`
- `PAD CUT FROM MAIN PIPE OR FAB. FROM C/S PLATE 12t MIN.`
- 角度 `120°`
- 長度 `400`

---

## 編碼格式

```text
76-{line_size}B
```

範例：

```text
76-30B
```

---

## Calculator Handoff

Calculator 使用 pipe OD 查表後計算：

```text
weight = (pi * OD * 120/360) * 400 * 12t * steel_density
```

這代表重量採 12t minimum plate，不會知道現場是否實際 cut from main pipe。

---

## 殘留風險

- 38" 不在目前 `pipe_table.py` OD map，因此未列入支援尺寸
- 若實際 pad 由 main pipe cut，厚度可能不是 12t；目前保守採圖面 minimum
