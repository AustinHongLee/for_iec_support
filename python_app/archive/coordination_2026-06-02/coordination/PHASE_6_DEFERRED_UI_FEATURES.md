# Phase 6 Deferred UI Features

Date: 2026-05-21

Scope: PyQt6 UI polish pass after Phase 1-5.

Decision: defer large UI/interaction features that require deeper state modeling,
background execution, or cross-page UX decisions. Do not implement these in the
current low-risk polish stream unless a real workflow pain point proves the cost.

## Completed Before This Phase

- Phase 1: visual baseline, font sizing, muted result colors, button color alignment.
- Phase 2: input safety and faster list operations.
- Phase 3: result summary bar and table readability.
- Phase 4: busy states for analyze/export and Ctrl+wheel PDF zoom.
- Phase 5: group-aware result table filtering.

## Deferred Features

| Feature | Status | Why Deferred | Start When |
|---|---|---|---|
| Full async analysis/export with progress and cancel | Deferred | Requires moving calculation/export work off the UI thread, deciding cancellation semantics, and guarding shared UI state while workers run. The current busy state is enough for normal project sizes. | Users regularly analyze/export large batches where the window freezes long enough to feel broken. |
| Undo/Redo stack | Deferred | Needs command objects for add/delete/clear, quantity edits, overrides, enable/disable state, and stale result invalidation. A partial undo model would be more dangerous than no undo. | Destructive edits become common enough that confirmation dialogs and shortcuts are not enough. |
| Side panel auto-collapse / persistent splitter state | Deferred | Auto-collapse can hide per-item overrides and PDF context. Persistent layout also needs a QSettings policy and reset path. | Screen-width complaints or repeated right-panel toggling become a real workflow issue. |
| Export UX redesign (split button/menu or separate export buttons) | Deferred | Main result export and material-cutting export should be redesigned together; changing only one page would make the workflow inconsistent. | Export format choice becomes frequent enough that the current combo + button flow slows users down. |
| SVG/QIcon replacement for emoji tab/button labels | Deferred | Requires an icon asset set, Windows rendering QA, and probably a small icon helper layer. Cosmetic gain is modest after Phase 1. | Packaging/release polish starts, or emoji rendering differs across target machines. |
| Disabled-tab explanations and tab state persistence | Deferred | Needs consistent tab availability policy across analysis, material cutting, Type overview, and ontology pages. Current status prompts are adequate. | Users repeatedly enter unavailable tabs or lose context between tabs. |
| Placeholder redesign and empty-state panels | Deferred | Low functional value compared with remaining engineering tasks. Should be bundled with a broader right-panel layout pass. | A full right-panel UX pass is scheduled. |

## Guardrails

- Keep future Phase 6 work split by behavior boundary; do not bundle undo,
  async workers, and layout persistence into one patch.
- Prefer measurable workflow pain over visual preference as the trigger.
- Any async worker phase must include GUI smoke tests for success, error, and
  cancel/reentry paths.
- Any undo phase must define which operations are intentionally not undoable.
- Any export UX phase should update both weight-analysis export and material
  cutting export together.

## Recommended Order If Resumed

1. Export UX consistency: small blast radius if both export surfaces are handled
   together.
2. Tab/empty-state polish: medium value, mostly UI-local.
3. Side panel persistence/toggle: useful but needs UX decisions.
4. Async workers with progress/cancel: high value only for large projects.
5. Undo/Redo: highest state complexity; implement only after command boundaries
   are explicit.
