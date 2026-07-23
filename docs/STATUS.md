# Repository Status

> This file is the short, current entry point for humans and AI agents. Update it after every decision or completed implementation wave. Calculation truth still follows `AGENTS.md`; this file is status context only.

## As of

- Pre-checkpoint baseline commit: `dc68dcd` (`docs: record green Linux validation`)
- Active plan: `施工單_G1-G4_功能延伸與主介面重整_2026-07-12.md`
- Local validation after the repository hygiene sweep: 233 passed; `VALIDATION COMPLETE`; 0 lines beginning with `X`; GUI launch check passed
- Last pre-wave GitHub Actions run: `29213757536` passed
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
- G4e screenshot diagnosis wave 1: separated correction/result/logic tabs, debounced automatic reanalysis after overrides, readable two-line input rows, compact list actions, and Excel-like independent result filters
- G4e screenshot diagnosis wave 2: designation-first input rows, explicit paste/import actions, guided Support MTO/CSV import, blank Excel template, and pre-import completeness/traceability warnings
- G4e real-project verification: 704/704 rows imported with 0 missing/defaulted fields and 0 analysis errors; GUI measured 0.524 s first analysis/render, 0.061 s column filter, and 0.611 s override auto-reanalysis
- Post-G4 data-maintenance UX correction: searchable Type navigation, separated editable/readonly data, localized field labels, automatic validation/diff, changed-cell highlighting, evidence-gated save readiness, unsaved-change protection, and clear numeric-input errors
- Multi-model defect stabilization: global-material and saved-Type changes now invalidate stale results, disable export, and automatically reanalyze; disabled project rows no longer misalign SidePanel results or full-detail status groups
- Global upper-material confirmation semantics: new projects start unconfirmed and temporarily use SUS304 as an estimate; completion counts only Types 01/01T/09/11, explicit global selection clears inherited assumptions, and Type 09/11 now emit matching assumption evidence
- Export readiness and change feedback: the export row now states whether the project is unbuilt, waiting, stale, error-bearing, estimate-ready, final-blocked, or ready; automatic reanalysis also shows the previous and current total weight with delta details in the tooltip
- Import problem-row details: Excel, CSV, and text imports retain source row numbers, original row snapshots, severity, handling outcome, and concrete repair guidance; the preview shows a copyable issue table and skips invalid quantities without aborting the remaining valid rows
- Search/filter responsibility cleanup: the left search explicitly filters only the input list; central free text is now a non-hiding result locator with previous/next navigation; Excel-like column conditions alone reduce rows, pending material is part of the status condition, and removable active-condition chips expose every applied filter
- One-step project undo: a visible toolbar action and Ctrl+Z restore the latest input, enable-state, list edit, import/clear, row override, batch material, or global-material change; projects that had been analyzed automatically recompute after restoration instead of reviving stale result objects
- Excel claim-audit wave: `PENETRATION HOLE` now exports as its `OPEN-…` display family in support-audit evidence; the existing project-scaled weight sheet remains, while `單組重量明細` is a two-column model-to-single-weight lookup without BOM expansion or project quantity scaling; the manager cover is now a claim-question entry point, and `長官-支撐分類` directly shows each contract name's rule, one current-project example, source reference, and row-level evidence link
- Excel real-project verification: the 704-row / 1,045-support MTO exported with 0 analysis errors and 5,520.702 kg total; all 11 sheets rendered for visual review, the workbook error scan found no formula errors, and the OPEN audit output contains 87 OPEN evidence rows with no exported `PENETRATION HOLE` label
- Claim drill-down correction: `查核-支撐明細` is now a client-question evidence table rather than an engineering trace dump. Each row keeps the exact contract name, contract total, drawing/serial/model source, project groups, support single weight, classification threshold, readable claim calculation, and row contribution visible together. Contract rows are contiguous, summary links show the source-row count, and the real `>15Kg` category reconciles 65 source rows back to 2,656.780 kg
- Single-weight lookup correction: `單組重量明細` no longer expands material entries. The 704-row real project collapses to 266 unique model/weight rows, exposes only `型號` and `單組重量(kg)`, and contains no conflicting weights for the same exported model label
- Linux GitHub Actions PyQt6 runtime provisioning (`libegl1`)
- Repository hygiene sweep: removed stale Qwen/Sixth/MCP/Codex-temp state, redundant local Python environment, caches, Windows metadata, duplicate archived deck output, and reproducible generated artifacts; retained the active GUI environment and relocated the two latest claim-audit workbooks under the ignored `python_app/output/` convention

## In progress / next

- No unconditional construction module remains from the active G1-G4 work order.
- Intended next architecture direction (not started): React + TypeScript frontend, Tauri desktop shell, Python data processing, and JSON/SQLite data exchange.
- Grok, DeepSeek, and Opus product reviews are complete under `docs/20260714-v1_主介面與功能體驗評議/`; synthesis and user decisions remain pending.
- No remaining unconditional candidate from the multi-model stabilization list; the next product change should come from fresh user testing or a concrete screen/workflow gap.
- Keep the improved left input list unless the user explicitly approves G4b-2 removal after normal use.
- Treat any further screenshots as targeted product feedback rather than unfinished G1-G4 construction.
- Collect the user's remaining expectation gaps as concrete screens/workflows; do not infer that this UX wave resolves unrelated product feedback.
- Have the supervisor review the new contract-rule wording against the actual upstream contract before treating the descriptions as contractual truth; the workbook now exposes the basis, but it does not replace contract confirmation.

## Deferred by decision or unmet prerequisite

- C2 variant overlay engine: deferred; requires real company data, drawing/PDF, and golden cases.
- C4 calculator-only constant externalization: deferred; requires a selected Type plus drawing/PDF golden.
- G4b-2 left-input-list removal: evaluate only after G4b-1 has been used for one real project cycle and the user approves.

## Current policy defaults

- Unconfirmed global upper material uses SUS304 only as an estimate; relevant Types remain pending until the user explicitly selects a global material or sets a row override.
- Final-mode export with unresolved assumptions uses hard block plus an explicit one-time exception with recorded reason.
- The legacy "全部明細" view remains available while the master-detail workflow is evaluated.
