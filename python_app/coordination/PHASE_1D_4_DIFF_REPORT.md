# Phase 1D-4 Material / Weight Diff Report

Scope: Type 07 / 10 / 14 / 15 / 16 only. Type 62 was not remapped.

Weight diff status: none
Unexpected material diff status: none

Expected remaps:
- `UPPER_BRACKET` pipe usages -> `SUPPORT_PIPE`
- `STRUCTURAL_STRUT` support-pipe usages -> `SUPPORT_PIPE`
- `GUSSET_PLATE` support plate usages -> `SUPPORT_PLATE`
- Channel/Angle `STRUCTURAL_STRUT`, anchor bolts, nuts, and M42 helper outputs stay unchanged.

## 07-2B-20J
### default
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | EXP.BOLT | `M16` | SUS304 | SUS304 | 4.0000 | 4.0000 | no change | no material/weight change |
| 2 | Pipe | `1-1/2"*SCH.80` | A36 / SS400 | A36 / SS400 | 0.9300 | 0.9300 | no change | no material/weight change |
| 3 | Pipe | `3"*SCH.40` | A36 / SS400 | A36 / SS400 | 21.2500 | 21.2500 | no change | no material/weight change |
| 4 | Plate_E | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 6 | Plate_b_有鑽孔 | `9` | A36/SS400 | A36/SS400 | 2.2900 | 2.2900 | no change | no material/weight change |

### legacy_upper
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | EXP.BOLT | `M16` | SUS304 | SUS304 | 4.0000 | 4.0000 | no change | no material/weight change |
| 2 | Pipe | `1-1/2"*SCH.80` | LEGACY_U | LEGACY_U | 0.9300 | 0.9300 | no change | no material/weight change |
| 3 | Pipe | `3"*SCH.40` | A36 / SS400 | LEGACY_U | 21.2500 | 21.2500 | yes | expected: legacy upper_material now targets remapped SUPPORT_PIPE entries |
| 4 | Plate_E | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 6 | Plate_b_有鑽孔 | `9` | A36/SS400 | A36/SS400 | 2.2900 | 2.2900 | no change | no material/weight change |

### global
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | EXP.BOLT | `M16` | SUS304 | SUS304 | 4.0000 | 4.0000 | no change | no material/weight change |
| 2 | Pipe | `1-1/2"*SCH.80` | GLOBAL | GLOBAL | 0.9300 | 0.9300 | no change | no material/weight change |
| 3 | Pipe | `3"*SCH.40` | GLOBAL | GLOBAL | 21.2500 | 21.2500 | no change | no material/weight change |
| 4 | Plate_E | `9` | GLOBAL | GLOBAL | 2.8300 | 2.8300 | no change | no material/weight change |
| 5 | Plate_F | `9` | GLOBAL | GLOBAL | 2.8300 | 2.8300 | no change | no material/weight change |
| 6 | Plate_b_有鑽孔 | `9` | A36/SS400 | A36/SS400 | 2.2900 | 2.2900 | no change | no material/weight change |

### remap_probe
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | EXP.BOLT | `M16` | SUS304 | SUS304 | 4.0000 | 4.0000 | no change | no material/weight change |
| 2 | Pipe | `1-1/2"*SCH.80` | OLD_UPPER | NEW_PIPE | 0.9300 | 0.9300 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 3 | Pipe | `3"*SCH.40` | OLD_STRUT | NEW_PIPE | 21.2500 | 21.2500 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 4 | Plate_E | `9` | OLD_PLATE | NEW_PLATE | 2.8300 | 2.8300 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 5 | Plate_F | `9` | OLD_PLATE | NEW_PLATE | 2.8300 | 2.8300 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 6 | Plate_b_有鑽孔 | `9` | A36/SS400 | A36/SS400 | 2.2900 | 2.2900 | no change | no material/weight change |

### high_temp
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | EXP.BOLT | `M16` | SUS304 | SUS304 | 4.0000 | 4.0000 | no change | no material/weight change |
| 2 | Pipe | `1-1/2"*SCH.80` | SA-240 | SA-240 | 0.9300 | 0.9300 | no change | no material/weight change |
| 3 | Pipe | `3"*SCH.40` | A36 / SS400 | SA-240 | 21.2500 | 21.2500 | yes | expected: support pipe now uses SUPPORT_PIPE high-temp default |
| 4 | Plate_E | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 6 | Plate_b_有鑽孔 | `9` | A36/SS400 | A36/SS400 | 2.2900 | 2.2900 | no change | no material/weight change |

### pipe_isolation
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | EXP.BOLT | `M16` | SUS304 | SUS304 | 4.0000 | 4.0000 | no change | no material/weight change |
| 2 | Pipe | `1-1/2"*SCH.80` | A36 / SS400 | A36 / SS400 | 0.9300 | 0.9300 | no change | no material/weight change |
| 3 | Pipe | `3"*SCH.40` | A36 / SS400 | A36 / SS400 | 21.2500 | 21.2500 | no change | no material/weight change |
| 4 | Plate_E | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.8300 | 2.8300 | no change | no material/weight change |
| 6 | Plate_b_有鑽孔 | `9` | A36/SS400 | A36/SS400 | 2.2900 | 2.2900 | no change | no material/weight change |

## 10-2B-05A
### default
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | ADJ.BOLT | `M12*160L` | A36 / SS400 | A36 / SS400 | 3.2000 | 3.2000 | no change | no material/weight change |
| 2 | HEX NUT | `M12` | A194 2H | A194 2H | 0.6000 | 0.6000 | no change | no material/weight change |
| 3 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 0.9300 | 0.9300 | no change | no material/weight change |
| 4 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 2.1600 | 2.1600 | no change | no material/weight change |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.0400 | 2.0400 | no change | no material/weight change |
| 6 | Plate_a_無鑽孔 | `9` | A36/SS400 | A36/SS400 | 1.5900 | 1.5900 | no change | no material/weight change |

### legacy_upper
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | ADJ.BOLT | `M12*160L` | A36 / SS400 | A36 / SS400 | 3.2000 | 3.2000 | no change | no material/weight change |
| 2 | HEX NUT | `M12` | A194 2H | A194 2H | 0.6000 | 0.6000 | no change | no material/weight change |
| 3 | Pipe | `1.5"*SCH.80` | LEGACY_U | LEGACY_U | 0.9300 | 0.9300 | no change | no material/weight change |
| 4 | Pipe | `1.5"*SCH.80` | A36 / SS400 | LEGACY_U | 2.1600 | 2.1600 | yes | expected: legacy upper_material now targets remapped SUPPORT_PIPE entries |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.0400 | 2.0400 | no change | no material/weight change |
| 6 | Plate_a_無鑽孔 | `9` | A36/SS400 | A36/SS400 | 1.5900 | 1.5900 | no change | no material/weight change |

### global
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | ADJ.BOLT | `M12*160L` | GLOBAL | GLOBAL | 3.2000 | 3.2000 | no change | no material/weight change |
| 2 | HEX NUT | `M12` | GLOBAL | GLOBAL | 0.6000 | 0.6000 | no change | no material/weight change |
| 3 | Pipe | `1.5"*SCH.80` | GLOBAL | GLOBAL | 0.9300 | 0.9300 | no change | no material/weight change |
| 4 | Pipe | `1.5"*SCH.80` | GLOBAL | GLOBAL | 2.1600 | 2.1600 | no change | no material/weight change |
| 5 | Plate_F | `9` | GLOBAL | GLOBAL | 2.0400 | 2.0400 | no change | no material/weight change |
| 6 | Plate_a_無鑽孔 | `9` | A36/SS400 | A36/SS400 | 1.5900 | 1.5900 | no change | no material/weight change |

### remap_probe
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | ADJ.BOLT | `M12*160L` | ANCHOR | ANCHOR | 3.2000 | 3.2000 | no change | no material/weight change |
| 2 | HEX NUT | `M12` | NUT | NUT | 0.6000 | 0.6000 | no change | no material/weight change |
| 3 | Pipe | `1.5"*SCH.80` | OLD_UPPER | NEW_PIPE | 0.9300 | 0.9300 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 4 | Pipe | `1.5"*SCH.80` | OLD_STRUT | NEW_PIPE | 2.1600 | 2.1600 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 5 | Plate_F | `9` | OLD_PLATE | NEW_PLATE | 2.0400 | 2.0400 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 6 | Plate_a_無鑽孔 | `9` | A36/SS400 | A36/SS400 | 1.5900 | 1.5900 | no change | no material/weight change |

### high_temp
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | ADJ.BOLT | `M12*160L` | A36 / SS400 | A36 / SS400 | 3.2000 | 3.2000 | no change | no material/weight change |
| 2 | HEX NUT | `M12` | A194 4 | A194 4 | 0.6000 | 0.6000 | no change | no material/weight change |
| 3 | Pipe | `1.5"*SCH.80` | SA-240 | SA-240 | 0.9300 | 0.9300 | no change | no material/weight change |
| 4 | Pipe | `1.5"*SCH.80` | A36 / SS400 | SA-240 | 2.1600 | 2.1600 | yes | expected: support pipe now uses SUPPORT_PIPE high-temp default |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.0400 | 2.0400 | no change | no material/weight change |
| 6 | Plate_a_無鑽孔 | `9` | A36/SS400 | A36/SS400 | 1.5900 | 1.5900 | no change | no material/weight change |

### pipe_isolation
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | ADJ.BOLT | `M12*160L` | A36 / SS400 | A36 / SS400 | 3.2000 | 3.2000 | no change | no material/weight change |
| 2 | HEX NUT | `M12` | A194 2H | A194 2H | 0.6000 | 0.6000 | no change | no material/weight change |
| 3 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 0.9300 | 0.9300 | no change | no material/weight change |
| 4 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 2.1600 | 2.1600 | no change | no material/weight change |
| 5 | Plate_F | `9` | A36 / SS400 | A36 / SS400 | 2.0400 | 2.0400 | no change | no material/weight change |
| 6 | Plate_a_無鑽孔 | `9` | A36/SS400 | A36/SS400 | 1.5900 | 1.5900 | no change | no material/weight change |

## 14-2B-1005
### default
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | EXP.BOLT | `5/8"` | A36 / SS400 | A36 / SS400 | 4.0000 | 4.0000 | no change | no material/weight change |
| 3 | Pipe | `2.0"*SCH.40` | A36 / SS400 | A36 / SS400 | 2.0800 | 2.0800 | no change | no material/weight change |
| 4 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 5 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 6 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 7 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 0.6900 | 0.6900 | no change | no material/weight change |

### legacy_upper
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | EXP.BOLT | `5/8"` | LEGACY_U | LEGACY_U | 4.0000 | 4.0000 | no change | no material/weight change |
| 3 | Pipe | `2.0"*SCH.40` | LEGACY_U | LEGACY_U | 2.0800 | 2.0800 | no change | no material/weight change |
| 4 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 5 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 6 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 7 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 0.6900 | 0.6900 | no change | no material/weight change |

### global
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | GLOBAL | GLOBAL | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | EXP.BOLT | `5/8"` | GLOBAL | GLOBAL | 4.0000 | 4.0000 | no change | no material/weight change |
| 3 | Pipe | `2.0"*SCH.40` | GLOBAL | GLOBAL | 2.0800 | 2.0800 | no change | no material/weight change |
| 4 | Plate_BASE | `9` | GLOBAL | GLOBAL | 2.5500 | 2.5500 | no change | no material/weight change |
| 5 | Plate_STOPPER | `6` | GLOBAL | GLOBAL | 0.5300 | 0.5300 | no change | no material/weight change |
| 6 | Plate_TOP | `9` | GLOBAL | GLOBAL | 0.4500 | 0.4500 | no change | no material/weight change |
| 7 | Plate_WING | `9` | GLOBAL | GLOBAL | 0.6900 | 0.6900 | no change | no material/weight change |

### remap_probe
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | OLD_STRUT | OLD_STRUT | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | EXP.BOLT | `5/8"` | ANCHOR | ANCHOR | 4.0000 | 4.0000 | no change | no material/weight change |
| 3 | Pipe | `2.0"*SCH.40` | OLD_UPPER | NEW_PIPE | 2.0800 | 2.0800 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 4 | Plate_BASE | `9` | OLD_PLATE | NEW_PLATE | 2.5500 | 2.5500 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 5 | Plate_STOPPER | `6` | OLD_PLATE | NEW_PLATE | 0.5300 | 0.5300 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 6 | Plate_TOP | `9` | OLD_PLATE | NEW_PLATE | 0.4500 | 0.4500 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 7 | Plate_WING | `9` | OLD_PLATE | NEW_PLATE | 0.6900 | 0.6900 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |

### high_temp
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | EXP.BOLT | `5/8"` | A36 / SS400 | A36 / SS400 | 4.0000 | 4.0000 | no change | no material/weight change |
| 3 | Pipe | `2.0"*SCH.40` | SA-240 | SA-240 | 2.0800 | 2.0800 | no change | no material/weight change |
| 4 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 5 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 6 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 7 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 0.6900 | 0.6900 | no change | no material/weight change |

### pipe_isolation
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | EXP.BOLT | `5/8"` | A36 / SS400 | A36 / SS400 | 4.0000 | 4.0000 | no change | no material/weight change |
| 3 | Pipe | `2.0"*SCH.40` | A36 / SS400 | A36 / SS400 | 2.0800 | 2.0800 | no change | no material/weight change |
| 4 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 5 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 6 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 7 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 0.6900 | 0.6900 | no change | no material/weight change |

## 15-2B-1005
### default
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | Pipe | `2.0"*SCH.40` | A36 / SS400 | A36 / SS400 | 2.0800 | 2.0800 | no change | no material/weight change |
| 3 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 4 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 5 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 6 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 1.0100 | 1.0100 | no change | no material/weight change |

### legacy_upper
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | Pipe | `2.0"*SCH.40` | LEGACY_U | LEGACY_U | 2.0800 | 2.0800 | no change | no material/weight change |
| 3 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 4 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 5 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 6 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 1.0100 | 1.0100 | no change | no material/weight change |

### global
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | GLOBAL | GLOBAL | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | Pipe | `2.0"*SCH.40` | GLOBAL | GLOBAL | 2.0800 | 2.0800 | no change | no material/weight change |
| 3 | Plate_BASE | `9` | GLOBAL | GLOBAL | 2.5500 | 2.5500 | no change | no material/weight change |
| 4 | Plate_STOPPER | `6` | GLOBAL | GLOBAL | 0.5300 | 0.5300 | no change | no material/weight change |
| 5 | Plate_TOP | `9` | GLOBAL | GLOBAL | 0.4500 | 0.4500 | no change | no material/weight change |
| 6 | Plate_WING | `9` | GLOBAL | GLOBAL | 1.0100 | 1.0100 | no change | no material/weight change |

### remap_probe
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | OLD_STRUT | OLD_STRUT | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | Pipe | `2.0"*SCH.40` | OLD_UPPER | NEW_PIPE | 2.0800 | 2.0800 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 3 | Plate_BASE | `9` | OLD_PLATE | NEW_PLATE | 2.5500 | 2.5500 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 4 | Plate_STOPPER | `6` | OLD_PLATE | NEW_PLATE | 0.5300 | 0.5300 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 5 | Plate_TOP | `9` | OLD_PLATE | NEW_PLATE | 0.4500 | 0.4500 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |
| 6 | Plate_WING | `9` | OLD_PLATE | NEW_PLATE | 1.0100 | 1.0100 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |

### high_temp
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | Pipe | `2.0"*SCH.40` | SA-240 | SA-240 | 2.0800 | 2.0800 | no change | no material/weight change |
| 3 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 4 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 5 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 6 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 1.0100 | 1.0100 | no change | no material/weight change |

### pipe_isolation
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Channel | `100*50*5` | A36 / SS400 | A36 / SS400 | 9.3600 | 9.3600 | no change | no material/weight change |
| 2 | Pipe | `2.0"*SCH.40` | A36 / SS400 | A36 / SS400 | 2.0800 | 2.0800 | no change | no material/weight change |
| 3 | Plate_BASE | `9` | A36 / SS400 | A36 / SS400 | 2.5500 | 2.5500 | no change | no material/weight change |
| 4 | Plate_STOPPER | `6` | A36 / SS400 | A36 / SS400 | 0.5300 | 0.5300 | no change | no material/weight change |
| 5 | Plate_TOP | `9` | A36 / SS400 | A36 / SS400 | 0.4500 | 0.4500 | no change | no material/weight change |
| 6 | Plate_WING | `9` | A36 / SS400 | A36 / SS400 | 1.0100 | 1.0100 | no change | no material/weight change |

## 16-2B-05
### default
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 1.1100 | 1.1100 | no change | no material/weight change |
| 2 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 3.6200 | 3.6200 | no change | no material/weight change |
| 3 | Plate | `6` | A36 / SS400 | A36 / SS400 | 0.2300 | 0.2300 | no change | no material/weight change |

### legacy_upper
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Pipe | `1.5"*SCH.80` | LEGACY_U | LEGACY_U | 1.1100 | 1.1100 | no change | no material/weight change |
| 2 | Pipe | `1.5"*SCH.80` | A36 / SS400 | LEGACY_U | 3.6200 | 3.6200 | yes | expected: legacy upper_material now targets remapped SUPPORT_PIPE entries |
| 3 | Plate | `6` | A36 / SS400 | A36 / SS400 | 0.2300 | 0.2300 | no change | no material/weight change |

### global
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Pipe | `1.5"*SCH.80` | GLOBAL | GLOBAL | 1.1100 | 1.1100 | no change | no material/weight change |
| 2 | Pipe | `1.5"*SCH.80` | GLOBAL | GLOBAL | 3.6200 | 3.6200 | no change | no material/weight change |
| 3 | Plate | `6` | GLOBAL | GLOBAL | 0.2300 | 0.2300 | no change | no material/weight change |

### remap_probe
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Pipe | `1.5"*SCH.80` | OLD_UPPER | NEW_PIPE | 1.1100 | 1.1100 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 2 | Pipe | `1.5"*SCH.80` | OLD_STRUT | NEW_PIPE | 3.6200 | 3.6200 | yes | expected: pipe entry remapped to HardwareKind.SUPPORT_PIPE |
| 3 | Plate | `6` | OLD_PLATE | NEW_PLATE | 0.2300 | 0.2300 | yes | expected: plate entry remapped to HardwareKind.SUPPORT_PLATE |

### high_temp
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Pipe | `1.5"*SCH.80` | SA-240 | SA-240 | 1.1100 | 1.1100 | no change | no material/weight change |
| 2 | Pipe | `1.5"*SCH.80` | A36 / SS400 | SA-240 | 3.6200 | 3.6200 | yes | expected: support pipe now uses SUPPORT_PIPE high-temp default |
| 3 | Plate | `6` | A36 / SS400 | A36 / SS400 | 0.2300 | 0.2300 | no change | no material/weight change |

### pipe_isolation
| line | name | spec | before_material | after_material | before_weight | after_weight | expected_change | reason |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 1.1100 | 1.1100 | no change | no material/weight change |
| 2 | Pipe | `1.5"*SCH.80` | A36 / SS400 | A36 / SS400 | 3.6200 | 3.6200 | no change | no material/weight change |
| 3 | Plate | `6` | A36 / SS400 | A36 / SS400 | 0.2300 | 0.2300 | no change | no material/weight change |

