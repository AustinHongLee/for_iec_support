# Work Log

這份檔案用來記錄已完成或已落地的工作，方便 Codex、Claude 與人工判讀同步上下文。

欄位建議：

- `Timestamp`: 區塊標題時間預設代表 `logged_at`，不是自動擷取的檔案 `LastWriteTime`
- `Action`: 做了什麼
- `Files`: 改了哪些檔案
- `Reason`: 為什麼改
- `Status`: `done` / `partial` / `blocked`
- `Safe to reference`: `yes` / `no`
- `Notes`: 額外提醒

## 2026-04-24 00:00:00 +08:00 | Codex

- Action: 將使用者於對話中貼入的 `type` PNG 視為最新版圖面來源，並依此更新 Type 14 / Type 15 家族判讀
- Files:
  - `core/types/type_14.py`
  - `core/types/type_15.py`
  - `docs/types/type_14.md`
  - `docs/types/type_15.md`
  - `validate_tables.py`
  - `coordination/WORKLOG.md`
- Reason:
  - 使用者明確指示：聊天中貼上的 `type.png` 為最新版圖面
  - 需避免沿用舊版 PDF/舊假設，造成 Type 14 / 15 板件數量與 DETAIL "a" 判讀偏差
- Status: done
- Safe to reference: yes
- Notes:
  - Type 14 / 15 最新判讀基準：
    1. `Plate_WING` 固定 4 片
    2. `Plate_STOPPER` 固定 2 片
    3. 10" / 12" 視為 `DETAIL "a"`，改為 2 支橫向 Channel
    4. 非四方板件之形狀資訊寫入 BOM `remark`，供後續加工圖自動化使用

---

## 2026-04-21 16:30:00 +08:00 | Claude (bug fix)

- Action: 修正 Type 59 計算錯誤（對照 VBA A1_Type_Calculator_.bas Sub Type_59）
- Files: `data/type59_table.py`, `core/types/type_59.py`
- Reason:
  1. **板片數量錯誤（最重要）**：Python 一律 qty=2；VBA 為 D=0（小/中管徑 ≤8"）→ qty=1、D≠0（大管徑 ≥10"）→ qty=2。小/中管徑重量多算一倍。
  2. **不鏽鋼厚度**：VBA 有 S_T override（small S_T=6、medium S_T=9）；Python 無此邏輯。
  3. **large group C 值**：VBA C=100；Python table 誤寫 C=50（C 目前未用於重量計算，但資料錯誤）。
- Changes:
  - `type59_table.py`: 加入 `S_T` 欄位與 `plate_qty` 欄位；修正 large C: 50→100
  - `type_59.py`: 讀取 `dims["plate_qty"]`；若 material=A240-304 且 S_T 存在則使用 S_T 作為板厚
- Status: done
- Safe to reference: yes
- Notes: VBA `Case 10 To 12` 僅含 10/12"（不含 14"），但 D-70 文件標示範圍至 14"；Python 沿用文件定義（含 14"），此差異不修改。large group S_T 在 VBA 未定義（S_T=0），故 Python 大管徑 SS 維持 T=12 不作 S_T 覆蓋。

---

## 2026-04-21 16:14:00 +08:00 | Codex

- Action: 依 Claude 三批審查做 P1/P2 系統一致性重構，新增集中 component fallback 規則層並修正 partial lookup 語意
- Files:
  - `core/component_rules.py`
  - `core/types/type_07.py`, `core/types/type_10.py`, `core/types/type_13.py`, `core/types/type_14.py`, `core/types/type_15.py`, `core/types/type_16.py`
  - `core/types/type_62.py`, `core/types/type_64.py`, `core/types/type_65.py`
  - `data/component_table_registry.py`
  - `data/m_clamp_common.py`
  - `data/m4_table.py`, `data/m5_table.py`, `data/m6_table.py`, `data/m7_table.py`
  - `ui/type_manager.py`
  - `validate_tables.py`
  - `configs/type_catalog.json`
  - `docs/COMPONENT_TABLE_STATUS.md`
  - `docs/PROJECT_LOGIC_TREE.md`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 統一 clamp / rod / eye nut / M-28 fallback 估算來源，避免各 Type 自己硬寫不同策略
  - M-5/M-6/M-7 只有 rod/load 可查，不能再被 UI 或 coverage 當作完整 lookup-ready
  - 先處理 Type 13/62/64/65 與 Type 10/07/14/15/16 的高風險一致性，不暴力重寫所有 Type
- Status: done
- Safe to reference: yes
- Notes:
  - component coverage 現為 `71/71` modules, `lookup-ready=19`, `partial-lookup=3`, `metadata-only=49`
  - M-5/M-6/M-7 不再保存 `_BASE_WEIGHT * multiplier` 的 table-side weight estimate；Type fallback 改走 `core.component_rules`
  - Type 62 支援 material overrides；Type 07/14/15/16 支援 upper material overrides 且保留既有預設
  - Type 10 新增 M42 allowed-letter warning (`A/B/E/G`)
  - `validate_tables.py`, `py_compile`, `json.tool` 已通過

---

## 2026-04-21 15:30:00 +08:00 | Claude (review)

- Action: 審核 Codex 的 M-54 strap component table + Type 72 hookup，以及 Type 73/76/77/78/79 calculators
- Files: `data/m54_table.py`, `core/types/type_72.py`, `data/type73_table.py`, `data/type76_table.py`, `data/type77_table.py`, `data/type79_table.py`, `core/types/type_73.py` ~ `type_79.py`
- Reason: REVIEW_HANDOFF.md 要求審核兩個批次
- Status: done
- Safe to reference: yes
- Notes: 兩批均 approve。16 個案例全部通過；validate_tables 27 個 check 全綠；component coverage 32/70 (45.7%)。3 個 low-risk follow-up items 記錄於 REVIEW_HANDOFF.md（Type 72 EXP. BOLT remark 補估算說明；Type 77 saddle comment 改詞；Type 73 strap 與 M-53 需在 M-53 weight_ready 升級時交叉確認）。

---

## 2026-04-21 15:28:00 +08:00 | Codex

- Action: 依「資料不可混放；邏輯可以共用」規則，重新補正 M-4/M-5/M-6/M-7 clamp family table source layout
- Files:
  - `data/m_clamp_common.py`
  - `data/m4_table.py`
  - `data/m5_table.py`
  - `data/m6_table.py`
  - `data/m7_table.py`
  - `core/types/type_62.py`
  - `validate_tables.py`
  - `configs/type_catalog.json`
  - `docs/COMPONENT_TABLE_STATUS.md`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 使用者指出 M-4/M-5/M-6/M-7 若共用 raw values，未來單張 PDF 表值變更時會很難修正
  - 新規則要求 raw PDF/source values 必須留在各 component table file，common 只能放 builder/normalizer/helper
- Status: done
- Safe to reference: yes
- Notes:
  - `m_clamp_common.py` 已移除 clamp series raw map，只保留共用建表與 lookup helper
  - `m4_table.py` 轉錄 M-4 visible table 的 `TYPE / LINE SIZE / LOAD / B / C / D / E / F / G / H`
  - `m5_table.py`, `m6_table.py`, `m7_table.py` 已把 rod/load raw rows 拆回各自檔案
  - M-5/M-6/M-7 仍是 partial transcription，B/C/D/E/G/H 尚待完整視覺轉錄
  - Type 62 不再 import common 舊常數，M-8/M-9/M-10 缺表估算改以 M-4 lookup weight 作為 base
  - `configs/type_catalog.json` 已同步移除 M-5/M-6/M-7 designation inferred wording
  - `validate_tables.py` 與 `py_compile` 已通過

---

## 2026-04-21 15:00:00 +08:00 | Claude (review)

- Action: 審核 Codex 的 Type 62 hanger combination calculator
- Files: `core/types/type_62.py`, `data/type62_table.py`, `docs/types/type_62.md`
- Reason: REVIEW_HANDOFF.md 要求審核
- Status: done
- Safe to reference: yes
- Notes: approve。8 個測試案例全部通過。2 個 low-risk follow-up items 記錄於 REVIEW_HANDOFF.md（FIG-E nut callout 待對圖確認；末端 else 死碼建議改為 raise）。

---

## 2026-04-21 14:38:00 +08:00 | Codex

- Action: 補齊 M/N component table 的全量 metadata baseline
- Files:
  - `data/component_table_registry.py`
  - `data/m1_table.py`, `data/m3_table.py`, `data/m8_table.py`, `data/m9_table.py`, `data/m10_table.py`
  - `data/m11_table.py`, `data/m12_table.py`, `data/m13_table.py`, `data/m27_table.py`, `data/m29_table.py`
  - `data/m30_table.py`, `data/m31_table.py`, `data/m32_table.py`, `data/m33_table.py`, `data/m41_table.py`
  - `data/m55_table.py`, `data/m56_table.py`, `data/m57_table.py`, `data/m58_table.py`, `data/m59_table.py`, `data/m60_table.py`
  - `data/n10_table.py`, `data/n11_table.py`, `data/n12_table.py`, `data/n12a_table.py`, `data/n13_table.py`, `data/n14_table.py`
  - `data/n15_table.py`, `data/n16_table.py`, `data/n19_table.py`, `data/n20_table.py`, `data/n21_table.py`, `data/n22_table.py`, `data/n23_table.py`, `data/n24_table.py`, `data/n25_table.py`, `data/n26_table.py`, `data/n28_table.py`
  - `validate_tables.py`
  - `docs/PROJECT_LOGIC_TREE.md`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 先消除 registry 層的 missing hole，讓每個 M/N PDF 都有可追蹤入口
  - 避免因缺 module 導致後續 Type 重構無法引用 component source
  - 不把尚未視覺轉錄的 PDF 假裝成 lookup-ready
- Status: done
- Safe to reference: yes
- Notes:
  - component modules: `71/71`
  - lookup-ready components: `21`
  - metadata-only components: `50`
  - missing component modules: `0`
  - `MISSING_COMPONENT_TABLES=[]` 只代表沒有缺 module，不代表沒有缺尺寸或重量
  - 後續升級應逐張把 metadata-only module 轉為 dimensional lookup，並同步接回 Type 49/62/79 等 custom estimate

---

## 2026-04-21 14:48:00 +08:00 | Codex

- Action: 補上 M/N component table 的 Markdown 總覽與 Type 總覽狀態顯示
- Files:
  - `docs/COMPONENT_TABLE_STATUS.md`
  - `ui/type_manager.py`
  - `data/component_table_registry.py`
  - `data/n27_pu_block_table.py`
  - `validate_tables.py`
  - `docs/PROJECT_LOGIC_TREE.md`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 使用者在 Type 總覽很難看出 M/N 是否已建 table，以及 table 是 lookup-ready 還是 metadata-only
  - 需要一份 Markdown 作為 M/N component 補表進度的審核入口
- Status: done
- Safe to reference: yes
- Notes:
  - Type 總覽 component 狀態欄現在會顯示 `可查表` 或 `待轉錄`
  - 底部統計新增 `M/N可查表` 與 `M/N待轉錄`
  - 右側 detail 會顯示 component table 狀態與 module file
  - `N27-PU BLOCK` 已納入 metadata-only registry，因此 component-like catalog items 為 `71`
  - 驗證：`validate_tables.py` 全綠；UI load smoke 顯示 lookup-ready `21`、metadata-only `50`、missing `0`

---

## 2026-04-21 14:58:00 +08:00 | Codex

- Action: 將 M-55 U-BAND 從 metadata-only 升級為 dimensional lookup，並接回 Type 79
- Files:
  - `data/m55_table.py`
  - `data/component_table_registry.py`
  - `core/types/type_79.py`
  - `data/type79_table.py`
  - `validate_tables.py`
  - `configs/type_catalog.json`
  - `docs/types/type_79.md`
  - `docs/COMPONENT_TABLE_STATUS.md`
  - `docs/PROJECT_LOGIC_TREE.md`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Type 79 直接依賴 M-55；先解掉會立即降低 missing-table 風險
  - M-55 PDF 表格可視覺判讀，但沒有 source unit-weight 欄，因此只能升級尺寸 lookup，不能升級為重量精算
- Status: done
- Safe to reference: yes
- Notes:
  - component lookup-ready: `22`
  - metadata-only: `49`
  - `79-8B(A)` 現在輸出 `PUBD1-8B`，unit weight 仍為 `3.62`
  - Type 79 不再有 `missing_table` evidence，但仍為 `估算/需審核`
  - `validate_tables.py`、manual smoke、`py_compile`、`json.tool` 均通過

---

## 2026-04-21 15:14:00 +08:00 | Codex

- Action: 建立 component table 維護規則，讓中級推理模型可照規範補表
- Files:
  - `coordination/SOURCE_OF_TRUTH.md`
  - `docs/COMPONENT_TABLE_STATUS.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 使用者指出 M-4/M-5/M-6/M-7 raw values 放在 common file 會讓未來修 PDF 表值時難以定位
  - 需要明確規則：資料不可混放，邏輯可以共用
- Status: done
- Safe to reference: yes
- Notes:
  - 新規則要求每張 component PDF 的 raw table values 放在自己的 `data/*_table.py`
  - common file 僅能放 normalize、builder、weight formula、validation helper
  - status 應拆開 `lookup_ready` / `source_transcribed` / `weight_ready`
  - M-4/M-5/M-6/M-7 已在 status 文件標示為 lookup usable，但 raw PDF table 應拆回各自檔案

---

## 2026-04-21 14:30:00 +08:00 | Claude (review)

- Action: 審核 Codex 的 Type 11 table lookup refactor 與 M-52/M-53 AI visual transcription 批次
- Files:
  - `coordination/REVIEW_HANDOFF.md`
- Reason:
  - 確認 `11:32` 與 `11:46` 兩批 Codex 變更是否可接受，並標示剩餘 caveat
- Status: done
- Safe to reference: yes
- Notes:
  - Verdict: `11:32 Type 11 table lookup refactor — approve`
  - Verdict: `11:46 M-52/M-53 AI visual transcription — approve with standing caveat`
  - Standing caveat: M-52/M-53 幾何數值來自 Codex bitmap 視覺判讀，升級為 `weight_ready=True` 前必須對照原始圖紙手動確認尺寸

## 2026-04-21 14:08:00 +08:00 | Codex

- Action: 建立專案基底邏輯與 Type 關係視覺化地圖
- Files:
  - `docs/PROJECT_LOGIC_TREE.md`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 目前 Type、component table、truth/evidence、catalog 狀態交錯，使用者需要一份能快速看懂專案基底邏輯與每個 Type 關係的地圖
  - 明確區分「calculator 能跑」與「工程可信」，避免把舊 Type 未審核公式誤標為精算
- Status: done
- Safe to reference: yes
- Notes:
  - 新文件包含 Mermaid 資料流、目錄樹、Type 家族樹、component 依賴樹、可信度樹
  - Type 關係表列出目前 `TYPE_HANDLERS` 已接線的 Type、用途、依賴與可信度註記
  - 舊 Type 保守標示為 `未知/需審核`；Type 72/73/76/77/78/79 標示為新契約但仍屬 `估算`
  - `validate_tables.py` 全綠；static doc coverage check 確認 66 個 `TYPE_HANDLERS` key 均有列入文件
  - 這份文件是專案地圖，不是工程圖紙裁決；已同步加入 `REVIEW_HANDOFF.md` 等 Claude spot-check

## 2026-04-21 14:00:00 +08:00 | Claude (residual risk fix)

- Action: 修正三項殘留風險：移除 M-23/M-28 的 1 1/8" 插值 row、M-5/M-6/M-7 designation 改為 PDF 原始格式、Type 65 Stiffener 改為動態幾何計算
- Files:
  - `data/m23_table.py`（移除 1 1/8" inferred row）
  - `data/m28_table.py`（移除 1 1/8" inferred row）
  - `data/m_clamp_common.py`（重構為 per-series rod/load map，designation 改 PCL-B/C/D 格式，涵蓋大管徑）
  - `core/types/type_65.py`（加入 `_STIFFENER_PL` 表 + `_stiffener_pl()` 動態計算）
  - `validate_tables.py`（1 1/8" 斷言改為預期 None）
- Reason:
  - M-23/M-28 原始 PDF 無 1 1/8" 欄位，Codex 插值 row 不可信，移除後由 fallback warning 正確提示
  - M-5/M-6/M-7 有原始 PDF 提供 PCL-B/C/D 型號與 rod size / load，應直接轉錄
  - Stiffener 固定 2.0 kg 過於粗糙，改為依管徑查表後套用鋼材密度公式
- Status: done
- Safe to reference: yes
- Notes:
  - validate_tables 22 checks 全綠
  - `1 1/8"` rod 的 16" 管仍走 fallback（PDF 本來就無此尺寸），這是 catalogue 限制，非程式錯誤

## 2026-04-21 13:46:01 +08:00 | Codex

- Action: 新增中文化 truth/evidence contract bootstrap，並替 Type 72/73/76/77/78/79 補第一批可信度標記
- Files:
  - `core/truth.py`
  - `core/models.py`
  - `core/calculator.py`
  - `core/types/type_72.py`
  - `core/types/type_73.py`
  - `core/types/type_76.py`
  - `core/types/type_77.py`
  - `core/types/type_78.py`
  - `core/types/type_79.py`
  - `data/type77_table.py`
  - `validate_tables.py`
  - `configs/type_catalog.json`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 不應把 Type 01~79 舊公式直接標為可信；先建立相容的新契約，舊 Type 預設 `未知/需審核`，高風險新 Type 先補 evidence
- Status: done
- Safe to reference: yes
- Notes:
  - `AnalysisResult` 保留舊欄位，新增 `meta/evidence`，不破壞 export/UI 既有使用
  - Type 72/73/76/77/78/79 catalog 新增 `truth_level/confidence/requires_review/missing/trust_notes`
  - `79-8B(A)` 現在標 `估算`、`confidence=0.35`、`requires_review=True`，且 evidence 明確包含 M-55 missing-table
  - Claude 15:30 follow-up item 1/2 已順手完成；item 3 保留到 M-53 未來升級 `weight_ready=True` 時處理
  - `validate_tables.py`、`json.tool`、`py_compile`、manual smoke、`git diff --check` 均通過；diff check 僅有既有 LF/CRLF warning

## 2026-04-21 13:16:47 +08:00 | Codex

- Action: 實作 Type 73/76/77/78/79 calculators，並補尺寸表、docs、catalog 與固定驗證
- Files:
  - `data/type73_table.py`
  - `data/type76_table.py`
  - `data/type77_table.py`
  - `data/type79_table.py`
  - `data/type72_table.py`
  - `core/types/type_73.py`
  - `core/types/type_76.py`
  - `core/types/type_77.py`
  - `core/types/type_78.py`
  - `core/types/type_79.py`
  - `core/calculator.py`
  - `configs/type_catalog.json`
  - `docs/types/type_73.md`
  - `docs/types/type_76.md`
  - `docs/types/type_77.md`
  - `docs/types/type_78.md`
  - `docs/types/type_79.md`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Type 73/76/77/78/79 均為 PDF 無文字層但圖面簡單的 support；可先用 visual transcription + 明確估算 warning 補成開發可用 calculator
- Status: done
- Safe to reference: yes
- Notes:
  - Type 73 支援 `73-{line_size}B-{S|G}`，輸出 strap/spring/stud bolt/washer，6" 以上另加 gusset
  - Type 76 支援 `76-{line_size}B`，依 120° arc × 400L × 12t minimum 計算 pad
  - Type 77 支援 `77-{line_size}B[(anchor_type)]`，輸出 estimated SADDLE
  - Type 78 支援 `78-{line_size}B[(anchor_type)]`，直接接 M-54 Fig.1
  - Type 79 支援 `79-{line_size}B[(anchor_type)]`，M-55 尚未建表，暫以 Type79 B×E×T 估 U-BAND 並 warning
  - `validate_tables.py`、`json.tool`、`py_compile`、manual smoke、`git diff --check` 均通過；diff check 僅有既有 LF/CRLF warning

## 2026-04-21 12:56:13 +08:00 | Codex

- Action: 補齊 `M-54-STRAP.pdf` component table，並將 Type 72 strap 改接 M-54 lookup
- Files:
  - `data/m54_table.py`
  - `data/component_table_registry.py`
  - `core/types/type_72.py`
  - `configs/type_catalog.json`
  - `docs/types/m_54.md`
  - `docs/types/type_72.md`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Type 72 的 `STRAP FIG.2 SEE M-54` 已可從 `M-54-STRAP.pdf` 補成可查尺寸表，避免繼續用 Type 72 本地估重 warning
- Status: done
- Safe to reference: yes
- Notes:
  - `M54_TABLE` 轉錄 `PUBS3-3/4B` ~ `PUBS3-4B` 的 `A/B/T/C/H/R/D` 尺寸與 `Carbon Steel` material
  - Fig.2 unit weight 由 `B×C×T` 扣除 `2-Ø11` 孔後依 carbon steel 密度計算；source drawing 無 unit-weight 欄位
  - component coverage 提升到 `32/70 (45.7%)`，lookup-ready components 提升到 `21`
  - `72-2B` smoke：`STRAP PUBS3-2B-2` unit weight `0.34`，無 M-54 warning
  - `validate_tables.py`、`json.tool`、manual smoke、`git diff --check` 均通過；diff check 僅有既有 LF/CRLF warning

## 2026-04-21 12:37:15 +08:00 | Codex

- Action: 實作 Type 72 strap support calculator，並補尺寸表、文件、catalog 與固定驗證
- Files:
  - `data/type72_table.py`
  - `core/types/type_72.py`
  - `core/calculator.py`
  - `docs/types/type_72.md`
  - `configs/type_catalog.json`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Type 72 原本是 placeholder；D-87 已可由 vector PDF render 後 AI 判讀出尺寸表與構件 callout
- Status: done
- Safe to reference: yes
- Notes:
  - 支援格式 `72-{line_size}B`
  - 可查表 component 接 `M-45 EB-3/8`，固定數量 2 SET
  - 當時 `M-54 STRAP FIG.2` 尚未 component table 化；已由 `2026-04-21 12:56:13` 的 M-54 table 批次取代
  - `validate_tables.py` 通過，新增 `type72 strap support OK`

## 2026-04-21 12:27:15 +08:00 | Codex

- Action: 收斂 Claude Type 62 review 的兩個低風險 follow-up
- Files:
  - `core/types/type_62.py`
  - `docs/types/type_62.md`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Claude 指出 FIG-E 是否需補 eye nut / heavy hex nut 待確認，以及 `_add_lower_part` 末端 else 是死碼
- Status: done
- Safe to reference: yes
- Notes:
  - 對照 D-75 FIG-E：無 M-25 / heavy hex nut callout，因此不補 nut，只保留 M-3 Adjustable Clevis placeholder
  - `_add_lower_part` 末端改為 `raise ValueError(f"unhandled lower_fig {lower_fig}")`
  - `validate_tables.py` 已固定 FIG-E 不輸出 `WELDLESS EYE NUT` / `HEAVY HEX. NUT`，並通過驗證

## 2026-04-21 12:07:46 +08:00 | Codex

- Action: 實作 Type 62 pipe hanger combination calculator，並補資料表、文件、catalog 與固定驗證
- Files:
  - `data/type62_table.py`
  - `core/types/type_62.py`
  - `core/calculator.py`
  - `docs/types/type_62.md`
  - `configs/type_catalog.json`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Type 62 原本是 placeholder；D-75/D-76 已可由 vector PDF render 後 AI 判讀出 FIG/M-No. 組合表，可先完成保守 calculator
- Status: done
- Safe to reference: yes
- Notes:
  - 支援格式 `62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]`
  - 可查表 component 接 `M-21/M-22/M-24/M-25/M-28/M-4/M-5/M-6/M-7`
  - 缺表 component `M-3/M-8/M-9/M-10/M-31/M-33` 會明確 warning 為估算
  - `validate_tables.py` 通過，新增 `type62 hanger combination OK`

## 2026-04-21 11:46:23 +08:00 | Codex

- Action: 將 M-52/M-53 從 metadata-only 修正為 AI 視覺判讀後的 dimensional lookup table
- Files:
  - `data/m52_table.py`
  - `data/m53_table.py`
  - `data/component_table_registry.py`
  - `configs/type_catalog.json`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - M-52/M-53 PDF 文字抽取不可用，但 render vector PDF 後可由 AI 視覺判讀；先前保持 metadata-only 的判斷過度保守，應補成可審核尺寸表
- Status: done
- Safe to reference: yes
- Notes:
  - M-52 補 `SPRW-2B~SPRW-24B` 與 spring data；M-53 補 `PUBS2-1B~PUBS2-24B`
  - `weight_ready=False`，本批不推導 unit weight，不把尺寸 lookup 包裝成重量精算
  - `validate_tables.py` 通過；lookup-ready components 從 `18` 提升到 `20`，metadata-only 從 `13` 降到 `11`

## 2026-04-21 11:32:50 +08:00 | Codex

- Action: 將 Type 11 的小五金與 spring 散落常數改成 `type11_table.py` lookup，並補 M-52/M-53 vector-PDF feasibility note
- Files:
  - `data/type11_table.py`
  - `core/types/type_11.py`
  - `core/bolt.py`
  - `data/m52_table.py`
  - `data/m53_table.py`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 先做低風險的單向接線：不改 Type 11 公式，只替換資料來源；M-52/M-53 PDF 目前無法可靠轉錄，故保持 metadata-only 並記錄證據
- Status: done
- Safe to reference: yes
- Notes:
  - `validate_tables.py` 新增 Type 11 hardware table + calculator smoke assertion
  - `analyze_single('11-2B-06G')`、`analyze_single('11-6B-08J')`、`analyze_single('65-16B-2008')` 已通過
  - component coverage 維持 `31/70`；本批是 Type 11 接線前置，不把 M-52/M-53 假升級成 lookup-ready

## 2026-04-21 11:25:37 +08:00 | Codex

- Action: 補齊 Claude residual-risk fix 後的 cleanup，移除 M-23 helper 內不再可達的 `1 1/8"` eye-end weight，新增 M-5/M-7 PDF designation 固定驗證，並修正 handoff wording
- Files:
  - `data/m23_table.py`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Claude 已確認 M-23/M-28 PDF 無 `1 1/8"` catalogue row；helper 內殘留該 key 會誤導後續維護，M-5/M-7 的 PDF designation 也應進入固定驗證
- Status: done
- Safe to reference: yes
- Notes:
  - `validate_tables.py` 新增 `PCL-B-12B`、`PCL-D-8B`、`M-7 2"` 不存在等 assertion
  - `validate_tables.py` 已通過，並手動重跑 `65-12B-2008` / `65-16B-2008`
  - `REVIEW_HANDOFF.md` 改用 `reviewed defects resolved; accepted limitations remain`，避免把 Type 65 accepted limitations 寫成完全沒有 backlog

## 2026-04-21 11:00:00 +08:00 | Claude (review)

- Action: 對 component table 第一波（M-4/M-5/M-6/M-7/M-21/M-24 + Type 13/64/65）完成最後審核；同步審閱第二波（M-47 lookup + M-52/M-53/N-1~N-9 metadata）
- Files:
  - `coordination/REVIEW_HANDOFF.md`（附加 Claude 審核回覆區塊）
  - `coordination/WORKLOG.md`
- Reason:
  - 依 Codex 建立的 review handoff 流程執行最終審核，給定 approve/backlog 判定
- Status: done
- Safe to reference: yes
- Notes:
  - 判定：`approve with minor notes`
  - 5 個 handoff 案例全跑通（`13-6B-05B`、`64-2-8-05A`、`64-1-3-08D`、`65-6B-1505`、`65-16B-2008`）
  - Type 65 source of truth 維持 M-23+M-28（與 `coordination/SOURCE_OF_TRUTH.md` 一致）
  - backlog 建議：1 1/8" rod size 補表為 high-priority（16" 是常見工業管徑）；`_fallback_rod_weight` 可下移到 `component_size_utils`；`designation_inferred` 建議曝露到 BOM remark 欄
  - 無 source conflict

## 2026-04-21 10:27:39 +08:00 | Codex

- Action: 對 coordination 文件做第二輪 audit cleanup，修正不只排序的問題：review 頂層入口、錯誤路徑、舊 timestamp 倒序、以及 IN_PROGRESS 完成時間不一致
- Files:
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 前一輪只修了頂部排序，仍會讓 reviewer 看不到 Claude review 的頂層狀態，也會被錯路徑與舊倒序紀錄誤導
- Status: done
- Safe to reference: yes
- Notes:
  - `REVIEW_HANDOFF.md` 已新增 Claude `Review Result Snapshot`
  - 錯誤的 `SOURCE_OF_TRUTH.md` 路徑已修正為 `coordination/SOURCE_OF_TRUTH.md`
  - `WORKLOG.md` 底部 `18:28` / `18:20` 舊紀錄已改回 recorded timestamp 新到舊
  - `IN_PROGRESS.md` 的 Claude backlog 完成時間已對齊 `WORKLOG.md` 的 `10:00`

## 2026-04-21 10:19:51 +08:00 | Codex

- Action: 修正 coordination 文件的 reviewer 狀態入口與 timestamp 排序，避免 Codex follow-up 被放在較晚的 Claude review 之前
- Files:
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - Claude review 已有 `2026-04-21 11:00:00 +08:00` 記錄，原先 `10:00:48 Codex` 區塊放在其上方會誤導 reviewer 判讀最新狀態
- Status: done
- Safe to reference: yes
- Notes:
  - `WORKLOG.md` 已改成依 timestamp 由新到舊排序
  - `REVIEW_HANDOFF.md` 已補 `Current Review State`，明確標示 Claude `11:00:00` review 是最新 reviewer record
  - Claude `11:00:00` 是 reviewer-provided timestamp；此 entry 依 recorded timestamp 放在其下方，但不要把兩個 agent 的 timestamp 當作已驗證的 wall-clock sequence

## 2026-04-21 10:00:48 +08:00 | Codex

- Action: 收斂 Claude backlog，補齊 `1 1/8"` rod 對應的 `M-23 / M-28` row，將 inferred clamp designation 顯示到 BOM remark，並清理 Type 64/65 的 fallback helper 與 normalize 邏輯
- Files:
  - `data/component_size_utils.py`
  - `data/m22_table.py`
  - `data/m23_table.py`
  - `data/m28_table.py`
  - `data/type64_table.py`
  - `data/type65_table.py`
  - `core/bolt.py`
  - `core/types/type_64.py`
  - `core/types/type_65.py`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 直接落實 Claude 的 minor notes，先消掉 `Type 65` 在 16" case 的 rod/bracket fallback，並把 M-6 的推論 designation 風險顯示到 BOM
- Status: partial
- Safe to reference: yes
- Notes:
  - `65-16B-2008` 現在只剩 `STIFFENER` 估算 warning
  - `64-2-8-05A` / `64-1-3-08D` 現在會在 clamp remark 顯示 `推論 designation` 或 `SEE M-4`
  - `M-23 / M-28` 的 `1 1/8"` row 目前屬 interpolation，不是原始 PDF 精準轉錄
  - `validate_tables.py` 與指定 handoff 案例已通過

## 2026-04-21 09:03:49 +08:00 | Codex

- Action: 補 component table 第二波低風險批次，新增 `M-47` 正式 table、`M-52 / M-53 / N-1~N-9` metadata-only tables，並把 `Type 13` 單向接到 `M-47`
- Files:
  - `data/component_metadata_registry.py`
  - `data/m47_table.py`
  - `data/m52_table.py`
  - `data/m53_table.py`
  - `data/n1_table.py`
  - `data/n2_table.py`
  - `data/n3_table.py`
  - `data/n4_table.py`
  - `data/n5_table.py`
  - `data/n6_table.py`
  - `data/n7_table.py`
  - `data/n7a_table.py`
  - `data/n8_table.py`
  - `data/n8a_table.py`
  - `data/n9_table.py`
  - `data/component_table_registry.py`
  - `data/__init__.py`
  - `core/types/type_13.py`
  - `configs/type_catalog.json`
  - `docs/types/m_47.md`
  - `validate_tables.py`
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 先把低風險、可批量落地的 component intake 工作建起來，同時避免把未轉錄 PDF 假裝成可精算 table
- Status: partial
- Safe to reference: yes
- Notes:
  - component coverage 從 `17/70` 提升到 `31/70` (`44.3%`)
  - 其中 `lookup-ready = 18`、`metadata-only = 13`
  - `Type 13` 現在改由 `M-47` table 取 gasket 尺寸 / 重量
  - `M-52 / M-53 / N-1~N-9` 目前僅為 metadata-only，不應視為 precision-ready table
  - `validate_tables.py` 與既有 handoff 案例 (`13/64/65`) 已通過

## 2026-04-21 08:52:51 +08:00 | Codex

- Action: 固化 Claude 審核交接規則，明確指定 `coordination/REVIEW_HANDOFF.md` 為 review 入口
- Files:
  - `coordination/REVIEW_HANDOFF.md`
  - `coordination/SOURCE_OF_TRUTH.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 讓後續每次 Codex 改動都有固定的 reviewer handoff，不必讓 Claude 從 `git diff` 或零散對話重建上下文
- Status: done
- Safe to reference: yes
- Notes:
  - 後續若需要 Claude 或人工快速審核，請優先查看 `coordination/REVIEW_HANDOFF.md`
  - `WORKLOG.md` 記錄完成事項；`REVIEW_HANDOFF.md` 聚焦審核重點與殘留風險

## 2026-04-21 08:48:29 +08:00 | Codex

- Action: 補齊高優先級 component table 第一波，新增 `M-4 / M-5 / M-6 / M-7 / M-21 / M-24`，並把 `Type 13 / 64 / 65` 接到 component table
- Files:
  - `data/component_size_utils.py`
  - `data/m_clamp_common.py`
  - `data/m4_table.py`
  - `data/m5_table.py`
  - `data/m6_table.py`
  - `data/m7_table.py`
  - `data/m21_table.py`
  - `data/m24_table.py`
  - `data/m22_table.py`
  - `data/m23_table.py`
  - `data/m25_table.py`
  - `data/m28_table.py`
  - `data/type64_table.py`
  - `data/component_table_registry.py`
  - `core/types/type_13.py`
  - `core/types/type_64.py`
  - `core/types/type_65.py`
  - `validate_tables.py`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - 直接回應 component table 覆蓋率不足與 clamp / hanger 類型仍以散落估算值輸出的問題
- Status: partial
- Safe to reference: yes
- Notes:
  - component coverage 從 `11/70` 提升到 `17/70` (`24.3%`)
  - `Type 13` 已改用 `M-4` table
  - `Type 64` 已改用 `M-22 / M-25 / M-4 / M-6`
  - `Type 65` 已改用 `M-23 / M-28`；但 `rod size = 1 1/8"` 目前 table 尚未覆蓋，仍保留 fallback warning
  - `validate_tables.py` 已通過

## 2026-04-20 20:34:34 +08:00 | Codex

- Action: 重新稽核 coordination 與 M-series 補表，修正 M-22 / M-23 designation 規則，補明確時間語義
- Files:
  - `data/m22_table.py`
  - `data/m23_table.py`
  - `validate_tables.py`
  - `coordination/SOURCE_OF_TRUTH.md`
  - `coordination/WORKLOG.md`
  - `coordination/IN_PROGRESS.md`
- Reason:
  - PDF 註記顯示 `M-22` / `M-23` designation 應包含長度，例如 `MTRL-3/8-600`、`WERL-3/8-500`
  - 既有 `WORKLOG.md` 時間為人工記錄，不應被誤解成精準的檔案修改秒數
- Status: done
- Safe to reference: yes
- Notes:
  - 後續若需要精準秒級時間，請以檔案系統 `LastWriteTime` snapshot 為準
  - 本次稽核已重新對照 `M-22 / M-23 / M-25 / M-26 / M-28` 原始 PDF
  - `file_last_write snapshot`: `m22_table.py` / `m23_table.py` / `validate_tables.py` / `SOURCE_OF_TRUTH.md` / `IN_PROGRESS.md` = `2026-04-20 20:35:30 +08:00`
  - `WORKLOG.md` 本身會因為寫入這筆紀錄而再次變動，不把它列入固定秒數 snapshot


## 2026-04-20 20:00:00 +08:00 | Claude

- Action: 實作 Type 58/59/60/64/65 計算器 + 資料表，註冊至 calculator.py，更新 catalog
- Files:
  - `data/type58_table.py` (新增, 24 entries)
  - `data/type59_table.py` (新增, 3 groups + material map)
  - `data/type60_table.py` (新增, 28 entries)
  - `data/type64_table.py` (新增, 14 rod entries + 4 figure combos)
  - `data/type65_table.py` (新增, 14 entries + L bucket)
  - `core/types/type_58.py` (新增 calculator)
  - `core/types/type_59.py` (新增 calculator)
  - `core/types/type_60.py` (新增 calculator)
  - `core/types/type_64.py` (新增 calculator)
  - `core/types/type_65.py` (新增 calculator)
  - `core/calculator.py` (新增 5 個 TYPE_HANDLERS 註冊)
  - `configs/type_catalog.json` (5 entries placeholder→documented)
- Reason:
  - 依 Codex 提供的 handoff docs 實作計算器
  - M-series tables (M-22/23/25/26/28) 為 Codex 施工, calculator 內以 add_custom_entry 佔位
- Status: done
- Safe to reference: yes
- Notes:
  - 10 個測試案例全數通過
  - 鋼材表尺寸已校正 (L90*90*9, C150*75*9)
  - Clamp/bracket 重量為估算值, 待 M-series table 整合後可精確化

---

## 2026-04-20 19:18:00 +08:00 | Codex

- Action: 補齊高優先級 M-series component tables，新增 `M-22 / M-23 / M-25 / M-26 / M-28`
- Files:
  - `data/m22_table.py`
  - `data/m23_table.py`
  - `data/m25_table.py`
  - `data/m26_table.py`
  - `data/m28_table.py`
  - `data/component_table_registry.py`
  - `validate_tables.py`
- Reason:
  - 直接支援 Type 58 / 64 / 65 的 calculator 實作，讓 Claude 可直接查 component 規格
- Status: done
- Safe to reference: yes
- Notes:
  - `validate_tables.py` 已驗證通過
  - component coverage 從 `6/70` 提升到 `11/70`
  - `M-22 / M-23 / M-25` 採「直徑 + 變動長度」設計
  - `M-28` 目前先補 Type-A（圖面 M-28）

## 2026-04-20 19:00:00 +08:00 | Codex

- Action: 建立 AI 協作機制，新增 `coordination` 工作區與協作規則
- Files:
  - `coordination/IN_PROGRESS.md`
  - `coordination/WORKLOG.md`
  - `coordination/SOURCE_OF_TRUTH.md`
- Reason:
  - 避免 Codex 與 Claude 在並行作業時拿到彼此「半改狀態」的檔案當參考
- Status: done
- Safe to reference: yes
- Notes:
  - `IN_PROGRESS.md` 用來標示不穩定檔案
  - `WORKLOG.md` 用來記錄已完成工作
  - `SOURCE_OF_TRUTH.md` 用來定義引用優先順序與衝突處理

## 2026-04-20 18:42:15 +08:00 | Codex

- Action: 新增 Type 58/59/60/64/65 的 PDF 解釋文件，並補強 Type 52 的 calculator handoff
- Files:
  - `docs/types/type_58.md`
  - `docs/types/type_59.md`
  - `docs/types/type_60.md`
  - `docs/types/type_64.md`
  - `docs/types/type_65.md`
  - `docs/types/type_52.md`
- Reason:
  - 提供 Claude 撰寫 calculator 前可直接使用的圖面解釋與實作交接資訊
- Status: done
- Safe to reference: yes
- Notes:
  - 內容偏向 `calculator handoff`
  - 可直接作為 `table + calculate()` 的規格輸入

## 2026-04-20 18:28:00 +08:00 | Codex

- Action: 建立 component table 覆蓋率清單與驗證入口
- Files:
  - `data/component_table_registry.py`
  - `validate_tables.py`
- Reason:
  - 為後續 M/N 系列補表建立盤點基礎，避免純手工追蹤
- Status: done
- Safe to reference: yes
- Notes:
  - 目前 component table 覆蓋率為 `6/70`

## 2026-04-20 18:20:00 +08:00 | Codex

- Action: 批量補齊 30 個已可計算 Type 的分析文件，並讓 UI 自動把有 `type_XX.md` 的項目升級為 `documented`
- Files:
  - `docs/types/type_01.md`
  - `docs/types/type_03.md`
  - `docs/types/type_05.md`
  - `docs/types/type_06.md`
  - `docs/types/type_07.md`
  - `docs/types/type_08.md`
  - `docs/types/type_09.md`
  - `docs/types/type_10.md`
  - `docs/types/type_11.md`
  - `docs/types/type_12.md`
  - `docs/types/type_13.md`
  - `docs/types/type_14.md`
  - `docs/types/type_15.md`
  - `docs/types/type_16.md`
  - `docs/types/type_19.md`
  - `docs/types/type_20.md`
  - `docs/types/type_21.md`
  - `docs/types/type_22.md`
  - `docs/types/type_23.md`
  - `docs/types/type_24.md`
  - `docs/types/type_25.md`
  - `docs/types/type_26.md`
  - `docs/types/type_27.md`
  - `docs/types/type_28.md`
  - `docs/types/type_30.md`
  - `docs/types/type_32.md`
  - `docs/types/type_33.md`
  - `docs/types/type_34.md`
  - `docs/types/type_35.md`
  - `docs/types/type_57.md`
  - `ui/type_manager.py`
  - `ui/ontology_browser.py`
- Reason:
  - 把高重複、模板化的文件工作先完成，並讓 UI 能直接顯示「已分析」
- Status: done
- Safe to reference: yes
- Notes:
  - loader 會自動偵測 `docs/types/type_XX.md`
  - 若存在文件，且原狀態為 `implemented`，則 UI 端視為 `documented`
