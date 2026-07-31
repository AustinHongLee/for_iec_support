# Cold Component Phase 3 — N-6 / N-7 / N-7A / N-8 / N-8A

日期：2026-07-30

## 範圍

本輪逐張渲染並目視核對：

- `N-6-SPECIAL BASE PLATE.pdf`
- `N-7-SPECIAL U-BOLT SUB.pdf`
- `N-7A-SPECIAL U-BOLT SUB1.pdf`
- `N-8-STRAP-1.pdf`
- `N-8A-STRAP-2.pdf`

五張均為 image-only PDF，文字抽取沒有可用內容，因此表值以高解析渲染圖逐列核對。

## N-6

已保存：

- finished assembly height 200 mm。
- Ø150×12 round base plate。
- Ø10 half hole。
- 3in SCH.40 A53 Gr.B pipe，source OD callout 89 mm。
- Ø15 pipe cross hole，hole bottom 距 plate top 7 mm。
- 3in 3000# coupling，OD 108、length 54。
- full female / pipe National Pipe Straight Threads。
- pipe-to-base 6 mm weld。

未把 `200-12` 直接當 pipe cut。原圖沒有釋出 pipe/coupling thread engagement，
且 base plate/coupling material grade 與 coupling unit weight未標示，所以 N-6
是 geometry lookup-ready，但仍為 weight/fabrication partial。

## N-7 與 N-7A

兩張表都涵蓋 CR2.5~CR29，但不是同一表的別名：

- R、rod A、B 大致共用。
- D thread length 與 E leg dimension 明顯不同。
- CR3 的 C 也有來源差異：N-7 為 105，N-7A 為 106。
- designation 分別為 `SUB-{CR}` 與 `SUB1-{CR}`。

U-bolt rod 依原圖中心線幾何：

`developed length = π × B / 2 + 2 × E`

rod-only 重量依 carbon-steel density 7.85e-6 kg/mm³ 計算。四顆 finished hex nuts
沒有 thread standard、grade 或 supplier unit weight，維持零重量採購 reference；
整組 `weight_ready=False`，但 rod 重量可用。

## N-8

依 cradle number CR5~CR25 查表，保存：

- R / A / B / T。
- strap width 100 mm。
- 2-Ø22 holes。
- hole center 距兩端各 32 mm，故來源列滿足 `A=B+64`。
- 2 組 3/4in×50 machine bolt/nut。

T 隨 CR 分成 10/12/16 mm。A/B/R/T 是 formed dimensions；原圖沒有 flat
developed length 或 bend allowance，因此不可用 `A×100×T` 當平板重量。

## N-8A

N-8A 的選型鍵不是 CR，而是 line size：

| Line size | R | A | B | T |
|---:|---:|---:|---:|---:|
| 6in | 87 | 328 | 264 | 10 |
| 8in | 113 | 380 | 316 | 10 |
| 10in | 140 | 434 | 370 | 10 |

雖然檔名是 `STRAP-2`，原圖 designation note 寫的是 `STR1-{LINE}B`；runtime
保留原圖 `STR1`，不自行改成 STR2。其 flat development、material grade 與
bolt/nut grade/weight 同樣未釋出。

## Type 串接

已接入七個 host Types：

- 04C：N-6。
- 18C：N-7。
- 20C：6/8/10in branch 的 N-8A。
- 22C：2in 以下 N-7A；3/4in branch N-8。
- 114C：3/4in branch N-8。
- 115C：2in 以下 N-7A；3/4in branch N-8。
- 116C：FIG-A N-7。

分支不命中時不建立該組件；例如 Type 20C 的 ≤4in 與 12~24in 不會誤套 N-8A。

## 加工圖成熟度

本輪遵守「可供未來加工圖使用」的輸出邊界：

- N-7/N-7A 保存 bend centerline、rod diameter、D thread、E leg 與 developed length。
- N-8/N-8A 保存 formed geometry、孔徑/孔位與 bolt callout，但不創造 flat blank。
- N-6 保存所有可讀 assembly 尺寸，但不猜 thread engagement 與 pipe cut。
- 所有不足項均輸出 component/source/parameters/fabrication blockers。

## Registry 與驗證

- Component modules：71/71。
- lookup-ready：45。
- partial-lookup：3。
- metadata-only：23。
- `pytest -q`：695 passed。
- Cold-support/component dedicated tests：127 passed。
- `validate_tables.py`：`VALIDATION COMPLETE`。
- 既有 soft warnings：40 個 `phase 2L-A unmanaged material entry`，本輪未增加。
