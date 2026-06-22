"""B1：驗證欄位用途分級表 (column_roles) 完整涵蓋 headers.py 所有欄名。

避免日後在 headers.py 新增欄位卻漏分類，造成 B2/B3/B4 行為不一致。
"""

from export.excel import column_roles, headers

# headers.py 中所有「欄名清單」常數
_HEADER_LISTS = [
    headers.HEADERS,
    headers.PROJECT_HEADERS,
    headers.SUMMARY_HEADERS,
    headers.CUTTING_HEADERS,
    headers.LEADER_STAT_HEADERS,
    headers.LEADER_GROUP_DETAIL_HEADERS,
    headers.LEADER_DETAIL_HEADERS,
    headers._CALC_BASIS_HEADERS,
]


def _all_header_names() -> set[str]:
    names: set[str] = set()
    for lst in _HEADER_LISTS:
        names.update(lst)
    return names


def test_every_header_name_is_classified():
    """headers.py 出現的每個欄名都必須在 COLUMN_ROLE 有定義。"""
    missing = sorted(n for n in _all_header_names() if n not in column_roles.COLUMN_ROLE)
    assert missing == [], f"以下欄名未在 COLUMN_ROLE 分類：{missing}"


def test_roles_are_valid():
    """所有分類角色都必須是合法角色之一。"""
    bad = {h: meta.get("role") for h, meta in column_roles.COLUMN_ROLE.items()
           if meta.get("role") not in column_roles.VALID_ROLES}
    assert bad == {}, f"以下欄位角色不合法：{bad}"


def test_default_visible_is_bool():
    """default_visible 必須是布林值。"""
    bad = {h: meta.get("default_visible") for h, meta in column_roles.COLUMN_ROLE.items()
           if not isinstance(meta.get("default_visible"), bool)}
    assert bad == {}, f"以下欄位 default_visible 非布林：{bad}"


def test_trace_columns_default_hidden():
    """稽核追溯欄一律預設隱藏（default_visible=False）。"""
    leaked = [h for h, meta in column_roles.COLUMN_ROLE.items()
              if meta.get("role") == "trace" and meta.get("default_visible") is not False]
    assert leaked == [], f"以下追溯欄不應預設顯示：{leaked}"


def test_helpers_preserve_order_and_subset():
    """visible_columns / trace_columns 維持原順序且為輸入子集。"""
    hdrs = list(headers._CALC_BASIS_HEADERS)
    vis = column_roles.visible_columns(hdrs)
    trace = column_roles.trace_columns(hdrs)
    # 子集
    assert set(vis).issubset(set(hdrs))
    assert set(trace).issubset(set(hdrs))
    # 維持原順序
    assert vis == [h for h in hdrs if h in vis]
    assert trace == [h for h in hdrs if h in trace]
    # 可見與追溯不重疊（追溯欄預設隱藏）
    assert set(vis).isdisjoint(set(trace))
