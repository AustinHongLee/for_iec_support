"""
M / N 系列 component table 覆蓋率清單。

用途:
1. 快速查看目前哪些 component 已經資料化成 Python table
2. 作為後續 PDF → data table 補表工作的入口
"""

EXISTING_COMPONENT_TABLES = {
    "M-22": "m22_table.py",
    "M-23": "m23_table.py",
    "M-25": "m25_table.py",
    "M-26": "m26_table.py",
    "M-28": "m28_table.py",
    "M-34": "m34_table.py",
    "M-35": "m35_table.py",
    "M-36": "m36_table.py",
    "M-37": "m37_table.py",
    "M-42": "m42_table.py",
    "M-45": "m45_table.py",
}

MISSING_COMPONENT_TABLES = [
    "M-1", "M-3", "M-4", "M-5", "M-6", "M-7", "M-8", "M-9", "M-10",
    "M-11", "M-12", "M-13", "M-21", "M-24", "M-27", "M-29", "M-30", "M-31", "M-32", "M-33",
    "M-41", "M-47", "M-52", "M-53", "M-54", "M-55", "M-56", "M-57",
    "M-58", "M-59", "M-60",
    "N-1", "N-2", "N-3", "N-4", "N-5", "N-6", "N-7", "N-7A", "N-8",
    "N-8A", "N-9", "N-10", "N-11", "N-12", "N-12A", "N-13", "N-14",
    "N-15", "N-16", "N-19", "N-20", "N-21", "N-22", "N-23", "N-24",
    "N-25", "N-26", "N-28",
]


def get_component_table_coverage() -> dict:
    """回傳 component table 覆蓋率摘要。"""
    implemented = len(EXISTING_COMPONENT_TABLES)
    missing = len(MISSING_COMPONENT_TABLES)
    total = implemented + missing
    return {
        "implemented": implemented,
        "missing": missing,
        "total": total,
        "coverage_ratio": implemented / total if total else 1.0,
    }
