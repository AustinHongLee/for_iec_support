# Core package
from .calculator import (
    analyze_single, analyze_batch, get_supported_types,
    set_analysis_setting, get_analysis_setting,
)
from .models import AnalysisResult, AnalysisEntry, HolePattern, GeometryHints
from .component_roles import ComponentRole, ROLE_AGGREGATE_TYPE, ROLE_DISPLAY_NAME, role_from_legacy_name
