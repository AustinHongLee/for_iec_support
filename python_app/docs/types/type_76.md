# Type 76 — 120° Large-Pipe Pad

| 項目 | 內容 |
|---|---|
| 圖面 | D-91 |
| 編號 | `76-{line_size}B` |
| 範圍 | 26"~42" 的來源表列尺寸 |
| 來源 | 中威與 22A profile |
| 狀態 | 幾何基準已知；實際展開與厚度未給時阻擋 |

D-91 指定 120°、軸向長 400 mm、12t minimum，並允許由 main pipe 切取或以 carbon-steel plate 製作。這不會唯一決定展開寬或實際厚度，因此舊版 `π×OD×120/360×400×12t` 估重已停用。

只有同時提供 `pad_developed_width_mm` 與 `pad_thickness_mm`（且厚度不小於 12 mm）時，系統才輸出可算重量與展開板尺寸；否則為零重量 reference。
