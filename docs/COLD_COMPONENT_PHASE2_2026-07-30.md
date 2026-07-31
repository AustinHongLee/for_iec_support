# Cold Component Phase 2 — N-1~N-5 / N-20~N-26

日期：2026-07-30

## 範圍

本輪逐張渲染並目視核對：

- `N-1-COLD INSULATION SUPPORT.pdf`
- `N-2-COLD SUPPORT LAYER.pdf`
- `N-3-COLD SUPPORT LAYER CONSTRUCTION.pdf`
- `N-4-COLD INSULATION PROTECTION.pdf`
- `N-5-MODLDED THERMAFORM.pdf`
- `N-20`~`N-26` 七張 `CRADLE NO. OF COLD SUPPORT`

N-20 原圖標示為 1 of 7，因此不能只轉錄 N-20/N-23；本輪將七頁連續表完整處理。

## 完成內容

### N-1 / N-4

- N-1：CR2.5~CR80 的 R/T1。
- N-1 large-pipe branch：CR32~CR80 的 A/B。
- CR41~CR44 依 pipe family 保留不同 T1：
  - 24in 以下：12 mm。
  - 30in 以上：10 mm。
- N-4：CR2.5~CR80 的 R/T2 與「shield axial length = steel cradle length」。

材料牌號、shield arc development 與 host-specific 淨輪廓未釋出，因此 `weight_ready=False`、`fabrication_ready=False`。

### N-2 / N-3

- N-2：25~200 mm insulation 的 inner/middle/outer layer 組合。
- N-3：
  - jacket = L + 100 mm。
  - foam + vapor barrier = L + 150 mm。
  - multi-layer inner foam = L + 200 mm。
- N-3 只圖示 single/double layer；N-2 的三層系統保留 project-detail blocker。
- N-3 Note 1 回指 C-14 的未顯示資料，不補畫未標示輪廓。

### N-5

已轉錄 160/224/320 kg/m³ 的：

- yield / 1% deflection load。
- compressive strength。
- deformation at yield。
- compressive modulus。
- safety factor 5 engineering strength。
- ambient strength。
- `C * (pi * D * L) / 6` sustainable-load formula。

這些是材料性能，不是成品自重；未有 molded net volume 時不計重量。

### N-20~N-26

- 小管徑表：1/2~24in，25~265 mm，保留原圖空白組合。
- 大管徑表：只接受 30/36/42/48/54/60in，25~200 mm。
- 解析 CR、F、H、PU density 與 allowable load。
- N-20~N-23 load 單位為 kg。
- N-24~N-26 load 單位為 lb；數值與 N-5 320 kg/m³、標準 300 mm support length 的公式一致。
- allowable load 是容量，不是 BOM 重量。

## 多解處理

反查 `CR + pipe size` 時只發現一個實際多解：

| Pipe | CR | 候選 insulation |
|---:|---|---|
| 1.5in | CR12 | 125 / 140 mm |

處理規則：

- 唯一解：自動解析。
- 多解：共同的 R/T1/F/H/load 仍可用，但 layer 保持 unresolved。
- 呼叫者可傳 `overrides={"insulation_thickness_mm": 125|140}` 選定。
- override 不在候選內時直接報錯，不猜最近值。

這與 project-level source profile 的原則一致：來源或工程條件不唯一時必須顯式選擇。

## Type 串接

已接入：

- 11C、12C、13C、14C、15C。
- 17C、18C、22C。
- 114C、115C、116C。
- 119C、120C、121C。

另外：

- 13C/14C/15C large-pipe branch 改為原圖實列 30/36/42/48/54/60in。
- 17C 移除 N-20~N-23 未列的 nominal sizes。
- 22C 的 CR/pipe 現在必須存在於 N-20~N-23；舊測例 `CR9-8B` 改為原圖有效的 `CR10-8B`。
- 114C 的 B 依 C-57/C-59 規則從 `F+13` 解析；115C 依圖面分支從 `F+3` 或 `F+13` 解析，不再把 B 當獨立猜值。
- C-67 Type 119C 的 host range 比 N-20~N-23 明細更廣；host-range-valid 但 N 表未列的 nominal size 可保留 assembly reference，但 F/H/load/insulation 明確 unresolved。
- 114C/115C/116C/120C 若 host 圖面允許、但 N-20~N-26 沒有該 pipe row，也採相同 unresolved 原則，不用鄰近尺寸代填。

## 加工圖成熟度

本輪提升的是選型、尺寸參數、層構造與材料能力，不代表 cold support 整組可直接發加工圖。主要 blocker：

- steel cradle / stiffener / molded half-shell 的淨輪廓與展開未完整。
- N-1/N-4 未指定完整材料牌號。
- N-3 未釋出所有 C-14 detail。
- N-5 沒有成品淨體積。
- allowable load 不可當自重。

所有 Type 輸出均保留 component/source/parameters/fabrication blockers，不把 envelope 當 finished cut。

## Registry 與驗證

- Component modules：71/71。
- lookup-ready：40。
- partial-lookup：3。
- metadata-only：28。
- `pytest -q`：681 passed。
- Cold-support/component dedicated tests：113 passed。
- `validate_tables.py`：`VALIDATION COMPLETE`。
- 既有 soft warnings：40 個 `phase 2L-A unmanaged material entry`，本輪未增加。
