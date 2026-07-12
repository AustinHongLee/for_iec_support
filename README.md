# for_iec_support

IEC support dimension/BOM analysis tool.

For AI agents: read [AGENTS.md](AGENTS.md) before using Markdown files as context. Many `.md` files are historical handoffs or design drafts, not current calculation truth.

## 材質核對與委外 round-trip

重量分析頁可多選輸入項目後，以右鍵批次套用上段管材質；「核對模式」會在選定材質後自動跳至下一筆待確認項目。儲存清單 CSV 時，每筆覆寫會保留在 `overrides_json` 欄，可交由同事填寫後再匯回合併；匯回後仍須重新分析與執行基線驗證。

## Quickstart

```powershell
.\run_app.cmd
```

On the first launch, the script automatically creates `.venv_gui` and installs
the GUI requirements. It uses the Codex bundled Python when available, or a
normal Windows `py -3` / `python` installation otherwise. If the automatic
setup is interrupted, run it directly:

```powershell
.\setup_app_env.ps1
```

## Verification

Run these before claiming calculation, import/export, or workbook changes are safe:

```powershell
python -m compileall -q python_app
python python_app\validate_tables.py
python -m pytest -q
```

`validate_tables.py` must finish with `=== VALIDATION COMPLETE ===` and no `X ... ERROR` lines.

## Outputs

Use `python_app/output/` for local generated exports and demos; that folder is ignored by git. Tracked workbook or presentation files in the repo should be treated as deliberate samples or deliverables, not scratch output.
