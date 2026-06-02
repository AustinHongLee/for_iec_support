# Home PC Handoff - 2026-04-30

Purpose: after pushing this repo to GitHub, clone it on the home PC and continue development without losing the current context.

## Clone

```powershell
git clone https://github.com/AustinHongLee/for_iec_support.git
cd for_iec_support
git switch main
git status --short --branch
```

Expected after push:

```text
## main...origin/main
```

If Git reports `behind`, run:

```powershell
git pull --ff-only origin main
```

## Environment Setup

### Option A: Codex desktop / bundled Python

Use this if the home PC also has the Codex bundled runtime at:

```text
%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

Then run:

```powershell
.\setup_app_env.ps1
.\run_app.ps1 -CheckOnly
.\run_app.ps1
```

### Option B: Normal Windows Python

Use this if the home PC is a normal Python environment without Codex bundled Python.

```powershell
py -3 -m venv .venv_gui
.\.venv_gui\Scripts\python.exe -m pip install --upgrade pip
.\.venv_gui\Scripts\python.exe -m pip install -r python_app\requirements.txt
.\run_app.ps1 -CheckOnly
.\run_app.ps1
```

`run_app.ps1` will detect `.venv_gui\Scripts\python.exe` if PyQt6 is installed.

## Developer Verification

Quick calculator / table validation:

```powershell
.\.venv_gui\Scripts\python.exe python_app\validate_tables.py
```

Pytest:

```powershell
.\.venv_gui\Scripts\python.exe -m pip install -r python_app\requirements-dev.txt
.\.venv_gui\Scripts\python.exe -m pytest -q
```

Current verified status before handoff:

```text
python_app\validate_tables.py: passes
pytest -q: 14 passed
```

Known validation output still includes historical warning text from the material migration audit:

- `phase 1D-6 material-system lock-in ERROR: core\types\type_07.py` path lookup warning
- `phase 2L-A unmanaged material entry` warnings

Those are soft audit messages inside `validate_tables.py`; the script still reaches `=== VALIDATION COMPLETE ===`.

## Run / Export Flow

1. Start app:

   ```powershell
   .\run_app.ps1
   ```

2. Paste or load support designations.
3. Set project quantities if needed.
4. Export Excel project workbook.

The project workbook currently contains:

```text
專案摘要
長官統計
重量分析
材料合計
下料明細
下料圖示
```

`長官統計` is the urgent leader-facing sheet. It summarizes:

- `U-Bolt & Band` by `<=6"` / `>=8"` and HDG / SUS304.
- `PIPE SHOE` by `<=4"` / `5"~10"` / `12"~24"` / `>=26"` and HDG / SUS304.
- Cold support count for cold type IDs such as `01C`.
- CS HDG pipe support fabrication `<=15kg` by set count.
- CS HDG pipe support fabrication `>15kg` by kg.

Material simplification for this sheet:

- If any exported BOM material contains `304`, it is counted as SUS304.
- Otherwise it is counted as hot-dip galvanized / CS HDG.

## Current Mainline Context

Latest important commits before this handoff:

```text
271c1c9 feat: add leader procurement summary sheet
075a78c test: lock pipe shoe lops override priority
5a46e02 fix: apply type66 pipe shoe core rules
b8b48bf fix: downgrade pipe shoe verification status
599bf62 docs: summarize leader list batch verification
636ef63 docs: record manual hardening workflow
c33be5a fix: correct type08 stopper quantity
6b9c28f fix: correct type07 sliding elbow offset
```

High-value docs to read first:

- `python_app/docs/AUDIT_2026-04-29.md`
- `python_app/docs/MANUAL_HARDENING_RECORD.md`
- `python_app/docs/STEEL_M42_TYPE_VERIFICATION_MATRIX.md`
- `python_app/docs/BATCH_VERIFY_LEADER_LIST_2026-04-30.md`
- `python_app/docs/TYPE_DEFINITION_CONTRACT.md`

Useful locator:

```powershell
.\.venv_gui\Scripts\python.exe python_app\tools\find_type.py 52
.\.venv_gui\Scripts\python.exe python_app\tools\find_type.py 66
```

## Pipe Shoe Rules Locked So Far

Type 66 / D-80 is the pipe shoe core. Type 52/53/54/55 add restraint/guide/clamp parts around the core.

Important locked rules:

- Pad width uses `OD*pi/3` and emits practical-calculation warning.
- Pad length is `LOPS + E*2` for `<=8"` and `LOPS + E*2 + 25*2` for `>=10"`.
- Pad thickness uses pipe SCH10S wall.
- Member C length is `LOPS/D` for `<=8"` and `LOPS + 25*2` for `10"~14"`.
- `16"~24"` uses fabricated 12t plate logic.
- `10"~24"` adds four reinforcing flat bars.
- Explicit designation `HOPS/LOPS` overrides D-80 table/default values.

Example:

```text
52-1/2B-A          -> LOPS defaults to 150
52-1/2B-A-150-200  -> HOPS=150, LOPS=200
```

## Immediate Known Risks

1. Pipe shoe `26"~50"` / D-80B remains provisional and must stay review until hardened.
2. Type 52/53/54/55/66/67/80/85 are safer than before, but still procurement-sensitive.
3. Cold support N-series is mostly metadata-only; do not treat it as fully calculated.
4. M42 is high impact. Before editing it, read `MANUAL_HARDENING_RECORD.md` and `M42_BASE_SUPPORT_RULES.md`.
5. `support_ontology.json` and `type_catalog.json` are metadata, not calculation anchors.

## Git Practice On Home PC

Before starting work:

```powershell
git status --short --branch
git pull --ff-only origin main
```

After a focused change:

```powershell
.\.venv_gui\Scripts\python.exe python_app\validate_tables.py
.\.venv_gui\Scripts\python.exe -m pytest -q
git status --short
git add --all
git commit -m "short: focused message"
git push origin main
```

Do not commit `.venv`, `.venv_gui`, `.codex`, `.codex_tmp`, or generated `python_app/output` files; `.gitignore` already excludes them.

