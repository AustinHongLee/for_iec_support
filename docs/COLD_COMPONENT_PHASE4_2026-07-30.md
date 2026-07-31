# Cold Component Phase 4 — 2026-07-30

## 範圍

逐張視覺複驗 DSP-500-006 Rev.0：

- `N-11-EXPANSION BOLT.pdf`
- `N-13-VESSEL CLIPS.pdf`
- `N-14-VESSEL CLIPS.pdf`
- `N-15-U-BAND.1.pdf`
- `N-16-U-BAND.2.pdf`
- `N-19-SLIDE PLATE A.pdf`

同時重開宿主 `17C.pdf`（C-23/C-24/C-25）、`114C.pdf`（C-57~C-59）與 `116C.pdf`（C-62/C-63），避免把組件表的 datum 直接覆蓋宿主表。

## 結果

| Component | 已完成 | 可計重範圍 | 尚未釋出 |
|---|---|---|---|
| N-11 | EB-1/4~7/8 的 L、thread、R.C. hole、tensile/shear 與 SF=5 設計值 | purchased weight 不計 | manufacturer、material/coating、unit weight、host fixed-plate K |
| N-13 | Type 5：2x10t plates、170x160 elevation、2-DIA22/plate、L75/L100 尺寸鏈、6 mm weld | 不計 clip weight | vessel Q/R、theta、B、t 所決定的平面 contour；設備廠材料 |
| N-14 | Type 6：2x12t plates、170x190 elevation、4-DIA22/plate、9/8 mm weld | 不計 clip weight | 同 N-13 的 vessel plan inputs |
| N-15 | CR2.5~CR12 D/T/RG/H/W、中性線展開 | U-band carbon-steel geometry weight | carbon-steel grade；因此 flat pattern ready，但不是完整 fabrication release |
| N-16 | CR14~CR40 D/T/RG/H/W、`H+10` leg、兩支 Member M cut、hole/bolt spec | U-band + Member M known-steel weight | carbon-steel grade、joint/weld、bolt grade/nuts/unit weight |
| N-19 | `SLP-A-AABB-LLWW` 解碼；3.6t SS upper 與 3.6t CS backing rectangles | 已知兩片 metal weight | PTFE thickness/grade/density/bonding；SS/CS grade |

## 重要來源差異

### 17C 與 N-16 必須雙軌保存

C-24/C-25 是 Type 17C 的宿主組立表；N-16 是 U-band/Member-M 組件表。兩者的 H/RG 不一定同 datum，也不一定數值相同：

- CR14：C-24 H=224；N-16 H=214，另有 10 mm end extension，U-band straight leg=224。
- CR26：C-25 H=360；N-16 H=370，另有 10 mm end extension，U-band straight leg=380。

所以 runtime 會同時保留 `source_rows.cradle` 與 `resolved_components.N-16`，不再試圖把其中一份平滑成另一份。

### N-11 / N-9 revision conflict

N-11 Note 寫「N-9 Type B/E/G/L/M」；本批供應的 N-9 Rev.0 有 B/E/G/J，但沒有 L/M。處理原則：

- B/E/G 是兩張圖的交集，可依 N-10 `expansion_bolt_J` 接入 4 支 N-11 EB。
- J 雖有 expansion-bolt hole，但不在 N-11 Note 清單，不自動套用，保留明確 warning。
- 不虛構已不存在的 L/M host route。

## 宿主接線

- Type 06C/07C/08C/09C/10C：N-9 B/E/G 接 N-11；J 保留來源衝突。
- Type 17C：CR2.5~12 接 N-15；CR14~40 接 N-16、兩支 Member M 與 C-24/C-25 的 2/4 支 machine-bolt reference。
- Type 114C：10 吋以下接 N-13；12~24 吋接 N-14。
- Type 116C FIG-A：接 N-13；FIG-B/C 不誤接。
- N-19：目前沒有 supplied host Type 明確引用，先提供可查的 parametric component API，不猜宿主。

## 加工圖成熟度

- N-15/N-16 已保留 inner radius、thickness、neutral-line flat development、straight-leg datum、Member-M cuts 與 known-steel weight。
- `flat_pattern_ready` 不等於 `fabrication_ready`：carbon-steel grade 未釋出時仍阻擋正式加工發圖。
- N-13/N-14 不把 170x160/190 elevation envelope 當成完整 plate blank；vessel-side curve 與 plan working points 未齊前只作 vendor reference。
- N-19 不用 10 mm overall stack 反推並宣稱 PTFE 成品厚度；PTFE 保持零重量、待 product specification。

## 驗證

- `python -m pytest -q python_app/tests/test_cold_component_phase4.py`：14 passed。
- cold component / host 相關回歸：141 passed。
- 完整 `python_app/tests`：709 passed。
- `python python_app/validate_tables.py`：`VALIDATION COMPLETE`。
- 既有 phase 2L-A unmanaged-material soft warnings：40（未新增 unconditional failure）。
- component registry：51 lookup-ready / 3 partial-lookup / 17 metadata-only / 0 missing。
