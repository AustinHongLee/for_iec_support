# Repo Cleanup Report — 2026-05-07

本文件只分類，不刪檔。目標是把 runtime、工程資料、歷史紀錄、暫存物分清楚，後續再分批搬移或封存。

## 快照

| 區域 | 檔案數 | 大小 |
|---|---:|---:|
| repo 全部 | 20077 | 552.94 MB |
| `python_app/` | 1094 | 30.11 MB |
| `python_app/assets/` | 232 | 24.92 MB |
| `.venv/` | 12990 | 428.73 MB |
| `.venv_gui/` | 1929 | 24.16 MB |
| `.codex_tmp/` | 57 | 3.27 MB |
| `單張-本案有關/` | 42 | 4.67 MB |
| `Module占存區/` | 32 | 0.39 MB |
| `PipeShoe_product/` | 2 | 0.68 MB |
| `PlateDrawer/` | 4 | 0.79 MB |

## Runtime 必要

這些是目前 app 執行或測試直接需要的主體。

| 路徑 | 用途 | 處置 |
|---|---|---|
| `python_app/main.py` | PyQt app entry point | 保留 |
| `python_app/core/` | calculator / material / aggregation 核心 | 保留 |
| `python_app/ui/` | UI screens | 保留 |
| `python_app/export/` | Excel/CSV/PDF/Inventor 匯出 | 保留 |
| `python_app/data/` | runtime lookup bridge/table modules | 保留 |
| `python_app/configs/` | type catalog、type json、pipe shoe spec、drawing index | 保留 |
| `python_app/assets/Type/` | 舊版 PDF fallback | 保留，暫不覆蓋 |
| `python_app/assets/Type_icon/` | Type 總覽 icon | 保留 |
| `run_app.ps1`, `run_app.cmd` | 啟動 app | 保留 |
| `setup_app_env.ps1` | 環境 setup | 保留 |
| `python_app/requirements.txt` | app dependencies | 保留 |
| `pytest.ini`, `python_app/tests/`, `python_app/requirements-dev.txt` | 回歸測試 | 保留 |

## 工程資料來源

這些是計算可信度與人工審核的來源，不應和暫存混在一起。

| 路徑 | 用途 | 建議 |
|---|---|---|
| `python_app/configs/type_*.json` | 每個 Type 的 table/config data | 保留；新增 `data_updated_at` / `data_update_note` |
| `python_app/configs/type_catalog.json` | UI catalog metadata | 保留，但不要當計算 truth |
| `python_app/configs/pipe_shoe_spec.json` | Pipe shoe family 規則資料 | 保留 |
| `python_app/configs/drawing_index.json` | 新版 CP-129 PDF index | 新增，保留 |
| `python_app/assets/Type_cp129_2026/` | 新版 CP-129 PDF source set | 新增；手動搬入新版 PDF |
| `python_app/docs/types/` | Type / M / N 文件化說明 | 保留 |
| `python_app/docs/M42_BASE_SUPPORT_RULES.md` | M-42 人工判讀規則 | 保留 |
| `python_app/docs/MANUAL_HARDENING_RECORD.md` | 人工確認過的計算規則 | 保留 |
| `Support_Annaysis.xlsm` | 舊 VBA/Excel 來源 | 建議移入 `archive/legacy_vba/` 前先確認是否仍需對照 |

## 歷史備份 / 交接紀錄

這些不該干擾 runtime，但目前仍有追溯價值。

| 路徑 | 用途 | 建議 |
|---|---|---|
| `python_app/coordination/` | 交接、review、worklog | 可保留；之後可搬到 `docs/archive/coordination/` |
| `python_app/docs/AUDIT_2026-04-29.md` | 舊 audit snapshot | 可保留或封存 |
| `python_app/docs/HOME_PC_HANDOFF_2026-04-30.md` | 舊交接 | 可封存 |
| `python_app/docs/BATCH_VERIFY_LEADER_LIST_2026-04-30.md` | 舊批次驗證紀錄 | 可封存 |
| `python_app/TABLE_MIGRATION_REPORT.md` | JSON migration 歷史 | 可封存 |
| `python_app/PROJECT_OVERVIEW.md` | 舊架構總覽 | 可保留；內容若過期則標 archival |
| `python_app/data/_pre_json_backup/` | JSON migration 前備份 | 可封存；確認 git history 足夠後可移出 runtime tree |
| `Update_Log.txt`, `CHANGELOG.md` | 舊版變更紀錄 | 可封存或整理入 docs |

## 可封存

這些看起來像早期工具、單張資料或 side project。先不要刪，建議移入一個明確 archive。

| 路徑 | 觀察 | 建議 |
|---|---|---|
| `單張-本案有關/` | 舊 PDF/單張資料區，和 `python_app/assets/Type` 重疊風險高 | 搬到 `archive/raw_drawings_legacy/` |
| `Module占存區/` | 名稱像暫存/早期 module | 搬到 `archive/legacy_modules/` |
| `PipeShoe_product/` | Pipe shoe 早期產物，含 `.bak` | 搬到 `archive/legacy_tools/pipe_shoe_product/` |
| `PlateDrawer/` | 早期底板繪圖工具，含 `.bak` | 搬到 `archive/legacy_tools/plate_drawer/` |
| `.sixth/` | 工具/外部環境痕跡 | 若無依賴可移出 repo |

## 可忽略暫存

這些不是 source。通常應由 `.gitignore` 排除，不應進入 commit。

| 路徑/模式 | 說明 | 建議 |
|---|---|---|
| `.venv/` | local Python env，約 428.73 MB | 不 commit；需要時重建 |
| `.venv_gui/` | GUI env，約 24.16 MB | 不 commit；本機保留即可 |
| `.codex/`, `.codex_tmp/` | Codex 工作暫存/下載依賴 | 不 commit |
| `.pytest_cache/`, `python_app/.pytest_cache/` | pytest cache | 不 commit |
| `python_app/pytest-cache-files-*` | pytest temp | 不 commit |
| `__pycache__/`, `*.pyc` | Python bytecode | 不 commit |
| `python_app/output/` | 匯出結果 | 不 commit，必要成果另存 |
| `*.bak` | 舊工具備份檔 | 若有保存價值，移入 archive；否則不 commit |
| `python_app/tests/tmp_pytest/`, `python_app/tests/.tmp_pytest/` | 測試暫存且目前有權限問題 | 不 commit；可在確認後清掉 |

## 建議整理順序

1. 先建立新版 PDF 區域：`python_app/assets/Type_cp129_2026/`，並用 `drawing_index.json` 管理。
2. UI 只讀 index，不覆蓋舊 `assets/Type`。
3. 每次更新計算 data 時，在對應 `configs/type_XX.json` 寫入 `data_updated_at` 和 `data_update_note`。
4. 建立 `archive/` 後，分批搬移 root legacy folders，不直接刪除。
5. 最後再檢查 `.gitignore` 是否涵蓋所有 temp/cache/generated output。

## 新版 PDF 工作流

1. 將 CP-129 PDF 原檔名搬入：

```text
python_app/assets/Type_cp129_2026/
```

2. 重建索引：

```powershell
.\.venv_gui\Scripts\python.exe python_app\tools\build_drawing_index.py
```

3. 開 app，Type 總覽會先用新版 PDF；找不到時才 fallback 舊 `assets/Type`。
