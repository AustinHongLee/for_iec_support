# Excel Workbook Design Spec

> Codex implementation brief — IEC 管架支撐 材料/重量分析 Excel 匯出 workbook 視覺與版面規格。
> 目標：純樣式/版面/呈現層升級。**不改任何 BOM、重量、數量、Type calculation、材料邏輯、public API、sheet 名稱（除非標 optional）。**
> 全部以 openpyxl 可實作為前提。檔案路徑均相對 `python_app/export/excel/`。

現況快照（實作對齊用）：
- 共用樣式集中在 `styles.py::_styles()`（已是「深靛 1F3864 + 琥珀 BF8F00」配色，2026-05）。本 spec 在此基礎上**收斂為命名 token + 補新 helper**，不重起爐灶。
- 9 張 sheet 由 `workbook.py::export_project_workbook()` 依序建立，順序與名稱維持。
- Header 常數集中在 `headers.py`（`PROJECT_HEADERS`/`SUMMARY_HEADERS`/`_CALC_BASIS_HEADERS`/`CUTTING_HEADERS`/`LEADER_*`/`VISUAL_SLOT_COUNT=30`）。
- legacy `_format_sheet()`（黃底表頭 FFFF00）僅供 `simple_exports.py` 的單表匯出使用 → 屬 public API，預設**不動**（見 §7）。

---

## 1. Design Direction

1. **三層閱讀動線**：主管/業主（第一眼 KPI + 異常）→ 採購/製造（合計、分類、下料）→ 工程/審查（明細、計算式、標準）。每張 sheet 標題列即標明它服務哪一層。
2. **工程審查可信感**：深靛主色 + 細灰格線 + 一致小數位，數字靠右對齊、千分位、單位欄分離；避免花俏，重在「看得懂、對得起來、印得出來」。
3. **一眼抓重點**：KPI 大數字用琥珀強調；Top N、佔比、使用率用 data bar / color scale，讓「最重 / 最低使用率 / 需確認」自己跳出來。
4. **語意化顏色，不靠記憶**：狀態色（OK 綠 / 需確認 紅 / 未納入 橘）與資料可信度色（精確/推導/估算/未知）兩套**獨立** ramp，固定語意、固定 hex。
5. **可操作的表格**：所有「平表」一律 freeze 表頭 + autofilter + zebra；凡有 merge / 重複表頭 / 小計列的 sheet **一律不上 autofilter**（避免破壞）。
6. **採購/主管印得出來**：每張 sheet 設定 print layout（方向、fit-to-width、重複表頭列、頁尾頁碼 + sheet 名），A4 直接送印或 PDF。
7. **單一樣式來源**：所有 hex / 數字格式 / 列高 收斂成 `styles.py` 的 `COLORS` / `NUMFMT` token 與共用 helper，sheet renderer 不再各自寫死樣式，杜絕漂移。
8. **異常前置**：主管頁直接顯示「錯誤項 / 需確認項」計數與導引，不必翻到明細頁才發現問題。

---

## 2. Global Style System

### 2.1 Color palette（命名 token → hex；放 `styles.py` 模組級 `COLORS` dict）

| Token | Hex | 用途 |
|---|---|---|
| `ink` | `1F3864` | 主標題列底、全案合計列底、medium 邊框、section 字色 |
| `ink2` | `2E5395` | 表頭列底（header fill） |
| `nav_sub` | `DEE3EE` | 次級表頭 / 區塊內表頭 |
| `section` | `D9E1F2` | 區塊小標題列（▌） |
| `canvas` | `F2F4F8` | 副標題列、KPI label 底 |
| `zebra` | `F7F9FC` | 隔行底色 |
| `accent` | `BF8F00` | KPI 大數字、重點 data bar、關鍵數值 |
| `subtotal` | `FFF2CC` | 小計列底（暖色） |
| `card_border` | `D0D7E2` | KPI 卡片邊框 |
| `grid` | `BFBFBF` | 資料格 thin 邊框 |
| `text_mute` | `595959` | 副標題、註解主文 |
| `text_note` | `808080` | KPI note / 次要說明 |
| **狀態（action）** | | |
| `ok_fill`/`ok_mark` | `E2EFDA` / `70AD47` | 命中、正常、餘料健康 |
| `warn_fill`/`warn_mark` | `FFF2CC` / `ED7D31` | 未納入、短料、待留意 |
| `bad_fill`/`bad_mark` | `FCE4D6` / `C00000` | 需確認、錯誤、廢料 |
| `info_fill`/`info_mark` | `DDEBF7` / `4472C4` | 資訊、下料使用段 |
| **資料可信度（data）** | | |
| `conf_exact` | `C6EFCE` | 精確 — 直接查表 |
| `conf_derive` | `BDD7EE` | 推導 — 公式計算 |
| `conf_estimate` | `FFEB9C` | 估算 — 工程假設 |
| `conf_unknown` | `FFC7CE` | 未知 — 需複核 |
| **下料圖示** | | |
| `bar_used` | `4472C4` | 已使用段 |
| `bar_remnant` | `A9D18E` | 健康餘料 |

> 多數 hex 已存在於 `_styles()`，本表只是把它們**命名並集中**；`_styles()` 改為「從 `COLORS` 組裝 PatternFill/Font」。狀態 ramp 與可信度 ramp 不可混用。

### 2.2 Fonts

| 用途 | 字體 | 大小 | 粗體 | 色 |
|---|---|---|---|---|
| 主標題 | `FONT_CJK`（預設 `Microsoft JhengHei`，缺字 fallback `Calibri`）| 18 | B | FFFFFF |
| 區塊標題 ▌ | `FONT_CJK` | 12 | B | `ink` |
| 表頭 | `FONT_CJK` | 11 | B | FFFFFF |
| KPI 數字 | `Calibri` | 22 | B | `ink`（一般）/ `accent`（強調）|
| KPI label / note | `Calibri` | 10 / 9 | — | `text_mute` / `text_note` |
| 資料列（文字）| `FONT_CJK` | 10–11 | — | 000000 |
| 資料列（數字）| `Calibri` | 10–11 | — | 000000 |
| 副標題 | `Calibri` italic | 10 | — | `text_mute` |
| 合計列 | `FONT_CJK` | 12 | B | FFFFFF |

- 新增 `FONT_CJK` token（模組級常數）。**CJK 字體切換標 optional**：若客戶機器無 `Microsoft JhengHei`，可回退 `Calibri`（Excel 自動 CJK fallback），純風格差異、不影響資料。
- 數字一律 `Calibri`（對齊與千分位較穩）。

### 2.3 Borders

- 資料格：四邊 `thin / grid`（沿用 `_styles()["border"]`）。
- 表頭：底邊 `medium / ink`，其餘 thin。
- 合計/小計列：上邊 `medium / ink`。
- KPI 卡片：四邊 `thin / card_border`。
- 下料圖示 slot 格：邊框改 `thin` 且色 `FFFFFF`（白），讓色塊連成一條 bar、不被灰線切碎。

### 2.4 Alignment

| 內容型別 | 水平 | 垂直 | 其他 |
|---|---|---|---|
| 文字短欄（型號/品名/材質/狀態）| left, indent=1（狀態欄 center）| center | — |
| 數字（重量/長度/數量/佔比/使用率）| right | center | — |
| 單位欄 | left, indent=1 | center | — |
| 長文字（計算式/來源/備註/命中明細）| left | center/top | `wrap_text=True` |
| 表頭 / KPI / 區塊標題 | center（區塊標題 left）| center | — |

### 2.5 Number formats（命名 token → 放 `styles.py::NUMFMT`）

| Token | 格式 | 套用 |
|---|---|---|
| `WEIGHT_KG` | `#,##0.00` | 展示用重量（材料合計、重量分析、Top 表）|
| `WEIGHT_KG3` | `#,##0.000` | 審查精度重量（重量明細表、計算頁、合計列）|
| `LEN_MM` | `#,##0` | 長度/寬度（mm，整數）|
| `LEN_MM1` | `#,##0.0` | 下料長度（mm，需 0.1）|
| `QTY_INT` | `#,##0` | 數量/組數/根數/段數 |
| `PCT` | `0.0%` | 佔比、使用率（**值存 0–1 比例**）|
| `PIPE_IN` | `0.##` | 管徑（in）|
| `MONEY` | `#,##0` | 金額感整數（如有）|

- **使用率改存數值比例 + `PCT` 格式**（目前 `下料明細/下料圖示` 存字串 `"xx.x%"`）→ 才能 filter / color scale。屬呈現層改動，數值不變。
- 千分位一律用 `#,##0` 系，避免大數字難讀。

### 2.6 Row heights / Column behavior

- 列高：標題 40、副標題 22、區塊標題 24、表頭 24–28、資料 16–20、KPI label/value/note = 18/34/16。
- 欄寬：沿用各 sheet 既有 `_set_widths(...)` 陣列，依 §4 微調；**不**用 legacy `_format_sheet` 的 auto-width（上限 30、含黃底，棄用於主 workbook）。
- 長文字欄（計算式/備註/來源）給足寬度 + wrap，不截斷。

### 2.7 Freeze panes / Autofilter / Gridlines（原則）

| 原則 | 規則 |
|---|---|
| Gridlines | 全部 `ws.sheet_view.showGridLines = False`（`_setup_sheet` 已做），靠邊框界定表格 |
| Freeze | 平表 freeze 在表頭下一列（如 `A4`）；儀表板 freeze 在標題下（`A3`）|
| Autofilter | **只給無 merge、無重複表頭、無內嵌小計列的平表**：重量分析、材料合計、支撐統計明細、重量明細表（範圍須排除合計列）|
| 禁用 Autofilter | 專案摘要、支撐分類統計、下料明細、下料圖示（含 merge / 重複表頭）|

---

## 3. Shared Helper Changes（`styles.py`）

> 新增為主、修改為輔；**保留所有現有函式簽章**（被 `excel_export.py` re-export，屬相容面）。新 helper 採加法，sheet 逐步遷移。

**新增 token / 常數**
- `COLORS: dict[str,str]`、`NUMFMT: dict[str,str]`、`FONT_CJK: str`、`ROW_H: dict[str,int]` — 用途：單一樣式來源；`_styles()` 改為消費 `COLORS`/`FONT_CJK` 組裝（行為等價、hex 不變）。

**新增 helper**
- `apply_status_fill(cell, status, *, set_font=False)` — 用途：集中狀態著色（取代 leader/cutting 內重複的 if/elif）。參數：`status ∈ {命中,需確認,未納入,正常,短料,廢料}`。行為：依 §2.1 狀態 ramp 設 `fill`（可選 `bad_mark` 字色），未知值不著色並回傳 False。
- `apply_confidence_fill(cell, level)` — 用途：資料可信度著色。參數：`level ∈ {精確,推導,估算,未知}`。行為：套 `conf_*`、粗體；沿用既有 `_CONFIDENCE_FILL` 對應。
- `set_print_layout(ws, *, orientation="landscape", fit_width=1, fit_height=None, title_rows="3:3", area=None, footer_title=None)` — 用途：統一列印版面。行為：設 `page_setup.orientation`、`sheet_properties.pageSetUpPr.fitToPage=True`、`page_setup.fitToWidth/Height`、`print_title_rows`、`print_area`、`oddFooter`（左=footer_title、中=sheet 名、右=`Page &P / &N`）、`oddHeader` 製表日期；A4。
- `freeze_and_filter(ws, header_row, last_row, last_col_letter, *, autofilter=True)` — 用途：平表標準收尾。行為：`freeze_panes = A{header_row+1}`；`autofilter=True` 時設 `auto_filter.ref = A{header_row}:{col}{last_row}`（呼叫端負責讓 `last_row` 不含合計列）。
- `apply_report_table(ws, header_row, headers, first_data_row, last_data_row, *, col_formats, widths=None, zebra=True, freeze=True, autofilter=True)` — 用途：平表一次成型（表頭 + 邊框 + zebra + number format + freeze/filter）。行為：內部呼叫 `_write_headers`、`_apply_table_style`、`_apply_zebra`、`_format_number_block`、`freeze_and_filter`。供「重量分析 / 材料合計 / 支撐統計明細」遷移。
- `write_grand_total_band(ws, row, last_col, label, value_col, value, *, fmt=NUMFMT["WEIGHT_KG3"], label_col=1)` — 用途：統一「全案合計」深靛橫幅（目前在 3 個 sheet 各寫一次）。行為：整列填 `ink` + 白粗字 + medium 上框，寫 label 與 value、套 fmt、列高 24。
- `add_color_scale(ws, cell_range, kind)` — 用途：包裝 `ColorScaleRule`。參數：`kind ∈ {util,weight,remnant}`。行為：`util` 紅→黃→綠（min/mid 50%/max）；`weight` 白→琥珀；`remnant` 綠→紅。openpyxl `ColorScaleRule`。
- `write_kpi_strip(ws, row, specs)` — 用途：一列多張 KPI 卡片（specs=list of dict）。行為：對每個 spec 以間隔 3 欄呼叫 `_kpi_card`（封裝專案摘要的重複呼叫，便於加「異常」卡）。

**修改現有 helper（向後相容）**
- `_setup_sheet(...)` — 新增可選參數 `freeze_title=False`（True 時 `freeze_panes='A3'`）、`audience=""`（在副標題右側附「適用：主管/採購/工程」標記）。預設行為不變。
- `_kpi_card(...)` — `value_format` 預設改吃 `NUMFMT` token 字串；新增可選 `tone ∈ {neutral,bad,warn}` 讓「異常」卡片用 `bad_fill` 底。預設不變。
- `_add_data_bar(...)` — 增可選 `color` 預設 `COLORS["accent"]`；其餘不變。
- `_apply_zebra(...)` — 維持，但補一個防呆：跳過已被狀態色/小計色填過的列（檢查 fill 是否屬 `COLORS` 狀態集）。
- `_format_sheet(...)`（legacy 黃底）— **不改**；標註 `# legacy: simple single-sheet export only`（見 §7）。

---

## 4. Sheet-by-Sheet Specification

### Sheet: 專案摘要
**File:** `project_summary_sheet.py::_write_project_summary_sheet`
**Audience:** 主管 / 業主（第一層）
**Purpose:** 一頁看完總重、重點材料、最重支撐、**異常/需確認項目**、各分頁導引。

**Layout（沿用現況 + 1 個新區塊）**
- R1 主標題（深靛白字 18），R2 副標題（製表日 + 總重 + 支撐數 + 材料數）。
- R3 空。**R4 ▌關鍵指標**；R5–R7 KPI×4（支撐組數 / 材料種類 / 專案總重 / 平均單組重）。
- R8 空；R9–R11 KPI×4（下料材料 / 建議原料根數 / 下料段數 / 平均使用率）。
- **新增 R12 空；R13–R15 ▌品質與異常 KPI×3**：①錯誤項目（`len(project.errors)`，tone=bad）②需確認分類（`status=="需確認"` 計數，tone=warn）③平均使用率或健康度。下接一行導引文字「→ 詳見『支撐統計明細』『重量明細表』」。
- 其後區塊整體下移：▌重型支撐 Top 5 → ▌材料重量分佈 Top 8 → ▌Workbook 索引 → ▌注意事項（皆沿用現有渲染）。

**Visual rules**
- title/subtitle：`ink`/`canvas`，副標題 italic 灰。
- KPI：label 灰小字、value 22pt（總重/根數/異常用 `accent` 或 `bad`）、note 9pt 灰；卡片 `card_border`。
- Top 表：表頭 `ink2` 白字；數字右對齊；「視覺比例」欄 data bar（Top5 用 `accent`、Top8 用 `info_mark`）。
- 索引/注意事項：zebra、bold 分頁名、項目符號「・」。

**Specific changes**
- 新增「品質與異常」KPI 區塊（上方）；用 `write_kpi_strip` + `_kpi_card(tone=...)`。
- `_setup_sheet(..., freeze_title=True)` → freeze `A3`，捲動時標題恆在。
- 所有 KPI `value_format` 改用 `NUMFMT` token（總重 `WEIGHT_KG`、計數 `QTY_INT`、使用率 `PCT`）。
- KPI「平均使用率」已存 0–1 比例 → 確認用 `PCT`。
- 套 `set_print_layout(orientation="landscape", fit_width=1, title_rows=None, area="A1:L<最後一列>", footer_title="專案摘要")`。

**Conditional formatting**
- Top5/Top8 data bar（保留）。
- 異常 KPI：值 > 0 時卡片底色 `bad_fill`/`warn_fill`（用 tone 參數，不需 CF rule）。

**Print/layout:** A4 橫向、fit 1 頁寬；footer 中=「專案摘要」、右=頁碼；不重複表頭（單頁儀表板）。

**Risk/notes:** 此頁 merge 多，**禁止加 autofilter**。新增區塊會推移後續列號 → 後面所有 `_section_header`/表頭/資料的起始 row 需同步 +3（建議改用「running `row` 游標」而非寫死列號，降低未來維護風險）。KPI 數字僅引用既有彙總值，不得重算。

---

### Sheet: 重量明細表
**File:** `calculation_sheets.py::_write_calculation_basis_sheet`
**Audience:** 工程/審查 + 採購（樞紐分析來源）
**Purpose:** 單件 × 組數 × 總重 的逐列平表，含每型號小計與全案合計。

**Layout**
- R1 標題 + R2 副標題（總組數/成功/錯誤/總重）。R3 表頭（`_CALC_BASIS_HEADERS`，17 欄）。
- R4+ 每型號明細列 → 該型號 `小計` 列（暖色）→ … → 末列 `全案合計`（深靛）。
- **新增第 18 欄 `列型`**（值：`明細`/`小計`/`合計`）→ 解決「平表夾小計」無法乾淨 filter/pivot 的問題。

**Visual rules**
- 表頭 `ink2`；明細 zebra；數量欄（9,10,11）淡藍 `EAF2F8`；小計列 `subtotal` 粗體；合計列 `ink` 白粗。
- 計算式欄（15）wrap、左對齊、寬 50。

**Specific changes**
- `headers.py::_CALC_BASIS_HEADERS` 末端 append `"列型"`（→ 18 欄）；明細列寫 `明細`、小計寫 `小計`、合計寫 `合計`。
- Number format 統一：欄 6,7 → `LEN_MM`；9,10,11 → `QTY_INT`；12,13,14 → `WEIGHT_KG3`。
- **Autofilter 範圍排除合計列**：`auto_filter.ref` 結束於「最後一筆小計列」而非 `全案合計` 列（合計列另起一列，落在 filter 範圍外）。
- 用 `write_grand_total_band` 渲染全案合計列。
- 欄寬補 `列型` ≈ 8。

**Conditional formatting**
- 總重欄（14）`add_color_scale(kind="weight")`（白→琥珀），僅套明細列範圍（不含小計/合計）。

**Print/layout:** A4 橫向、fit 1 頁寬、`title_rows="3:3"`（每頁重複表頭）、footer 右頁碼。

**Risk/notes:** 加欄會讓 `last_col_letter` 由 Q→R，所有引用 `n_cols`/`get_column_letter(n_cols)` 自動跟著（程式已用 `len(...)`，安全）。**Optional（更激進）**：若要真正 pivot-friendly，可移除內嵌小計列、只留合計列於 filter 外——但會犧牲審查者偏好的逐型小計，預設**不做**，僅標記。

---

### Sheet: 計算標準與假設
**File:** `calculation_sheets.py::_write_calc_reference_sheet`
**Audience:** 主管 / 業主 / 客戶（靜態說明頁）
**Purpose:** 揭示重量計算引用標準、資料狀態圖例、各支撐可信度彙整。

**Layout（沿用）**
- R1 標題 + R2 副標題。▌計算標準與假設（表：計算項目 / 引用標準 / 說明，說明欄 merge C:F）。
- ▌資料狀態圖例（4 色塊：精確/推導/估算/未知）。▌各支撐重量彙整（型號/組數/資料狀態/單組重/合計重/備註）+ 全案合計列。

**Visual rules**
- 標準表：表頭 `nav_sub` 粗體；說明欄 wrap、左對齊 indent。
- 圖例：4 格 `conf_*` 色塊、置中粗體。
- 彙整表：資料狀態欄用 `apply_confidence_fill`；合計列深靛橫幅。

**Specific changes**
- 圖例/彙整改呼叫 `apply_confidence_fill`（取代散落的 `PatternFill(...)`）。
- 合計列改 `write_grand_total_band`。
- 單組重/合計重欄套 `WEIGHT_KG3`。
- 標準表「說明」欄列高自適應（wrap），確保長公式（鋼板密度式）不被切。

**Conditional formatting:** 無（靜態頁，以固定色塊表達語意即可）。

**Print/layout:** **A4 直向**、fit 1 頁寬、footer 中=「計算標準與假設」；此頁最常被印出/附報告 → 版面務必置中、留白均勻。

**Risk/notes:** 純靜態，無 filter。`_STANDARDS_TABLE` 文案/標準名屬內容，不更動。

---

### Sheet: 支撐分類統計
**File:** `leader_sheets.py::_write_leader_procurement_sheet`
**Audience:** 採購 / 製造（第二層）+ 主管摘要
**Purpose:** 僅列本批有數量或需確認的支撐分類；每項下方列命中型號與判定依據。

**Layout（沿用區塊式）**
- R1 標題 + R2 摘要說明（merge A2:I2）。R4+ 每個 active stat 一個區塊：①統計表頭（`LEADER_STAT_HEADERS`）②統計摘要列（`section` 底粗體）③命中明細表頭（`LEADER_GROUP_DETAIL_HEADERS`，`nav_sub`）④逐筆明細列⑤空行。

**Visual rules**
- 統計表頭 `ink2` 白字；摘要列 `section` 粗體；明細表頭 `nav_sub`。
- 明細「狀態」欄（col1）用 `apply_status_fill`（命中綠/需確認紅/未納入橘）置中。
- 管徑欄 `PIPE_IN`；數量欄 `QTY_INT`/`0.000`(KG)。

**Specific changes**
- 狀態著色改呼叫 `apply_status_fill`（取代 `write_detail_row` 內 if/elif）。
- 區塊間距固定（明細後恆留 1 空列，已有 → 保持）。
- 各統計摘要列的「命中/確認筆數」欄維持，字級一致化。
- 套 `set_print_layout`。

**Conditional formatting:** 以 `apply_status_fill` 直接著色（區塊式不適合 range CF）。

**Print/layout:** A4 橫向、fit 1 頁寬；**不**設 `print_title_rows`（重複表頭會與區塊內表頭打架）；footer 頁碼。

**Risk/notes:** 重複表頭 + merge → **嚴禁 autofilter**（現況正確，維持）。freeze `A4` 維持。所有 stat 值/命中判定來自 `_leader_procurement_stats`，不更動。

---

### Sheet: 支撐統計明細
**File:** `leader_sheets.py::_write_leader_detail_sheet`
**Audience:** 工程/審查 / 製表者查核（第三層）
**Purpose:** 逐筆列出命中 / 需確認 / 未納入來源，供查核。

**Layout（平表）**
- R1 標題 + R2 說明（merge A2:L2）。R3 表頭（`LEADER_DETAIL_HEADERS`，12 欄）。R4+ 逐筆。

**Visual rules**
- 表頭 `ink2`；狀態欄（col1）`apply_status_fill` 置中；數值欄（5,6,7）右對齊；命中明細/條件/備註 wrap。
- **新增 R2 右側狀態圖例**（命中/需確認/未納入 三色小方塊 + 文字），讓查核者秒懂色碼。

**Specific changes**
- col1 著色改 `apply_status_fill`。
- 改用 `apply_report_table`（表頭 + 邊框 + zebra + number format + freeze + filter 一次到位）。
- 數字格式：管徑(6) `PIPE_IN`、計入數量(7) `QTY_INT`/`0.000`(KG)、組數(5) `QTY_INT`。

**Conditional formatting**
- Optional：以 `FormulaRule` 依「狀態」欄自動著整列（比逐格手動更耐未來改動）；預設仍用 `apply_status_fill`，CF 標 optional。

**Print/layout:** A4 橫向、fit 1 頁寬、`title_rows="3:3"`、footer 頁碼。

**Risk/notes:** 平表無 merge → autofilter 安全（範圍 `A3:L{last_row}`，現況正確）。狀態/判定值不更動。

---

### Sheet: 重量分析
**File:** `weight_sheets.py::_write_project_weight_sheet`
**Audience:** 工程/審查（第三層）
**Purpose:** 單件與總量並列、按 entry 展開的逐列明細。

**Layout（平表）**
- R1 標題。R3 表頭（`PROJECT_HEADERS`，18 欄）。R4+ 每 entry 一列；錯誤型號占一列（col2=`Error`，col3=訊息，col9=數量）。

**Visual rules**
- 表頭 `ink2`；zebra；數字右對齊；計算說明(18) wrap。
- **錯誤列整列 `bad_fill`**（目前無著色 → 改善：一眼看到失敗項）。

**Specific changes**
- Number format 修正：6,7（長度/寬度 mm）由 `0.00` → `LEN_MM`；8,9,10（數量/組數/總數量）→ `QTY_INT`；11,12（單組重/總重）→ `WEIGHT_KG`。
- 錯誤列：寫入後對該列 1..18 套 `bad_fill`（值不變）。
- 改用 `apply_report_table` 收尾（freeze `A4` + filter `A3:R{last}`）。

**Conditional formatting**
- 總重欄（12）`add_color_scale(kind="weight")`（明細列範圍），凸顯重項。

**Print/layout:** A4 橫向、fit 1 頁寬、`title_rows="3:3"`、footer 頁碼。

**Risk/notes:** 平表無 merge → filter 安全。`scaled/single` 數值原樣輸出，僅改格式與底色。

---

### Sheet: 材料合計
**File:** `material_sheets.py::_write_material_summary_sheet`
**Audience:** 採購（第二層）
**Purpose:** 依材質聚合的採購清單 + 合計總重。

**Layout（平表）**
- R1 標題。R3 表頭（`SUMMARY_HEADERS`，13 欄）。R4+ 每材料一列。**合計列改為緊接資料下一列**（移除中間空白 gap）。

**Visual rules**
- 表頭 `ink2`；zebra；數量/長度右對齊；來源編碼(13) wrap、寬 46。
- 合計列：深靛橫幅（`write_grand_total_band`），label 在「總重」欄左側、值在總重欄。

**Specific changes**
- Number format：需求總長(7)/原料長度(10) → `LEN_MM`（或 `LEN_MM1`）；需求件數(8)/建議採購量(11) → `QTY_INT`；總重(9) → `WEIGHT_KG`。
- 移除資料與合計間的空白列；合計列用 `write_grand_total_band(value_col=9)`，落在 autofilter 範圍**外**。
- 改用 `apply_report_table`（freeze `A4` + filter `A3:M{last_data_row}`，`last_data_row` 不含合計）。

**Conditional formatting**
- 總重欄（9）`add_color_scale(kind="weight")`，凸顯採購大項。

**Print/layout:** A4 橫向、fit 1 頁寬、`title_rows="3:3"`、footer 頁碼。

**Risk/notes:** 聚合值來自 `summary.lines`，不更動。注意合計列**不可**落在 filter ref 內（否則被當資料列篩選）。

---

### Sheet: 下料明細
**File:** `cutting_sheets.py::_write_cutting_detail_sheet`
**Audience:** 採購 / 製造（第二層）
**Purpose:** 每根原料的切割順序、累計、餘料、使用率。

**Layout（區塊式，每材料一塊）**
- R3+ 每 plan：①plan 標題列（深靛 merge A:I）②plan 摘要列（需求段數/總長/原料根數/平均使用率）③下料表頭（`CUTTING_HEADERS`，9 欄）④各原料的段列 + 餘料列⑤空行。

**Visual rules**
- plan 標題 `ink` 白字；**plan 摘要列改為次級樣式**（`canvas` 底 + 標籤粗體，目前裸列 → 美化）。
- 段列邊框；餘料列依 `廢料/短料/正常` → `bad/warn/ok` 著色（`apply_status_fill`）。

**Specific changes**
- 使用率改存**數值比例**（餘料列 col7、摘要列）+ `PCT` 格式（目前存 `"xx.x%"` 字串）。
- 長度欄（需求長3/含損耗4/累計5/餘料6 或對應欄）套 `LEN_MM1`。
- 餘料列著色改 `apply_status_fill`。
- plan 摘要列以 `canvas` 底 + 粗標籤呈現。
- 套 `set_print_layout`。

**Conditional formatting**
- 使用率欄 `add_color_scale(kind="util")`（紅→黃→綠）——僅在「使用率為數值」後可用。

**Print/layout:** A4 橫向、fit 1 頁寬；**不**設重複表頭（區塊式）；footer 頁碼。

**Risk/notes:** 區塊 + merge → **無 autofilter**（維持）。freeze `A3` 維持。切割結果（bar/piece/remnant）為計算輸出，**只改顯示格式與著色**，數值不動。

---

### Sheet: 下料圖示
**File:** `cutting_sheets.py::_write_cutting_visual_sheet`
**Audience:** 採購 / 製造（第二層）
**Purpose:** 每根原料一列、色塊長條呈現使用率與餘料狀態。

**Layout**
- R2 圖例說明。R4 表頭（材料/原料#/使用率/餘料/下料配置…30 slot…/用於）。R5+ 每根原料一列：col1–4 + 30 個 slot 色塊 + 末欄文字配置。
- **新增 R3 比例尺列**：在 slot 區上方標 0% / 50% / 100% 刻度（merge 對應 slot 區段），讓長條可讀數。

**Visual rules**
- slot：已用段 `bar_used`、健康餘料 `bar_remnant`、短料 `warn_fill`、廢料 `bad_fill`；**slot 邊框改白色**讓條塊連續。
- 使用率欄右對齊；餘料欄 `LEN_MM1`。

**Specific changes**
- 使用率（col3）改數值比例 + `PCT`。
- slot 邊框色改 `FFFFFF`。
- 新增比例尺列（靜態 merge + 置中小灰字）。
- 套 `set_print_layout`。

**Conditional formatting**
- 使用率欄（col3）`add_color_scale(kind="util")`。

**Print/layout:** A4 橫向、fit-to-width=1（30 slot 需壓寬）；footer 頁碼；freeze `A5` 維持。

**Risk/notes:** 30 slot 寬度固定 2.2；列印壓縮後仍可辨色塊即可。色塊比例由 `used_slots` 計算（既有邏輯），不動。

---

## 5. Implementation Order For Codex（低風險）

> 原則：先地基（token/helper，純加法）→ 先改最小最獨立的平表 → 最後動最複雜的儀表板。每步皆「匯出 → openpyxl 讀回 → 比對關鍵值」。

| # | 動作 | 檔案 | 驗證 |
|---|---|---|---|
| 1 | 加 `COLORS`/`NUMFMT`/`FONT_CJK`/`ROW_H` token；`_styles()` 改為消費 token（hex 不變）；新增 `apply_status_fill`/`apply_confidence_fill`/`set_print_layout`/`freeze_and_filter`/`apply_report_table`/`write_grand_total_band`/`add_color_scale`/`write_kpi_strip` | `styles.py` | `python -c "from python_app.export.excel_export import *"` 不報錯；跑一次匯出，workbook 開得起來、外觀與舊版**等價** |
| 2 | 材料合計：number format + 合計橫幅 + 移除 gap + `apply_report_table` | `material_sheets.py` | `load_workbook` 讀回；合計總重 cell 值 == 改前；`sheetnames` 不變 |
| 3 | 重量分析：number format + 錯誤列著色 + color scale + `apply_report_table` | `weight_sheets.py` | 比對任一 entry 的總重/數量值不變；filter ref = `A3:R{last}` |
| 4 | 支撐統計明細：`apply_status_fill` + 狀態圖例 + `apply_report_table` | `leader_sheets.py` | 命中/需確認/未納入筆數不變；filter 可用 |
| 5 | 重量明細表：加 `列型` 欄 + number format + filter 範圍排除合計 + 合計橫幅 + color scale | `calculation_sheets.py` + `headers.py` | 全案合計值不變；filter `列型=明細` 後僅見明細；小計/合計列在 filter 外 |
| 6 | 計算標準與假設：`apply_confidence_fill` + 合計橫幅 + 直向 print | `calculation_sheets.py` | 圖例 4 色正確；列印預覽單頁置中 |
| 7 | 支撐分類統計：`apply_status_fill` + print（無重複表頭） | `leader_sheets.py` | 區塊結構不亂；無 autofilter |
| 8 | 下料明細 + 下料圖示：使用率轉數值 + `PCT` + color scale + 餘料著色 + 比例尺 + slot 白框 + print | `cutting_sheets.py` | 任一 bar 使用率值（比例×100）== 舊字串值；色塊數不變 |
| 9 | 專案摘要：異常 KPI 區塊 + freeze 標題 + token 化 number format + landscape print | `project_summary_sheet.py` | KPI 數字 == 既有彙總；後續區塊列號正確未重疊；Top5/Top8 data bar 在 |

每步通用驗證指令：
```
python -c "import openpyxl; wb=openpyxl.load_workbook('OUT.xlsx'); print(wb.sheetnames)"
```
並對「全案總重」「支撐組數」等關鍵 cell 做改前/改後比對（值必須相同）。

---

## 6. QA Checklist（實作後）

- [ ] workbook 可正常開啟（Excel + `openpyxl.load_workbook`，無修復提示）。
- [ ] `wb.sheetnames` == 原 9 名、原順序（專案摘要→…→下料圖示）。
- [ ] public API 不變：`export_to_excel` / `export_project_to_excel` / `export_project_workbook` 簽章與行為一致。
- [ ] 關鍵儲存格值未變：全案總重、各型號小計、支撐組數、材料項數、各 entry 重量/數量（改前/改後逐一比對）。
- [ ] Number format 正確：kg=`#,##0.00`/`.000`、mm=`#,##0`、數量=`#,##0`、百分比=`0.0%`（且使用率/佔比實際存 0–1）。
- [ ] Frozen panes：平表 `A4`、儀表板 `A3`、下料圖示 `A5`、下料明細 `A3` 皆正確。
- [ ] Autofilter：僅平表 4 張有；範圍**不含**合計/小計列；含 merge/重複表頭的 4 張**無** filter。
- [ ] 無 merged cell 落在任何 autofilter ref 內（破壞 filter）。
- [ ] Conditional formatting 規則數合理、範圍不含表頭/合計列；color scale 在數值欄。
- [ ] 狀態色/可信度色語意正確（命中綠/需確認紅/未納入橘；精確/推導/估算/未知）。
- [ ] `列型` 欄存在於重量明細表且值為 明細/小計/合計。
- [ ] Print/layout：各 sheet 方向、fit-to-width、重複表頭列、footer 頁碼正確；A4 預覽不爆欄。
- [ ] 不適用情境說明：本 workbook 為**桌面/列印**導向，不針對手機；下料圖示 30 slot 在窄螢幕需橫向捲動，屬預期。
- [ ] legacy `_format_sheet` 路徑（simple_exports）仍可獨立匯出、未被破壞。
- [ ] 字體 fallback：無 `Microsoft JhengHei` 時回退 `Calibri`，CJK 仍正常顯示。

---

## 7. Non-Goals（明確不做）

- 不改任何 BOM、重量、數量、Type calculation、材料/聚合邏輯（`core.*` 一律不動）。
- 不改資料模型（`models.py`、`AnalysisEntry`、`MaterialSummary`、`CuttingPlan` 等結構）。
- 不改 Type config / 規則判定（命中、可信度、分類條件維持）。
- 不改 sheet 名稱與順序（§4 內標 optional 者除外，且 optional 預設不執行）。
- 不改 public API（`excel_export.py` re-export 全保留；現有 helper 簽章不刪不改）。
- 不引入任何非 openpyxl 依賴（不裝 xlsxwriter/pandas styler 等）。
- 不做需要 Excel macro/VBA、巢狀真實圖表物件、或外部圖片資產的功能（data bar / color scale / 色塊條 已足夠）。
- 不改 legacy `simple_exports.py` 的黃底單表輸出（屬相容面；對齊主題色標為 future optional，本批不動）。
- 不為手機/響應式做特別處理（桌面 + 列印導向）。
```
