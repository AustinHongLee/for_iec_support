# for_iec_support 優化前導報告

> 產生日期：2026-06-15 ｜ 性質：盤點與提案（非實作）｜ 權威性：本檔為人類/AI context，**不得**當計算真值（依 AGENTS.md）
> 所有「驗證結果」皆為本輪實際執行，環境為 Linux 沙箱（Python 3.10.12、openpyxl 3.1.5）。與使用者 Windows 機器的差異已逐項標註。

---

## 1. 現況摘要

### Branch 狀態
- 分支 `main`，`## main...origin/main`，**未顯示 ahead/behind**（與 origin 同步，無本地未推送 commit）。

### 工作樹狀態（關鍵發現：83% 的「變更」是假的）
`git status` 顯示約 48 個檔案被改，但用 `git diff -w`（忽略空白/換行）重新檢查後：

| 類別 | 檔案 | 是否真實變更 |
|---|---|---|
| **真實變更（8）** | `AGENTS.md`(+2)、`pytest.ini`(+1)、`export/excel/headers.py`、`export/excel/simple_exports.py`、`export/excel/weight_sheets.py`、`export/excel/calculation_sheets.py`、`validate_tables.py` | 是（Excel 欄序收斂 + 驗證同步） |
| **二進位** | `python_app/analysis_result.xlsx` | 是（產出物，內容變動） |
| **純 CRLF 換行雜訊（約 40）** | `core/trunnion_engine.py`、`core/types/type_43.py`、`export/excel_export_legacy.py`、全部 `data/_pre_json_backup/type*_table.py` | **否**：`git diff -w` 為 0，內容完全相同，只有行尾 CRLF↔LF 差異 |
| **未追蹤（untracked）** | `IEC_管架支撐分析工具_專案介紹.pptx`(1.5M)、`python_app/docs/analysis_result.xlsx`(392K) | 新增 artifact，待分類 |

> **重點**：`core/types/type_43.py` 與 `trunnion_engine.py` 看起來被改，實際上**計算邏輯零變動**，只是換行符。請勿因為它們「亮黃燈」就以為核心被動過。根因：repo **沒有 `.gitattributes`**、`core.autocrlf` 未設定。

### 測試 / 驗證結果（本輪實跑）

| 指令 | 結果 | 說明 |
|---|---|---|
| `python -m compileall -q python_app` | **exit 0** | 全數可編譯（首次 exit 1 為沙箱寫入 .pyc 的暫時性問題，重跑即 0） |
| `python python_app/validate_tables.py` | **exit 0 ＋ VALIDATION COMPLETE** | 所有 `v` 檢查通過、21 筆預期 soft-lock 警告。**但**夾帶 1 行 `X project aggregation wrapper ERROR: No module named 'PyQt6'` |
| `python -m pytest -q` | **39 passed, 1 failed**（沙箱）｜ 使用者機器應為 **40 passed** | 唯一失敗是 `test_validate_tables.py::test_validate_tables_script_passes` |

**那 1 個失敗不是計算 bug，是環境問題，已追到根因：**
- `validate_tables.py:149` 直接 `from ui.main_window import MainWindow`（為了測 xlsx 匯入解析）。
- 此 import 透過 `ui/` 連帶需要 **PyQt6**。我的 Linux 沙箱沒裝 PyQt6（GUI 套件），所以該檢查印出 `X ...`，連帶讓 grep `^X` 的那個 pytest 失敗。
- 使用者 Windows 機器**有** PyQt6（這是 GUI app），所以該檢查會通過 → 即先前宣稱的 **40 passed**。我本輪嘗試在沙箱安裝 PyQt6 但套件過大逾時，故誠實回報 39/40 + 根因；請在 Windows 端用下方指令自行確認 40/40。

**沙箱專屬假警報（與程式邏輯無關，使用者端不會發生）：**
- 直接 `pytest` 會出 `PermissionError: .../tests/.tmp_pytest`。原因：`.tmp_pytest`/`tmp_pytest` 是 Windows 端 pytest 暫存目錄，Linux 沙箱連 `stat()` 都被拒（`d?????????`）。`pytest.ini` 已加 `norecursedirs`，但 pytest 仍需先 `stat` 才能套用忽略規則，故在沙箱觸發。**使用者端權限正常，不受影響。**

### Windows 端最短可重現驗證指令（建議使用者親自跑一次）
```powershell
python -m compileall -q python_app
python python_app\validate_tables.py
python python_app\validate_tables.py | Select-String '^X'   # 應為「無輸出」；有輸出代表有隱性失敗
python -m pytest -q                                          # 預期 40 passed
```

### 目前最重要的 4 個事實
1. **基線是健康的**：計算真值未被破壞，具 PyQt6 的機器上 40/40 通過，`validate_tables` 全綠。
2. **進行中的 Excel 欄序收斂寫得很穩**：採 `_CALC_BASIS_HEADERS.index(...)` 解析欄位、明細列留空、小計列承擔 traceability、color scale 用欄名反查——而且**有 regression 覆蓋**（`validate_tables` 會驗欄位/列印區/隱藏欄並通過）。
3. **工作樹 diff 有 83% 是 CRLF 雜訊**，真正要 review 的面只有 8 檔，且範圍乾淨可控。
4. **兩個潛在韌性問題**：`validate_tables.py` 出 `X` 仍 exit 0（會遮蔽真失敗）；以及驗證層耦合 GUI（PyQt6）。這兩點正是「真實驗證」最該先補的。

---

## 2. 架構地圖

| 區塊 | 主要檔案 | 責任 | 優化風險 |
|---|---|---|---|
| **啟動入口** | `python_app/main.py`、`run_app.ps1`、`run_app.cmd` | 啟動 PyQt6 GUI、組裝視窗 | 低 |
| **UI／呈現** | `ui/main_window.py`（含 **xlsx 匯入解析**、export flow）、`ui/material_cutting_page.py`、`ui/type_manager.py`、`ui/ontology_browser.py` | 使用者操作、匯入欄位 mapping、觸發匯出 | 中（匯入解析邏輯藏在 MainWindow，已洩漏進 validate_tables） |
| **core 計算層（真值）** | `core/calculator.py`(dispatch)、`core/parser.py`、`core/models.py`、`core/project_aggregation.py`、`core/material_summary.py`、`core/types/type_XX.py`(**60 檔**)、引擎 `trunnion_engine.py`/`pipe_shoe_engine.py`/`type_spec_engine.py`、`material_identity.py`、`hardware_material.py`、`weight_policy.py`、`truth.py` | **計算真值**：解析型號→展開 BOM→尺寸/重量/材料 | **高（regression 重災區）** |
| **data／config 層（表真值）** | `configs/type_XX.json`(**38 檔**)、`data/*.py`(**118 檔**：`typeXX_table`/`mXX_table`/`nXX_table`)、`data/component_table_registry.py` | 查表數據、零件表登記 | 高 |
| **catalog（僅 UI 標籤）** | `configs/type_catalog.json` | UI/搜尋/狀態標籤 | 低（**不可當計算真值**） |
| **export／輸出** | `export/excel_export.py`(facade)、`export/excel/`(**15 模組**)、`export/excel_export_legacy.py`(**3594 行，死碼**)、`pdf_export.py`、`csv_export.py`、`summary_export.py`、`inventor_params.py` | 重量/材料/下料報表、Inventor 參數 | 中（欄位對齊，剛動過） |
| **validation／test** | `validate_tables.py`(**2866 行**：smoke+regression+golden)、`tests/`(**11 檔 / 40 cases**)、`test_material_cutting.py`(**孤兒，在 root 不被收集**) | regression 守門 | 中 |
| **legacy／reference** | `excel_export_legacy.py`、`data/_pre_json_backup/*`、`archive/**/*.md`、`*_REPORT/_HANDOFF/WORKLOG.md`、`docs/types/*.md`(70 檔) | 歷史快照、人類說明 | 低（**勿當真值**） |

**分層判讀：**
- **核心真值** = `core/`（尤其 `types/`、引擎、`parser`、`calculator`）、`configs/*.json`、`data/*.py`、`tests/` golden cases、`validate_tables` 的 golden/regression 斷言。
- **UI／呈現** = `ui/`、`export/`（Excel 版面、PDF、CSV）、`type_catalog.json`、`docs/types/*.md`。
- **legacy／reference** = `excel_export_legacy.py`、`data/_pre_json_backup/*`、`archive/**`、各種 `*_REPORT/_HANDOFF` md。
- **最易因優化造成 regression** = `export/excel/*` 欄位對齊（剛改）、`validate_tables` 欄序斷言、material canonicalization（21 警告基線）、任何 `core/types/*` 編輯。

**Workbook 產出 10 個 sheet**（`export/excel/workbook.py`）：長官-摘要 → 專案摘要 → 重量明細表 → 計算標準與假設 → 長官-支撐分類 → 查核-支撐明細 → 重量分析 → 材料合計 → 下料明細 → 下料圖示。已有分頁顏色、zoom、列印版面、長官封面。

---

## 3. 已發現問題（依嚴重度排序）

### P0（會導致錯誤結果或測試失敗）
**目前無 P0。** 計算真值完好；唯一的 pytest 失敗是 PyQt6 缺套件造成的環境假失敗（見 §1），非邏輯錯誤。

### P1（資料錯位／匯出錯誤／使用者誤判）

**P1-1　`validate_tables.py` 出 `X` 仍回傳 exit 0（會遮蔽真實 regression）**
- 位置：`validate_tables.py` 各檢查區塊的 `except Exception as e: print(f"X ... ERROR: {e}")`（例：第 364–366 行附近），未設失敗旗標、結尾未 `sys.exit(1)`。
- 影響：若有人只跑 `python validate_tables.py` 並用 exit code 判定，**真失敗會被當成功**。目前僅靠 `tests/test_validate_tables.py` grep `^X` 把關，而那支測試又綁 PyQt6（見 P1-2），headless/CI 直接掛。
- 建議解法：累積 `failures` 計數，結尾 `if failures: sys.exit(1)`；保留印 `X` 行以利定位。
- 建議驗證：暫時植入一個會失敗的 assert，確認 exit code 變 1；移除後恢復 0。

**P1-2　驗證層耦合 GUI：`validate_tables.py:149 from ui.main_window import MainWindow`**
- 位置：`validate_tables.py:149`（為測 xlsx 匯入解析，做 `MainWindow.__new__(MainWindow)` 再呼叫 reader）。
- 影響：核心/聚合的驗證被 GUI（PyQt6）綁架——headless/CI 無法在不裝整套 GUI 下驗證；「第 40 個測試」實際上是 GUI-gated。這與使用者「重視真實驗證」直接衝突。
- 建議解法：把 xlsx 匯入解析從 `MainWindow` 抽到 `core/`（或 `io/`）的純函式（不依賴 Qt），UI 與 validate 都改呼叫該函式；或將該段 import 包成可選、缺 PyQt6 時標記為 skip 而非 `X`。
- 建議驗證：在無 PyQt6 環境 `python validate_tables.py | findstr /R "^X"` 應無輸出；`pytest -q` 應在 headless 也能綠。

### P2（維護成本高／UX 不清楚）

**P2-1　CRLF 換行雜訊污染工作樹（缺 `.gitattributes`）**
- 位置：repo 根缺 `.gitattributes`；`core.autocrlf` 未設。約 40 檔（含 `core/types/type_43.py`、`trunnion_engine.py`、`excel_export_legacy.py`、全部 `_pre_json_backup/*`）顯示假 diff。
- 影響：每次 review 都要從 40 檔噪音裡撈出 8 檔真改；`core/types/*` 亮燈會嚇到人以為真值被動。
- 建議解法：新增 `.gitattributes`（`* text=auto`、`*.py text eol=lf`），用**獨立 commit**做一次正規化；勿與邏輯變更混在同一 commit。
- 建議驗證：`git add --renormalize . && git diff -w --stat` 應為空；`python -m pytest -q` 仍 40 passed。

**P2-2　`validate_tables.py` 2866 行巨石（smoke＋regression＋golden 混雜）**
- 影響：難維護、難定位、cwd 相依（`os.chdir(APP_DIR)` 在第 7 行，全檔吃相對路徑）。
- 建議解法：見 §5 Phase 3（先 snapshot 再拆，分 `tests/regression/` 多模組；保留 `validate_tables.py` 作「單檔總驗證」入口呼叫拆出的模組）。
- 建議驗證：拆分前後 `validate_tables` 輸出做 golden diff（逐行相同）。

**P2-3　`excel_export_legacy.py` 3594 行死碼**
- 位置：`export/excel_export.py` 僅在 **docstring** 提到它（`grep` 確認無實際 import），無人使用。
- 影響：吃 context、CRLF 雜訊大戶、誤導讀者以為仍在用。
- 建議解法：移到 `archive/` 或刪除（**先確認使用者是否要留作參考**，勿擅自刪）。
- 建議驗證：移除後 `python -m pytest -q` 與 `validate_tables` 不受影響。

**P2-4　`README.md` 僅 4 行、無「如何跑/驗證/匯出」**
- 影響：新人/非工程師無法上手；交接成本高。
- 建議解法：補一段精簡 Quickstart（執行 `run_app.ps1`、三條驗證指令、匯出檔落點）。勿寫成長篇，勿讓文件凌駕 code。

**P2-5　孤兒測試 `python_app/test_material_cutting.py`（在 root，不被收集）**
- 位置：`pytest.ini` 的 `testpaths = python_app/tests`，root 的 `test_material_cutting.py` 不在範圍；本輪單獨跑得到「no tests ran」（無 `test_` 函式，實為腳本）。
- 影響：看似有測試其實沒在跑，給人假的安全感。
- 建議解法：若是有效測試→移入 `tests/` 並改成 `test_` 函式；若是手動腳本→改名（去掉 `test_` 前綴）或移到 `scripts/`。

**P2-6　跨 sheet 欄序慣例不一致（本次收斂只做了 3 張）**
- 位置：`headers.py`。`PROJECT_HEADERS`、`_CALC_BASIS_HEADERS` 已改「型號優先、來源右側」；但 `LEADER_DETAIL_HEADERS`（查核-支撐明細）仍是「`Drawing line number` / `流水號.sort` / `數量` / `單位`」在左、且用英文欄名，`型號` 排在第 8。`SUMMARY_HEADERS`（材料合計）以品名/材質為主鍵（合理，材料導向）。
- 影響：主管在「重量明細表」與「查核-支撐明細」間切換時，欄位邏輯不一致；英文 `Drawing line number` 與其他中文欄並列突兀。
- 建議解法：確認「查核-支撐明細」是否刻意以來源為主（稽核用）；若否，套同一慣例並把英文欄名中文化。**屬呈現層，不碰計算真值，但要先確認意圖。**
- 建議驗證：匯出一份實樣，肉眼對齊；`validate_tables` 欄位斷言通過。

**P2-7　22 個 Type 有 core 實作但無 JSON config**
- 清單：`[3, 5, 6, 16, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 47, 49, 52, 61, 78]`（core 60 ／ config 38；JSON→core 無孤兒）。
- 影響：這些 Type 的數據/解讀散在 `data/*.py` 或 core 內，config 層不完整；未來「改 config 即可」的維運假設對它們不成立。注意其中 Type 27 等仍有 golden case，**無 config ≠ 沒測試**，但三邊（core/config/data）一致性較難稽核。
- 建議解法：列為 Phase 4 候選，逐一補 JSON 或明確標記「此 Type 不走 config 層」。

### P3（整理與美化）

**P3-1　Artifact hygiene**
- `python_app/analysis_result.xlsx`（392K，**已追蹤**且每次匯出就變）：僅被 `archive/excel_design_2026-06-02/...reference_demo.py` 參考，非測試 fixture。建議改為**不追蹤**（`.gitignore` 已忽略 `python_app/output/`，可把產出導向該資料夾，或加忽略規則）。
- `python_app/docs/analysis_result.xlsx`（392K，未追蹤）：像是 docs 用的匯出樣本，建議改有意義檔名或移入 fixtures。
- `IEC_管架支撐分析工具_專案介紹.pptx`（1.5M，未追蹤，在 repo 根）：應是交付/簡報物。建議移到 `docs/` 或 deliverables，並決定是否要追蹤 1.5M 二進位。**以上一律先建議、不擅自刪。**

**P3-2　`docs/types/*.md` 涵蓋 5 個無 `type_XX.py` 的型號**：`[53, 54, 55, 66, 67]`（屬 pipe-shoe/引擎處理的型號）。需確認 Type overview UI 不會因此誤導；屬呈現層。

**P3-3　`AGENTS.md` 結尾留了空標題**「## Imported Claude Cowork project instructions」（本次 +2 行，無內容）。補內容或移除空標題。

---

## 4. 優化候選清單

| # | 名稱 | 目標 | 涉及檔案 | 風險 | 收益 | 碰計算真值？ | 優先級 |
|---|---|---|---|---|---|---|---|
| 1 | **`.gitattributes` + CRLF 正規化** | 消除 40 檔假 diff、固定行尾 | `.gitattributes`(新)、全 repo renormalize | 低（獨立 commit） | 高（review 立刻乾淨） | 否 | **P1** |
| 2 | **validate_tables exit-code 硬化** | 出 `X` 即 `exit 1` | `validate_tables.py` | 低 | 高（真驗證守門） | 否 | **P1** |
| 3 | **xlsx 匯入解析脫離 GUI** | validate/CI 不需 PyQt6 | `ui/main_window.py`→`core/io_*`、`validate_tables.py:149` | 中 | 高（headless 可驗） | 否（純搬移，需回歸測） | P1 |
| 4 | **README Quickstart** | 跑/驗/匯出三步上手 | `README.md` | 低 | 中 | 否 | P2 |
| 5 | **artifact gitignore 收斂** | 停止追蹤產出 xlsx | `.gitignore`、`analysis_result.xlsx` | 低 | 中 | 否 | P2 |
| 6 | **Excel 跨 sheet 欄序一致化** | 主管閱讀一致；英文欄名中文化 | `headers.py`、`leader_sheets.py` | 中 | 中-高 | 否（呈現層） | P2 |
| 7 | **Manager 封面加 sheet 超連結索引** | 主管一鍵跳轉 10 張表 | `manager_cover_sheet.py` | 低 | 中 | 否 | P2 |
| 8 | **拆分 validate_tables.py** | 2866 行→多模組 + 總入口 | `validate_tables.py`、`tests/regression/*` | **中-高（需先 snapshot）** | 中 | 否（但動到 regression 結構） | P3→Phase3 |
| 9 | **孤兒測試歸位** | `test_material_cutting.py` 入 `tests/` 或改名 | 該檔、`pytest.ini` | 低 | 中 | 否 | P2 |
| 10 | **excel_export_legacy.py 歸檔** | 移除 3594 行死碼 | `export/excel_export_legacy.py` | 低（確認後） | 中 | 否 | P3 |
| 11 | **Material canonicalization（21 警告）** | 把 string material 收斂成 canonical_id | `data/*_table.py`、`core/material_identity.py`、`validate_tables.py`(基線數) | **高** | 中-高（BOM/採購一致） | **是** | Phase4 |
| 12 | **補 22 個 Type 的 JSON config** | 三邊一致、可稽核 | `configs/type_XX.json`、對應 `data/`、`core/types/` | **高** | 中 | **是** | Phase4 |
| 13 | **高風險 Type 補 golden case** | 風險高但測試少者先補 | `tests/`、`validate_tables`(golden) | 中（需 PDF/drawing） | 高（防 regression） | **是（驗證對照真值）** | Phase4 |
| 14 | **匯出前 preview/summary** | 非工程師匯出前看懂筆數/低信心項 | `ui/main_window.py` | 中 | 中 | 否 | Phase2/5 |

**A–G 對應**：A(Excel)=#6/#7/#14；B(validate 可維護性)=#2/#3/#8/#9；C(material)=#11；D(Type 完整度)=#12/#13；E(UI 體驗)=#3/#14；F(artifact hygiene)=#1/#5/#10；G(文件)=#4＋P3-3。

---

## 5. 建議 Roadmap

### Phase 1：立即收斂（1 天內、零碰計算真值）
- **任務**：候選 #1（`.gitattributes`+renormalize，**獨立 commit**）、#2（validate exit-code 硬化）、#4（README Quickstart）、#5（artifact gitignore）、#9（孤兒測試歸位）。
- **產出**：乾淨工作樹、可信的 `validate_tables` exit code、可上手的 README、不再追蹤產出 xlsx。
- **驗證指令**：
  ```powershell
  git add --renormalize . ; git diff -w --stat   # 應為空
  python python_app\validate_tables.py ; echo "exit=$LASTEXITCODE"
  python python_app\validate_tables.py | Select-String '^X'   # 無輸出
  python -m pytest -q                              # 40 passed
  ```
- **停損條件**：renormalize 後 `git diff -w` 非空、或任何測試由綠轉紅 → 立即還原該步。

### Phase 2：Excel／UX 強化
- **任務**：#6（跨 sheet 欄序一致 + 英文欄名中文化）、#7（封面 sheet 超連結索引）、#14（匯出前 preview）。
- **產出**：主管/採購/工程三種角色都讀得順的 workbook；匯出前可預覽。
- **驗證**：以固定輸入匯出實樣，肉眼對齊 + `validate_tables` 欄位/列印區斷言通過 + `pytest -q` 綠。
- **停損條件**：任何 sheet 欄位與資料錯位（header 數 ≠ 值數）、或 color scale 打錯欄 → 回退該 sheet。

### Phase 3：validation/test 拆分
- **任務**：#8。先對 `validate_tables.py` 輸出做 golden snapshot，再依主題拆成 `tests/regression/test_*`，`validate_tables.py` 收斂為呼叫各模組的「單檔總驗證」入口；順手解 cwd 相依（用 `Path(__file__)` 絕對路徑取代 `os.chdir`）。
- **產出**：可定位的測試、headless 可跑。
- **驗證**：拆分前後 `validate_tables` 輸出**逐行相同**（golden diff 為空）；`pytest -q` case 數 ≥ 原本。
- **停損條件**：golden diff 非空且無法解釋 → 暫停拆分。

### Phase 4：material canonicalization／Type 真值硬化
- **任務**：#11、#12、#13。**每一項都需先查 PDF/drawing 或既有 golden 對照**；canonicalize 後同步更新 `validate_tables` 的「21 筆警告」基線。
- **產出**：material canonical_id 收斂、22 個 Type config 補齊、高風險 Type 有 golden。
- **驗證**：對照原始圖號逐型驗算；`validate_tables` golden cases + 新 golden 全綠；BOM/重量/採購數量與圖一致。
- **停損條件**：任一型號算出與 PDF/drawing 不符 → 停手、記錄衝突、回報使用者。

### Phase 5：文件與交付整理
- **任務**：#10（legacy 歸檔）、P3-1（artifact 落點）、P3-2（docs/types 校對）、P3-3（AGENTS 空標題）。
- **產出**：乾淨 repo、清楚的 historical 標示、交付物歸位。
- **驗證**：`pytest -q` 綠；`grep -r "excel_export_legacy" --include=*.py` 僅剩 docstring/無。
- **停損條件**：刪檔前未取得使用者確認 → 不刪。

---

## 6. 下一輪實作 Prompt（聚焦 Phase 1，可直接交付）

```
任務：for_iec_support 的「Phase 1 立即收斂」。只做低風險、零碰計算真值的項目。
環境：Windows / PowerShell / Python（已裝 PyQt6、openpyxl、pytest）。
鐵則：依 AGENTS.md 權威順序；不要改 core/ 計算邏輯；不要 revert 別人的變更；
     不要把 40 個 CRLF 假變更與邏輯改動混在同一 commit；任何 .xlsx/.pptx 先別刪。

先驗證基線（必須親自跑，貼出輸出）：
  python -m compileall -q python_app
  python python_app\validate_tables.py
  python -m pytest -q          # 預期 40 passed

依序實作，每步獨立 commit：
1) 新增 .gitattributes：「* text=auto」與「*.py text eol=lf」。
   執行 `git add --renormalize .`，單獨 commit「chore: normalize line endings」。
   驗收：`git diff -w --stat` 為空；pytest 仍 40 passed。
2) 硬化 python_app\validate_tables.py：用一個 failures 計數累積所有 `X ... ERROR`，
   檔案結尾 `if failures: sys.exit(1)`。不可改變任何 `v`/`X` 既有輸出文字。
   驗收：植入一個臨時失敗 assert → exit code 為 1；移除後為 0 並印「VALIDATION COMPLETE」。
3) README.md 補精簡 Quickstart：如何啟動（run_app.ps1）、三條驗證指令、匯出檔落點。≤30 行，勿長篇。
4) .gitignore：停止追蹤 python_app\analysis_result.xlsx（或將匯出導向已被忽略的 python_app\output\）。
   不要刪除使用者未追蹤的 .pptx 與 docs\analysis_result.xlsx，只在報告說明分類。
5) 將 python_app\test_material_cutting.py 歸位：若是有效測試→移到 python_app\tests\ 並改成 test_ 函式；
   若是手動腳本→移到 scripts\（去掉 test_ 前綴）。

完成後再次貼出三條驗證指令輸出，確認 40 passed 且 `validate_tables` 無 `^X` 行。
不要進行 Phase 2 以後的任何項目。
```

---

## 7. 不建議現在做的事

1. **不要在改邏輯的同一 commit 內正規化那 40 個 CRLF 檔**——務必獨立 commit，否則真改動永遠被噪音淹沒。
2. **不要大規模重構 `validate_tables.py`（2866 行）而沒有先做 golden snapshot**——它混了 smoke/regression/golden，無對照就拆很可能靜默丟失檢查。
3. **不要在沒查 PDF/drawing 的情況下動 material canonicalization 或 Type 計算**（候選 #11/#12/#13）。這些**碰計算真值**；且 canonicalize 會改變「21 筆警告」基線，必須同步更新斷言，否則 `validate_tables` 反而轉紅。依 AGENTS：真值順序為 使用者指令 > 原圖/PDF > `core/` > `config/data` > `tests/validate_tables` > docs.md > catalog。
4. **不要清掉 `analysis_result.xlsx` / `.pptx` / `docs/analysis_result.xlsx`**——先分類、先問使用者是否保留；本報告只標示，不動手。
5. **不要把 `archive/**/*.md`、`docs/types/*.md`、各種 `*_REPORT/_HANDOFF` 當計算真值**——它們可能過時；判斷 Type 行為一律回到 `core/types/type_XX.py` 與 `configs/*.json` 與 `tests/`。
6. **不要因為 `core/types/type_43.py`、`trunnion_engine.py` 在 `git status` 亮燈就以為核心被改**——`git diff -w` 證實為 0，純換行。

---

### 本輪我據以判斷的來源（透明聲明）
- 計算真值相關判斷一律以 **`core/`、`configs/*.json`、`data/*.py`、`tests/`、`validate_tables.py`** 的實際內容與**實跑輸出**為準，未採信任何 Markdown。
- 「CRLF 為假變更」依 `git diff -w` 與 `file` 指令實證。
- 「40/40 需 PyQt6」依 `validate_tables.py:149` 的 import 鏈與 `pytest` 實跑（39/40 + 根因）佐證；我**未**在沙箱裝成 PyQt6（套件過大逾時），此點請於 Windows 端複核。
