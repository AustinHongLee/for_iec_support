# M/N Component Table Status

建立時間：2026-04-21 14:45 +08:00  
用途：讓人、Claude、Type 總覽都能分清楚「已建檔入口」與「已可查表精算」。

---

## 狀態定義

| 狀態 | 意義 | 可否用於精算 |
|---|---|---|
| `lookup-ready` | 已有可被 Type calculator 查詢的尺寸/重量或可計算資料 | 視該 table 的 `weight_ready` 與 evidence 而定 |
| `partial-lookup` | 只有部分欄位可查，例如 rod/load；完整尺寸或重量尚未轉錄 | 不可精算，只能作受限 lookup / 估算 fallback |
| `metadata-only` | 已建立 Python module 與 PDF 來源入口，但尚未轉錄尺寸表 | 不可精算，只能追蹤來源 |
| `missing` | 尚未建立 component module | 不可引用 |

目前 registry 狀態：

| 指標 | 數量 |
|---|---:|
| component modules | 71 / 71 |
| lookup-ready | 60 |
| partial-lookup | 3 |
| metadata-only | 8 |
| missing modules | 0 |

重點：`71/71` 代表 **全部有入口**，不是全部已精算。工程可信度請看 `lookup-ready`、`partial-lookup` 與各 table 的 `weight_ready`。

---

## Component Table 維護規則

原則：**資料不可混放；邏輯可以共用。**

中級推理模型執行 component table 時，照以下規則即可：

| 規則 | 要求 |
|---|---|
| 一張 PDF 一個 table file | 例如 M-4 的 raw table values 應放 `m4_table.py`，不要藏在 common |
| common 只放邏輯 | normalize、builder、weight formula、validation helper 可以共用 |
| raw values 不放 common | `TYPE / LINE SIZE / LOAD / B / C / D / E / F / G / H` 這種 PDF 表格值應留在各自檔案 |
| 修改資料只改單檔 | 若 M-4 PDF 改值，理想上只改 `m4_table.py`，不影響 M-5/M-6/M-7 |
| status 要拆開 | `lookup_ready`、`source_transcribed`、`weight_ready` 不可混為一談 |

Clamp family 補充：

- `m4_table.py`~`m10_table.py` 應各自保存自己的 PDF 轉錄表
- `m_clamp_common.py` 只應負責把各表轉成統一輸出格式
- 若某一張 clamp table 只轉錄 rod/load 而缺 B/C/D/E/G/H，status 必須降為 `partial-lookup`

---

## M-Series

| Component | Name | Module | Status | Notes |
|---|---|---|---|---|
| M-1 | SPECIAL BASE PLATE | `m1_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-3 | ADJUSTABLE CLEVIS | `m3_table.py` | lookup-ready | Type 62 FIG-E；21列尺寸/負載已轉錄，formed assembly成品重量未給 |
| M-4 | PIPE CLAMP A | `m4_table.py` | lookup-ready | source table values now live in `m4_table.py`; weight remains estimated because PDF has no unit-weight column |
| M-5 | PIPE CLAMP B | `m5_table.py` | partial-lookup | rod/load rows now live in `m5_table.py`; B/C/D/E/G/H and source weight still pending |
| M-6 | PIPE CLAMP C | `m6_table.py` | partial-lookup | rod/load rows now live in `m6_table.py`; B/C/D/E/G/H and source weight still pending |
| M-7 | PIPE CLAMP D | `m7_table.py` | partial-lookup | rod/load rows now live in `m7_table.py`; B/C/D/E/G/H and source weight still pending |
| M-8 | PIPE CLAMP E | `m8_table.py` | lookup-ready | Type 62 FIG-L；9列B~H與650~1050°F負載已轉錄，formed-half展開/成品重量仍blocked |
| M-9 | PIPE CLAMP F | `m9_table.py` | lookup-ready | Type 62 FIG-M；7列C~K與750~1050°F負載已轉錄，clamp/U-bolt展開/成品重量仍blocked |
| M-10 | PIPE CLAMP G | `m10_table.py` | lookup-ready | Type 62 FIG-N；7列OD range/C~M與950~1075°F負載已轉錄，clamp/U-bolt展開/成品重量仍blocked |
| M-11 | RISER CLAMP A | `m11_table.py` | lookup-ready | Type 49 FIG-A；兩片formed-strip毛重可算，孔位/fastener成品仍blocked |
| M-12 | RISER CLAMP B | `m12_table.py` | lookup-ready | Type 49 FIG-B；150/50直段及兩片formed-strip毛重可算，孔位/fastener成品仍blocked |
| M-13 | PIPE ROLL A | `m13_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-21 | TURNBUCKLE | `m21_table.py` | lookup-ready | Type 62/65 hanger |
| M-22 | MACHINE THREADED ROD | `m22_table.py` | lookup-ready | Type 62/64 rod |
| M-23 | WELDED EYE ROD | `m23_table.py` | lookup-ready | Type 65 |
| M-24 | FORGED STEEL CLEVIS | `m24_table.py` | lookup-ready | Type 62 |
| M-25 | WELDLESS EYE NUT | `m25_table.py` | lookup-ready | Type 62/64 |
| M-26 | U-BOLT | `m26_table.py` | lookup-ready | Type 57/58 reference |
| M-27 | ANGLE BRACKET | `m27_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-28 | BEAM ATTACHMENT A | `m28_table.py` | lookup-ready | Type 65 |
| M-29 | BEAM ATTACHMENT B | `m29_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-30 | BEAM ATTACHMENT C | `m30_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-31 | STEEL WASHER PLATE | `m31_table.py` | lookup-ready | Type 62 FIG-A；方板扣中心圓孔淨重可算，3-1/2in原圖D=75保留 |
| M-32 | LUG PLATE A | `m32_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-33 | LUG PLATE B | `m33_table.py` | lookup-ready | Type 62 FIG-Q；12列尺寸/負載已轉錄，pipe-contact輪廓/重量仍blocked |
| M-34 | LUG PLATE C | `m34_table.py` | lookup-ready | vessel / trunnion group |
| M-35 | LUG PLATE D | `m35_table.py` | lookup-ready | has markdown doc |
| M-36 | LUG PLATE E | `m36_table.py` | lookup-ready | has markdown doc |
| M-37 | LUG PLATE F | `m37_table.py` | lookup-ready | legacy lookup |
| M-41 | LUG PLATE P | `m41_table.py` | lookup-ready | Type 49 FIG-A；A/B/C/D/T polygon blank可算，pipe-end prep仍blocked |
| M-42 | BASE PLATE SYSTEM | `m42_table.py` | lookup-ready | core `m42.py` uses this |
| M-45 | EXPANSION BOLT | `m45_table.py` | lookup-ready | no unit weight column in some use cases |
| M-47 | COMPRESSED GASKET | `m47_table.py` | lookup-ready | Type 13 |
| M-52 | SPRING WEDGE | `m52_table.py` | lookup-ready | dimensional lookup, not weight-ready |
| M-53 | STRAP PUBS2 | `m53_table.py` | lookup-ready | dimensional lookup, not weight-ready |
| M-54 | STRAP | `m54_table.py` | lookup-ready | dimensional + calculated weight |
| M-55 | U-BAND | `m55_table.py` | lookup-ready | dimensional lookup; weight remains estimated because no source unit-weight column |
| M-56 | PIPE CLAMP H | `m56_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-57 | NON-FERROUS PIPE SADDLE | `m57_table.py` | lookup-ready | Type 118~120；actual pipe OD 驅動 roll/cut geometry |
| M-58 | U-BOLT A | `m58_table.py` | lookup-ready | Type 119/120 small branch；rod 可精算，finished nuts 無單重 |
| M-59 | U-BAND A | `m59_table.py` | lookup-ready | Type 119/120 large branch；R/H/W 與中性層展開可精算 |
| M-60 | SLIDE PLATE A | `m60_table.py` | metadata-only | 待 PDF 視覺轉錄 |

---

## N-Series

目前 N-series 全部已有 module。第一批 N-9/N-10/N-12/N-12A/N-27/N-28、
第二批 N-1~N-5/N-20~N-26，以及第三批 N-6/N-7/N-7A/N-8/N-8A
均已完成原圖 lookup。N-27 具備完整來源幾何與密度；N-7/N-7A 可精算
U-bolt rod，但 finished nuts 仍無單重。N-5 無成品淨體積，N-8/N-8A
無 flat development；各 table 仍須依 `weight_ready` 與加工 blocker 使用。

| Component | Name | Module | Status |
|---|---|---|---|
| N-1 | COLD INSULATION SUPPORT | `n1_table.py` | lookup-ready |
| N-2 | COLD SUPPORT LAYER | `n2_table.py` | lookup-ready |
| N-3 | COLD SUPPORT LAYER CONSTRUCTION | `n3_table.py` | lookup-ready |
| N-4 | COLD INSULATION PROTECTION | `n4_table.py` | lookup-ready |
| N-5 | MODLDED THERMAFORM | `n5_table.py` | lookup-ready |
| N-6 | SPECIAL BASE PLATE | `n6_table.py` | lookup-ready |
| N-7 | SPECIAL U-BOLT SUB | `n7_table.py` | lookup-ready |
| N-7A | SPECIAL U-BOLT SUB1 | `n7a_table.py` | lookup-ready |
| N-8 | STRAP-1 | `n8_table.py` | lookup-ready |
| N-8A | STRAP-2 | `n8a_table.py` | lookup-ready |
| N-9 | LOWER COMPONENT OF BASE COLD SUPPORT.1 | `n9_table.py` | lookup-ready |
| N-10 | LOWER COMPONENT OF BASE COLD SUPPORT.2 | `n10_table.py` | lookup-ready |
| N-11 | EXPANSION BOLT | `n11_table.py` | lookup-ready |
| N-12 | VESSEL CLIPS.1 | `n12_table.py` | lookup-ready |
| N-12A | VESSEL CLIPS.2 | `n12a_table.py` | lookup-ready |
| N-13 | VESSEL CLIPS | `n13_table.py` | lookup-ready |
| N-14 | VESSEL CLIPS | `n14_table.py` | lookup-ready |
| N-15 | U-BAND.1 | `n15_table.py` | lookup-ready |
| N-16 | U-BAND.2 | `n16_table.py` | lookup-ready |
| N-19 | SLIDE PLATE A | `n19_table.py` | lookup-ready |
| N-20 | CRADLE NO. OF COLD SUPPORT.1 | `n20_table.py` | lookup-ready |
| N-21 | CRADLE NO. OF COLD SUPPORT.2 | `n21_table.py` | lookup-ready |
| N-22 | CRADLE NO. OF COLD SUPPORT.3 | `n22_table.py` | lookup-ready |
| N-23 | CRADLE NO. OF COLD SUPPORT.4 | `n23_table.py` | lookup-ready |
| N-24 | CRADLE NO. OF COLD SUPPORT.5 | `n24_table.py` | lookup-ready |
| N-25 | CRADLE NO. OF COLD SUPPORT.6 | `n25_table.py` | lookup-ready |
| N-26 | CRADLE NO. OF COLD SUPPORT.7 | `n26_table.py` | lookup-ready |
| N-28 | WOOD BLOCK | `n28_table.py` | lookup-ready |
| N27-PU BLOCK | PU BLOCK | `n27_pu_block_table.py` | lookup-ready |

---

## 後續升級順序

建議下一批不要平均用力，先補會直接影響現有 Type 估算值的 component：

| Priority | Component | Why |
|---|---|---|
| 1 | M-1 / M-13 / M-27 / M-29 / M-30 / M-32 | hot-support metadata-only components |
| 2 | M-56 / M-60 | remaining metadata-only clamp/slide components |
| 3 | M-55 reviewer spot-check | M-55 已 lookup-ready，但重量仍是幾何估算 |
