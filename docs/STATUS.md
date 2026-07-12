# Repository Status

> This file is the short, current entry point for humans and AI agents. Update it after every decision or completed implementation wave. Calculation truth still follows `AGENTS.md`; this file is status context only.

## As of

- Baseline commit: `e2f3238` (`chore: complete line-ending normalization`)
- Active plan: `施工單_G1-G4_功能延伸與主介面重整_2026-07-12.md`
- Validation: 97 passed; `VALIDATION COMPLETE`; 0 lines beginning with `X`
- Expected warnings: 21 `phase 2L-A unmanaged material entry` warnings

## Completed — do not redo

- A1 design tokens and global stylesheet
- B3 header localization/reordering and header-index guardrails
- C1 config loader hardening and strict validation
- C3 code aliases and opt-in alias seam
- Validation exit-code hardening, GUI-independent xlsx import, and CI
- G0a line-ending rules and tracked-file normalization
- G1a variant directory/schema convention
- G1b reserved `load_config(..., variant=None)` interface
- G1c config change author tracking
- G3a Type 01 declarative `variation_axes`
- G3b unknown-material assumption evidence with unchanged BOM numbers
- G3c material-confirmation progress and pending-only filter
- G4a persistent project status header

## In progress / next

1. G0b-G0d repository hygiene completion
2. G2a-G2c safe data-maintenance page
3. G1d config-version footprint
4. G4b-1/G4c/G4d master-detail workspace and entry-point cleanup
5. G3d/G3e batch review and estimate/final export policy

## Deferred by decision or unmet prerequisite

- C2 variant overlay engine: deferred; requires real company data, drawing/PDF, and golden cases.
- C4 calculator-only constant externalization: deferred; requires a selected Type plus drawing/PDF golden.
- G4b-2 left-input-list removal: evaluate only after G4b-1 has been used for one real project cycle and the user approves.
- G4e second-round screenshot diagnosis: requires 3–5 screenshots from normal user operation.

## Current policy defaults

- Unknown material uses the visible project/global upper-material setting for estimate calculations.
- Final-mode export with unresolved assumptions uses hard block plus an explicit one-time exception with recorded reason.
- The legacy "全部明細" view remains available while the master-detail workflow is evaluated.
