import codecs
from pathlib import Path

from export.inventor_params import export_to_csv, extract_params, get_ilogic_snippet


def _values(params):
    return {name: value for name, value, _unit, _comment in params["params"]}


def _units(params):
    return {name: unit for name, _value, unit, _comment in params["params"]}


def test_h_beam_exports_raw_and_cut_height():
    params = extract_params("52-2B(P)-A(A)-130-500", "52")

    assert params is not None
    values = _values(params)
    units = _units(params)
    assert values["C_type"] == "200*100*5.5"
    assert units["C_type"] == "text"
    assert values["C_raw_H_mm"] == 200
    assert values["C_H_mm"] == 130
    assert values["C_B_mm"] == 100
    assert values["pad_len_mm"] == 600
    assert values["IEC_Designation"] == "52-2B(P)-A(A)-130-500"
    assert values["IEC_SupportQtyText"] == "1 組"
    assert values["IEC_MemberText"] == "H200*100*5.5 L=500 x1"
    assert values["IEC_PadText"] == "PAD 600x63x2.11t x1"
    assert values["IEC_AngleText"] == "角鋼 40*40*5 L=150 x2"
    assert values["IEC_GeometryText"] == "HOPS 130 / LOPS 500 / E 50 / A 100 / B 0 / D 150"
    assert "Pad_52Type" in values["IEC_BomText"]
    assert "角鋼 40*40*5 L=150 x2" in values["IEC_BomText"]


def test_fabricated_member_exports_modeled_dimensions():
    params = extract_params("66-20B(P)-A-200-600", "66")

    assert params is not None
    values = _values(params)
    assert values["C_type"] == "FB12"
    assert values["C_thk_mm"] == 12
    assert values["C_bot_wid_mm"] == 250
    assert values["C_bot_len_mm"] == 650
    assert values["C_web_hgt_mm"] == 200
    assert values["C_web_len_mm"] == 650


def test_export_to_csv_writes_excel_friendly_bom():
    params = extract_params("52-2B(P)-A(A)-130-500", "52")
    output = Path(__file__).with_name("inventor_params_test_output.csv")

    try:
        export_to_csv(params, str(output))

        raw = output.read_bytes()
        assert raw.startswith(codecs.BOM_UTF8)
        text = raw.decode("utf-8-sig")
        assert "# Designation: 52-2B(P)-A(A)-130-500" in text
        assert "ParameterName,Value,Unit,Comment" in text
        assert "C_H_mm,130,mm" in text
    finally:
        output.unlink(missing_ok=True)


def test_ilogic_snippet_uses_vb_safe_csv_parser_and_updates_document():
    snippet = get_ilogic_snippet()

    assert "Sub Main()" in snippet
    assert "End Sub" in snippet
    assert "Dim fields As New System.Collections.Generic.List(Of String)()" in snippet
    assert 'field.Append(""""c)' in snippet
    assert 'ElseIf ch = ","c AndAlso Not inQuotes Then' in snippet
    assert "ThisDoc.Document.Update()" in snippet
    assert "Imports " not in snippet
    assert "MsgBoxStyle" not in snippet
    assert "System.IO.File.Exists" in snippet
    assert "System.Windows.Forms.MessageBox.Show" in snippet
    assert "Sub TrySetMm" not in snippet
    assert "Sub TrySetUl" not in snippet
    assert "invP.Item(pName).Expression" in snippet
    assert "textParams" in snippet
    assert "knownTextNames" in snippet
    assert 'textParams("IEC_Designation") = designation' in snippet
    assert 'textParams("IEC_Type") = prefix' in snippet
    assert 'textParams("IEC_SupportQtyText") = qtyValueText & " 組"' in snippet
    assert "parsedParamCount = parsedParamCount + 1" in snippet
    assert "If parsedParamCount = 0 Then" in snippet
    assert "Dim qtyValueText As String = \"1\"" in snippet
    assert 'textParams("IEC_PipeText") = pipeTxt' in snippet
    assert 'textParams("IEC_BomText") = System.String.Join(" | ", bomParts.ToArray())' in snippet
    assert 'PropertySets.Item("Inventor User Defined Properties")' in snippet
    assert 'activeName.ToLower() <> "value_control.ipt"' in snippet
    assert "ThisDoc.Document.Save()" in snippet
    assert 'New String() {"Pad.ipt", "Channel.ipt", "組合.iam", "a.dwg"}' in snippet
    assert "RuleParametersOutput()" in snippet
    assert "iLogicVb.UpdateWhenDone = True" in snippet
    assert "ThisDoc.Document.Update2(True)" in snippet
    assert "InventorVb.DocumentUpdate()" in snippet
    assert 'textParams("IEC_GeometryText")' in snippet
    assert "IEC_AngleText" in snippet
    assert "watchedTextReport" in snippet
    assert "customProps.Item(pName).Delete()" in snippet
    assert "customProps.Add(expectedText, pName)" in snippet
    assert "createdParams" in snippet
    assert 'invP.UserParameters.AddByExpression(pName, expr, "mm")' in snippet
    assert 'invP.UserParameters.AddByExpression(pName, expr, "ul")' in snippet
    assert "depCustomProps" in snippet
    assert "ThisApplication.Documents.Open(depPath, False)" in snippet
    assert "depCustomProps.Add(depExpectedText, textName)" in snippet
    assert "depDoc.Update2(True)" in snippet
