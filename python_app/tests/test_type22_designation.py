from core.calculator import analyze_single


def _names(result):
    return [entry.name for entry in result.entries]


def test_type22_parenthesized_fig_preserves_m42_suffix():
    result = analyze_single("22-L50-12(A)X")

    assert not result.error
    assert "M42 字母" not in "\n".join(result.warnings)
    assert "H=1200mm 超過 L50 的上限 1000mm" in result.warnings

    names = _names(result)
    assert names.count("角鋼") == 2
    assert "Plate_c_有鑽孔" in names
    assert "EXP.BOLT" in names
    assert "Plate_a_無鑽孔" not in names


def test_type22_fig_c_uses_fourth_part_for_l_length():
    result = analyze_single("22-L50-05(C)L-07")

    assert not result.error
    angles = [entry for entry in result.entries if entry.name == "角鋼"]
    assert [entry.length for entry in angles] == [500, 700]


def test_type22_rejects_legacy_unparenthesized_format():
    result = analyze_single("22-L50-05AL")

    assert "第三段格式錯誤" in result.error
    assert not result.entries


def test_type22_rejects_extra_l_for_non_c_fig():
    result = analyze_single("22-L50-05(A)L-07")

    assert "只有 Fig.C 可指定第四段 L 值" in result.error
    assert not result.entries


def test_type22_rejects_fig_c_without_l():
    result = analyze_single("22-L50-05(C)L")

    assert "Fig.C 需要第四段指定 L 值" in result.error
    assert not result.entries


def test_type22_rejects_unknown_m42_letter():
    result = analyze_single("22-L50-05(A)Z")

    assert "不支援的 M42 字母 'Z'" in result.error
    assert not result.entries
