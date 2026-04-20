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

---

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
