# Phase 2K Unmanaged Material Audit Report

Date: 2026-04-22

Scope: `python_app/core`, `python_app/data`, `python_app/core/types`

Phase 2K is report-only. No runtime code was changed.

## Executive Summary

MaterialSpec migration is complete for the Phase 1D migrated Type set:

`07`, `10`, `14`, `15`, `16`, `62`, `64`, `65`

Deterministic runtime audit over 59 representative designations:

| Scope | Types audited | Entries audited | Entries missing `material_canonical_id` |
|---|---:|---:|---:|
| Migrated Phase 1D Types | 8 | 41 | 0 |
| Unmigrated Types | 51 | 147 | 147 |
| Total | 59 | 188 | 147 |

Conclusion:

- The Phase 1D/2J material path is working: migrated Type entries carry `material_canonical_id`.
- The remaining unmanaged material risk is concentrated in unmigrated Types and shared helper defaults.
- The largest source of unmanaged entries is the legacy `A36/SS400` string path.

## Audit Method

Static scan:

```powershell
rg -n 'material\s*=\s*["'']|\.material\s*=\s*["'']|add_custom_entry\(|add_steel_section_entry\(|add_bolt_entry\(|add_pipe_entry\(|add_plate_entry\(' python_app/core python_app/data
```

Dynamic scan:

- Ran `analyze_single(...)` on a deterministic representative designation for every implemented Type.
- Sorted/recorded by Type id.
- Counted entries where `getattr(entry, "material_canonical_id", None)` is missing.
- This audit checks representative paths, not every possible FIG/material branch.

Validation:

- `validate_tables.py` remains a pass/fail gate and is not modified by Phase 2K.

## Helper Routes Not Fully Managed

| Helper | Current behavior | Impact | Current mitigation |
|---|---|---|---|
| `core.pipe.add_pipe_entry` | Accepts `str` or `MaterialSpec`; string path emits no canonical id | Existing unmigrated callers still produce unmanaged pipe entries | Migrated Types pass `MaterialSpec` |
| `core.plate.add_plate_entry` | Accepts `str` or `MaterialSpec`; default/string path emits no canonical id | Existing unmigrated callers and M42 default plates remain unmanaged unless caller post-tags | Migrated `07`/`10` post-tag M42 entries |
| `core.steel.add_steel_section_entry` | Accepts only `str`; defaults to `A36/SS400`; emits no canonical id | Most structural Types produce unmanaged steel entries | Migrated `14`/`15`/`65` post-tag after calling helper |
| `core.bolt.add_custom_entry` | Accepts only `str`; emits no canonical id | Most bolt/custom entries remain unmanaged | Migrated `10`/`62`/`64`/`65` wrap and post-tag |
| `core.bolt.add_bolt_entry` | Hardcodes `SUS304`; emits no canonical id | M42 expansion bolts remain unmanaged outside migrated post-tag callers | Migrated `07`/`10` post-tag M42 entries |
| `core.m42.perform_action_by_letter` | Calls plate/bolt/steel helpers without `MaterialSpec` | Any Type using M42 gets unmanaged downstream entries unless caller tags after the call | Only migrated `07`/`10` post-tag after M42 |

## Direct String Material Paths

### Helper/Core

| File | Line | Path |
|---|---:|---|
| `python_app/core/bolt.py` | 26 | `entry.material = "SUS304"` in `add_bolt_entry` |
| `python_app/core/steel.py` | 16 | default `material = "A36/SS400"` in `add_steel_section_entry` |

### Migrated Types

These are intentionally bridged in Phase 2J and still produce `material_canonical_id`:

| Type | File | Route |
|---|---|---|
| 07 | `type_07.py` | M42 downstream entries are post-tagged after `perform_action_by_letter(...)` |
| 10 | `type_10.py` | ADJ.BOLT / HEX NUT set `material.name` and `material_canonical_id`; M42 downstream entries are post-tagged |
| 14 | `type_14.py` | `add_steel_section_entry(..., material=steel_material.name)` is post-tagged; anchor bolt sets canonical id |
| 15 | `type_15.py` | `add_steel_section_entry(..., material=steel_material.name)` is post-tagged |
| 62 | `type_62.py` | local `_add_custom_entry(...)` wrapper passes `.name` to legacy helper and tags canonical id |
| 64 | `type_64.py` | local `_add_custom_entry(...)` wrapper passes `.name` to legacy helper and tags canonical id |
| 65 | `type_65.py` | steel helper and local custom wrapper pass `.name` but tag canonical id |

### Unmigrated Types With Direct Literal Material

Static literal material hits were found in:

`03`, `09`, `13`, `19`, `25`, `26`, `27`, `36`, `39`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `51`, `56`, `57`, `58`, `59`, `60`, `61`

Common literal values:

- `A36/SS400`
- `SUS304`
- `A53Gr.B`
- `A307Gr.B(HDG)`
- `SS400`
- `M-47`

## Runtime Missing Canonical ID Matrix

Representative sample audit:

| Type | Designation | Scope | Entries | Missing canonical id |
|---|---|---|---:|---:|
| 01 | `01-2B-05A` | unmigrated | 3 | 3 |
| 03 | `03-1B-05N` | unmigrated | 5 | 5 |
| 05 | `05-L50-05L` | unmigrated | 4 | 4 |
| 06 | `06-L50-0510-0401` | unmigrated | 2 | 2 |
| 07 | `07-2B-20J` | migrated | 6 | 0 |
| 08 | `08-2B-1005G` | unmigrated | 6 | 6 |
| 09 | `09-2B-05B` | unmigrated | 7 | 7 |
| 10 | `10-2B-05A` | migrated | 6 | 0 |
| 11 | `11-2B-06G` | unmigrated | 8 | 8 |
| 12 | `12-6B-05B` | unmigrated | 6 | 6 |
| 13 | `13-6B-05B` | unmigrated | 8 | 8 |
| 14 | `14-2B-1005` | migrated | 7 | 0 |
| 15 | `15-2B-1005` | migrated | 6 | 0 |
| 16 | `16-2B-05` | migrated | 3 | 0 |
| 19 | `19-2B` | unmigrated | 1 | 1 |
| 20 | `20-L50-05A` | unmigrated | 1 | 1 |
| 21 | `21-L50-05A` | unmigrated | 2 | 2 |
| 22 | `22-L50-05AL` | unmigrated | 4 | 4 |
| 23 | `23-L50-05A` | unmigrated | 2 | 2 |
| 24 | `24-L50-05` | unmigrated | 1 | 1 |
| 25 | `25-L50-0505A` | unmigrated | 2 | 2 |
| 26 | `26-L50-1005A` | unmigrated | 2 | 2 |
| 27 | `27-L75-0505L-0401` | unmigrated | 3 | 3 |
| 28 | `28-L50-1005L` | unmigrated | 3 | 3 |
| 30 | `30-L75-0505A-0401` | unmigrated | 1 | 1 |
| 31 | `31-L50-1005` | unmigrated | 2 | 2 |
| 32 | `32-L50-1005` | unmigrated | 2 | 2 |
| 33 | `33-L50-1005` | unmigrated | 2 | 2 |
| 34 | `34-L50-1005` | unmigrated | 2 | 2 |
| 35 | `35-C125-05A` | unmigrated | 1 | 1 |
| 36 | `36-C125-05` | unmigrated | 3 | 3 |
| 37 | `37-C125-1200A` | unmigrated | 2 | 2 |
| 39 | `39-C100-500 A` | unmigrated | 5 | 5 |
| 41 | `41-1` | unmigrated | 3 | 3 |
| 42 | `42-8B-C125-500 A` | unmigrated | 5 | 5 |
| 43 | `43-8B-C125-500 A` | unmigrated | 7 | 7 |
| 44 | `44-8B-C125-500 A` | unmigrated | 3 | 3 |
| 45 | `45-8B-C125-500 A` | unmigrated | 5 | 5 |
| 46 | `46-8B-C125-500 A` | unmigrated | 3 | 3 |
| 47 | `47-8B-C125-500 A` | unmigrated | 5 | 5 |
| 48 | `48-2` | unmigrated | 1 | 1 |
| 49 | `49-8A` | unmigrated | 2 | 2 |
| 51 | `51-2B` | unmigrated | 1 | 1 |
| 52 | `52-2B(P)-A(A)-130-500` | unmigrated | 3 | 3 |
| 56 | `56-2B` | unmigrated | 1 | 1 |
| 57 | `57-2B-A` | unmigrated | 2 | 2 |
| 58 | `58-4B-A` | unmigrated | 2 | 2 |
| 59 | `59-6B-A` | unmigrated | 1 | 1 |
| 60 | `60-20B-A` | unmigrated | 1 | 1 |
| 61 | `61-4B-T1-05` | unmigrated | 1 | 1 |
| 62 | `62-4B-5/8-05~30D-J(T)` | migrated | 6 | 0 |
| 64 | `64-2-8-05A` | migrated | 4 | 0 |
| 65 | `65-6B-1505` | migrated | 3 | 0 |
| 72 | `72-2B` | unmigrated | 2 | 2 |
| 73 | `73-6B-G` | unmigrated | 5 | 5 |
| 76 | `76-30B` | unmigrated | 1 | 1 |
| 77 | `77-40B-(A)` | unmigrated | 1 | 1 |
| 78 | `78-2B(A)` | unmigrated | 1 | 1 |
| 79 | `79-8B(A)` | unmigrated | 1 | 1 |

## Missing Canonical ID by Material String

| Material string | Missing entry count |
|---|---:|
| `A36/SS400` | 93 |
| `SUS304` | 27 |
| `A53Gr.B` | 9 |
| `Carbon Steel` | 5 |
| `A307Gr.B(HDG)` | 4 |
| `AS` | 2 |
| `A283 Gr.C` | 1 |
| `A283-C` | 1 |
| `ASTM A229` | 1 |
| `ASTM A229 Class 1` | 1 |
| `M-47` | 1 |
| `Same as pipe / Carbon Steel` | 1 |
| `Same/similar to pipe` | 1 |

## Migration Backlog

Recommended order:

1. Central helper hardening:
   `core.steel.add_steel_section_entry`, `core.bolt.add_custom_entry`, `core.bolt.add_bolt_entry`, and `core.m42.perform_action_by_letter`.
2. M42 callers:
   Types `01`, `03`, `05`, `08`, `09`, `11`, `12`, `13`, `22`, `27`, `28`.
3. Structural steel families:
   Types `20`-`37`, `39`, `41`-`47`, `51`, `56`.
4. Recent visual/estimate Types:
   Types `72`, `73`, `76`, `77`, `78`, `79`.
5. Material catalog additions before hard lock:
   `A53Gr.B`, `A307Gr.B(HDG)`, `ASTM A229`, `ASTM A229 Class 1`, `A283-C`, `A283 Gr.C`, `A240-304`, `A387-22`, `A516-60`, `Carbon Steel`, `Same as pipe / Carbon Steel`, `Same/similar to pipe`, `M-47`.

## Phase 2K Result

Phase 2K should not fail validation. It documents unmanaged paths for later migration and lock-in phases.
