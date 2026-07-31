# Type 61 — Trunnion Support

| 項目 | 內容 |
|---|---|
| 圖面 | D-72 / D-73 / D-74 |
| 編號 | `61-{TRUNNION}B-T{1|2}-{H/100}[(P)]` |
| 來源 | 中威 E25-24、22A_5123A、20E4588 已分 profile |
| 狀態 | 直管備料可算；貼管切口、補強板及容量驗算仍需工程輸入 |

## 已證實規則

- T1 為 1 支，T2 為 2 支；`H` 是 trunnion 名義備料長。
- 2" 使用 SCH.80；3"~10" 使用 SCH.40 或更厚；12"/14" 使用 3/8" wall 或更厚。
- `(P)` 只表示需要 reinforcing pad，不足以決定 pad 展開尺寸。
- D-73/D-74 容量核對還需要 main-line size/schedule、材質、設計溫度與 moment。

## 加工圖契約

預設只輸出 trunnion 直管備料重量，並保留 main-line saddle cut blocker。Pad 不再用舊版 `OD+50` 方板；只有明確提供 `pad_developed_length_mm`、`pad_width_mm`、`pad_thickness_mm` 時才計算。即使 pad 尺寸齊全，容量仍需另行核定。
