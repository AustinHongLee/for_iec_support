# Type 56 — D-67／D-67A Pipe Stop

> 2026-07-30 全重製。只有中威來源可用；保留原圖 A～R 查表，但不再把未尺寸化的組件拆成虛構矩形板或整支母 H 型鋼。

## 輸入

`56-{LINE SIZE}B`

## BOM 真值

| 管徑 | 系統輸出 |
|---|---|
| 3/4"～2-1/2" | PL100×100×6，2 片；BOM 與加工圖可用 |
| 3"～4" | `FAB. FROM 6t PLATE` 的 Member C assembly reference，2 組 |
| 5"～14" | `CUT FROM H...` 的 Member C assembly reference，2 組 |
| 16"～24" | `FAB. FROM 12t PLATE` 的 Member C assembly reference，2 組 |
| 26"～42" | D-67A support assembly 2 組，加 D-91 pad reference 1 組 |

3" 以上的 reference 暫為零重量，因圖面沒有完整拆片、保留截面、切割路徑或組焊定位。

## D-91

D-67A 可確認：

- 120° 接觸角
- 軸向長度 400 mm
- 厚度至少 12 mm
- 由主管切取或採同材質

在主管材質與實際厚度未確認前，不計 pad 重量，也不輸出下料圖。
