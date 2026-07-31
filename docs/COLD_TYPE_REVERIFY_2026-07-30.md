# Cold-support Type 全系列原圖複驗與加工圖資料基線

日期：2026-07-30

## 結論

冷保溫系列不只原先盤點到的 11 個 60 以上 `xxC` Type。`python_app/assets/Type/`
實際共有 37 個 cold-support Type、58 頁 Type 原圖：

- `01C~26C`：26 個 Type、42 頁。
- `109C, 110C, 112C, 113C, 114C, 115C, 116C, 117C, 119C, 120C, 121C`：
  11 個 Type、16 頁。

37 個 Type 現在全部具有 runtime handler、JSON config、catalog entry、UI 說明與
drawing-truth regression tests。Catalog 已無 cold-support placeholder。

## 判讀原則

每個 Type 都以對應的 C-series PDF 為第一真值，逐頁檢查 designation、管徑表、
CR 組別、figure/branch、數量、組立尺寸與可證實的 finished cut。

本輪同時沿用加工圖契約：

1. 組立高度、中心距、外框尺寸不可直接冒充 finished cut 或 flat development。
2. 原圖可證實的管徑對照、CR 表、型鋼規格、數量、孔／扣件與 branch 必須保存。
3. 片件輪廓、接觸曲線、現場切配或供應商資料不完整時，回傳結構化零重量
   reference 與 blocker，不以矩形外框或相近型鋼估算。
4. 同一編號存在多個合法來源列時必須明選。例如 Type 16C 的 CR2.5 分別有
   1/2 與 3/4 吋管，不允許只用 CR 編號猜測。
5. 原圖中的不規則數值照圖保留，不做「看起來比較合理」的平滑修正。

## Type 01C~10C

| Type | 原圖 | 本輪保留的資料 |
|---|---|---|
| 01C | C-1 | H、N-9 lower component 與 A/S branch |
| 02C | C-2 | line size 到 Supporting Pipe B 的完整對照 |
| 03C | C-3 | line、H 與調整式 small-bore 結構 |
| 04C | C-4 | line 到 Pipe B/F 的對照與 lower component |
| 05C | C-5 | line 到 Pipe B/C 的 elbow-trunnion 表 |
| 06C | C-6 | H、lower component 與 small deep-cold branch |
| 07C | C-7/C-8 | Pipe B/E、PU Block 與 sliding branch |
| 08C | C-9/C-10 | Pipe B/C/D/E/G/J、PU Block 與 fixed/guide branch |
| 09C | C-11 | line、H、lower component 與 adjustable branch |
| 10C | C-12/C-13 | F/K、Pipe B/C/D/E/G/J、PU Block 完整表 |

## Type 11C~19C

| Type | 原圖 | 本輪保留的資料 |
|---|---|---|
| 11C | C-14/C-15 | cradle group、A/B branch、扣件與 optional cradle length |
| 12C | C-16 | CR/line designation 與 wood-resting trunnion references |
| 13C | C-17/C-18 | large-bore cradle groups 與 B branch |
| 14C | C-19/C-20 | CR、rod size、L 與 trapeze references |
| 15C | C-21 | 三組 pipe/cradle 表與 optional cradle length |
| 16C | C-22 | CR2.5~CR28 的 Pipe OD/T1/R/T/A 與 tie-bend B/D/J |
| 17C | C-23/C-24/C-25 | CR2.5~CR40 的 Bar Q/RG/H/W/reinforcement 表 |
| 18C | C-26/C-27 | CR2.5~CR29 的 U-bolt/RD/W/H/L/size/cut/quantity 表 |
| 19C | C-28 | line size 到 trunnion pipe 的對照 |

Type 17C 的 CR34 `H=495`，以及 Type 18C 的 CR17 `H=252`、CR22 `W=597`、
CR25 `H=357` 均為原圖表列值，已鎖入測試，不自行改成連續趨勢值。

## Type 20C~26C

| Type | 原圖 | 本輪保留的資料 |
|---|---|---|
| 20C | C-29/C-30/C-31 | vessel-to-bare-pipe 三個 construction branch |
| 21C | C-32/C-33/C-34 | vessel-to-hot-pipe 三個 branch 與 shoe height |
| 22C | C-35/C-36/C-37/C-38 | A/B、CR、line、C 與四圖 branch |
| 23C | C-39 | trunnion CR、pipe、C/B 與 frame references |
| 24C | C-40 | braced trunnion dimensions 與 references |
| 25C | C-47 | sliding braced trunnion dimensions 與 M-34 interface |
| 26C | C-48 | T1/T2 trunnion-on-trunnion branch 與 M-34 interface |

## Type 109C~121C

此 11-Type 波次的逐項判讀保留在
`docs/TYPE_60_PLUS_REVERIFY_2026-07-30.md`。其中：

- Type 113C 依 source row 計算 Member M 型鋼備料長 C。
- Type 117C 計算 Member M finished cut `C-9`。
- Type 121C 計算左右兩支 H125 Member Q。
- 其餘 Type 保留來源尺寸與 component chain，但不將組立尺寸換成虛構重量。

## Cold-component M 圖

另檢查三張 cold-component 原圖：

- `M-6-PIPE CLAMP C.pdf`
- `M-30-BEAM ATTACHMENT C.pdf`
- `M-34-LUG PLATE C.pdf`

三者已存在於 `m6_table.py`、`m30_table.py`、`m34_table.py`，並已登錄
`component_table_registry.py`；本輪不重複建立第二套資料。

## 驗證

- Cold catalog：37/37 有 config、doc、drawing；placeholder 0。
- Cold config metadata：37/37 有 `data_updated_at` 與 `data_update_note`。
- `test_type01c_26c_source_fabrication.py` 與
  `test_type109c_121c_source_fabrication.py`：75 passed。
- 全庫基線在全 Type 建立時為 `pytest -q` 643 passed；cold-component phase 1
  完成後為 664 passed，phase 2 完成後為 681 passed，phase 3 完成後為
  695 passed。
- `python validate_tables.py`：`VALIDATION COMPLETE`，40 個既有
  `phase 2L-A unmanaged material entry` soft warnings。
- Table JSON coverage：37/37 Type tables 有 config 與 JSON bridge；全域只剩
  `PENETRATION HOLE` 為 calculator-only anchor。

## 後續加工圖工作

全 Type 建立完成後，第一批共用零件 `N-9/N-10/N-12/N-12A/N-27/N-28`
已完成並接回十個 host Types，詳見
`docs/COLD_COMPONENT_PHASE1_2026-07-30.md`。

第二批 cradle／insulation 高依賴組件 `N-1~N-5/N-20~N-26` 亦已完成並接回
十四個 host Types，詳見 `docs/COLD_COMPONENT_PHASE2_2026-07-30.md`。

第三批 base／anchor／restraint 組件 `N-6/N-7/N-7A/N-8/N-8A` 已完成並接回
七個 host Types。N-7/N-7A rod 可精算，nuts 仍為零重量；N-8/N-8A 無 flat
development，詳見 `docs/COLD_COMPONENT_PHASE3_2026-07-30.md`。

這仍不代表 37 個 Type 全部能直接出加工圖；N-1/N-4 材料、N-3/C-14 淨輪廓、
N-5 molded volume、N-6 thread engagement、N-7/N-7A thread/nuts、
N-8/N-8A flat development 與 host cradle developments 仍是 blocker。
下一批可轉向 `N-11/N-13/N-14/N-15/N-16/N-19`。
