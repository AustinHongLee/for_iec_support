"""
Excel 匯出模組 — public compatibility facade.

Implementation lives in export.excel.* so individual sheet layouts can be
edited without loading the full workbook exporter into context.
The pre-split monolith is retained in excel_export_legacy.py for reference.
"""

from .excel.headers import (
    CUTTING_HEADERS,
    HEADERS,
    LEADER_DETAIL_HEADERS,
    LEADER_GROUP_DETAIL_HEADERS,
    LEADER_STAT_HEADERS,
    PROJECT_HEADERS,
    SUMMARY_HEADERS,
    VISUAL_SLOT_COUNT,
    _CALC_BASIS_HEADERS,
    _CONFIDENCE_FILL,
    _STANDARDS_TABLE,
)
from .excel.models import LeaderHitDetail, LeaderStatRow
from .excel.styles import (
    Alignment_for_subtitle,
    _add_data_bar,
    _apply_table_style,
    _apply_zebra,
    _format_number_block,
    _format_number_columns,
    _format_sheet,
    _kpi_card,
    _section_header,
    _set_widths,
    _setup_sheet,
    _styles,
    _write_headers,
)
from .excel.simple_exports import export_project_to_excel, export_to_excel
from .excel.workbook import export_project_workbook, _build_cutting_plans
from .excel.project_summary_sheet import _write_project_summary_sheet
from .excel.calculation_sheets import (
    _confidence_label,
    _weight_formula_str,
    _write_calc_reference_sheet,
    _write_calculation_basis_sheet,
)
from .excel.leader_sheets import (
    _is_304_material,
    _is_cold_support_type,
    _is_ubolt_or_band_entry,
    _leader_procurement_stats,
    _leader_size_bucket,
    _leader_stat_template,
    _parse_designation_pipe_size,
    _parse_designation_type,
    _support_has_304_material,
    _write_leader_detail_sheet,
    _write_leader_procurement_sheet,
)
from .excel.weight_sheets import _write_project_weight_sheet
from .excel.material_sheets import _write_material_summary_sheet
from .excel.cutting_sheets import _write_cutting_detail_sheet, _write_cutting_visual_sheet

__all__ = [
    "export_to_excel",
    "export_project_to_excel",
    "export_project_workbook",
]
