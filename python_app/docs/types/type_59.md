# Type 59 — D-70 Detail Z 支撐

> 2026-07-31 依中威、22A 與 20E4588 三來源全重製。FIG-A／FIG-B 現在會產生不同 BOM，不再永遠只列翼形角板。

## 輸入

`59-{LINE SIZE}B-{A|B}{MATERIAL SYMBOL}`

## Detail Z 翼形角板

三來源共用 A／B／C／P25 的翼形淨面積：

`A×B - (B-C)×(A-25)/2`

| 管徑群組 | A | B | C | 一般 t | SS t | 數量 |
|---|---:|---:|---:|---:|---:|---:|
| ≤2-1/2" | 80 | 55 | 15 | 9 | 6 | 1 |
| 3"～8" | 150 | 100 | 50 | 12 | 9 | 1 |
| 10"～14" | 150 | 130 | 50 | 12 | 未給 | 2 |

10"～14" 的不鏽鋼厚度原圖空白。依本專案決議，中威來源 `(S)` 可暫借
同列碳鋼 `T=12 mm` 計算，材料仍是 `A240-304`，並固定列為高風險；
正式 BOM、強度確認、下料及加工圖皆 blocked。22A／20E 未取得相同決議，
仍不可自動借用。

## Figure 與來源差異

- FIG-B：D-68 沒有標 `NOT FURNISHED`。中威／22A BOM 加 M-26 U-bolt rod 1 支與 finished hex nuts 4 只；rod 名義展開為 `π×B/2 + 2×E`，螺帽依棒徑及比例六角幾何列理論估重。材料 grade、螺紋細節、切斷餘量及供應商螺帽成品重仍 blocked。
- 中威／22A FIG-A：pipe shoe 與 L40 明示不供應，不列 BOM。
- 20E FIG-A ≤8"：另列 L40×40×5×150，2 支，現場切割。
- 20E FIG-A 10"～14"：圖上有兩片 6t interface plate，但尺寸不完整；列零重量 reference 並 blocked。
- 20E FIG-B 只到 6"，且 `PAD IF REQ'D SEE D-91` 必須由 `reinforcing_pad_required` 明確確認。若需要 pad，D-91 適用範圍與此分支衝突，仍須工程確認。

材料符號依來源分開；22A 額外支援 `(N)` Alloy 825，20E 只支援空白與 `(S)`。
