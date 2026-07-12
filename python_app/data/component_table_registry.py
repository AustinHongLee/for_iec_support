"""
M / N 系列 component table 覆蓋率清單。

用途:
1. 快速查看目前哪些 component 已經建立 Python module
2. 作為後續 PDF → data table 補表工作的入口

注意:
- `EXISTING_COMPONENT_TABLES` 表示已有可追蹤 module，不等於可精算
- `METADATA_ONLY_COMPONENT_TABLES` 表示只有 PDF/source metadata，尚未 lookup-ready
- `PARTIAL_LOOKUP_COMPONENT_TABLES` 表示已有部分欄位可查，但不可當完整 dimensional lookup
"""

EXISTING_COMPONENT_TABLES = {
    "M-1": "m1_table.py",
    "M-3": "m3_table.py",
    "M-4": "m4_table.py",
    "M-5": "m5_table.py",
    "M-6": "m6_table.py",
    "M-7": "m7_table.py",
    "M-8": "m8_table.py",
    "M-9": "m9_table.py",
    "M-10": "m10_table.py",
    "M-11": "m11_table.py",
    "M-12": "m12_table.py",
    "M-13": "m13_table.py",
    "M-21": "m21_table.py",
    "M-22": "m22_table.py",
    "M-23": "m23_table.py",
    "M-24": "m24_table.py",
    "M-25": "m25_table.py",
    "M-26": "m26_table.py",
    "M-27": "m27_table.py",
    "M-28": "m28_table.py",
    "M-29": "m29_table.py",
    "M-30": "m30_table.py",
    "M-31": "m31_table.py",
    "M-32": "m32_table.py",
    "M-33": "m33_table.py",
    "M-34": "m34_table.py",
    "M-35": "m35_table.py",
    "M-36": "m36_table.py",
    "M-37": "m37_table.py",
    "M-41": "m41_table.py",
    "M-42": "m42_table.py",
    "M-45": "m45_table.py",
    "M-47": "m47_table.py",
    "M-52": "m52_table.py",
    "M-53": "m53_table.py",
    "M-54": "m54_table.py",
    "M-55": "m55_table.py",
    "M-56": "m56_table.py",
    "M-57": "m57_table.py",
    "M-58": "m58_table.py",
    "M-59": "m59_table.py",
    "M-60": "m60_table.py",
    "N-1": "n1_table.py",
    "N-2": "n2_table.py",
    "N-3": "n3_table.py",
    "N-4": "n4_table.py",
    "N-5": "n5_table.py",
    "N-6": "n6_table.py",
    "N-7": "n7_table.py",
    "N-7A": "n7a_table.py",
    "N-8": "n8_table.py",
    "N-8A": "n8a_table.py",
    "N-9": "n9_table.py",
    "N-10": "n10_table.py",
    "N-11": "n11_table.py",
    "N-12": "n12_table.py",
    "N-12A": "n12a_table.py",
    "N-13": "n13_table.py",
    "N-14": "n14_table.py",
    "N-15": "n15_table.py",
    "N-16": "n16_table.py",
    "N-19": "n19_table.py",
    "N-20": "n20_table.py",
    "N-21": "n21_table.py",
    "N-22": "n22_table.py",
    "N-23": "n23_table.py",
    "N-24": "n24_table.py",
    "N-25": "n25_table.py",
    "N-26": "n26_table.py",
    "N-28": "n28_table.py",
    "N27-PU BLOCK": "n27_pu_block_table.py",
}

METADATA_ONLY_COMPONENT_TABLES = {
    "M-1",
    "M-3",
    "M-8",
    "M-9",
    "M-10",
    "M-11",
    "M-12",
    "M-13",
    "M-27",
    "M-29",
    "M-30",
    "M-31",
    "M-32",
    "M-33",
    "M-41",
    "M-56",
    "M-57",
    "M-58",
    "M-59",
    "M-60",
    "N-1",
    "N-2",
    "N-3",
    "N-4",
    "N-5",
    "N-6",
    "N-7",
    "N-7A",
    "N-8",
    "N-8A",
    "N-9",
    "N-10",
    "N-11",
    "N-12",
    "N-12A",
    "N-13",
    "N-14",
    "N-15",
    "N-16",
    "N-19",
    "N-20",
    "N-21",
    "N-22",
    "N-23",
    "N-24",
    "N-25",
    "N-26",
    "N-28",
    "N27-PU BLOCK",
}

PARTIAL_LOOKUP_COMPONENT_TABLES = {
    "M-5",
    "M-6",
    "M-7",
}

MISSING_COMPONENT_TABLES = []


def get_component_table_coverage() -> dict:
    """回傳 component table 覆蓋率摘要。"""
    implemented = len(EXISTING_COMPONENT_TABLES)
    missing = len(MISSING_COMPONENT_TABLES)
    total = implemented + missing
    metadata_only = len(METADATA_ONLY_COMPONENT_TABLES)
    partial_lookup = len(PARTIAL_LOOKUP_COMPONENT_TABLES)
    return {
        "implemented": implemented,
        "missing": missing,
        "total": total,
        "metadata_only": metadata_only,
        "partial_lookup": partial_lookup,
        "lookup_ready": implemented - metadata_only - partial_lookup,
        "coverage_ratio": implemented / total if total else 1.0,
    }
