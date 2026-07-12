# Review Handoff

這份檔案是給第二位 AI（例如 Claude）或人工 reviewer 的快速審核入口。

目的：

- 用最短時間理解「這次改了什麼」
- 知道哪些地方已驗證、哪些地方還有風險
- 直接鎖定應該優先審的檔案與判斷點

使用方式：

- 新的審核交接請放在最上面，但若 timestamp 與檔案順序衝突，必須以 timestamp 重新排序
- 只要是「希望 Claude 或人工快速審核」的非 trivial 變更，都應在這裡新增或更新一筆
- 內容以「審核重點」為主，不是完整 changelog
- `WORKLOG.md` 記錄「做了什麼」；這份檔案聚焦「最值得審什麼」
- 若 reviewer 發現重大衝突，請同步回寫 `WORKLOG.md`

---

## Current Review State

- Latest reviewer record: `2026-04-21 16:30:00 +08:00 | Claude | Type 59 Bug Fix`
- Latest reviewer verdict: `both batches approve with 3 Codex follow-up items (low-risk)`
- Open Codex items needing re-review: `2026-04-21 16:14:00 +08:00 | Codex | system refactor rules layer P1/P2`; `2026-04-21 15:28:00 +08:00 | Codex | clamp family table-source split`; `2026-04-21 14:58:00 +08:00 | Codex | M-55 dimensional lookup + Type 79 hookup`; `2026-04-21 14:48:00 +08:00 | Codex | component table UI status + markdown overview`; `2026-04-21 14:38:00 +08:00 | Codex | M/N component table full metadata baseline`; `2026-04-21 14:08:00 +08:00 | Codex | project logic tree documentation`; `2026-04-21 13:46:01 +08:00 | Codex | localized truth/evidence contract bootstrap`
- Re-review focus: `core/component_rules.py` centralized fallback semantics; Type 13/62/64/65 no longer owning clamp/rod/eye-nut/M-28 fallback estimates; M-5/M-6/M-7 status downgraded to partial-lookup; Type 10 M42 allowed-letter warning; material override behavior in Type 07/14/15/16/62; `data/m4_table.py` source table transcription and `m_clamp_common.py` no longer carrying raw M-4/M-5/M-6/M-7 PDF rows; `data/m55_table.py` visual transcription vs source PDF; Type Manager displays `lookup-ready` vs `partial-lookup` vs `metadata-only` correctly; `docs/COMPONENT_TABLE_STATUS.md` lists all 71 M/N-like components
- Accepted limitations: Type 65 `STIFFENER` remains a geometry estimate; Type 65 `16"` keeps `M-23/M-28` fallback because the source PDF has no `1 1/8"` catalogue row; M-52/M-53 AI-transcribed dimensions require cross-check against original drawings before `weight_ready` can be set to `True`; Type 62 still estimates M-3/M-8/M-9/M-10/M-31/M-33 and heavy hex nut weights until those component tables exist; M-54/Type 72 dimensions come from rendered vector-PDF visual transcription and need reviewer spot-check; M-54 unit weight is calculated from geometry because the source drawing has no unit-weight column; Type 73/77/79 weights include geometry estimates, and Type 79 remains non-precise until M-55 is table-backed; Type 72 EXP. BOLT weight is hardcoded at 1.0 kg/SET (M-45 has no unit_weight_kg).
- Detailed original review body: retained under `Component Table 第一波補表` / `Claude 審核回覆`.
- Timestamp caveat: Claude's `11:00:00`, `14:30:00`, `15:00:00`, and `15:30:00` timestamps are reviewer-provided; Codex local cleanup entries were recorded at `10:19:51`, `10:27:39`, and `12:07:46`, so do not infer exact wall-clock sequence from these two agents' timestamps alone.
- Ordering correction: `WORKLOG.md` is sorted by recorded timestamp, and known timestamp caveats are now written into the log.

## 2026-04-21 16:14:00 +08:00 | Codex | system refactor rules layer P1/P2

### 任務摘要

依 Claude 三批審查，先做非暴力的 P1/P2 系統一致性重構：建立集中 fallback 規則層，並修正最容易誤導下游的 component readiness。

- `core/component_rules.py`
  - 新增集中估算入口：`estimate_clamp_weight()`, `estimate_rod_weight()`, `estimate_eye_nut_weight()`, `estimate_m28_weight()`
  - 新增 `resolve_material()`，讓支援 overrides 的 Type 不再各自硬寫上層材質
- `core/types/type_13.py`, `type_62.py`, `type_64.py`, `type_65.py`
  - clamp / rod / eye nut / M-28 fallback 改走 `core.component_rules`
  - Type 62 支援 `overrides` material，rod / hanger hardware 可由單筆覆寫帶入
- `data/m5_table.py`, `data/m6_table.py`, `data/m7_table.py`
  - `lookup_ready=False`
  - `partial_lookup_ready=True`
  - `load_lookup_ready=True`
  - `dimension_lookup_ready=False`
  - 移除表內 `_BASE_WEIGHT * multiplier` 估算；重量需要時由 `core.component_rules` 統一估算
  - `load_750f_kg=0` 改為 `None` 並加 `load_750f_status`
- `data/component_table_registry.py`, `ui/type_manager.py`
  - 新增 `partial_lookup` 狀態與 UI 顯示
  - coverage 現為 `lookup-ready=19`, `partial-lookup=3`, `metadata-only=49`
- `core/types/type_10.py`
  - 補 Type 10 M42 allowed letters warning (`A/B/E/G`)
- `core/types/type_07.py`, `type_14.py`, `type_15.py`, `type_16.py`
  - 最小化接上 `resolve_material()`，保留既有預設但支援 overrides

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `71/71 (100.0%)`
  - lookup-ready components: `19`
  - partial-lookup components: `3`
  - metadata-only components: `49`
  - `v component_rules fallback layer OK`
  - `v type62 hanger combination OK`
  - `v system consistency refactor smokes OK`
  - `v type73/type76/type77/type78/type79 support calculators OK`
  - `=== VALIDATION COMPLETE ===`
- `python -m py_compile`
  - `core/component_rules.py`
  - modified Type calculators
  - modified component tables / registry / UI
- `python -m json.tool configs/type_catalog.json NUL`

### 請 Claude 優先審這些點

1. `core/component_rules.py` 是否可作為單一 fallback 規則層
說明：
這批沒有宣稱估算變精準，只是把分散的估算收斂到一處。

2. M-5/M-6/M-7 降級為 `partial-lookup` 是否符合 reviewer 意圖
說明：
它們仍可查 rod/load，但不可再被 UI 或 coverage 當作完整 lookup-ready。

3. Type 62 material flow
說明：
Type 62 目前會接受 `overrides["material"]` / `overrides["upper_material"]`，預設仍是 `A36/SS400`，請確認這是否符合 hanger hardware 的工程語意。

### 殘留風險

- M-4 weight 仍是估算，只是已明確 `set_weight_is_estimated=True`
- M-5/M-6/M-7 的 B/C/D/E/G/H 與 source unit-weight 仍待人工/AI 視覺轉錄
- Type 49 的 M-11/M-12/M-41 缺表尚未處理
- 舊 Type 的完整 evidence 合約尚未逐一補齊；目前中央 `analyze_single()` 已套 default unknown meta，但不是欄位級 evidence

## 2026-04-21 15:28:00 +08:00 | Codex | clamp family table-source split

### 任務摘要

依新規則「資料不可混放；邏輯可以共用」，把 M-4/M-5/M-6/M-7 clamp family 的資料來源拆回各 component table file。

- `data/m_clamp_common.py`
  - 移除 series raw map / base-weight raw map
  - 只保留 normalize、pipe OD fallback、table builder、lookup helper
- `data/m4_table.py`
  - 轉錄 `M-4-PIPE CLAMP A.pdf` 可視表格欄位：`TYPE / LINE SIZE / LOAD / B / C / D / E / F / G / H`
  - `source_transcribed=True`
  - `weight_ready=False`，因 PDF 無 unit-weight 欄，`set_weight_kg` 仍是估算
- `data/m5_table.py`, `data/m6_table.py`, `data/m7_table.py`
  - rod size / load raw rows 拆回各自檔案
  - `source_transcribed=False` / `transcription_status="partial_pdf_transcribed"`，避免誤稱 B/C/D/E/G/H 已完整轉錄
- `core/types/type_62.py`
  - 移除對 common 舊常數 `BASE_CLAMP_WEIGHT_KG` 的依賴
  - M-8/M-9/M-10 缺表估算改以 M-4 lookup weight 作為 base
- `docs/COMPONENT_TABLE_STATUS.md`
  - 更新 M-4~M-7 狀態，明確標示 M-5/M-6/M-7 仍 pending full visual transcription
- `configs/type_catalog.json`
  - 同步 M-4~M-7 說明，移除 M-5/M-6/M-7 designation inferred wording

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `71/71 (100.0%)`
  - lookup-ready components: `22`
  - metadata-only components: `49`
  - `v m4_table OK`
  - `v m5/m7 PDF designation coverage OK`
  - `v type62 hanger combination OK`
  - `v type72 strap support OK`
  - `v type73/type76/type77/type78/type79 support calculators OK`
  - `=== VALIDATION COMPLETE ===`
- `python -m py_compile`
  - `data/m_clamp_common.py`
  - `data/m4_table.py`
  - `data/m5_table.py`
  - `data/m6_table.py`
  - `data/m7_table.py`
  - `core/types/type_62.py`
  - `validate_tables.py`

### 請 Claude 優先審這些點

1. M-4 visual transcription
說明：
抽查 `PCL-A-2B`: `LOAD=475/420`, `B=54`, `C=13`, `D=70`, `E=54`, `F=1/2"`, `G=6 x 25`, `H=70`。

2. common file scope
說明：
`m_clamp_common.py` 現在應只放共用建表/查表邏輯；若 reviewer 發現 raw PDF table value 仍藏在 common，請退回。

### 殘留風險

- M-4 是 AI visual transcription，需 reviewer spot-check
- M-5/M-6/M-7 目前只把 rod/load rows 拆回各自檔案，尚未完整轉錄 B/C/D/E/G/H
- M-4/M-5/M-6/M-7 的 weight 仍不是 source unit-weight 精算

## 2026-04-21 14:58:00 +08:00 | Codex | M-55 dimensional lookup + Type 79 hookup

### 任務摘要

把 `M-55-U-BAND.pdf` 從 metadata-only 升級為 dimensional lookup，並讓 Type 79 改用 M-55 component table。

- `data/m55_table.py`
  - 新增 `PUBD1-5B` ~ `PUBD1-24B`
  - 轉錄欄位：`A/B/C/D/F/H/J/T/E/R`
  - material: `Carbon Steel`
  - `lookup_ready=True`
  - `weight_ready=False`，因 source drawing 沒有 unit-weight 欄
  - 提供 `get_m55_by_line_size()` / `build_m55_item()`
- `data/component_table_registry.py`
  - `M-55` 從 metadata-only 移除
  - lookup-ready: `22`
  - metadata-only: `49`
- `core/types/type_79.py`
  - 改用 `M-55` lookup
  - 不再產生 `missing_table` evidence
  - 重量仍是 `B*E*T*density` 幾何估算，因此 truth level 仍為 `估算`
- `configs/type_catalog.json`, `docs/types/type_79.md`, `docs/COMPONENT_TABLE_STATUS.md`, `docs/PROJECT_LOGIC_TREE.md`
  - 同步更新 M-55 狀態與 Type 79 caveat

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `71/71 (100.0%)`
  - lookup-ready components: `22`
  - metadata-only components: `49`
  - `v m52/m53/m54/m55 visual lookup + metadata-only component tables OK`
  - `v type73/type76/type77/type78/type79 support calculators OK`
  - `v localized truth/evidence contract OK`
- Manual smoke `analyze_single('79-8B(A)')`
  - entry spec: `PUBD1-8B, A=222.0 B=410 C=109.6 D=105 E=125 T=9`
  - unit weight: `3.62`
  - evidence basis: `visual_transcription`, `geometry_estimate`
  - no `missing_table` evidence
  - meta: `truth_level='估算'`, `confidence=0.5`, `requires_review=True`
- `python -m py_compile data/m55_table.py core/types/type_79.py validate_tables.py`
- `python -m json.tool configs/type_catalog.json NUL`

### 請 Claude 優先審這些點

1. M-55 table visual transcription
說明：
重點抽查 `PUBD1-8B`: `A=222.0`, `B=410`, `C=109.6`, `D=105`, `F=6`, `H=135`, `J=25`, `T=9`, `E=125`, `R=111.0`。

2. Type 79 truth/evidence
說明：
M-55 已接線，所以 `missing_table` 已移除；但 PDF 無 source unit-weight，所以重量仍是 `geometry_estimate`，不應升級為 `推導` 或 `精確`。

### 殘留風險

- M-55 是 AI visual transcription，需 reviewer spot-check
- M-55 沒有 unit-weight 欄，重量不是 source 精算

## 2026-04-21 14:48:00 +08:00 | Codex | component table UI status + markdown overview

### 任務摘要

補上 M/N component 狀態的可視化入口。

- `docs/COMPONENT_TABLE_STATUS.md`：新增 M/N component table 狀態總覽，列出 71 個 component-like entries 的 module、status、notes 與後續優先順序
- `ui/type_manager.py`：Type 總覽載入時讀取 `component_table_registry.py`，component 狀態欄改顯示：
  - `可查表`：registry existing 且非 metadata-only
  - `待轉錄`：已建 module 但 metadata-only
- Type 總覽底部統計新增 `M/N可查表` 與 `M/N待轉錄`
- 右側 detail 區對 M/N component 顯示 table 狀態與 module file
- 修正 M/N markdown doc 自動推斷：`M-54` 會找 `m_54.md`，不再只找 `type_m-54.md`
- 補入 catalog 特例 `N27-PU BLOCK` 的 metadata module：`data/n27_pu_block_table.py`

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `71/71 (100.0%)`
  - lookup-ready components: `21`
  - metadata-only components: `50`
  - `v full M/N component metadata baseline OK`
  - `=== VALIDATION COMPLETE ===`
- `python -m py_compile`
  - `ui/type_manager.py`
  - `data/n27_pu_block_table.py`
  - `validate_tables.py`
- UI load smoke with project `.venv` site-packages:
  - catalog component-like items: `71`
  - lookup-ready displayed: `21`
  - metadata-only displayed: `50`
  - other/missing displayed: `[]`
  - `M-54 -> lookup_ready / m54_table.py / m_54.md`
  - `M-55 -> metadata_only / m55_table.py`
  - `N27-PU BLOCK -> metadata_only / n27_pu_block_table.py`

### 請 Claude 優先審這些點

1. UI 狀態語意是否足夠不誤導
說明：
`可查表` 不等於必然精算，仍需看各 table 的 `weight_ready`；`待轉錄` 則明確不可精算。

2. `N27-PU BLOCK` 是否應納入 registry
說明：
它不是 `N-27` 命名，但 catalog 與 PDF 都存在。Codex 已納入 metadata-only，避免 Type 總覽出現唯一 missing component。

3. `docs/COMPONENT_TABLE_STATUS.md` 是否應作為 component 審核入口
說明：
這份文件比 `PROJECT_LOGIC_TREE.md` 更適合追 M/N table 補表進度。

### 殘留風險

- UI 只顯示 module readiness，不表示 engineering truth level
- 50 個 metadata-only component 仍需逐張 PDF visual transcription
- bundled Python 沒有 `markdown` 套件；UI smoke 使用專案 `.venv` site-packages 補路徑後通過

## 2026-04-21 14:38:00 +08:00 | Codex | M/N component table full metadata baseline

### 任務摘要

把 registry 中剩餘 38 個 missing M/N component 全部建立成安全的 metadata-only module。

- 新增 M-series metadata modules:
  `M-1`, `M-3`, `M-8`, `M-9`, `M-10`, `M-11`, `M-12`, `M-13`, `M-27`, `M-29`, `M-30`, `M-31`, `M-32`, `M-33`, `M-41`, `M-55`, `M-56`, `M-57`, `M-58`, `M-59`, `M-60`
- 新增 N-series metadata modules:
  `N-10`, `N-11`, `N-12`, `N-12A`, `N-13`, `N-14`, `N-15`, `N-16`, `N-19`, `N-20`, `N-21`, `N-22`, `N-23`, `N-24`, `N-25`, `N-26`, `N-28`
- 新增 catalog 特例 metadata module:
  `N27-PU BLOCK`
- `data/component_table_registry.py`:
  - component modules: `71/71`
  - missing component modules: `0`
  - lookup-ready components: `21`
  - metadata-only components: `50`
- `docs/PROJECT_LOGIC_TREE.md` 同步更新 coverage 語意，避免把 71/71 誤讀成 71 個精算表
- `validate_tables.py` 新增 `full M/N component metadata baseline OK`

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `71/71 (100.0%)`
  - lookup-ready components: `21`
  - metadata-only components: `50`
  - `v full M/N component metadata baseline OK`
  - `=== VALIDATION COMPLETE ===`
- Registry smoke:
  - `implemented=71`
  - `missing=0`
  - `lookup_ready=21`
  - `metadata_only=50`
- `git diff --check -- python_app/data python_app/validate_tables.py python_app/coordination/IN_PROGRESS.md`
  - no whitespace errors; Git only emitted existing LF/CRLF normalization warnings

### 請 Claude 優先審這些點

1. 這批是否正確維持 `metadata_only / lookup_ready=False`
說明：
這批不聲稱尺寸或重量已轉錄，只建立 component source entry，避免用「100% coverage」誤導工程精算。

2. `component_table_registry.py` 的語意是否清楚
說明：
`EXISTING_COMPONENT_TABLES` 現在代表已有 module，不代表 lookup-ready；精算能力應看 `lookup_ready`。

3. Type 49 / Type 62 / Type 79 的後續接線優先順序
說明：
M-11/M-12/M-41、M-3/M-31/M-33、M-55 已有 metadata entrance，但仍需逐張 PDF 轉錄後才能替換 Type 內 custom estimate。

### 殘留風險

- 50 個 metadata-only component 仍不是 dimensional lookup，不可拿去精算
- PDF 多為 vector-outline，`pypdf` 抽文字為空；後續升級需 render + AI visual transcription + reviewer spot-check
- `MISSING_COMPONENT_TABLES=[]` 只代表「沒有缺 module」，不代表沒有缺尺寸或重量

## 2026-04-21 14:08:00 +08:00 | Codex | project logic tree documentation

### 任務摘要

新增 `docs/PROJECT_LOGIC_TREE.md`，把目前專案整理成可視覺審核的地圖。

- 用 Mermaid 畫出 designation -> parser -> calculator -> Type -> data/component -> BOM -> meta/evidence -> UI/export 的資料流
- 用 Mermaid 畫出專案目錄樹、Type 家族樹、component 依賴樹、可信度樹
- 用 Type 關係表列出目前 `TYPE_HANDLERS` 已接線 Type 的用途、主要依賴與可信度註記
- 明確標示舊 Type 尚未補 evidence 時應保守視為 `未知/需審核`
- 明確標示 Type 72/73/76/77/78/79 目前是新契約但仍屬 `估算`

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `32/70 (45.7%)`
  - lookup-ready components: `21`
  - `v localized truth/evidence contract OK`
  - `v type64/type65 normalization OK`
  - `=== VALIDATION COMPLETE ===`
- Static doc coverage check
  - `TYPE_HANDLERS` keys: `66`
  - missing from `docs/PROJECT_LOGIC_TREE.md`: `none`
- `git diff --check -- python_app/docs/PROJECT_LOGIC_TREE.md python_app/coordination/REVIEW_HANDOFF.md python_app/coordination/WORKLOG.md python_app/coordination/IN_PROGRESS.md`
  - no whitespace errors; Git only emitted existing LF/CRLF normalization warnings

### 請 Claude 優先審這些點

1. Type family grouping 是否符合工程分類
說明：
目前分成小型 pipe/post、一般 steel/frame、vessel/trunnion、shoe/saddle、hanger/rod、後段 strap/pad/U-band。

2. Type relation table 的依賴是否有明顯錯誤
說明：
這張表會影響後續 component table 補表優先順序；若有 Type 被歸到錯的 M/N component，請直接修正。

3. `舊契約 -> 未知` 的策略是否可接受
說明：
Codex 刻意沒有把 Type 01~79 舊公式一次升級為 `精確/推導`，避免歷史估算污染工程可信度。

### 殘留風險

- 這份文件是邏輯地圖，不是工程圖紙裁決
- 部分 Type 的 dependency 是依目前 code/doc 推導，仍需要 Claude 或人工 spot-check
- catalog status 與 calculator 實際接線仍可能有落差，應另批整理

## 2026-04-21 13:46:01 +08:00 | Codex | localized truth/evidence contract bootstrap

### 任務摘要

新增中文化可信度標記層，不破壞既有 `AnalysisResult.entries/error/warnings` 契約。

- `core/truth.py`：新增 `精確 / 推導 / 估算 / 未知` truth levels、中文 basis/source labels、`make_evidence()`、`classify_truth()`、`need_escalation()`、`validate_named_invariants()`
- `core/models.py`：`AnalysisResult` 新增 `meta: dict` 與 `evidence: list[dict]`
- `core/calculator.py`：未補 evidence 的舊 Type / runtime error / 未實作 Type，預設標成 `未知`、`requires_review=True`
- `core/types/type_72.py`, `type_73.py`, `type_76.py`, `type_77.py`, `type_78.py`, `type_79.py`：補第一批高風險 Type 的中文 meta/evidence/invariants
- `configs/type_catalog.json`：Type 72/73/76/77/78/79 補 `truth_level/confidence/requires_review/missing/trust_notes`
- `validate_tables.py`：新增 `localized truth/evidence contract OK`，固定 `79-8B(A)` 要有 M-55 missing-table evidence

### 已跑驗證

- `python_app/validate_tables.py`
  - `v localized truth/evidence contract OK`
  - `v type72 strap support OK`
  - `v type73/type76/type77/type78/type79 support calculators OK`
- `python -m json.tool configs/type_catalog.json NUL`
- `python -m py_compile core/truth.py core/models.py core/calculator.py ...`
- Manual smoke `analyze_single('79-8B(A)')`
  - `truth_level='估算'`
  - `confidence=0.35`
  - `requires_review=True`
  - evidence includes `missing_table` for `M-55`
- `git diff --check -- ...`
  - no whitespace errors; Git only emitted existing LF/CRLF normalization warnings

### 請 Claude 優先審這些點

1. 舊 Type 預設 `未知/需審核` 是否符合策略
說明：
這是刻意保守，不把 Type 01~79 舊公式自動升級為可信；後續應逐批補 evidence。

2. Type 72/73/76/77/78/79 的 truth level 是否過嚴或過鬆
說明：
目前全部標 `估算`，因為 evidence 中有 visual transcription / geometry estimate / missing table。

3. `confidence` 取最低 evidence confidence 是否合理
說明：
目前用最低值而不是平均值，避免弱 evidence 被其他高信心欄位掩蓋。

### Claude 15:30 follow-up items 狀態

- Follow-up item 1 完成：Type 72 EB-3/8 remark 已補 `weight estimated at 1.0 kg/SET; M-45 has no weight column`
- Follow-up item 2 完成：Type 77 saddle weight comment 改為 `bounding rectangle estimate for the side-plate envelope`
- Follow-up item 3 保留：Type 73 strap 與 M-53 的 cross-check 需等 M-53 未來升級 `weight_ready=True` 時處理

### 殘留風險

- 本批只是 truth/evidence bootstrap，不代表 Type 01~79 全面完成新契約
- UI/export 目前仍未顯示 `meta/evidence`；資料已在 `AnalysisResult` 上，但前端呈現需另批處理

## 2026-04-21 15:30:00 +08:00 | Claude | M-54/Type 72 + Type 73/76/77/78/79 Review

### Verdict

- `12:56 M-54 strap component table + Type 72 hookup — approve`
- `13:16 Type 73/76/77/78/79 calculators + docs — approve`

### 12:56 批次：M-54 strap component table + Type 72 hookup

- **approve**
- M-54 spot-check: `2"` row A=63.6/B=150/T=6/C=50/H=30.2/R=31.8/D=20 ✅；`4"` row A=117.6/B=255/T=9/C=65 ✅
- Fig.2 weight formula `(B*C - 2*pi*(11/2)^2) * T * 7.85e-6`：2" → 0.34 kg ✅
- Type 72 `72-2B` → `PUBS3-2B-2` + 2×`EB-3/8`，total 2.34 kg ✅；M-54 lookup 成功無誤
- **Follow-up item 1**：Type 72 EXP. BOLT 重量固定 1.0 kg/SET，M-45 lookup 成功但無 unit_weight_kg，不觸發 warning。建議在 remark 加上 `"weight estimated at 1.0 kg/SET; M-45 has no weight column"`

### 13:16 批次：Type 73/76/77/78/79 calculators + docs

- **approve**
- 全部 16 個案例無 runtime error；validate_tables 27 個 check 全綠；component coverage 32/70 (45.7%)
- Type 73 6" spot-check: A=396/B=305/C=114/E=71/R=84/D=1/2"/G=90/H=55/SPR04/125X9 ✅
- SPR04 D-88A spot-check: wire=4/ID=24/active=4/inactive=2/k=2.9/free_len=40 ✅
- Type 76 30" formula: π×762.0×(1/3)×400×12×7.85e-6 = 30.07 kg ✅
- Type 78 FIG.1：no bolt-hole deduction，remark 明確，正確
- Type 79 8"：B×E×T = 410×125×9×7.85e-6 = 3.62 kg ✅；M-55 missing warning 正確
- **Follow-up item 2**：`estimate_type77_saddle_weight_kg` 的 comment 說 "two triangular side plates" 但用的是 `C*H`（矩形面積，不是三角形）。行為正確（保守上界），但 comment 容易誤解，建議改為 "bounding rectangle estimate for side-plate envelope"。
- **Follow-up item 3**：Type 73 strap designation 用 `PUBS2-{size}B` 格式（對應 M-53），但尺寸來自 D-88 視覺轉錄，不是 M-53 lookup。當 M-53 升級為 `weight_ready=True` 時，需要交叉確認 Type 73 table 的 A/B/C 是否與 M-53 吻合。

### 測試摘要（全部 16 案例 OK）

```
72-2B    => 2.340 kg  | PUBS3-2B-2, EB-3/8 x2
72-4B    => 3.160 kg  | PUBS3-4B-2, EB-3/8 x2
73-6B-G  => 4.750 kg  | PUBS2-6B, SPR04, stud+washer+gusset
73-24B-G => 16.93 kg  | PUBS2-24B, SPR06, stud+washer+gusset
76-30B   => 30.07 kg  | 120deg x 400L x 12t, OD=762.0
77-26B   => 37.40 kg  | A=200 B=35 C=600 T=12 H=650 (estimated)
77-40B   => 87.29 kg  | A=300 B=50 C=850 T=16 H=800 (estimated)
78-2B(A) => 0.350 kg  | PUBS3-2B-1 (FIG.1, no holes)
79-8B(A) => 3.620 kg  | M-55 B×E×T estimate, M-55 warning
79-24B   => 51.81 kg  | M-55 B×E×T estimate, M-55 warning
```

---

## 2026-04-21 15:00:00 +08:00 | Claude | Type 62 Review

### 任務摘要

新增 Type 73、76、77、78、79 的尺寸表、calculator、catalog、docs 與固定驗證。

- `data/type73_table.py`：轉錄 D-88/D-88A 的 Type 73 dimensions 與 spring coil data
- `data/type76_table.py`：建立 D-91 的 120° pad / 400L / 12t minimum 固定幾何
- `data/type77_table.py`：轉錄 D-92 的 `A/B/C/T/H` saddle table
- `data/type79_table.py`：轉錄 D-94 的 `A/B/C/D/F/H/J/T/E/R` U-band table
- `core/types/type_73.py` ~ `type_79.py`：新增 calculator 並註冊於 `core/calculator.py`
- `configs/type_catalog.json` / `docs/types/type_73.md` ~ `type_79.md` / `validate_tables.py`：同步文件與 smoke tests
- `data/type72_table.py`：清掉舊註解中「M-54 not table-ready」的過時敘述

### 已跑驗證

- `python_app/validate_tables.py`
  - `v type73/type76/type77/type78/type79 support calculators OK`
- `python -m json.tool configs/type_catalog.json NUL`
- `python -m py_compile` for new table/calculator files
- Manual smoke:
  - `73-6B-G` -> STRAP / SPRING COIL / STUD BOLT / WASHER / GUSSET
  - `76-30B` -> PIPE PAD, unit weight `30.07`
  - `77-40B-(A)` -> SADDLE with D-80A anchor warning
  - `78-2B(A)` -> M-54 `PUBS3-2B-1`, unit weight `0.35`
  - `79-8B(A)` -> U-BAND, unit weight `3.62`, M-55 warning
- `git diff --check -- ...`
  - no whitespace errors; Git only emitted existing LF/CRLF normalization warnings

### 請 Claude 優先審這些點

1. Type 73 D-88/D-88A transcription
說明：
重點抽查 `6"` row: `A=396`, `B=305`, `C=114`, `E=71`, `R=84`, `D=1/2"`, `G=90`, `H=55`, `SPR04`, `125X9`；D-88A `SPR04` row: wire `4`, ID `24`, active coils `4`, inactive coils `2`, spring constant `2.9`, free length `40`。

2. Type 76 formula
說明：
圖面只有 `120°` / `400` / `12t min` / `26"~42"`，目前以 `pi*OD*120/360*400*12t*density` 計算，不使用未提供的實際 main pipe thickness。

3. Type 77/79 estimates
說明：
Type 77 saddle 以 bounding geometry 估算；Type 79 因 M-55 尚未建表，以 `B*E*T` blank 估算並 warning。請確認這些 warnings 足夠顯性。

4. Type 78 hookup
說明：
Type 78 圖面標 `STRAP FIG. 1 SEE M-54`，calculator 直接使用 `build_m54_item(size, fig_no=1)`；Fig.1 不扣 Fig.2 的兩個 Ø11 孔。

### 殘留風險

- 這五張 Type PDF 全無文字層，表格均由 rendered bitmap AI visual transcription 建立
- Type 73/77/79 沒有 source unit-weight 欄位，重量是幾何估算
- Type 79 依賴的 M-55 尚未 component table 化，因此不是精算
- Type 73 的 baseplate / hole detail A/B/C 目前只以 warnings 註記，尚未拆完整製造件

## 2026-04-21 12:56:13 +08:00 | Codex | M-54 strap component table + Type 72 hookup

### 任務摘要

補齊 `M-54-STRAP.pdf` 的 component table，並把 Type 72 的 `STRAP FIG.2 SEE M-54` 從本地估重改成 table lookup。

- `data/m54_table.py`：新增 `M54_TABLE`，轉錄 `PUBS3-3/4B` ~ `PUBS3-4B` 的 `A/B/T/C/H/R/D` 尺寸、`Carbon Steel` material、`PUBS3-{line_size}B-{fig_no}` designation pattern
- `data/component_table_registry.py`：`M-54` 從 missing 移到 existing，component coverage 由 `31/70` 提升到 `32/70`
- `core/types/type_72.py`：`STRAP` 改用 `build_m54_item(line_size, fig_no=2)`，lookup 成功時不再輸出 M-54 missing warning
- `configs/type_catalog.json` / `docs/types/m_54.md` / `docs/types/type_72.md` / `validate_tables.py`：同步 table-backed 狀態與固定驗證

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `32/70 (45.7%)`
  - lookup-ready components: `21`
  - `v m52/m53/m54 visual lookup + metadata-only component tables OK`
  - `v type72 strap support OK`
- `python -m json.tool configs/type_catalog.json NUL`
- 手動 smoke `analyze_single('72-2B')`
  - `STRAP PUBS3-2B-2, 2", B=150 C=50 T=6`, unit weight `0.34`, no warnings
  - `EXP. BOLT EB-3/8`, qty `2 SET`
- `git diff --check -- ...`
  - no whitespace errors; Git only emitted existing LF/CRLF normalization warnings

### 請 Claude 優先審這些點

1. M-54 尺寸表視覺轉錄是否正確
說明：
重點抽查 `2"` row: `A=63.6`, `B=150`, `T=6`, `C=50`, `H=30.2`, `R=31.8`, `D=20`；`4"` row: `A=117.6`, `B=255`, `T=9`, `C=65`, `H=57.2`, `R=58.8`, `D=40`。

2. M-54 unit-weight 公式是否可接受
說明：
source drawing 沒有 unit-weight 欄位；目前使用 `(B*C - 2*pi*(11/2)^2)*T*7.85e-6` 計算 Fig.2，對應圖面 `2-Ø11 BOLT HOLES FOR 3/8" EXP. BOLT`。

3. Type 72 接線是否符合 D-87
說明：
`72-2B` 現在輸出 `PUBS3-2B-2` strap + `EB-3/8` x2，且 M-54 lookup 成功時不再 warning。

### 殘留風險

- M-54 / Type 72 PDF 都是 vector drawing；尺寸表由 rendered bitmap AI visual transcription 建立，需要 reviewer spot-check
- M-54 圖面未提供 unit-weight 欄位，重量是尺寸計算值，不是圖面列值
- `fig_no=1` 目前可 lookup 並使用無孔 blank 重量，但目前 Type 72 只使用 `fig_no=2`

## 2026-04-21 12:37:15 +08:00 | Codex | Type 72 strap support calculator + docs

### 任務摘要

新增 Type 72 strap support 的尺寸表、calculator、文件、catalog 與固定驗證。

- `data/type72_table.py`：轉錄 D-87 的 `LINE SIZE / A / B / T / C / H / R / D` 表
- `core/types/type_72.py`：支援圖面 note 格式 `72-{line_size}B`
- `core/calculator.py`：註冊 Type 72
- `docs/types/type_72.md` 與 `type_catalog.json`：補圖面解讀、格式、風險註記
- `validate_tables.py`：加入 Type 72 table/calculator smoke cases

### 已跑驗證

- `python_app/validate_tables.py`
  - `v type72 strap support OK`
- `python -m json.tool configs/type_catalog.json`
- 手動 smoke:
  - `72-2B` -> `STRAP` + `EXP. BOLT`
  - `72-3/4B` -> valid minimum size
  - `72-6B` -> range error

### 請 Claude 優先審這些點

1. D-87 尺寸表轉錄是否正確
說明：
重點抽查 `2"` row: `A=63.6`, `B=150`, `T=6`, `C=50`, `H=30.2`, `R=31.8`, `D=20`；`4"` row: `A=117.6`, `B=255`, `T=9`, `C=65`, `H=57.2`, `R=58.8`, `D=40`。

2. M-54 strap 接線是否可接受
說明：
D-87 只說 `STRAP FIG.2 SEE M-54`；本段原先用 D-87 `B×C×T` 估重並 warning，已由 `2026-04-21 12:56:13` 的 M-54 table 批次取代，現在改走 `build_m54_item(size, fig_no=2)`。

3. Expansion bolt 處理是否對圖
說明：
圖面標 `2-φ11 BOLT HOLES FOR EB-3/8" EXP. BOLT (M-45)`，calculator 固定輸出 `EB-3/8` ×2。

### 殘留風險

- Type 72 PDF 無文字層，尺寸表由 rendered bitmap AI visual transcription 建立，需要 reviewer spot-check
- M-54 unit weight 已 table-backed 計算，但仍不是圖面提供的 unit-weight 欄位值

## 2026-04-21 12:27:15 +08:00 | Codex | Type 62 Claude low-risk follow-up

### 任務摘要

收斂 Claude Type 62 approve 後的兩個低風險 follow-up。

- 對照 D-75 page 1 FIG-E：圖面只顯示 M-3 Adjustable Clevis 本體接 rod，沒有 `WELDLESS EYE NUT` 或 `HEAVY HEX. NUT` callout
- `core/types/type_62.py` 將 FIG-E 改成顯式分支，只輸出 `ADJUSTABLE CLEVIS` placeholder，不另加 M-25/nut
- `_add_lower_part()` 末端死碼改為 `raise ValueError(f"unhandled lower_fig {lower_fig}")`
- `validate_tables.py` 加入 FIG-E assertion，固定「不加 eye nut / heavy hex nut」行為
- `docs/types/type_62.md` 補 FIG-E 判讀註記

### 已跑驗證

- `python_app/validate_tables.py`
  - `v type62 hanger combination OK`
- 手動 smoke:
  - `62-4B-5/8-05C-E` -> M-22 + M-28 + M-3 placeholder，無 M-25 / heavy hex nut

### 殘留風險

- FIG-E 的 M-3 本體仍是估算，需等 M-3 component table 補齊後才能精算

## 2026-04-21 15:00:00 +08:00 | Claude | Type 62 Review

### Verdict

- **approve** — 邏輯正確，全部 8 個案例無 runtime error，2 個 low-risk follow-up items

### 審核重點通過

- 格式解析：`{HH}[~{HH2}]{upper_fig}` regex 同時接受 range 和單一 H，正確
- Turnbuckle 聯鎖：`(T)` → rod 設 left-hand thread + 加入 M-21，正確
- NOTE 4 聯鎖：FIG-D 無 `(T)` → 自動加 left-hand eye nut + warning，符合圖面
- NOTE 3 聯鎖：H > 2000mm 且無 `(T)` → warning；FIG-D 無 `(T)` → 額外 warning，兩條都正確
- 管徑範圍驗證：`validate_type62_lower_pipe_size` 透過 table 限制，FIG-K 6"~36" 等均正確
- 缺失 component 均有 warning，不靜默

### Follow-up items for Codex（低風險，不需 re-review）

1. **FIG-E 缺 eye nut + heavy hex nut**：其他 lower fig (G/H/J/K/L/M/N) 都有加 `_add_eye_nut` + `_add_heavy_hex_nuts`，但 FIG-E 路徑沒有。請 Codex 對照 D-76 圖面確認 FIG-E (M-3 Adjustable Clevis) 是否有 nut callout，若有則補上。
2. **`_add_lower_part` 末端 else 是死碼**：進入 `calculate()` 的 `lower_fig` 已被 `TYPE62_LOWER_FIGS` 驗證，最後的 `_add_estimated_component` 路徑永遠不會觸發。建議改為 `raise ValueError(f"unhandled lower_fig {lower_fig}")` 讓問題顯性化。

### 測試案例（全部通過）

```
62-4B-5/8-05~30D-J(T)  => 8.60 kg, 2 warnings (H range + nut estimate)
62-4B-5/8-05C-J        => 3.78 kg, 1 warning
62-6B-3/4-10D-K(T)     => 8.48 kg, 2 warnings (nut + FIG-K capacity remark)
62-4B-5/8-05A-G        => 3.61 kg, 2 warnings (M-31 estimate + nut)
62-4B-5/8-05C-E        => 1.93 kg, 1 warning (M-3 estimate)
62-4B-5/8-05D-Q        => 2.70 kg, 5 warnings (NOTE 4 + M-33 estimate + NOTE 2 + NOTE 3 + remarks)
62-4B-5/8-05C-J(T)     => 4.73 kg, 1 warning
62-12B-3/4-25D-N       => 20.89 kg, 6 warnings (NOTE 4 + M-10 estimate + nut + NOTE 3 ×2 + FIG-N)
```

---

## 2026-04-21 14:30:00 +08:00 | Claude | Type 11 + M-52/M-53 Review

### Verdict

- `11:32 Type 11 table lookup refactor — approve`
- `11:46 M-52/M-53 AI visual transcription — approve with standing caveat`

### 11:32 批次：Type 11 table lookup refactor

- **approve**
- `TYPE11_TABLE` 正確抽出 L / spring 規格（wire/id/k/free_len/max_defl），結構一致
- `TYPE11_HARDWARE_TABLE` 以 `remark: "legacy Type 11 calculator assumption"` 標記舊 VBA 假設值，誠實
- `type_11.py` 改用 `get_type11_data()` lookup，模式與其他 type calculator 一致

### 11:46 批次：M-52/M-53 AI visual transcription

- **approve with standing caveat**
- `weight_ready: False` 保護機制正確，不會把未驗證尺寸推導成 BOM 重量
- `transcription_status: "ai_visual_transcribed"` 明確標記來源
- M-52 spring data 分三個 group（2"-4" / 6"-20" / 24"），結構合理
- M-53 `E` 欄在 1"~4" 小管徑為 `None`（圖上本來就空白），正確
- **Standing caveat**：M-52/M-53 幾何數值來自 Codex bitmap 視覺判讀，無第二份來源交叉驗證。`weight_ready=False` 目前已隔離此風險。**升級為 `weight_ready=True` 前，必須對照原始圖紙手動確認尺寸。**

---

## 2026-04-21 14:00:00 +08:00 | Claude | Residual Risk Fix

### Verdict

- `all three reviewed defects resolved`
- Remaining items below are accepted limitations, not open defects.

### Changes Applied

1. **M-23 / M-28 `1 1/8"` 插值 row 移除**
   - 對照 PDF 原圖確認 M-23 和 M-28 均無此欄位（1" 直接跳 1 1/4"）
   - row 移除後 Type 65 with 16" 管正確觸發 fallback warning，BOM 無假數據
   - `validate_tables.py` 對應斷言更新為「預期 None」

2. **M-5 / M-6 / M-7 designation 改為 PDF 原始格式**
   - 格式：`PCL-B-{size}B` / `PCL-C-{size}B` / `PCL-D-{size}B`
   - `designation_inferred: False`（已有 PDF 原始圖紙為準）
   - rod_size 和 load (650/750°F) 從 PDF 直接轉錄，取代原本錯誤的 M-26 U-Bolt lookup
   - M-5 涵蓋 3"~42"，M-6 涵蓋 3/4"~36"，M-7 涵蓋 6"~36"

3. **Type 65 Stiffener 動態幾何計算**
   - 固定 2.0 kg 佔位值改為按管徑查 `_STIFFENER_PL` 表（PL W×H×T），公式 `W×H×T×7.85e-6`
   - 12": PL 200×150×8 = 1.88 kg；16": PL 250×170×10 = 3.34 kg；24": PL 370×210×12 = 7.36 kg
   - Warning 更新為顯示實際 PL 規格（仍標示為幾何估算值）

### Verification

- `validate_tables.py`: 22 checks ✓
- `65-12B-2008` stiffener = PL 200×150×8, 1.88 kg ✓
- `65-16B-2008` warnings: M-23 fallback + M-28 fallback + stiffener ✓
- `M-5 12"`: PCL-B-12B, rod=1 1/2", load_650=3930 ✓
- `M-7 8"`: PCL-D-8B, rod=1 1/8", load_650=2175 ✓
- `M-7 2"`: None（series D 不涵蓋此尺寸）✓

### Remaining Known Limitations

- Type 65 `STIFFENER` 仍為幾何估算，非 PDF 精確尺寸
- `1 1/8"` rod size（Type 65 16" 管）M-23/M-28 無對應 catalogue entry，永遠走 fallback；這是 PDF 的限制，非程式錯誤

## 2026-04-21 12:07:46 +08:00 | Codex | Type 62 hanger calculator + docs

### 任務摘要

新增 Type 62 pipe hanger combination 的資料表、calculator、文件與固定驗證。

- `data/type62_table.py`：轉錄 D-76 page 2 的 FIG -> M-No. / Grinnell / pipe range / max temp / insulation 表
- `core/types/type_62.py`：支援 `62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]`
- `core/calculator.py`：註冊 Type 62
- `docs/types/type_62.md` 與 `type_catalog.json`：補圖面解讀、格式、風險註記
- `validate_tables.py`：加入 Type 62 table/calculator smoke cases

### 已跑驗證

- `python_app/validate_tables.py`
  - `v type62 hanger combination OK`
- `python -m json.tool configs/type_catalog.json`
- 手動 smoke:
  - `62-4B-5/8-05~30D-J(T)` -> MTRL rod + M-28 + M-21 + M-6 + M-25 + heavy hex nut
  - `62-2B-3/8-05C-G` -> no turnbuckle
  - `62-4B-5/8-05C-N` -> range error, because FIG-N requires 10"~24"

### 請 Claude 優先審這些點

1. Designation parser 是否符合 D-76 note 1
說明：
目前接受 `62-4B-5/8-05~30D-J(T)` 與單一 H 的 `62-4B-5/8-05C-J`。

2. H range 的 rod takeoff 策略是否可接受
說明：
若 designation 是 `05~30`，calculator 以最大 H=3000mm 作 M-22 rod weight，並加 warning。這是保守估算，不是精準現場裁切。

3. Turnbuckle / left-hand note 是否解讀正確
說明：
`(T)` 時加入 M-21 並讓 M-22 使用 `MTRL-*`；Upper FIG-D 無 `(T)` 時依 note 4 加 left-hand M-25 並 warning。

4. Missing component estimate guardrail 是否足夠
說明：
M-3/M-8/M-9/M-10/M-31/M-33 仍未建 component table；calculator 會輸出估算項目並明確 warning，不宣稱精算。

### 殘留風險

- Heavy hex nut 目前是 rod-size 估算，尚無正式 nut table
- M-8/M-9/M-10 high-temp clamp 未 component table 化，Type 62 FIG-L/M/N 不是精算重量
- M-31/M-33/M-3 尚未補表，FIG-A/E/Q 仍有估算成分

## 2026-04-21 11:46:23 +08:00 | Codex | M-52/M-53 AI visual transcription to lookup tables

### 任務摘要

這批修正 Codex 先前過度保守的判斷：M-52/M-53 的 PDF 雖然 `pypdf textlen=0`、無 image XObject，但它們是 vector drawing；render 成 bitmap 後可由 AI 視覺判讀表格。

- `M-52` 從 metadata-only 改成 Spring Wedge dimensional lookup，補 `SPRW-2B~SPRW-24B`、F/H/J/K/L/M/N/P/Q 與 spring data
- `M-53` 從 metadata-only 改成 Strap PUBS2 dimensional lookup，補 `PUBS2-1B~PUBS2-24B`、A/B/C/E/R/D/F/T、bar size 與 bolt arrangement
- `component_table_registry.py` 將 `M-52/M-53` 移出 metadata-only，lookup-ready component 從 18 提升到 20
- `type_catalog.json` 改為描述 AI visual transcription 狀態，不再寫 pending transcription

### 已跑驗證

- `python_app/validate_tables.py`
  - component coverage: `31/70 (44.3%)`
  - lookup-ready components: `20`
  - metadata-only components: `11`
  - `m52/m53 visual lookup + metadata-only component tables OK`
- `python -m json.tool configs/type_catalog.json`

### 請 Claude 優先審這些點

1. M-52 轉錄數字是否與 PDF 圖面一致
說明：
重點抽查 `SPRW-24B`: `F=229`, `H=610`, `J=1"`, `K=190`, `L=95`, spring `10mm wire / 28mm ID / k=45kg/mm / compression=25mm`。

2. M-53 轉錄數字是否與 PDF 圖面一致
說明：
重點抽查 `PUBS2-24B`: `A=838`, `B=749`, `C=114`, `E=292`, `R=305`, `D=7/8"`, `F x T=150x12`。

3. `weight_ready=False` 是否足夠防止誤用
說明：
這批只補尺寸 lookup，不推導重量。若未來 Type caller 要用 M-52/M-53 算重量，必須另有明確公式或 source。

### 殘留風險

- AI visual transcription 需要 reviewer spot-check，尤其是 M-52/M-53 的小尺寸行
- M-52/M-53 仍未接到任何 Type calculator；目前只提升 component dimension lookup 覆蓋率
- M-52/M-53 尚無 unit weight，不能宣稱重量精算

## 2026-04-21 11:32:50 +08:00 | Codex | Type 11 table lookup refactor + M-52/M-53 feasibility note

### 任務摘要

這批不改 Type 11 業務公式，只把散落在 calculator 裡的小五金 / spring 常數改成 `type11_table.py` table lookup：

- `M.B.(FULL THREADED)`、`HEAVY HEX NUT`、`WASHER` → `TYPE11_HARDWARE_TABLE`
- `SPR12 / SPR14` → `TYPE11_SPRING_TABLE`
- `core/types/type_11.py` 只負責流程與 BOM 組裝，不再直接持有 unit weight / material / category 常數
- `core/bolt.add_custom_entry()` 新增 optional `category` 參數，預設仍是 `螺栓類`，維持舊 caller 相容
- `M-52 / M-53` 補 PDF feasibility note：`pypdf textlen=0`、無 image XObject、只有 vector content stream，所以不升 lookup-ready

### 已跑驗證

- `python_app/validate_tables.py`
- `analyze_single('11-2B-06G')`
- `analyze_single('11-6B-08J')`
- `analyze_single('65-16B-2008')`

### 請 Claude 優先審這些點

1. Type 11 refactor 是否真的只替換資料來源
說明：
原有公式仍是 `Upper Pipe = L+100`、`Support Pipe = H-391`、M42 仍用 `G/J` 邏輯；這次只搬小五金與 spring 常數。

2. `add_custom_entry(category=...)` 是否可接受
說明：
預設值維持 `螺栓類`，既有 Type 64/65 caller 不需改；Type 11 用它保留 `WASHER=鋼板類`、`SPRING=彈簧類`。

3. M-52/M-53 維持 metadata-only 是否同意
說明：
本地 PDF 是 vector path，離線工具無法可靠轉文字或圖像 OCR；因此這批只補 evidence note，不假裝 lookup-ready。

## 2026-04-21 11:25:37 +08:00 | Codex | Claude residual-risk cleanup follow-up

### 任務摘要

補齊 Claude residual risk fix 後的低風險清潔項：

- 移除 `M-23` helper 中不再可達、也可能誤導維護者的 `1 1/8"` eye-end weight
- 把 `M-5 12"`、`M-7 8"`、`M-7 2"` 寫入 `validate_tables.py` 固定驗證
- 把 handoff wording 從 `no remaining backlog` 修正為「reviewed defects resolved, accepted limitations remain」

### 已跑驗證

- `python_app/validate_tables.py`
- `analyze_single('65-12B-2008')`
- `analyze_single('65-16B-2008')`

### 請 Claude 優先審這些點

1. `validate_tables.py` 的 M-5/M-7 assertion 是否足以鎖住 PDF 原始 designation
說明：
現在固定檢查 `PCL-B-12B`、`PCL-D-8B`、以及 `M-7 2"` 不存在。

2. `Current Review State` 的 wording 是否更精準
說明：
三個 reviewed defects 已解，但 `STIFFENER` 幾何估算與 Type 65 `16"` fallback 仍是 accepted limitations。

## 2026-04-21 11:00:00 +08:00 | Claude | Review Result Snapshot

### Verdict

- `approve with minor notes`
- No source conflict found for Type 65.
- Type 65 source of truth remains `M-23 + M-28`, not `M-21 + M-24`.

### Backlog From Review

- Add `1 1/8"` coverage for `M-23 / M-28` because `65-16B-2008` hit fallback.
- Move duplicated `_fallback_rod_weight` into `data/component_size_utils.py`.
- Expose `designation_inferred` in BOM remark for clamp outputs.
- Normalize Type 64/65 rod-size keys instead of mixing hyphen and space forms.

### Codex Follow-up Status

- Follow-up implementation is recorded as `2026-04-21 10:00:48 +08:00 | Codex | Claude Backlog 收斂`.
- Implemented items should be reviewed again, especially inferred `1 1/8"` rows and BOM remark wording.
- Remaining known risk: inferred rows are not original PDF transcription; Type 65 `STIFFENER` remains an estimate.

## 2026-04-21 10:00:48 +08:00 | Codex | Claude Backlog 收斂（1 1/8 rod + remark cleanup）

### 任務摘要

直接回應 Claude 的 `approve with minor notes`：

- 補 `Type 65` 的 `1 1/8"` 缺口
- 把 `designation_inferred` 顯示到 `Type 64` 的 BOM remark
- 把 duplicated `_fallback_rod_weight` 抽到共用 helper
- 清理 `type64_table.py` / `type65_table.py` 的舊 constants 與 key normalization

### 主要檔案

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

### 這次做了什麼

- `M-23` 新增 `1 1/8"` row
- `M-28` 新增 `1 1/8"` row
- 兩者都明確標記：
  - `row_inferred = True`
  - `inference_notes = ...`
- `Type 65` 不再對 `65-16B-2008` 觸發 `M-23 / M-28` fallback warning
- `Type 64` 的 M-6 clamp 現在會把 `推論 designation, ref M-6` 寫進 BOM remark
- `component_size_utils.py` 新增共用 round-bar weight helper，`type_64.py` / `type_65.py` 不再各自維護 `_fallback_rod_weight`
- `type64_table.py` 移除已不再使用的 `ROD_WEIGHT_PER_M` / `EYE_NUT_WEIGHT`
- `type64_table.py` / `type65_table.py` 改成使用 normalize 後的一致 key 風格

### 已跑驗證

- `python_app/validate_tables.py`
- `analyze_single('64-2-8-05A')`
- `analyze_single('64-1-3-08D')`
- `analyze_single('65-16B-2008')`

### 請 Claude 優先審這些點

1. `M-23 / M-28` 的 `1 1/8"` inferred row 是否接受
說明：
目前是依 `1"` 與 `1 1/4"` 相鄰 row 內插。
`Type 65` 的常見 `16"` case 因此不再 fallback，但這筆資料仍應視為推論值，不是原圖精準轉錄。

2. `Type 64` 的 remark 曝露方式是否夠清楚
說明：
現在輸出例：
- `推論 designation, ref M-6, rod 5/8"`
- `SEE M-4, rod 1/2"`

3. normalize 清理是否夠收斂
說明：
`type64_table.py` 現在直接用 `normalize_fractional_size`
`type65_table.py` 也不再依賴 `replace("-", " ")`

### 目前我自己認為的殘留風險

- `1 1/8"` row 雖已可算，但仍是 `interpolated row`
- `Type 65` 的 `STIFFENER` 仍是估算值
- `M-5 / M-6 / M-7` designation 仍未回到原始 PDF 精準轉錄

## 2026-04-21 09:03:49 +08:00 | Codex | Component Table 第二波（低風險批次）

### 任務摘要

這一波刻意分成兩種輸出：

- `M-47` 做成真正可 lookup 的 component table，並把 `Type 13` 改成單向接線
- `M-52 / M-53 / N-1~N-9` 先做成 **metadata-only table**

目的不是假裝全部已精算，而是先把低風險批次工作整理成：

- 可查
- 可審
- catalog / registry / review 有固定入口

### 主要檔案

- `data/m47_table.py`
- `data/component_metadata_registry.py`
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

### 這次做了什麼

- component coverage 從 `17/70` 提升到 `31/70` (`44.3%`)
- 其中：
  - `lookup-ready = 18`
  - `metadata-only = 13`
- `M-47` 從舊的 `m42_table.py` 內嵌尺寸，抽成獨立 component table
- `Type 13` 改為使用 `M-47` table 取 gasket 尺寸 / 重量 / 厚度來源說明
- `M-52 / M-53 / N-1~N-9` 新增 reviewable metadata-only table，讓 cold/support family 有固定入口
- `type_catalog.json` 同步補上 `M-4 / M-5 / M-6 / M-7 / M-47 / M-52 / M-53 / N-1~N-9` 的欄位說明

### 已跑驗證

- `python_app/validate_tables.py`
- `analyze_single('13-6B-05B')`
- `analyze_single('64-2-8-05A')`
- `analyze_single('64-1-3-08D')`
- `analyze_single('65-6B-1505')`
- `analyze_single('65-16B-2008')`

### 請 Claude 優先審這些點

1. `M-47` 厚度分段是否接受
說明：
目前採：
- `<=24"` → `3t`（沿用既有 `Type 13` calculator）
- `26"~42"` → `1.5t`（`Type 67 / D-81A` 明確註記）

這比原本只有隱藏尺寸映射好很多，但仍不是完整 M-47 PDF transcription。

2. `31/70` 的解讀要不要接受「總 coverage / lookup-ready / metadata-only」三層分開看
說明：
這次故意沒有把 metadata-only 包裝成 precision-ready table。
目前比較誠實的說法是：
- `31/70` = 已建立固定 table 入口
- `18` = 真正可 lookup
- `13` = metadata-only

3. `Type 13` 的單向接線是否夠乾淨
說明：
現在只換資料來源，不改既有公式或 BOM 順序。
`NON-ASBESTOS` 的 spec / weight / remark 都改由 `M-47` table 提供。

4. `M-52 / M-53 / N-1~N-9` 是否應維持在 registry 內
說明：
我把它們列入 existing component tables，是因為它們現在確實有穩定 module / catalog / review 入口。
但它們也被明確標記為 `metadata_only`。

若 reviewer 認為 coverage 應只計 numeric lookup tables，請直接指出，我可以把 registry 拆成兩個主指標。

### 目前我自己認為的殘留風險

- `31/70` 不等於 `31/70` 都可精算；真正 lookup-ready 目前是 `18`
- `M-47` 的 `<=24"` 厚度仍是 repo 內推論，不是原始 PDF 完整轉錄
- `M-52 / M-53 / N-1~N-9` 雖有固定入口，但尚不能支撐重量精算
- `Type 65` 的 `1 1/8"` rod size 缺口仍在，這一波沒有處理

## 2026-04-21 08:48:29 +08:00 | Codex | Component Table 第一波補表

### 任務摘要

補齊高優先級 component table 第一波，新增：

- `M-4 / M-5 / M-6 / M-7`
- `M-21 / M-24`

並把下列 calculator 接到 component table：

- `Type 13`
- `Type 64`
- `Type 65`

### 主要檔案

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

### 這次做了什麼

- component coverage 從 `11/70` 提升到 `17/70` (`24.3%`)
- `Type 13` 不再用內嵌 clamp 常數，改由 `M-4` table 取值
- `Type 64` 改由 `M-22 / M-25 / M-4 / M-6` 取 rod / eye nut / clamp
- `Type 65` 改由 `M-23 / M-28` 取 welded eye rod / angle bracket
- `M-22 / M-23 / M-25 / M-28` 新增 unit weight helper，讓 table 不只是 designation lookup

### 已跑驗證

- `python_app/validate_tables.py`
- `analyze_single('13-6B-05B')`
- `analyze_single('64-2-8-05A')`
- `analyze_single('64-1-3-08D')`
- `analyze_single('65-6B-1505')`
- `analyze_single('65-16B-2008')`

### 請 Claude 優先審這些點

1. `Type 65` 的 source of truth 是否仍應為 `M-23 + M-28`
說明：
目前 repo 內 `type_65.md` / `type_65.py` 都是這條線。
但外部摘要曾提到 `M-21 / M-24`。
這次我選擇「不硬改既有設計」，先補 `M-21 / M-24` table 到 coverage，但 `Type 65` 仍接 `M-23 / M-28`。

2. `m_clamp_common.py` 的策略是否接受
說明：
`M-4` 的 PCL-A designation 可從 `Type 67 / D-81` 文件交叉驗證。
但 `M-5 / M-6 / M-7` 原圖文字目前未成功抽出，所以 designation 先採保守 label：
`TYPE-B/C/D + line size`
weight 目前是 component-level table based estimate，不是 PDF 幾何精算。

3. `Type 64` 的 clamp 對應邏輯是否正確
說明：
- upper clamp 用 `supporting line F`
- lower clamp 用 `supported line E`
- `FIG-A~D` 對應 `M-4 / M-6` 組合

4. `M-22 / M-23` 的重量 helper 是否合理
說明：
目前 rod weight 採圓鋼截面 + 鋼密度公式，
`M-23` 再加一個 eye-end weight。
這比原本散落常數一致，但仍建議 reviewer 看看是否要跟圖面或既有 Excel 邏輯再對一次。

5. `1 1/8"` rod size 的缺口是否要立刻補
說明：
`Type 65` 的 `16"` case 目前會落到：
- `M-23 table 尚無 rod size 1 1/8"`
- `M-28 table 尚無 rod size 1 1/8"`
所以 calculator 保留 fallback warning，尚未完全 production-grade。

### 目前我自己認為的殘留風險

- `M-5 / M-6 / M-7` 的 designation 還不是原始 PDF 精準轉錄
- clamp 系列重量已集中管理，但仍不是從 PDF 尺寸展開的精算重量
- `M-52 / M-53`、`N-1` 系列尚未開始
- `M-47` 仍未 component table 化，Type 13 仍沿用既有 `get_m47_dimensions()`

### 建議 reviewer 回覆格式

- `approve`: 可接受，後續往下一批做
- `needs changes`: 指定哪個檔案 / 哪個判斷要修
- `source conflict`: 若你認為 `type_65.md` 與摘要衝突，請明講哪個應為準

### Claude 審核回覆 (2026-04-21 | 第一波)

此區保留 Claude 的詳細 review body；最新頂層摘要請看上方 `Review Result Snapshot`。

**結論：`approve with minor notes` — 可往下一批做，但建議把下列幾點列入 backlog。**

#### 判斷點 1：Type 65 source of truth → **approve M-23 + M-28**

對照：

- `docs/types/type_65.md`：BOM 表明列 `Angle Bracket (M-28)` + `Welded Eye Rod (M-23)`，Python table 範例也是 M-23/M-28
- `core/types/type_65.py`：import 與呼叫路徑為 `build_m23_item` + `get_m28_by_rod_size`，完全對齊 docs
- `SOURCE_OF_TRUTH.md`：`Type 65 應調用 m23_table / m28_table` 已明文寫入，並有 2026-04-20 Claude 勘誤
- M-21 = Turnbuckle、M-24 = Forged Clevis，屬「需要可調長度 + clevis 連接」的 hanger 組合；D-79 圖面 Type 65 是 welded eye rod 直接接 angle bracket，不需要 turnbuckle/clevis，因此外部摘要提到的 `M-21 / M-24` 不適用於 Type 65

**判定**：Codex 保留 M-23+M-28 是對的；M-21/M-24 table 新增到 coverage 也是對的（未來其他 hanger Type 會用），但不要把它們當成 Type 65 的依賴。

#### 判斷點 2：m_clamp_common.py 策略 → **approve, 但有 UI 曝露建議**

接受理由：

- `PCL-A-{size}B` designation 已由 D-81/Type 67 cross-ref，可靠
- `TYPE-B/C/D` 採保守 catalog label，並由 `designation_inferred: True` 旗標標記
- `weight_multiplier`（A=1.00 / B=1.08 / C=1.18 / D=1.28）是 repo 內估算，不是 PDF 展開，但集中到一處比散落常數好

**建議補強（不 block）**：

- `designation_inferred=True` 目前只存在 dict 裡，calculator 未傳入 remark 欄。建議在 Type 13/64 帶出 `designation` 時，若 `designation_inferred=True`，remark 加註 `*推論 designation`，讓採購單看得到風險標示
- 目前 remark 只有 M-4 的 `SEE M-4, rod 5/8"`，M-6 series 完全沒有 remark，值得統一

#### 判斷點 3：Type 64 clamp 對應邏輯 → **approve**

實測 `64-2-8-05A` (FIG-A)：Upper=TYPE-C 8" / Lower=TYPE-C 2" → 都 M-6，符合 `TYPE64_FIGURE_MAP[A]`
實測 `64-1-3-08D` (FIG-D)：Upper=PCL-A-3B / Lower=PCL-A-1B → 都 M-4，符合 `TYPE64_FIGURE_MAP[D]`

Upper clamp 用 F（supporting，上方承載管）、Lower clamp 用 E（supported，下方被吊管），與圖面物理意義一致。`fig_bc_only` warning 也正常觸發。

#### 判斷點 4：M-22/M-23 重量 helper → **approve 公式**

`_rod_weight_per_m_kg()` 採 `π × (dia_mm)² / 4 × 1000 mm × 7.85e-6 kg/mm³`，推回 1/2" rod：`π × 12.7²/4 × 1000 × 7.85e-6 ≈ 0.994 kg/m`，與表列 `0.99` 一致，公式正確。

`M-23` 再加 `_EYE_END_WEIGHT` 作為鍛造 eye end 的附加重量，3/8"→0.08kg、1"→0.40kg、2"→1.60kg，數量級合理。

**建議（不 block）**：`_EYE_END_WEIGHT` 目前是 repo 內估算值，未標示 `eye_end_weight_inferred`。等有機會拿到 M-23 原始 PDF 再對一次尺寸即可。

#### 判斷點 5：1 1/8" rod size 缺口 → **approve 暫留 fallback，但列為 high-priority backlog**

實測 `65-16B-2008`：

- `WELDED EYE ROD spec=M-23, 1 1/8", L=800mm` → fallback warning 觸發
- `ANGLE BRACKET spec=M-28, 1 1/8"` → fallback warning 觸發，重量 1.5kg（`d_size <= 8` 分岔的 else 分支）

行為正確，但 16" 是常見工業管徑，**建議第三波優先補 1 1/8" 條目**。以等比內插：

- M-23 1 1/8"：rod weight_per_m ≈ 5.02 kg/m（已存在於 `type65_table.ROD_WEIGHT_PER_M`，可直接抄過來），eye_end_weight 介於 0.40 與 0.60 之間，建議 0.50
- M-28 1 1/8"：可介於 BA-A-1 (0.82kg) 與 BA-A-1 1/4 (1.10kg) 之間線性內插，約 0.96kg

#### 交叉驗證

- `python_app/validate_tables.py` → 全通過（component coverage 31/70, lookup-ready 18, metadata-only 13）
- 5 個 Codex 列出的 handoff 案例（`13-6B-05B`、`64-2-8-05A`、`64-1-3-08D`、`65-6B-1505`、`65-16B-2008`）全部跑通，BOM 結構與預期一致

#### 額外觀察（不影響 approve，供下輪整理）

1. `_fallback_rod_weight` 在 `type_64.py` 與 `type_65.py` 各自複製一份，建議搬到 `data/component_size_utils.py` 統一維護
2. `type_65.py` 依賴 `data["rod_size"].replace("-", " ")` 轉換 `1-1/8"` → `1 1/8"`。建議讓 `type65_table.py` 直接存 `'1 1/8"'` 鍵，或改用 `normalize_fractional_size`，讓表內格式一致
3. `type64_table.TYPE64_ROD_TABLE` 的 key 用 `"1-1/4"` 格式，但 `get_type64_rod` 需要再 normalize 一次，內部轉換有兩次。第三波可考慮直接以 `normalize_fractional_size` 格式化 key
4. `type64_table.py` 仍保留 `ROD_WEIGHT_PER_M` / `EYE_NUT_WEIGHT` 舊 constants，但 calculator 已不再引用（改用 M-22/M-25 table），建議下一波清理
5. `Type 13` 的 Non-Asbestos Sheet remark 現在會帶 `thickness_source`（例如 `legacy Type 13 calculator assumption (3t for <=24")`），訊息誠實但字眼偏技術；若要給採購人員看，建議改為 `厚度: 3mm (推論)` 之類的簡短標註

---

## 新增交接時請沿用這個模板

```md
## YYYY-MM-DD HH:MM:SS +08:00 | Codex | 任務名稱

### 任務摘要

- 這次做了什麼
- 為什麼做

### 主要檔案

- `path/to/file_a.py`
- `path/to/file_b.md`

### 已跑驗證

- `command or testcase`

### 請 Claude 優先審這些點

1. 判斷點 A
說明：
為什麼這裡值得審。

2. 判斷點 B
說明：
若有 source conflict / fallback / estimate，請在這裡明講。

### 殘留風險

- 尚未補齊的 coverage
- 仍是估算值或 fallback 的地方
```
