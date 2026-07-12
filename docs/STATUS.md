# Repository Status

> This file is the short, current entry point for humans and AI agents. Update it after every decision or completed implementation wave. Calculation truth still follows `AGENTS.md`; this file is status context only.

## As of

- Baseline commit: `899543b` (`ci: install Qt EGL runtime on Ubuntu`)
- Active plan: `施工單_G1-G4_功能延伸與主介面重整_2026-07-12.md`
- Validation: 120 passed; `VALIDATION COMPLETE`; 0 lines beginning with `X`; GitHub Actions run `29213757536` passed
- Expected warnings: 21 `phase 2L-A unmanaged material entry` warnings

## Completed — do not redo

- A1 design tokens and global stylesheet
- B3 header localization/reordering and header-index guardrails
- C1 config loader hardening and strict validation
- C3 code aliases and opt-in alias seam
- Validation exit-code hardening, GUI-independent xlsx import, and CI
- G0a line-ending rules and tracked-file normalization
- G0b current-status entry point
- G0c regenerated changelog
- G0d VBA update log archived as UTF-8
- G1a variant directory/schema convention
- G1b reserved `load_config(..., variant=None)` interface
- G1c config change author tracking
- G1d config-version footprint in result meta, project header, and Excel reference block
- G2a safe data-maintenance page with diff preview and required drawing/revision evidence
- G2b config sanity rules and large-change confirmation
- G2c golden-validation guidance after saved data changes
- G3a Type 01 declarative `variation_axes`
- G3b unknown-material assumption evidence with unchanged BOM numbers
- G3c material-confirmation progress and pending-only filter
- G3d batch material application and keyboard review mode
- G3e estimate/final modes, export blocking, exception reason, and workbook markings
- G4a persistent project status header
- G4b-1 one-row-per-support master table with BOM detail and retained full detail view
- G4c role-based engineering/procurement/audit UI column views
- G4d safe data-maintenance entry point and final tab ordering
- Linux GitHub Actions PyQt6 runtime provisioning (`libegl1`)

## In progress / next

- No unconditional construction module remains from the active G1-G4 work order.
- Use G4b-1 for a real project cycle, then decide whether G4b-2 should retire the left input list.
- Provide 3–5 normal-operation screenshots if a G4e second-round layout diagnosis is desired.

## Deferred by decision or unmet prerequisite

- C2 variant overlay engine: deferred; requires real company data, drawing/PDF, and golden cases.
- C4 calculator-only constant externalization: deferred; requires a selected Type plus drawing/PDF golden.
- G4b-2 left-input-list removal: evaluate only after G4b-1 has been used for one real project cycle and the user approves.
- G4e second-round screenshot diagnosis: requires 3–5 screenshots from normal user operation.

## Current policy defaults

- Unknown material uses the visible project/global upper-material setting for estimate calculations.
- Final-mode export with unresolved assumptions uses hard block plus an explicit one-time exception with recorded reason.
- The legacy "全部明細" view remains available while the master-detail workflow is evaluated.
