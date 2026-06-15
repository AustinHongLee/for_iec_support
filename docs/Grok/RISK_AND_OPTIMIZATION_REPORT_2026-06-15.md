# for_iec_support 專案風險盤點與前瞻建議

> 產生日期：2026-06-15 ｜ 性質：盤點與提案（非實作）｜ 權威性：本檔為人類/AI context，**不得**當計算真值（依 [AGENTS.md](../../AGENTS.md)）
> 驗證環境：Windows 10、Python 3.10+、PyQt6、openpyxl、pytest。所有「驗證結果」皆為本輪實際執行。

---

## 1. 現況摘要（已驗證）

| 指標 | 結果 |
|---|---|
| `python -m compileall -q python_app` | 通過 |
| `python python_app/validate_tables.py` | 全綠，21 筆 material soft-lock 警告（基線） |
| `python -m pytest -q` | **40 passed** |
| 工作樹真實變更 | **8 檔**（Excel 欄序收斂 + 驗證同步），非 48 檔噪音 |
| 支援 Type 數 | 67（config 39、shared_spec 7、**calculator-only 21**） |
| M/N 零件表 | 71/71 有 module，但 **lookup-ready 僅 19**（27%） |

### 進行中的工作

Excel 匯出欄序收斂進行中，品質良好：採 `_CALC_BASIS_HEADERS.index(...)` 解析欄位，並在 `validate_tables.py` 有 regression 覆蓋。真實變更檔案：

- `python_app/export/excel/headers.py`
- `python_app/export/excel/calculation_sheets.py`
- `python_app/export/excel/weight_sheets.py`
- `python_app/export/excel/simple_exports.py`
- `python_app/validate_tables.py`
- `pytest.ini`
- `AGENTS.md`
- `python_app/analysis_result.xlsx`（產出物）

---

## 2. 架構地圖

| 區塊 | 主要檔案 | 責任 | 優化風險 |
|---|---|---|---|
| **啟動入口** | `python_app/main.py`、`run_app.ps1`、`run_app.cmd` | 啟動 PyQt6 GUI | 低 |
| **UI／呈現** | `ui/main_window.py`（含 xlsx 匯入解析）、`ui/material_cutting_page.py`、`ui/type_manager.py` | 使用者操作、匯入、匯出 | 中（匯入解析藏在 MainWindow，已洩漏進 validate_tables） |
| **core 計算層（真值）** | `core/calculator.py`、`core/types/type_XX.py`（60 檔）、引擎、`material_identity.py`、`truth.py` | 解析型號→展開 BOM→尺寸/重量/材料 | **高（regression 重災區）** |
| **data／config 層（表真值）** | `configs/type_XX.json`（38 檔）、`data/*.py`（118 檔）、`component_table_registry.py` | 查表數據、零件表登記 | 高 |
| **catalog（僅 UI 標籤）** | `configs/type_catalog.json` | UI/搜尋/狀態標籤 | 低（**不可當計算真值**） |
| **export／輸出** | `export/excel/`（15 模組）、`excel_export_legacy.py`（3594 行死碼） | 重量/材料/下料報表 | 中（欄位對齊，剛動過） |
| **validation／test** | `validate_tables.py`（2866 行）、`tests/`（11 檔 / 40 cases） | regression 守門 | 中 |
| **legacy／reference** | `archive/**/*.md`、`docs/types/*.md`（70 檔） | 歷史快照、人類說明 | 低（**勿當真值**） |

**分層判讀：**

- **核心真值** = `core/`、`configs/*.json`、`data/*.py`、`tests/`、`validate_tables` golden/regression。
- **UI／呈現** = `ui/`、`export/`、`type_catalog.json`、`docs/types/*.md`。
- **legacy／reference** = `excel_export_legacy.py`、`archive/**`、各種 `*_REPORT/_HANDOFF` md。

---

## 3. 風險矩陣（依嚴重度排序）

### P0 — 會直接產生錯誤結果

**目前無 P0。** 計算真值未被破壞，40/40 測試通過。

---

### P1 — 工程可信度／驗證盲點

#### P1-1　資料完整度缺口（最大業務風險）

```
71 個 M/N component module
├── lookup-ready:     19 (27%)  ← 可精算
├── partial-lookup:    3 ( 4%)  ← M-5/6/7，尺寸不全
└── metadata-only:    49 (69%)  ← 只有入口，不能精算
```

- **N 系列 29 個全部 metadata-only** → 冷管支撐目前無法精算，只能估算或 fallback。
- **21 個 Type 為 calculator-only**（03, 05, 06, 16, 24–28, 30–37, 47, 49, 61, 78）→ 標準尺寸散在 Python 內，難以稽核、難以「改 config 即可」維運。
- **21 筆 material canonicalization 警告** → 材質字串（如 `A36/SS400`、`Carbon Steel`）未收斂到 `canonical_id`，BOM/採購合併可能不一致。

這三項不會讓測試失敗，但會讓**特定 Type 的輸出落在「估算」區間**，使用者若當精算用就有風險。

**建議驗證：** 對照 `python_app/tools/audit_table_json_coverage.py` 輸出與 `validate_tables.py` 的 21 筆 WARN 基線。

#### P1-2　驗證層韌性不足

- 位置：`validate_tables.py:149` — `from ui.main_window import MainWindow`（為測 xlsx 匯入解析）。
- `validate_tables.py` 有 **47 處** `X ... ERROR` 輸出，但結尾固定印 `VALIDATION COMPLETE` 且 **exit code 永遠為 0**。
- 目前只靠 `tests/test_validate_tables.py` grep `^X` 把關，且該測試同樣需要 PyQt6。

**影響：**

1. headless / CI 無法獨立驗證 xlsx 匯入。
2. 只看 exit code 會被誤導為成功。

**建議解法：**

1. 累積 `failures` 計數，結尾 `if failures: sys.exit(1)`。
2. 把 xlsx 匯入解析從 `MainWindow` 抽到 `core/`（或 `io/`）純函式。

#### P1-3　Golden case 覆蓋偏窄

- `pytest` 40 cases，集中在少數 Type（51, 56, 59, 60, 22, pipe-shoe 等）。
- `validate_tables` 內約 21 個 golden case（27, 39, 42, 43, 56 等）。
- **67 個支援 Type 中，多數沒有 golden 對照** → 重構或改表時 regression 偵測力弱。

---

### P2 — 維護成本／團隊效率

| 編號 | 問題 | 影響 |
|---|---|---|
| P2-1 | 無 `.gitattributes` | CRLF/LF 假 diff，review 噪音 |
| P2-2 | `validate_tables.py` 2866 行巨石 | smoke + regression + golden + Excel 斷言混雜 |
| P2-3 | `excel_export_legacy.py` 3594 行死碼 | 無 import，佔 context、誤導讀者 |
| P2-4 | `test_material_cutting.py` 在 root | 命名像測試，實為手動腳本，pytest 不收集 |
| P2-5 | `README.md` 僅 4 行 | 新人無法快速上手 |
| P2-6 | 無 CI（`.github/` 不存在） | 依賴本機手動跑驗證 |
| P2-7 | Excel 跨 sheet 欄序不一致 | `PROJECT_HEADERS` / `_CALC_BASIS_HEADERS` 已「型號優先」；`LEADER_DETAIL_HEADERS` 仍英文欄名在前 |

#### 文件權威性風險

依 [AGENTS.md](../../AGENTS.md) 與 [python_app/docs/README.md](../../python_app/docs/README.md)：

| 文件 | 狀態 |
|---|---|
| `python_app/docs/types/*.md`（70 檔） | UI 說明，可能過時，**不可當計算真值** |
| `STEEL_PLATE_NAMING_PLAN.md`（1300+ 行） | 設計草案，**尚未實作** |
| `readiness_schema.md` | 欄位級 readiness 定義，**尚未遷移**（仍是 table 級 status） |
| `COMPONENT_TABLE_STATUS.md` | 需對照 `component_table_registry.py` 才可信 |

---

### P3 — 整理與交付

| 編號 | 問題 | 建議 |
|---|---|---|
| P3-1 | `python_app/analysis_result.xlsx` 被 git 追蹤 | 改為不追蹤，產出導向 `python_app/output/` |
| P3-2 | 未追蹤：`IEC_管架支撐分析工具_專案介紹.pptx`、`python_app/docs/analysis_result.xlsx` | 移到 `docs/` 或 deliverables，決定是否追蹤 |
| P3-3 | `AGENTS.md` 結尾空標題 | 補內容或移除 |
| P3-4 | `docs/types/*.md` 涵蓋 5 個無 `type_XX.py` 的型號（53, 54, 55, 66, 67） | 確認 Type overview UI 不誤導（屬 pipe-shoe 引擎處理） |

---

## 4. 風險熱力圖

```
影響程度
  高 │  ● N-series 全 metadata     ● 21 calculator-only Types
     │  ● material 未 canonicalize
     │
  中 │  ● validate exit 0 遮罩     ● golden 覆蓋窄
     │  ● GUI 耦合驗證
     │
  低 │  ● CRLF 噪音    ● legacy 死碼    ● README 短
     └────────────────────────────────────────────
         低              中              高
                    發生機率／緊迫性
```

---

## 5. 優化候選清單

| # | 名稱 | 目標 | 涉及檔案 | 風險 | 收益 | 碰計算真值？ | 優先級 |
|---|---|---|---|---|---|---|---|
| 1 | **`.gitattributes` + CRLF 正規化** | 消除假 diff | `.gitattributes`(新) | 低 | 高 | 否 | **P1** |
| 2 | **validate_tables exit-code 硬化** | 出 `X` 即 `exit 1` | `validate_tables.py` | 低 | 高 | 否 | **P1** |
| 3 | **xlsx 匯入解析脫離 GUI** | validate/CI 不需 PyQt6 | `ui/main_window.py`→`core/io_*` | 中 | 高 | 否 | P1 |
| 4 | **README Quickstart** | 跑/驗/匯出三步上手 | `README.md` | 低 | 中 | 否 | P2 |
| 5 | **artifact gitignore 收斂** | 停止追蹤產出 xlsx | `.gitignore` | 低 | 中 | 否 | P2 |
| 6 | **Excel 跨 sheet 欄序一致化** | 主管閱讀一致；英文欄名中文化 | `headers.py`、`leader_sheets.py` | 中 | 中-高 | 否 | P2 |
| 7 | **Manager 封面加 sheet 超連結索引** | 主管一鍵跳轉 10 張表 | `manager_cover_sheet.py` | 低 | 中 | 否 | P2 |
| 8 | **拆分 validate_tables.py** | 2866 行→多模組 + 總入口 | `validate_tables.py`、`tests/regression/*` | 中-高 | 中 | 否 | P3 |
| 9 | **孤兒測試歸位** | `test_material_cutting.py` 入 `tests/` 或改名 | 該檔 | 低 | 中 | 否 | P2 |
| 10 | **excel_export_legacy.py 歸檔** | 移除 3594 行死碼 | `export/excel_export_legacy.py` | 低 | 中 | 否 | P3 |
| 11 | **Material canonicalization（21 警告）** | string material 收斂成 canonical_id | `data/*`、`material_identity.py` | **高** | 中-高 | **是** | Phase4 |
| 12 | **補 21 個 Type 的 JSON config** | 三邊一致、可稽核 | `configs/type_XX.json` | **高** | 中 | **是** | Phase4 |
| 13 | **高風險 Type 補 golden case** | 風險高但測試少者先補 | `tests/`、`validate_tables` | 中 | 高 | **是** | Phase4 |
| 14 | **匯出前 preview/summary** | 非工程師匯出前看懂筆數/低信心項 | `ui/main_window.py` | 中 | 中 | 否 | Phase2/5 |

---

## 6. 建議 Roadmap

### Phase 1：立即收斂（1 天內、零碰計算真值）

- **任務**：#1、#2、#4、#5、#9
- **產出**：乾淨工作樹、可信的 `validate_tables` exit code、可上手的 README、不再追蹤產出 xlsx
- **驗證指令**：

```powershell
git add --renormalize . ; git diff -w --stat   # 應為空
python python_app\validate_tables.py ; echo "exit=$LASTEXITCODE"
python python_app\validate_tables.py | Select-String '^X'   # 無輸出
python -m pytest -q                              # 40 passed
```

- **停損條件**：renormalize 後 `git diff -w` 非空、或任何測試由綠轉紅 → 立即還原該步

### Phase 2：Excel／UX 強化

- **任務**：完成進行中的欄序收斂（8 檔 commit）、#6、#7、#14
- **產出**：主管/採購/工程三種角色都讀得順的 workbook；匯出前可預覽
- **驗證**：固定輸入匯出實樣，肉眼對齊 + `validate_tables` 欄位/列印區斷言通過 + `pytest -q` 綠
- **停損條件**：任何 sheet 欄位與資料錯位 → 回退該 sheet

### Phase 3：validation/test 拆分

- **任務**：#3、#8；加 GitHub Actions headless 驗證
- **產出**：可定位的測試、headless 可跑、CI 守門
- **驗證**：拆分前後 `validate_tables` 輸出逐行相同；`pytest -q` case 數 ≥ 原本
- **停損條件**：golden diff 非空且無法解釋 → 暫停拆分

### Phase 4：material canonicalization／Type 真值硬化

- **任務**：#11、#12、#13；component 補表（見下方優先順序）
- **每一項都需先查 PDF/drawing 或既有 golden 對照**
- **產出**：material canonical_id 收斂、21 個 Type config 補齊、高風險 Type 有 golden
- **停損條件**：任一型號算出與 PDF/drawing 不符 → 停手、記錄衝突、回報使用者

**Component 補表優先順序：**

| 優先 | Component | 原因 |
|---|---|---|
| 1 | M-11 / M-12 / M-41 | Type 49 目前仍 custom estimate |
| 2 | M-3 / M-31 / M-33 | Type 62 lower figures 仍有 missing-table warning |
| 3 | M-8 / M-9 / M-10 | Type 62 lower clamp family |
| 4 | N-series first lookup batch | cold support 目前只有 metadata baseline |
| 5 | M-55 reviewer spot-check | 已 lookup-ready，但重量仍是幾何估算 |

### Phase 5：文件與交付整理

- **任務**：#10、P3-1～P3-4、前瞻架構落地（見 §7）
- **產出**：乾淨 repo、清楚的 historical 標示、交付物歸位
- **停損條件**：刪檔前未取得使用者確認 → 不刪

---

## 7. 前瞻架構

### 7.1 欄位級 Readiness Matrix

`python_app/docs/readiness_schema.md` 已定義目標 schema，但尚未遷移。目前 component status 是 table 級（lookup-ready / metadata-only），無法表達 M-5「rod/load 可查、B/C/D/E/G/H 缺失」的實際情況。

**前瞻：** UI 可顯示「M-5：rod_size ✅、load ✅、dimension B–H ❌ → 重量為估算」。

### 7.2 鋼板命名標準化

`python_app/docs/STEEL_PLATE_NAMING_PLAN.md` 定義 `{type_id}_{source_role}_{shape_spec}` 規則，尚未實作。

**建議試點：** 先選 2–3 個高頻 Type（07, 59, M42），有 golden 再擴散。

### 7.3 Type 六錨點合約強化

`python_app/docs/TYPE_DEFINITION_CONTRACT.md` 已定義六錨點。建議加：

- 「缺 regression 的 Type 清單」自動報表
- 「confidence=估算 比例」儀表板

既有工具：

```powershell
python python_app/tools/audit_table_json_coverage.py
python python_app/tools/find_type.py 51 --json
```

### 7.4 可信度分層輸出

`core/truth.py` 已有 evidence contract。前瞻可讓 Excel 匯出自動標示：

| 層級 | 意義 |
|---|---|
| 精確 | lookup-ready + golden 覆蓋 |
| 推導 | 公式計算 |
| 估算 | metadata-only fallback |
| 未知 | Type 未實作 |

這比單純印重量更能降低誤用風險。

---

## 8. 建議行動順序（本週可執行）

1. **Commit 進行中的 Excel 欄序收斂**（8 檔，已有 regression）
2. **Phase 1 五項**（`.gitattributes`、exit code、README、gitignore、孤兒腳本）
3. **選 1 個高影響 component 補表**（建議 M-11/M-12 for Type 49）
4. **為 3 個 calculator-only 高頻 Type 補 golden**（如 49, 62, 27）

---

## 9. 不建議現在做的事

1. 大規模重構 `validate_tables.py` 而無 golden snapshot
2. 未查 PDF 就動 material canonicalization 或 Type 計算
3. 把 CRLF 正規化與邏輯變更混在同一 commit
4. 把 `docs/types/*.md` 或 `archive/**/*.md` 當計算真值
5. 刪除 `analysis_result.xlsx` / `.pptx` 而未先分類確認

---

## 10. 總結評價

| 維度 | 評價 |
|---|---|
| **計算基線** | 健康（40/40，validate 全綠） |
| **資料完整度** | 主要風險（69% component 不能精算、31% Type 無 JSON） |
| **驗證韌性** | 中等風險（exit 0 遮罩、GUI 耦合、無 CI） |
| **維運結構** | 可改善（巨石腳本、死碼、文件權威分層已定義但未全面落地） |
| **前瞻方向** | 欄位級 readiness → 可信度分層輸出 → 鋼板命名標準 → config 驅動維運 |

專案已從「能算」進入「要算得可信、可稽核、可維運」的階段。下一步重點不是加功能，而是**補資料、硬化驗證、讓估算與精算在輸出上可被區分**。

---

## 11. 下一輪實作 Prompt（Phase 1，可直接交付）

```
任務：for_iec_support 的「Phase 1 立即收斂」。只做低風險、零碰計算真值的項目。
環境：Windows / PowerShell / Python（已裝 PyQt6、openpyxl、pytest）。
鐵則：依 AGENTS.md 權威順序；不要改 core/ 計算邏輯；不要把 CRLF 正規化與邏輯改動混在同一 commit。

先驗證基線（必須親自跑，貼出輸出）：
  python -m compileall -q python_app
  python python_app\validate_tables.py
  python -m pytest -q          # 預期 40 passed

依序實作，每步獨立 commit：
1) 新增 .gitattributes：「* text=auto」與「*.py text eol=lf」。
2) 硬化 validate_tables.py：failures 計數，結尾 if failures: sys.exit(1)。
3) README.md 補精簡 Quickstart（≤30 行）。
4) .gitignore：停止追蹤 python_app\analysis_result.xlsx。
5) test_material_cutting.py 歸位到 scripts/ 或 tests/。

完成後再次貼出三條驗證指令輸出。不要進行 Phase 2 以後的任何項目。
```

---

### 本輪判斷依據（透明聲明）

- 計算真值相關判斷以 `core/`、`configs/*.json`、`data/*.py`、`tests/`、`validate_tables.py` 的實際內容與**實跑輸出**為準。
- 文件判斷依 [AGENTS.md](../../AGENTS.md) 權威順序，未採信過時 Markdown。
- 與 [docs/Opus/OPTIMIZATION_PRESCAN_REPORT_2026-06-15.md](../Opus/OPTIMIZATION_PRESCAN_REPORT_2026-06-15.md) 交叉驗證，並在 Windows 端實跑確認 40/40 passed。