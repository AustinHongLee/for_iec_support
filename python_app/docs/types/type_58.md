# Type 58 — D-69 U-Bolt Plate Support

> 2026-07-31 依中威 D-69 與 M-26 重製並補入扣件理論估重。只有中威來源可用。

## 輸入

`58-{LINE SIZE}B-{A|B}`

FIG 必填；缺少 A／B 不再自動當成 FIG-A。

## BOM 與幾何

- Steel plate 1 片：L、B、T 逐列查 D-69。
- 兩孔：孔徑與孔距逐列查 D-69。
- M-26 U-bolt rod 1 支：名義展開 `π×B/2 + 2×E`，rod-only 重量可算。
- M-26 finished hex nuts 4 只：依棒徑及比例六角幾何列理論估重；供應商成品重仍待確認。
- FIG-B：保留圖上的 fillet weld `X`。

Plate 的材料只寫 `Carbon Steel (grade not specified in D-69)`；M-26 只寫 Carbon Steel，不再虛構 A36／SS400。

Plate 下料與孔位可直接出加工資料。M-26 的 B／C／D／E 足以產生名義成形幾何，但材料 grade、thread pitch／class／runout、加工切斷餘量與供應商螺帽成品重未釋出，因此整套支撐仍保持 fabrication blocked。
