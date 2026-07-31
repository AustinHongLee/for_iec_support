# Type 57 — D-68 U-Bolt Support

> 2026-07-31 依中威、22A 與 20E4588 三來源分別重製並補入扣件理論估重。

## 輸入

`57-{LINE SIZE}B-{A|B}{MATERIAL SYMBOL}`

- A：SLIDE
- B：FIXED

## BOM

M-26 明確定義一組為：

- 1 支 U-bolt
- 4 顆 finished hex nuts

中威／22A 的 M-26 分成兩筆實體 BOM：

- `M-26 U-BOLT ROD` 1 支：B 為中心距、C 為外寬、D 為螺紋段、E 為端部至彎曲中心線；名義展開為 `π×B/2 + 2×E`，可計 rod-only 重量。
- `M-26 FINISHED HEX NUTS` 4 只：依棒徑及比例六角幾何列理論估重；供應商成品重仍待確認。

M-26 只指定 Carbon Steel，沒有 grade，也沒有 thread pitch／class／runout 或製程切斷餘量。因此圓鋼名義幾何及 U-bolt／螺帽理論重量可用，但尚不能宣告完整加工圖 ready。

## 來源差異

| 來源 | 規則 |
|---|---|
| 中威／22A | M-26 英制表，至 30"；Carbon Steel |
| 20E4588 | 公制表，頁首寫 1/2"～6"；`(S)` 為 Stainless Steel；來源未給腿長／螺紋長／展開 |

20E 的 `(S)` 另加 A240-304 shim plate；厚度依原圖 `BWG #21 = 0.8128 mm`，不是 1.0 mm。

20E 表內有 1/4" 列，但頁首範圍從 1/2" 起。系統保留該列供辨識，但因來源自相矛盾，1/4" 結果保持 blocked。
