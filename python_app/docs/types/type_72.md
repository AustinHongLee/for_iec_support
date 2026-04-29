# Type 72 — Strap Support

| 項目 | 內容 |
|------|------|
| 圖號 | D-87 |
| 圖名 | DETAIL OF PIPE SUPPORT |
| 分類 | 小管徑 strap support |
| 適用範圍 | 3/4"~4" |
| 狀態 | 已實作 calculator，M-54 strap 已 table-backed |

---

## 系統本質

Type 72 是小管徑管線用的 strap support。管子由 `STRAP FIG.2` 包覆固定，strap 兩端以 expansion bolt 固定在支撐面。

圖面直接標註：

- `STRAP FIG.2 SEE M-54`
- `2-Ø11 BOLT HOLES`
- `FOR EB-3/8" EXP. BOLT (M-45)`

---

## 編碼格式

```text
72-{line_size}B
```

圖面 note 範例：

```text
72-2B
```

拆解如下：

| 段位 | 例 | 意義 |
|------|----|------|
| `72` | `72` | Type number |
| line size | `2B` | 管徑 |

---

## 尺寸表

| Line size | A | B | T | C | H | R | D |
|-----------|---:|---:|---:|---:|---:|---:|---:|
| 3/4" | 30.0 | 110 | 6 | 32 | 13.4 | 15.0 | 20 |
| 1" | 36.6 | 120 | 6 | 32 | 16.7 | 18.3 | 20 |
| 1-1/2" | 51.6 | 140 | 6 | 50 | 24.2 | 25.8 | 20 |
| 2" | 63.6 | 150 | 6 | 50 | 30.2 | 31.8 | 20 |
| 2-1/2" | 76.0 | 220 | 9 | 65 | 36.5 | 38.0 | 40 |
| 3" | 92.0 | 230 | 9 | 65 | 44.5 | 46.0 | 40 |
| 3-1/2" | 105.0 | 240 | 9 | 65 | 50.8 | 52.5 | 40 |
| 4" | 117.6 | 255 | 9 | 65 | 57.2 | 58.8 | 40 |

---

## Calculator Handoff

目前 calculator 只做保守 BOM：

| 構件 | 來源 | 精度 |
|------|------|------|
| Strap | M-54 FIG.2 | M-54 table lookup；重量由 `B×C×T` 扣除 Fig.2 兩個 Ø11 孔計算 |
| Expansion bolt | M-45 `EB-3/8` | table lookup；數量固定 2 SET |

---

## 殘留風險

- M-54 / Type 72 PDF 都是 vector drawing；尺寸表由 rendered bitmap AI visual transcription 建立，建議 reviewer spot-check
- M-54 圖面未提供 unit-weight 欄位，重量由尺寸與 carbon steel 密度計算
