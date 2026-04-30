# M42 / M42A / M43 Base Support Rules

Purpose: capture the human-verified visual interpretation of the M-42, M-42A, and M-43 standard drawings. The source PDF has no extractable text, so keep this file updated when a user confirms drawing interpretation.

Standard source: `HP6-DSD-A4-500-001`, M-42 / M-42A / M-43 Rev.1.

Standard date / check date: 2024-07-15.

Evidence path: user-provided PDF image snapshots, interpreted by AI vision and corrected/confirmed by the user.

## Plate Definitions

| Plate | Meaning | Size source |
|---|---|---|
| `a` | Plain square base plate | `B x B x Kt` |
| `b` | Drilled square base plate | `C x C x Kt`, 4 holes, pitch `D x D`, hole dia `H`, bolt `J` |
| `c` | Drilled base plate for angle/channel/H-beam support steel | `C x C x Kt`, 4 holes, pitch `D x D`, hole dia `H`, bolt `J` |
| `d` | Larger drilled square base plate | `E x E x Kt`, 4 holes, pitch `F x F`, hole dia `H`, bolt `J` |
| `e` | Plain square intermediate/base plate | `G x G x Kt` |

The `L3` / `L4` values shown near plate `c` are support-steel positioning center distances. They are not plate cutouts.

## Type Composition

| Lower component | Components |
|---|---|
| A | plate `a` |
| B | plate `a` + plate `d` + 4 expansion bolts |
| C | plate `a` on existing steel |
| D | plate `a` + plate `e` |
| E | plate `a` + plate `d` + 4 expansion bolts + L40x40x5x150 angle x2 |
| F | plate `a` + L40x40x5x150 angle x2 |
| G | plate `b` + 4 expansion bolts |
| H | plate `a`, foundation by civil |
| J | plate `b` + 4 expansion bolts, foundation by civil |
| K | plate `a` + L40x40x5x150 angle x2, foundation by civil |
| L | plate `c` + 4 expansion bolts for angle steel or H-beam |
| M | plate `a` for angle steel |
| N | plate `a` for angle steel, foundation by civil |
| P | plate `c` + 4 expansion bolts for channel steel or angle steel, foundation by civil |
| R | plate `a` on insert plate or existing steel |
| S | plate `a` + plate `e` + L40x40x5x150 angle x2 on existing steel |
| T | plate `a`, SS304 |
| U | plate `a` + plate `d` SS304 + 4 expansion bolts |
| V | plate `a` + plate `d` SS304 + 4 expansion bolts + L40x40x5x150 angle x2 |
| W | plate `b` SS304 + 4 expansion bolts |
| X | plate `c` SS304 + 4 expansion bolts for angle steel or H-beam |
| Y | plate `a` SS304 for angle steel |

## Fallback Policy

The M-43 table does not list every pipe size. Calculator flows should continue with a warning:

| Requested size | Fallback row |
|---|---|
| 0.5", 0.75" | 1" row |
| 20", 22" | 24" row |
| 26" | 28" row |

Fractional values inside drawing ranges, such as 1.5" and 2.5", use the 1"~3" row without warning.

For non-listed support steel sizes, use the next same-family listed steel row when possible and emit a warning. If no larger same-family listed row exists, use the largest same-family listed row and emit a stronger warning for manual review.

## Current Code Anchors

- `python_app/data/m42_table.py`: M-43 table and fallback resolver.
- `python_app/core/m42.py`: M-42 / M-42A letter expansion.
- `python_app/core/bolt.py`: expansion bolt helper using the same M-42 resolver.
