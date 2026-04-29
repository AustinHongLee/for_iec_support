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
| lookup-ready | 19 |
| partial-lookup | 3 |
| metadata-only | 49 |
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

- `m4_table.py`, `m5_table.py`, `m6_table.py`, `m7_table.py` 應各自保存自己的 PDF 轉錄表
- `m_clamp_common.py` 只應負責把各表轉成統一輸出格式
- 若某一張 clamp table 只轉錄 rod/load 而缺 B/C/D/E/G/H，status 必須降為 `partial-lookup`

---

## M-Series

| Component | Name | Module | Status | Notes |
|---|---|---|---|---|
| M-1 | SPECIAL BASE PLATE | `m1_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-3 | ADJUSTABLE CLEVIS | `m3_table.py` | metadata-only | Type 62 FIG-E 後續優先 |
| M-4 | PIPE CLAMP A | `m4_table.py` | lookup-ready | source table values now live in `m4_table.py`; weight remains estimated because PDF has no unit-weight column |
| M-5 | PIPE CLAMP B | `m5_table.py` | partial-lookup | rod/load rows now live in `m5_table.py`; B/C/D/E/G/H and source weight still pending |
| M-6 | PIPE CLAMP C | `m6_table.py` | partial-lookup | rod/load rows now live in `m6_table.py`; B/C/D/E/G/H and source weight still pending |
| M-7 | PIPE CLAMP D | `m7_table.py` | partial-lookup | rod/load rows now live in `m7_table.py`; B/C/D/E/G/H and source weight still pending |
| M-8 | PIPE CLAMP E | `m8_table.py` | metadata-only | Type 62 lower components 後續優先 |
| M-9 | PIPE CLAMP F | `m9_table.py` | metadata-only | Type 62 lower components 後續優先 |
| M-10 | PIPE CLAMP G | `m10_table.py` | metadata-only | Type 62 lower components 後續優先 |
| M-11 | RISER CLAMP A | `m11_table.py` | metadata-only | Type 49 FIG-A 後續優先 |
| M-12 | RISER CLAMP B | `m12_table.py` | metadata-only | Type 49 FIG-B 後續優先 |
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
| M-31 | STEEL WASHER PLATE | `m31_table.py` | metadata-only | Type 62 lower components 後續優先 |
| M-32 | LUG PLATE A | `m32_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-33 | LUG PLATE B | `m33_table.py` | metadata-only | Type 62 lower components 後續優先 |
| M-34 | LUG PLATE C | `m34_table.py` | lookup-ready | vessel / trunnion group |
| M-35 | LUG PLATE D | `m35_table.py` | lookup-ready | has markdown doc |
| M-36 | LUG PLATE E | `m36_table.py` | lookup-ready | has markdown doc |
| M-37 | LUG PLATE F | `m37_table.py` | lookup-ready | legacy lookup |
| M-41 | LUG PLATE P | `m41_table.py` | metadata-only | Type 49 FIG-A 後續優先 |
| M-42 | BASE PLATE SYSTEM | `m42_table.py` | lookup-ready | core `m42.py` uses this |
| M-45 | EXPANSION BOLT | `m45_table.py` | lookup-ready | no unit weight column in some use cases |
| M-47 | COMPRESSED GASKET | `m47_table.py` | lookup-ready | Type 13 |
| M-52 | SPRING WEDGE | `m52_table.py` | lookup-ready | dimensional lookup, not weight-ready |
| M-53 | STRAP PUBS2 | `m53_table.py` | lookup-ready | dimensional lookup, not weight-ready |
| M-54 | STRAP | `m54_table.py` | lookup-ready | dimensional + calculated weight |
| M-55 | U-BAND | `m55_table.py` | lookup-ready | dimensional lookup; weight remains estimated because no source unit-weight column |
| M-56 | PIPE CLAMP H | `m56_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-57 | NON-FERROUS PIPE SADDLE | `m57_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-58 | U-BOLT A | `m58_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-59 | U-BAND A | `m59_table.py` | metadata-only | 待 PDF 視覺轉錄 |
| M-60 | SLIDE PLATE A | `m60_table.py` | metadata-only | 待 PDF 視覺轉錄 |

---

## N-Series

目前 N-series 全部已有 module，但全部仍是 `metadata-only`，不可視為 cold support 精算表。

| Component | Name | Module | Status |
|---|---|---|---|
| N-1 | COLD INSULATION SUPPORT | `n1_table.py` | metadata-only |
| N-2 | COLD SUPPORT LAYER | `n2_table.py` | metadata-only |
| N-3 | COLD SUPPORT LAYER CONSTRUCTION | `n3_table.py` | metadata-only |
| N-4 | COLD INSULATION PROTECTION | `n4_table.py` | metadata-only |
| N-5 | MODLDED THERMAFORM | `n5_table.py` | metadata-only |
| N-6 | SPECIAL BASE PLATE | `n6_table.py` | metadata-only |
| N-7 | SPECIAL U-BOLT SUB | `n7_table.py` | metadata-only |
| N-7A | SPECIAL U-BOLT SUB1 | `n7a_table.py` | metadata-only |
| N-8 | STRAP-1 | `n8_table.py` | metadata-only |
| N-8A | STRAP-2 | `n8a_table.py` | metadata-only |
| N-9 | LOWER COMPONENT OF BASE COLD SUPPORT.1 | `n9_table.py` | metadata-only |
| N-10 | LOWER COMPONENT OF BASE COLD SUPPORT.2 | `n10_table.py` | metadata-only |
| N-11 | EXPANSION BOLT | `n11_table.py` | metadata-only |
| N-12 | VESSEL CLIPS.1 | `n12_table.py` | metadata-only |
| N-12A | VESSEL CLIPS.2 | `n12a_table.py` | metadata-only |
| N-13 | VESSEL CLIPS | `n13_table.py` | metadata-only |
| N-14 | VESSEL CLIPS | `n14_table.py` | metadata-only |
| N-15 | U-BAND.1 | `n15_table.py` | metadata-only |
| N-16 | U-BAND.2 | `n16_table.py` | metadata-only |
| N-19 | SLIDE PLATE A | `n19_table.py` | metadata-only |
| N-20 | CRADLE NO. OF COLD SUPPORT.1 | `n20_table.py` | metadata-only |
| N-21 | CRADLE NO. OF COLD SUPPORT.2 | `n21_table.py` | metadata-only |
| N-22 | CRADLE NO. OF COLD SUPPORT.3 | `n22_table.py` | metadata-only |
| N-23 | CRADLE NO. OF COLD SUPPORT.4 | `n23_table.py` | metadata-only |
| N-24 | CRADLE NO. OF COLD SUPPORT.5 | `n24_table.py` | metadata-only |
| N-25 | CRADLE NO. OF COLD SUPPORT.6 | `n25_table.py` | metadata-only |
| N-26 | CRADLE NO. OF COLD SUPPORT.7 | `n26_table.py` | metadata-only |
| N-28 | WOOD BLOCK | `n28_table.py` | metadata-only |
| N27-PU BLOCK | PU BLOCK | `n27_pu_block_table.py` | metadata-only |

---

## 後續升級順序

建議下一批不要平均用力，先補會直接影響現有 Type 估算值的 component：

| Priority | Component | Why |
|---|---|---|
| 1 | M-11 / M-12 / M-41 | Type 49 目前仍 custom estimate |
| 2 | M-3 / M-31 / M-33 | Type 62 lower figures 仍有 missing-table warning |
| 3 | M-8 / M-9 / M-10 | Type 62 lower clamp family |
| 4 | N-series first lookup batch | cold support 目前只有 metadata baseline |
| 5 | M-55 reviewer spot-check | M-55 已 lookup-ready，但重量仍是幾何估算 |
