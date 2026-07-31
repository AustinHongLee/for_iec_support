"""Project-level calculation source profiles.

The same numeric Type designation is reused by several drawing sets.  A profile
therefore belongs to the project context and must never be inferred from the
designation alone.  Row-level exceptions may explicitly override the project
profile.
"""

from __future__ import annotations

from dataclasses import dataclass


CW_E25_24_HP6 = "cw_e25_24_hp6"
CTCI_22A_5123A = "ctci_22a_5123a"
CTCI_20E4588 = "ctci_20e4588"
EKO = "eko"
CHANGCHUN_DES_M15172 = "changchun_des_m15172"
CW_CHANGCHUN_E25_24 = "cw_e25_24_changchun_des_m15172"

DEFAULT_SOURCE_PROFILE = CW_E25_24_HP6

# Non-default numeric drawing sets are enabled Type by Type only after their
# source drawings have been inspected and the divergent rules are represented
# explicitly.  "partial" means the known sizing boundary is implemented, but
# the Type still requires drawing-by-drawing review before it can be called
# fully hardened.
SOURCE_PROFILE_TYPE_STATUS: dict[str, dict[str, str]] = {
    CTCI_22A_5123A: {
        "01": "partial",
        "01T": "partial",
        "08": "partial",
        "09": "partial",
        "11": "partial",
        "15": "partial",
        "16": "partial",
        "20": "partial",
        "21": "partial",
        "22": "partial",
        "23": "partial",
        "24": "unsupported",
        "25": "partial",
        "26": "partial",
        "27": "partial",
        "28": "partial",
        "30": "partial",
        "31": "partial",
        "32": "partial",
        "33": "partial",
        "34": "partial",
        "35": "partial",
        "37": "partial",
        "39": "partial",
        "51": "partial",
        "52": "partial",
        "53": "partial",
        "54": "partial",
        "55": "partial",
        "61": "partial",
        "66": "partial",
        "67": "partial",
        "76": "partial",
        "80": "partial",
        "83": "partial",
        "85": "partial",
        "86": "partial",
        "87": "partial",
        "102": "partial",
        "103": "partial",
        "57": "partial",
        "59": "partial",
    },
    CTCI_20E4588: {
        "01": "partial",
        "01T": "partial",
        "08": "partial",
        "09": "partial",
        "10": "partial",
        "15": "partial",
        "16": "partial",
        "20": "partial",
        "21": "partial",
        "22": "partial",
        "23": "partial",
        "24": "unsupported",
        "25": "partial",
        "26": "partial",
        "27": "partial",
        "28": "partial",
        "30": "partial",
        "31": "partial",
        "32": "partial",
        "33": "partial",
        "35": "partial",
        "37": "partial",
        "39": "partial",
        "43": "partial",
        "47": "partial",
        "52": "partial",
        "53": "partial",
        "61": "partial",
        "66": "partial",
        "80": "partial",
        "83": "partial",
        "85": "partial",
        "101": "partial",
        "103": "partial",
        "105": "partial",
        "110": "partial",
        "57": "partial",
        "59": "partial",
    },
}


@dataclass(frozen=True)
class SourceProfile:
    id: str
    label_zh: str
    design_company: str
    project: str
    drawing_standard: str
    numeric_type_family: bool


SOURCE_PROFILES = {
    CW_E25_24_HP6: SourceProfile(
        id=CW_E25_24_HP6,
        label_zh="中威｜E25-24｜HP6",
        design_company="中威工程顧問股份有限公司",
        project="E25-24",
        drawing_standard="HP6-DSD-A4-500-001",
        numeric_type_family=True,
    ),
    CTCI_22A_5123A: SourceProfile(
        id=CTCI_22A_5123A,
        label_zh="中鼎｜22A_5123A｜D7TS",
        design_company="中鼎工程股份有限公司",
        project="22A/E/P/C/K 5123A",
        drawing_standard="D7TS-701-E",
        numeric_type_family=True,
    ),
    CTCI_20E4588: SourceProfile(
        id=CTCI_20E4588,
        label_zh="中鼎｜20E4588｜STM-05.01",
        design_company="中鼎工程股份有限公司",
        project="20E4588",
        drawing_standard="STM-05.01",
        numeric_type_family=True,
    ),
    EKO: SourceProfile(
        id=EKO,
        label_zh="益高｜EKO",
        design_company="益高工程有限公司",
        project="EKO",
        drawing_standard="EKO drawing set",
        numeric_type_family=False,
    ),
    CHANGCHUN_DES_M15172: SourceProfile(
        id=CHANGCHUN_DES_M15172,
        label_zh="長春｜DES-M15172",
        design_company="長春石油化學／長春人造樹脂／大連化學工業",
        project="長春業主配管支撐基準",
        drawing_standard="DES-M15172",
        numeric_type_family=False,
    ),
    CW_CHANGCHUN_E25_24: SourceProfile(
        id=CW_CHANGCHUN_E25_24,
        label_zh="中威＋長春｜E25-24／DES-M15172",
        design_company="中威工程顧問股份有限公司＋長春業主",
        project="E25-24／長春集團苗栗廠 HP6 專案",
        drawing_standard="HP6-DSD-A4-500-001／DES-M15172",
        numeric_type_family=True,
    ),
}


def normalize_source_profile(profile_id: str | None) -> str:
    value = str(profile_id or "").strip().lower()
    if not value:
        return DEFAULT_SOURCE_PROFILE
    if value not in SOURCE_PROFILES:
        raise ValueError(
            f"未知計算來源 {profile_id!r}；可用來源: {sorted(SOURCE_PROFILES)}"
        )
    return value


def get_source_profile(profile_id: str | None) -> SourceProfile:
    return SOURCE_PROFILES[normalize_source_profile(profile_id)]


def source_profile_choices() -> list[tuple[str, str]]:
    return [
        (profile.id, profile.label_zh)
        for profile in SOURCE_PROFILES.values()
    ]


def numeric_calculation_profile(profile_id: str | None) -> str:
    """Return the actual numeric-Type drawing family for a project selection."""
    normalized = normalize_source_profile(profile_id)
    if normalized == CW_CHANGCHUN_E25_24:
        return CW_E25_24_HP6
    return normalized


def source_profile_allows(profile_id: str | None, family: str) -> bool:
    """Whether an explicit project profile may route to a company extension."""
    normalized = normalize_source_profile(profile_id)
    allowed = {
        "eko": {EKO},
        "changchun": {CHANGCHUN_DES_M15172, CW_CHANGCHUN_E25_24},
        "chungwei_special": {CW_E25_24_HP6, CW_CHANGCHUN_E25_24},
    }
    return normalized in allowed.get(str(family), set())


def numeric_type_profile_status(
    profile_id: str | None,
    type_id: str,
) -> str:
    """Return the implementation state for a numeric Type/source pairing."""
    normalized = numeric_calculation_profile(profile_id)
    if normalized == CW_E25_24_HP6:
        return "current_baseline"
    if normalized == EKO:
        return "unsupported"
    return SOURCE_PROFILE_TYPE_STATUS.get(normalized, {}).get(
        str(type_id),
        "unsupported",
    )
