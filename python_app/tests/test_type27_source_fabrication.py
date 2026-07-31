from core.calculator import analyze_single


def _component(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type27_source_member_tables_and_envelopes():
    assert "未表列 MEMBER H125" in analyze_single("27-H125-1010L",source_profile="cw_e25_24_hp6").error
    assert not analyze_single("27-H125-1010L",source_profile="ctci_22a_5123a").error
    overrun=analyze_single("27-L50-0605L",source_profile="ctci_20e4588")
    assert not overrun.error
    assert overrun.meta["issues"][0]["severity"]=="high"


def test_type27_host_m42_variance_requires_source_m42_definition():
    cw=analyze_single("27-L50-0305T",source_profile="cw_e25_24_hp6")
    assert not cw.error
    assert cw.meta["issues"][0]["code"]=="HOST_M42_NOT_LISTED"
    assert "不存在於此來源 M-42 圖" in analyze_single("27-L50-0505P",source_profile="ctci_22a_5123a").error


def test_type27_requires_measured_post_cut_not_h_minus_guess():
    result=analyze_single("27-L75-0505L-0401",source_profile="cw_e25_24_hp6")
    ids=[entry.geometry.component_id for entry in result.entries]
    assert "D30-MEMBER-M" not in ids
    assert "D30-TOP-PLATE" not in ids
    excluded={
        row["component_id"]
        for row in result.meta["fabrication"]["excluded_bom_components"]
    }
    assert {"D30-MEMBER-M","D30-TOP-PLATE","M42-FASTENER"}<=excluded
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type27_explicit_post_cut_is_used():
    result=analyze_single("27-L75-0505L-0401",source_profile="cw_e25_24_hp6",overrides={"member_cut_length_mm":472,"top_plate_width_mm":150})
    assert _component(result,"D30-MEMBER-M").length==472
    top=_component(result,"D30-TOP-PLATE")
    assert (top.length,top.width,top.spec)==(500,150,"6")


def test_type27_no_fake_second_member_or_three_side_plates():
    result=analyze_single("27-H150-0505L-0401",source_profile="cw_e25_24_hp6")
    ids=[entry.geometry.component_id for entry in result.entries]
    assert ids.count("D30-MEMBER-M")==0
    assert ids.count("D30-TOP-PLATE")==0
    assert not any(entry.name=="Plate_6t_Side" for entry in result.entries)


def test_type27_screenshot_case_excludes_three_unresolved_zero_rows():
    result=analyze_single("27-L50-0204X-0101",source_profile="cw_e25_24_hp6")
    ids={entry.geometry.component_id for entry in result.entries}
    assert "D30-GUSSET-PLATE" in ids
    assert "M42-PLATE-C" in ids
    assert "D30-MEMBER-M" not in ids
    assert "D30-TOP-PLATE" not in ids
    assert "M42-FASTENER" not in ids
    assert all(
        not (
            entry.unit_weight == 0
            and entry.geometry.component_id in {
                "D30-MEMBER-M","D30-TOP-PLATE","M42-FASTENER"
            }
        )
        for entry in result.entries
    )


def test_type27_ctci_gusset_only_when_h_ge_1000():
    low=analyze_single("27-L75-0808L",source_profile="ctci_22a_5123a")
    high=analyze_single("27-L75-0810L",source_profile="ctci_22a_5123a")
    assert all(entry.geometry.component_id!="D30-GUSSET-PLATE" for entry in low.entries)
    gusset=_component(high,"D30-GUSSET-PLATE")
    assert gusset.quantity==2
    assert gusset.geometry.net_area_mm2==18750


def test_type27_l1_l2_mismatch_is_high_risk():
    result=analyze_single("27-L75-0505L-0202",source_profile="cw_e25_24_hp6")
    assert not result.error
    assert result.meta["issues"][0]["code"]=="DESIGNATION_L1_L2_MISMATCH"
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type27_20e_adjustable_joint_stays_blocked():
    result=analyze_single("27-L75-0808L-0404",source_profile="ctci_20e4588")
    assert any("NOTE5" in item for item in result.meta["fabrication"]["blockers"])
