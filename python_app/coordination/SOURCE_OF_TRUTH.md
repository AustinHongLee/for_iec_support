# Source Of Truth

這份檔案定義 Codex / Claude / 人工判讀在並行協作時的引用優先順序。

## 核心原則

1. 任何列在 `coordination/IN_PROGRESS.md` 且標記為 `unstable` 的檔案，都不是可靠參考。
2. 不要把「正在施工中的檔案」當作設計真相。
3. 若 `docs` 與 `code` 不一致，要先在 `WORKLOG.md` 記錄衝突，再決定以哪一邊為準。

## 參考優先順序

### 工程圖面解釋

優先順序：

1. 原始 PDF 圖面
2. 經人工或 Codex 判讀後的 `docs/types/type_XX.md`
3. `type_catalog.json` 摘要欄位

### 已實作行為

優先順序：

1. `core/types/type_XX.py`
2. `data/*.py`
3. `docs/types/type_XX.md`
4. `type_catalog.json`

### 新 Type / 待實作 Type

優先順序：

1. 原始 PDF 圖面
2. `docs/types/type_XX.md` 中的 `Calculator Handoff`
3. `type_catalog.json`

## 協作規則

### 開始編輯前

- 先在 `IN_PROGRESS.md` 登記：
  - 誰在改
  - 任務名稱
  - 檔案列表
  - 狀態是否 `unstable`

### 完成後

- 把摘要寫進 `WORKLOG.md`
- 清除或更新 `IN_PROGRESS.md`

### 時間戳規則

- `WORKLOG.md` 區塊標題上的時間，預設代表 `logged_at`，也就是「這筆紀錄是在什麼時候寫入 log」
- 若需要精準到秒的檔案修改時間，請以檔案系統 `LastWriteTime` 為準
- 不要把手寫時間直接當成精準的 file modification time
- 若本次任務特別需要精準時間，請在 `Notes` 附上 `file -> LastWriteTime` snapshot

### 若發現衝突

- 先在 `WORKLOG.md` 留下衝突描述
- 再由人工判讀決定採信版本

### 審核入口

- 若本次任務需要第二位 AI 或人工快速審核，優先查看 `coordination/REVIEW_HANDOFF.md`
- 凡是希望 Claude 協助審核的非 trivial 變更，Codex 應同步在 `REVIEW_HANDOFF.md` 新增或更新一筆交接
- `REVIEW_HANDOFF.md` 應聚焦於：
  - 這次改了什麼
  - 哪些檔案最值得審
  - 哪些地方仍是估算 / fallback / 推論
- `WORKLOG.md` 是完成紀錄；`REVIEW_HANDOFF.md` 是 reviewer 的閱讀入口，兩者用途不要混淆

## 分層原則

### Type 層

`Type XX` 屬於支撐系統級 / 組合級。

職責：

- 解析 designation / 編碼
- 決定結構型式與 figure
- 決定要調用哪些 component
- 組裝最終 BOM
- 處理跨 component 的邏輯與限制條件

`Type` 層應該做 orchestration，不應該大量硬寫零件尺寸表。

### M / N 層

`M-*` 與 `N-*` 屬於被調用的零件級 / component library。

職責：

- 提供標準零件規格
- 提供 table lookup / designation helper
- 提供零件級尺寸、材質、推薦載重、配合尺寸

`M/N` 層不應主導整個支撐型式邏輯，也不應反向承擔 Type 的組裝判斷。

### Component Table 維護規則

核心規則：

`資料不可混放；邏輯可以共用。`

實作要求：

- 每一張原始 component PDF 應對應自己的 `data/*_table.py`
- 該 PDF 轉錄出的 raw table values 必須放在自己的 table file，例如 `M-4-PIPE CLAMP A.pdf` 的 `TYPE / LINE SIZE / LOAD / B / C / D / E / F / G / H` 應放在 `data/m4_table.py`
- 共用檔案可以存在，但只能放 normalize、builder、weight formula、validation helper 等共用邏輯
- 共用檔案不應存放跨 PDF 的 raw source values，除非該檔名稱和文件明確標示它是 shared source table
- 若多張 PDF 欄位結構相似，仍應保留各自的 raw table，再由 common helper 組裝成統一輸出格式
- 修改某張 PDF 的資料時，應能只改該 component 的 table file，不應需要改會影響其他 component 的 common file

狀態欄位建議分開看：

- `lookup_ready`: 程式是否可查表
- `source_transcribed`: 是否已依原始 PDF 逐欄轉錄
- `weight_ready`: 是否有可信重量或完整可審公式

判斷原則：

- `lookup_ready=True` 不代表已精算
- `source_transcribed=False` 時，不應宣稱是 PDF-backed table
- `weight_ready=False` 時，重量必須標示為估算或 fallback

M-4/M-5/M-6/M-7 clamp family 特別規則：

- `m_clamp_common.py` 可以保留共用 builder 與 normalize helper
- `m_clamp_common.py` 不應承擔 M-4/M-5/M-6/M-7 各 PDF 的 raw table values
- `m4_table.py`, `m5_table.py`, `m6_table.py`, `m7_table.py` 應各自保存自己的 PDF 轉錄表
- 若目前資料仍由 common file 推導，必須在 docs/status 中標示為 `lookup usable but source table not fully transcribed`

### 一句話原則

`Type = assembly / orchestration layer`

`M / N = component-level library`

### 實作上應遵守

- `type_58.py` 應調用 `m26_table.py` (U-bolt)
- `type_64.py` 應調用 `m22` (threaded rod) / `m25` (eye nut) / `m4` or `m6` (clamp)，而不是重抄尺寸
- `type_65.py` 應調用 `m23_table.py` (welded eye rod)、`m28_table.py` (angle bracket)
- `N-*` 也視為 cold-service component library，而不是支撐型式本體

> **勘誤 (Claude, 2026-04-20)**: 原版將 `m23` 列在 type_64 依賴中，實際上 M-23 (welded eye rod) 屬於 Type 65，Type 64 使用的是 M-22 (threaded rod)。

### 佔位機制 (Staging)

- 當 component table (`M-*` / `N-*`) 尚未穩定或尚未交付時，Type calculator 可使用 `add_custom_entry()` 佔位
- 佔位不視為違反分層原則，而是合理的 staging 策略
- 待對應 component table 標記為 stable 後，再重構為正式 table lookup 調用

### 發生混用時的處理

- 若某個 `Type` 檔案內出現大量 M/N 尺寸硬編碼（非佔位），優先考慮抽回對應的 component table
- 若某個 `M/N` 檔案開始承擔 figure / family / structural decision，優先把判斷移回 `Type` 層

## 建議分工

- Codex:
  - PDF interpretation
  - handoff 文件
  - M/N component table 建立與維護
  - 第二輪技術審查
  - 結構收斂
- Claude:
  - Type-level data table 建立
  - Type calculator 實作
  - 批次化 code production
  - Component table 整合（待 Codex 交付 stable 後）
- Human:
  - 最終工程判讀
  - 異議裁決
  - 規則定稿
