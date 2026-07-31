# 獨立公式稽核裁決紀錄（2026-07-30）

本紀錄處置兩份獨立唯讀稽核報告：

- `獨立公式稽核報告_第一批_2026-07-30.md`
- `獨立公式稽核報告_第二批_2026-07-30.md`

裁決仍以原始 PDF 為最高資料依據。來源互相矛盾時不以推論補成確定 BOM
或加工尺寸，而是保留原值、替代讀法、warning 與 fabrication blocker。

## 已由原圖複驗並修正

| 範圍 | 裁決與實作 |
|---|---|
| Type 49 designation | 接受 D-60 正式四段語意，拒絕缺 FIG 的 `49-{size}B`；regex 同時支援 `1-1/2` 混合分數。 |
| M-12 展開 | 逐尺寸表列 L 優先於固定草圖 150/50。已知扁鋼展開改由 `L-OD-2T` 加半圓中性層弧長；150/50 與 L 的差額保留為 source conflict，左右直段仍不宣告為加工釋出。 |
| M-11/M-12 fasteners | 兩個 bolt-with-nut 位置另列零重量採購 reference，不再只藏在 clamp 規格字串。 |
| D-60 FIG-B lug | 未直接補 M-41。3 吋以上新增零重量 source-conflict reference，明列 FIG-B 圖形疑似 lug、只有 FIG-A 有 M-41 引線及 NOTE 2 遺失。 |
| Type 17C / C-23 vs N-15 | CR5/CR6 的 host `50x6` 與 N-15 `75x10` 衝突明列；runtime 保留由 W 公式支持的 N-15 組件值，不把 host 欄靜默套入下料。 |
| N-11 / N-9 | grout 型別差異改成完整雙向描述：N-9 NOTE 2 為 A/B/E/G，N-11 為 B/E/G/L/M，僅 B/E/G 是交集。 |
| N-13/N-14 | 補 N-13 6 mm weld、3/4" bolt 規格，以及 N-14 L130x130x12、160 free-end plate depth、18/12 offsets 等加工參考欄位。 |
| N-16 | 型鋼 kg/m 明列為共用專案 lookup、標準未證實；C-24/C-25 的 2/4 bolt 數仍保留，但標成 provisional host callout 並輸出 source-conflict blocker。 |
| N-19 | 保存 NOTE 與剖面對 L/W 的兩種讀法；現行幾何讀法不變。PTFE 厚度另記可由 10-3.6-3.6 推得 2.8 mm，但密度與產品規格仍未釋出。 |
| M-58 | 確認 B 是兩腳內淨距，展開修正為 `π×(B+rod_dia)/2+2E`；輸出分開保存 `inside_clear_B_mm` 與 `centerline_span_mm`。目前實際呼叫 M-58 的 Type 119/120 已受測；Type 118 現行 handler 並未呼叫 M-58。 |
| Type 114C | 2 吋以下補 N-7A SUB1 rod 與四顆 nuts，並停止虛構該分支的 `B=F+13`。 |
| Type 116C FIG-B | 補 N-12 Type 1、N-28 Wood Block 1、4 studs、8 nuts、A193/A194 grades、4-DIA22 與 180/40/100 幾何、N-12A reference 及 320 kg/m³ PU 例外。 |
| N-24/N-25/N-26 load | N-24 的 KG 與 N-25/N-26 的 LB 衝突明列；保留 source raw value，但在裁決前不再產生 canonical kg/lb 換算值，也不可用於自動載重選型。 |
| 大管徑 cradle matrix | 重新逐格查看尚未核對的 54 格；連同報告已核 36 格，共 90/90 均與 `start+6k` 相符。runtime 仍改為 15×6 明列矩陣，測試鎖住全部 90 格，避免未來規則壓縮掩蓋來源異常。 |
| M-58/M-59 maturity | `weight_ready` 統一解釋為「組件在 runtime 是否有來源可證的重量路徑」，並記錄實際計算位置；不再把「表模組本身是否執行數學」混成另一套語意。 |
| M-57／Type 118~120 | 重新查看 M-57 與 D-131~D-134。M-57 一組為兩片 180° saddle、四片 drilled lug、兩組對向 bolt/nut joints；rubber/neoprene lining 是兩片 180°、合計 360°，不是只包半圓。runtime 改以實體件數輸出，總已知鋼重保持不變。 |
| Type 120 D-134 | E=`OD/2+2H`、F=`1.5H` 與 collar `T+3` 維持；D-134 自己的 collar bolt 表與 M-57 不同，改逐組採 `1/4x40`、`3/8x50`、`1/2x60`、`5/8x80`、`3/4x90`，每組兩支。原圖未釋出 collar material grade，移除虛構的 A36/SS400。 |
| M-26／Type 57~59 | 確認 B 為 rod 中心距、C 為外寬、D 為螺紋段、E 為端部至彎曲中心線。M-26 rod 名義展開為 `π×B/2+2E`，rod-only 重量可由圓鋼體積計算；四只 finished nuts 改列獨立零重量 reference。材料 grade、thread pitch/class/runout、切斷餘量及 nut product weight 未釋出，因此完整加工圖仍 blocked。 |
| M-53／M-54 follow-up | M-53 的 A 是明示平板展開總長；D+3 孔在 ≤4" 為 2 孔、≥6" 為 4 孔，現行 Type 73 路徑正確。M-54 的 B 是成形後外形尺寸，不是平板展開；原圖沒有 bend allowance／neutral-line release，Type 72/78 維持零重量 blocker 正確。 |
| 全域重量／材質覆寫鏈 | 專案層只在 deep-copy 結果上將 entry quantity、subtotal 與 weight output 各乘支撐數量一次；材料彙總直接使用 scaled entries，未再乘第二次。新增 M-26 專案數量回歸鎖住 rod weight 與四只 nuts 的倍率，並確認 global `upper_material` 不會覆寫 M-26 明示的 Carbon Steel。 |
| 全型號重量欄位不變量 | 從現有測試擷取 480 組 `analyze_single` 呼叫做動態掃描；353 組成功案例共 1,152 筆 entry。未發現負值、非有限值或重量二次放大。掃描抓到共用 `add_pipe_entry` 未填 `qty_subtotal`，使所有管材單組與專案彙總的數量小計維持 0；已修為 `quantity × factor`，並新增單組／專案三組／聚合層回歸及 `validate_tables.py` 全域 guardrail。 |
| UI 稽核資訊落地 | 支撐總覽改顯示 runtime 實際材料，不再讓不使用全域材質的 Type 誤顯示 SUS304。總覽新增圖面來源與 `BOM/加工` 狀態；選中支撐可查看逐零件密度值、密度依據、密度覆核及加工成熟度，並可只看待確認零件。側欄與匯出就緒提示也會區分「BOM 可匯出」和「已可出加工圖」，但不改變任何既有計算值或精算放行規則。 |

上述 calculation/config 變更均更新對應 `data_updated_at` /
`data_update_note`；Type 49、114C、116C 的 UI 說明同步修正。

## 保留為來源衝突，未擅自裁決

- D-60 FIG-B 是否實際需要 M-41。
- M-12 草圖 150/50 的真正設計意圖與左右直段釋出值。
- N-16 machine bolt 的最終總數，以及型鋼單位重採用的正式標準。
- N-19 的 L/W 文字與剖面語意何者優先。
- N-24/N-25/N-26 大管徑允許載重的真正單位；數列疑似力值的觀察不足以
  取代設計確認。
- Type 17C C-23 CR5/CR6 host BAR Q 是否為原圖抄寫錯誤。
- 共用鋼板重量函式對未識別的材質字串仍沿用 legacy 7.85 g/cm³ fallback；
  這包含部分只由來源寫成 `Stainless Steel`、`matching main line` 或未釋出
  grade 的項目。此行為沒有改寫材質名稱，但密度不是由原圖直接證實。現在每筆
  plate entry 會輸出 `density_g_cm3`、`density_source` 與
  `density_requires_review`；legacy fallback 明列為
  `legacy_unverified_default_7_85`。在建立正式的 density/grade override 契約前，
  不把這些重量宣告成採購或加工最終值。

這些項目現在會暴露為 source conflict / provisional / blocker，不會再被
系統包裝成已確定的加工或安全資料。

## 複驗後未判為程式錯誤

- M-41 polygon 面積、數量與材質 suffix；M-11 半圓中性層模型；
  N-15/N-16 U-band 中性層模型；M-59 U-band 模型均維持。
- CR13 沒有來源列值，既有拒絕行為正確，不做內插。
- Type 114C 的 22" 與 1-1/4" 是宿主範圍推論；cold-core 沒有表列組合時
  仍回 unresolved，沒有虛構 F/H/B。
- 10"/12" pipe OD 的 0.05 mm 差異對目前結果可忽略，且尚未證明專案表
  應改採另一套小數精度，本輪不動共用 pipe table。
- 大管徑 `start+6k` 本身經 90 格複驗沒有算錯；改成明列矩陣屬防回歸，
  不是數值更正。

## 本輪後仍未釋出的加工資料

- M-57 elastomer product weight、finished fastener product weight。
- D-134 collar／pour shoulder 的完整切割 recipe、field-pour material 與 collar
  material grade。
- M-26 thread pitch/class/runout、製程切斷餘量、Carbon Steel grade 與 finished
  nut 標準／單重。
- M-53 gusset 精確輪廓／件數；M-54 strap 平板展開／bend allowance。

這些資料不足均保留為 blocker；沒有用外框、供應商猜值或其他 Type 的表格
代替原圖釋出。
