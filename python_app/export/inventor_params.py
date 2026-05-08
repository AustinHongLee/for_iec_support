"""
inventor_params.py
------------------
匯出 Pipe Shoe 系列計算結果為 Autodesk Inventor iLogic 可讀的 CSV 參數檔案。

CSV 格式（UTF-8 BOM，Excel 可直接開啟）：
    ParameterName, Value, Unit, Comment

呼叫範例：
    from export.inventor_params import extract_params, export_to_csv, get_ilogic_snippet

    params = extract_params("52-2B-A-150-200", "52")
    if params:
        export_to_csv(params, r"C:/output/shoe_params.csv")
        print(get_ilogic_snippet(r"C:/output/shoe_params.csv"))

iLogic 讀取範本請呼叫 get_ilogic_snippet() 取得。
"""

from __future__ import annotations

import csv
import os
from datetime import date
from typing import Optional


def extract_params(designation: str, type_id: str, support_qty: int = 1) -> Optional[dict]:
    """從 Pipe Shoe 計算結果提取 Inventor 參數字典。

    回傳格式::

        {
            "params":      [("ParameterName", value, "unit", "comment"), ...],
            "designation": str,
            "type_id":     str,
            "warnings":    [str, ...],
        }

    若 type_id 不屬於 Pipe Shoe 家族（52~55/66/67/85），回傳 None。
    """
    from core.pipe_shoe_engine import (
        PIPE_SHOE_TYPE_IDS,
        calculate,
        get_sizing_context,
    )

    if type_id not in PIPE_SHOE_TYPE_IDS:
        return None

    ctx = get_sizing_context(designation, type_id)
    if ctx is None:
        return None

    result = calculate(designation, type_id)
    support_qty = max(1, int(support_qty or 1))

    rows: list[tuple] = []

    def add(name: str, value, unit: str, comment: str):
        rows.append((name, value, unit, comment))

    def add_text(name: str, value, comment: str):
        rows.append((name, str(value), "text", comment))

    # ── 管路基本 ──────────────────────────────────────────────────────────────
    add_text("IEC_Designation", designation, "圖面用：支撐編號 / Designation")
    add_text("IEC_Type", type_id, "圖面用：Type 編號")
    add("IEC_SupportQty", support_qty, "ul", "圖面用：支撐組數（數值）")
    add_text("IEC_SupportQtyText", f"{support_qty} 組", "圖面用：支撐組數（文字）")
    add("pipe_size_in",  ctx["pipe_size_in"],  "ul", f"管徑英吋 ({ctx['pipe_size_str']})")
    add("OD_mm",         ctx["OD_mm"],          "mm", "管路外徑")
    add("wall_mm",       ctx["wall_mm"],         "mm", "管壁厚度 (SCH10S)")
    add_text(
        "IEC_PipeText",
        f"{ctx['pipe_size_str']} / OD {ctx['OD_mm']:g} / SCH10S t={ctx['wall_mm']:g}",
        "圖面用：管路摘要",
    )

    # ── 管鞋幾何 ──────────────────────────────────────────────────────────────
    add("HOPS_mm",       ctx["HOPS_mm"],         "mm", "管鞋高度 (管中心至底板底面)")
    add("LOPS_mm",       ctx["LOPS_mm"],         "mm", "管鞋長度")
    add("E_mm",          ctx["E_mm"],            "mm", "端部餘量 (側向)")

    # ── D-80 規格表查值 ────────────────────────────────────────────────────────
    add("A_mm",          ctx["A_mm"],            "mm", "D-80 表 A（底板寬度參考）")
    add("B_mm",          ctx["B_mm"],            "mm", "D-80 表 B（板厚參考）")
    add("D_default_mm",  ctx["D_mm"],            "mm", "D-80 表 D（預設管鞋長度）")
    add_text(
        "IEC_GeometryText",
        f"HOPS {ctx['HOPS_mm']:g} / LOPS {ctx['LOPS_mm']:g} / E {ctx['E_mm']:g} / A {ctx['A_mm']:g} / B {ctx['B_mm']:g} / D {ctx['D_mm']:g}",
        "圖面用：主要幾何尺寸摘要",
    )

    # ── 弧形墊板 ──────────────────────────────────────────────────────────────
    pad_entry = next((e for e in result.entries if "Pad_" in e.name), None)
    if pad_entry:
        try:
            thk = float(pad_entry.spec)
        except (ValueError, TypeError):
            thk = ctx["pad_t_mm"]
        add("pad_len_mm", pad_entry.length, "mm", "墊板長度 (=LOPS + E×2)")
        add("pad_wid_mm", pad_entry.width,  "mm", "墊板寬度 (≈OD×π/3, 120° 弧形)")
        add("pad_thk_mm", thk,              "mm", "墊板厚度 (SCH10S 管壁厚)")
        add_text(
            "IEC_PadText",
            f"PAD {pad_entry.length:g}x{pad_entry.width:g}x{thk:g}t x{pad_entry.quantity * support_qty}",
            "圖面用：補強墊板需求摘要",
        )
    else:
        add("pad_thk_mm", ctx["pad_t_mm"],  "mm", "墊板厚度 (SCH10S 管壁厚)")
        add_text("IEC_PadText", "無補強墊板", "圖面用：補強墊板需求摘要")

    # ── 結構件 (MEMBER C) ──────────────────────────────────────────────────────
    if ctx["is_fabricated"]:
        # FB12 路徑：T 型組合鋼板
        add_text("C_type", "FB12", "結構件型式：組合 T 型鋼板")
        add("C_thk_mm",  12,      "mm", "組合鋼板厚度")
        fb_bot = next((e for e in result.entries if e.name == "FB_52Type_1"), None)
        fb_web = next((e for e in result.entries if e.name == "FB_52Type_2"), None)
        fabricated_len = ctx["LOPS_mm"] + 50
        add_text(
            "IEC_MemberText",
            f"FB12 T組合板 底板 {ctx['A_mm']:g}x{fabricated_len:g}x12t x{support_qty} 腹板 {ctx['HOPS_mm']:g}x{fabricated_len:g}x12t x{support_qty}",
            "圖面用：C 構件需求摘要",
        )
        if fb_bot:
            add("C_bot_wid_mm", ctx["A_mm"], "mm", "T 底板寬度 (=A)")
            add("C_bot_len_mm", fabricated_len, "mm", "T 底板長度 (=LOPS+50)")
        if fb_web:
            add("C_web_hgt_mm", ctx["HOPS_mm"], "mm", "T 腹板高度 (=HOPS)")
            add("C_web_len_mm", fabricated_len, "mm", "T 腹板長度 (=LOPS+50)")
    else:
        # H Beam 路徑
        beam_entry = next((e for e in result.entries if e.name == "H型鋼"), None)
        add_text("C_type", ctx["C_spec"], "H 型鋼規格字串（採購規格）")
        add("C_raw_H_mm", ctx["C_H_mm"], "mm", "H 型鋼截面名義高度（採購原料規格，如 H200 = 200mm）")
        add("C_H_mm",    ctx["HOPS_mm"], "mm", "H 型鋼裁切後高度 = HOPS（Inventor 建模用實際尺寸）")
        add("C_B_mm",    ctx["C_B_mm"], "mm", "H 型鋼翼板寬")
        add("C_t_mm",    ctx["C_t_mm"], "mm", "H 型鋼板厚 (翼板/腹板厚)")
        if beam_entry:
            add("beam_len_mm", beam_entry.length, "mm", "H 型鋼切割長度")
            add_text(
                "IEC_MemberText",
                f"H{ctx['C_spec']} L={beam_entry.length:g} x{beam_entry.quantity * support_qty}",
                "圖面用：C 構件需求摘要",
            )
        else:
            add_text("IEC_MemberText", f"H{ctx['C_spec']}", "圖面用：C 構件需求摘要")

    angle_entries = [e for e in result.entries if e.name == "角鋼"]
    angle_texts = []
    for e in angle_entries:
        qty = e.quantity * support_qty
        if e.width:
            angle_texts.append(f"{e.name} {e.length:g}x{e.width:g}x{e.spec} x{qty}")
        elif e.length:
            angle_texts.append(f"{e.name} {e.spec} L={e.length:g} x{qty}")
        else:
            angle_texts.append(f"{e.name} {e.spec} x{qty}")
    add_text(
        "IEC_AngleText",
        " / ".join(angle_texts) if angle_texts else "無角鋼",
        "圖面用：角鋼需求摘要",
    )

    # ── 底板 (M42 base plate) ──────────────────────────────────────────────────
    base_entries = [e for e in result.entries if e.name.startswith("Plate_")]
    base_texts = []
    for i, e in enumerate(base_entries, 1):
        sfx = f"_{i}" if len(base_entries) > 1 else ""
        try:
            thk = float(e.spec)
        except (ValueError, TypeError):
            thk = 0.0
        add(f"base{sfx}_len_mm", e.length, "mm", f"底板{sfx} 長度")
        add(f"base{sfx}_wid_mm", e.width,  "mm", f"底板{sfx} 寬度")
        add(f"base{sfx}_thk_mm", thk,      "mm", f"底板{sfx} 厚度")
        base_texts.append(f"{e.name} {e.length:g}x{e.width:g}x{thk:g}t x{e.quantity * support_qty}")
    add_text(
        "IEC_BaseText",
        " / ".join(base_texts) if base_texts else "無底板",
        "圖面用：底板需求摘要",
    )

    # ── 錨栓 ──────────────────────────────────────────────────────────────────
    bolt_entry = next(
        (e for e in result.entries
         if e.name in ("EXP.BOLT", "ANCHOR BOLT", "M.BOLT", "K BOLT")),
        None,
    )
    if bolt_entry:
        add("anchor_spec", bolt_entry.spec,     "ul", "錨栓規格")
        add("anchor_qty",  bolt_entry.quantity, "ul", "錨栓數量")
        add_text(
            "IEC_AnchorText",
            f"{bolt_entry.name} {bolt_entry.spec} x{bolt_entry.quantity * support_qty}",
            "圖面用：錨栓需求摘要",
        )
    else:
        add_text("IEC_AnchorText", "無錨栓", "圖面用：錨栓需求摘要")

    def _entry_need_text(entry) -> str:
        qty = entry.quantity * support_qty
        if entry.width:
            return f"{entry.name} {entry.length:g}x{entry.width:g}x{entry.spec} x{qty}"
        if entry.length:
            return f"{entry.name} {entry.spec} L={entry.length:g} x{qty}"
        return f"{entry.name} {entry.spec} x{qty}"

    add_text(
        "IEC_BomText",
        " | ".join(_entry_need_text(e) for e in result.entries),
        "圖面用：本支撐需求摘要",
    )
    add_text(
        "IEC_Warnings",
        " | ".join(result.warnings) if result.warnings else "",
        "圖面用：計算警告摘要",
    )

    return {
        "params":      rows,
        "designation": designation,
        "type_id":     type_id,
        "warnings":    list(result.warnings),
    }


def export_to_csv(params_dict: dict, output_path: str) -> str:
    """將參數字典寫出為 CSV 檔案（UTF-8 BOM），回傳實際寫出路徑。"""
    designation = params_dict["designation"]
    rows = params_dict["params"]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["# IEC Support Tool - Inventor Parameters"])
        writer.writerow([f"# Designation: {designation}"])
        writer.writerow([f"# Generated: {date.today().isoformat()}"])
        writer.writerow(["# Usage: load via iLogic rule (see .vb file in same folder)"])
        writer.writerow([])
        writer.writerow(["ParameterName", "Value", "Unit", "Comment"])
        for name, value, unit, comment in rows:
            writer.writerow([name, value, unit, comment])

    return output_path


def export_ilogic_snippet(output_path: str, csv_path: str = "") -> str:
    """將 iLogic VBA 讀取範本寫出為 .vb 文字檔，回傳寫出路徑。"""
    snippet = get_ilogic_snippet(csv_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(snippet)
    return output_path


def get_ilogic_snippet(csv_path: str = "") -> str:
    """回傳 Inventor iLogic VBA 規則字串。

    產生的規則功能：
    - 彈出「開啟檔案」對話框讓使用者選擇 CSV
    - 驗證 CSV 內 ``# Designation:`` 前綴必須為 ``52`` 且包含 ``(P)``
    - 通過驗證後才將所有數值參數套用至模型
    - ``csv_path`` 若有值，會作為對話框的預設目錄（可留空）
    """
    default_dir_vb = csv_path.replace("/", "\\") if csv_path else ""

    return f"""\
' ============================================================
' IEC Support Tool - Pipe Shoe 52(P) Parameter Loader
' 版本：自動選擇 CSV 檔案，並驗證 Designation 合法性
' 規則：# Designation 前綴必須為 "52"，且必須包含 "(P)"
' ============================================================

Sub Main()

Dim activeName As String = ThisDoc.Document.DisplayName
If activeName.ToLower() <> "value_control.ipt" Then
    System.Windows.Forms.MessageBox.Show("請在 Value_Control.ipt 執行此規則。" & vbCrLf & "目前文件：" & activeName, "IEC - 執行位置錯誤", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Warning)
    Return
End If

' ── 1. 開啟選檔對話框 ─────────────────────────────────────────
Dim dlg As New System.Windows.Forms.OpenFileDialog()
dlg.Title  = "選擇 IEC 管鞋參數 CSV 檔案"
dlg.Filter = "CSV 參數檔 (*.csv)|*.csv|所有檔案 (*.*)|*.*"
dlg.FilterIndex = 1
dlg.Multiselect = False
Dim initDir As String = "{default_dir_vb}"
If initDir <> "" AndAlso System.IO.Directory.Exists(System.IO.Path.GetDirectoryName(initDir)) Then
    dlg.InitialDirectory = System.IO.Path.GetDirectoryName(initDir)
End If

If dlg.ShowDialog() <> System.Windows.Forms.DialogResult.OK Then
    Return   ' 使用者取消
End If
Dim csvPath As String = dlg.FileName

' ── 2. 讀取 CSV ───────────────────────────────────────────────
If Not System.IO.File.Exists(csvPath) Then
    System.Windows.Forms.MessageBox.Show("找不到檔案：" & vbCrLf & csvPath, "IEC - 讀取失敗", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error)
    Return
End If

Dim lines() As String = System.IO.File.ReadAllLines(csvPath, System.Text.Encoding.UTF8)

' ── 3. 驗證 Designation ───────────────────────────────────────
Dim designation As String = ""
For Each ln As String In lines
    Dim trimmed As String = ln.Trim()
    If trimmed.StartsWith("# Designation:") Then
        designation = trimmed.Substring("# Designation:".Length).Trim()
        Exit For
    End If
Next

If designation = "" Then
    System.Windows.Forms.MessageBox.Show("CSV 檔案缺少 ""# Designation:"" 欄位。" & vbCrLf & "請確認這是由 IEC Support Tool 產生的檔案。", "IEC - 驗證失敗", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error)
    Return
End If

' 規則 A：前綴（第一個 "-" 之前）必須為 "52"
Dim dashIdx As Integer = designation.IndexOf("-")
Dim prefix  As String  = If(dashIdx > 0, designation.Substring(0, dashIdx).Trim(), designation.Trim())
Dim prefixOk As Boolean = (prefix = "52")

' 規則 B：Designation 必須包含 "(P)"
Dim hasParen As Boolean = designation.Contains("(P)")

If Not prefixOk OrElse Not hasParen Then
    Dim msg As New System.Text.StringBuilder()
    msg.AppendLine("此 CSV 的 Designation 不符合載入條件：")
    msg.AppendLine()
    msg.AppendLine("  Designation：" & designation)
    msg.AppendLine()
    If prefixOk Then
        msg.AppendLine("  [OK] 前綴為 " & Chr(34) & "52" & Chr(34))
    Else
        msg.AppendLine("  [X]  前綴非 " & Chr(34) & "52" & Chr(34) & "（目前為 " & Chr(34) & prefix & Chr(34) & "）")
    End If
    If hasParen Then
        msg.AppendLine("  [OK] 包含 " & Chr(34) & "(P)" & Chr(34))
    Else
        msg.AppendLine("  [X]  未包含 " & Chr(34) & "(P)" & Chr(34))
    End If
    msg.AppendLine()
    msg.AppendLine("請選擇正確的 52(P) 系列管鞋參數檔案。")
    System.Windows.Forms.MessageBox.Show(msg.ToString(), "IEC - 驗證未通過", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Warning)
    Return
End If

' ── 4. 解析參數表 ─────────────────────────────────────────────
Dim numParams As New System.Collections.Generic.Dictionary(Of String, Double)()
Dim textParams As New System.Collections.Generic.Dictionary(Of String, String)()
Dim headerPassed As Boolean = False
Dim parsedParamCount As Integer = 0

For Each ln As String In lines
    Dim trimmed As String = ln.Trim()
    If trimmed = "" OrElse trimmed.StartsWith("#") Then Continue For
    If Not headerPassed Then
        If trimmed.StartsWith("ParameterName") Then headerPassed = True
        Continue For
    End If
    ' 解析 CSV 欄位；支援 quoted field 與 "" 跳脫
    Dim fields As New System.Collections.Generic.List(Of String)()
    Dim field As New System.Text.StringBuilder()
    Dim inQuotes As Boolean = False
    Dim i As Integer = 0
    While i < trimmed.Length
        Dim ch As Char = trimmed.Chars(i)
        If ch = \"\"\"\"c Then
            If inQuotes AndAlso i + 1 < trimmed.Length AndAlso trimmed.Chars(i + 1) = \"\"\"\"c Then
                field.Append(\"\"\"\"c)
                i = i + 1
            Else
                inQuotes = Not inQuotes
            End If
        ElseIf ch = ","c AndAlso Not inQuotes Then
            fields.Add(field.ToString())
            field.Length = 0
        Else
            field.Append(ch)
        End If
        i = i + 1
    End While
    fields.Add(field.ToString())
    If fields.Count < 2 Then Continue For
    Dim pName As String = fields.Item(0).Trim()
    Dim pVal  As String = fields.Item(1).Trim()
    Dim pUnit As String = ""
    If fields.Count >= 3 Then pUnit = fields.Item(2).Trim().ToLower()
    If pUnit = "text" Then
        textParams(pName) = pVal
        parsedParamCount = parsedParamCount + 1
        Continue For
    End If
    Dim numVal As Double = 0
    If Double.TryParse(pVal, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, numVal) Then
        numParams(pName) = numVal
        parsedParamCount = parsedParamCount + 1
    End If
Next

Dim knownTextNames() As String = New String() {{
    "IEC_Designation", "IEC_Type", "IEC_SupportQtyText",
    "IEC_PipeText", "IEC_GeometryText", "IEC_PadText", "IEC_MemberText",
    "IEC_AngleText", "IEC_BaseText", "IEC_AnchorText",
    "IEC_BomText", "IEC_Warnings", "C_type"
}}
For Each textName As String In knownTextNames
    If Not textParams.ContainsKey(textName) Then
        textParams(textName) = ""
    End If
Next
textParams("IEC_Designation") = designation
textParams("IEC_Type") = prefix
Dim qtyValueText As String = "1"
If numParams.ContainsKey("IEC_SupportQty") Then
    qtyValueText = numParams("IEC_SupportQty").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
End If
If textParams("IEC_SupportQtyText") = "" Then
    textParams("IEC_SupportQtyText") = qtyValueText & " 組"
End If

' 舊格式 CSV 若沒有文字列，這裡用已讀到的數值重建最基本的圖面文字，
' 避免 Custom iProperties 留住上一包資料。
Dim pipeToken As String = ""
Dim firstDash As Integer = designation.IndexOf("-")
If firstDash >= 0 Then
    Dim secondDash As Integer = designation.IndexOf("-", firstDash + 1)
    If secondDash > firstDash Then
        pipeToken = designation.Substring(firstDash + 1, secondDash - firstDash - 1).Trim()
    End If
End If
If textParams("IEC_PipeText") = "" Then
    Dim pipeTxt As String = If(pipeToken <> "", pipeToken, designation)
    If numParams.ContainsKey("OD_mm") Then
        pipeTxt = pipeTxt & " / OD " & numParams("OD_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
    End If
    If numParams.ContainsKey("wall_mm") Then
        pipeTxt = pipeTxt & " / SCH10S t=" & numParams("wall_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
    End If
    textParams("IEC_PipeText") = pipeTxt
End If
If textParams("IEC_PadText") = "" AndAlso numParams.ContainsKey("pad_len_mm") AndAlso numParams.ContainsKey("pad_wid_mm") AndAlso numParams.ContainsKey("pad_thk_mm") Then
    textParams("IEC_PadText") = "PAD " & numParams("pad_len_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "x" & numParams("pad_wid_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "x" & numParams("pad_thk_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "t x" & qtyValueText
End If
If textParams("IEC_GeometryText") = "" AndAlso numParams.ContainsKey("HOPS_mm") AndAlso numParams.ContainsKey("LOPS_mm") AndAlso numParams.ContainsKey("E_mm") Then
    textParams("IEC_GeometryText") = "HOPS " & numParams("HOPS_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " / LOPS " & numParams("LOPS_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " / E " & numParams("E_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
    If numParams.ContainsKey("A_mm") Then textParams("IEC_GeometryText") = textParams("IEC_GeometryText") & " / A " & numParams("A_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
    If numParams.ContainsKey("B_mm") Then textParams("IEC_GeometryText") = textParams("IEC_GeometryText") & " / B " & numParams("B_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
    If numParams.ContainsKey("D_default_mm") Then textParams("IEC_GeometryText") = textParams("IEC_GeometryText") & " / D " & numParams("D_default_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
End If
Dim memberSpec As String = textParams("C_type")
If memberSpec = "" AndAlso numParams.ContainsKey("C_raw_H_mm") AndAlso numParams.ContainsKey("C_B_mm") AndAlso numParams.ContainsKey("C_t_mm") Then
    memberSpec = numParams("C_raw_H_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "*" & numParams("C_B_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "*" & numParams("C_t_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture)
    textParams("C_type") = memberSpec
End If
If textParams("IEC_MemberText") = "" Then
    If memberSpec <> "" AndAlso numParams.ContainsKey("beam_len_mm") Then
        textParams("IEC_MemberText") = "H" & memberSpec & " L=" & numParams("beam_len_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " x" & qtyValueText
    ElseIf numParams.ContainsKey("C_thk_mm") AndAlso numParams.ContainsKey("C_bot_wid_mm") AndAlso numParams.ContainsKey("C_bot_len_mm") AndAlso numParams.ContainsKey("C_web_hgt_mm") AndAlso numParams.ContainsKey("C_web_len_mm") Then
        textParams("IEC_MemberText") = "FB" & numParams("C_thk_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " T組合板 底板 " & numParams("C_bot_wid_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "x" & numParams("C_bot_len_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " 腹板 " & numParams("C_web_hgt_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & "x" & numParams("C_web_len_mm").ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " x" & qtyValueText
    End If
End If
If textParams("IEC_BomText") = "" Then
    Dim bomParts As New System.Collections.Generic.List(Of String)()
    If textParams("IEC_PadText") <> "" Then bomParts.Add(textParams("IEC_PadText"))
    If textParams("IEC_MemberText") <> "" Then bomParts.Add(textParams("IEC_MemberText"))
    If textParams("IEC_AngleText") <> "" Then bomParts.Add(textParams("IEC_AngleText"))
    If textParams("IEC_BaseText") <> "" Then bomParts.Add(textParams("IEC_BaseText"))
    If textParams("IEC_AnchorText") <> "" Then bomParts.Add(textParams("IEC_AnchorText"))
    textParams("IEC_BomText") = System.String.Join(" | ", bomParts.ToArray())
End If

If parsedParamCount = 0 Then
    System.Windows.Forms.MessageBox.Show("CSV 中未讀到任何參數，請確認檔案格式。", "IEC - 無參數", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Warning)
    Return
End If

' ── 5. 套用參數至模型 ─────────────────────────────────────────
Dim invP As Object = ThisDoc.Document.ComponentDefinition.Parameters
Dim applied  As Integer = 0
Dim appliedText As Integer = 0
Dim createdParams As Integer = 0
Dim skipped  As Integer = 0
Dim skipList As New System.Text.StringBuilder()
Dim watchedTextReport As New System.Text.StringBuilder()
Dim watchNames() As String = New String() {{
    "IEC_Designation", "IEC_SupportQtyText", "IEC_PipeText",
    "IEC_GeometryText", "IEC_PadText", "IEC_MemberText",
    "IEC_AngleText", "IEC_BaseText", "IEC_AnchorText",
    "IEC_BomText", "IEC_Warnings"
}}

' 圖面字串：寫入 Custom iProperties，供 idw/dwg 標題欄或文字欄位引用
Dim customProps As Object = ThisDoc.Document.PropertySets.Item("Inventor User Defined Properties")
For Each pName As String In textParams.Keys
    Dim expectedText As String = textParams(pName)
    Dim wroteTextOk As Boolean = False
    Try
        customProps.Item(pName).Value = expectedText
        If CStr(customProps.Item(pName).Value) = expectedText Then wroteTextOk = True
    Catch
    End Try
    If Not wroteTextOk Then
        Try
            Try
                customProps.Item(pName).Delete()
            Catch
            End Try
            customProps.Add(expectedText, pName)
            If CStr(customProps.Item(pName).Value) = expectedText Then wroteTextOk = True
        Catch
        End Try
    End If
    If wroteTextOk Then
        appliedText = appliedText + 1
    Else
        skipped = skipped + 1
        skipList.AppendLine("  iProperty: " & pName)
    End If
Next

For Each watchName As String In watchNames
    Try
        watchedTextReport.AppendLine("  " & watchName & " = " & CStr(customProps.Item(watchName).Value))
    Catch
        watchedTextReport.AppendLine("  " & watchName & " = [讀取失敗]")
    End Try
Next

' mm 參數
Dim mmNames() As String = New String() {{
    "OD_mm", "wall_mm",
    "HOPS_mm", "LOPS_mm", "E_mm",
    "A_mm", "B_mm", "D_default_mm",
    "pad_len_mm", "pad_wid_mm", "pad_thk_mm",
    "C_H_mm", "C_raw_H_mm", "C_B_mm", "C_t_mm", "beam_len_mm",
    "C_thk_mm", "C_bot_wid_mm", "C_bot_len_mm", "C_web_hgt_mm", "C_web_len_mm",
    "base_len_mm", "base_wid_mm", "base_thk_mm"
}}

For Each pName As String In mmNames
    If numParams.ContainsKey(pName) Then
        Dim expr As String = numParams(pName).ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " mm"
        Dim paramOk As Boolean = False
        Try
            invP.Item(pName).Expression = expr
            paramOk = True
            applied = applied + 1
        Catch
        End Try
        If Not paramOk Then
            Try
                invP.UserParameters.AddByExpression(pName, expr, "mm")
                createdParams = createdParams + 1
                applied = applied + 1
                paramOk = True
            Catch
            End Try
        End If
        If Not paramOk Then
            skipped = skipped + 1
            skipList.AppendLine("  " & pName)
        End If
    End If
Next

' unitless 參數
Dim ulNames() As String = New String() {{"IEC_SupportQty", "pipe_size_in", "anchor_qty"}}

For Each pName As String In ulNames
    If numParams.ContainsKey(pName) Then
        Dim expr As String = numParams(pName).ToString("0.######", System.Globalization.CultureInfo.InvariantCulture) & " ul"
        Dim paramOk As Boolean = False
        Try
            invP.Item(pName).Expression = expr
            paramOk = True
            applied = applied + 1
        Catch
        End Try
        If Not paramOk Then
            Try
                invP.UserParameters.AddByExpression(pName, expr, "ul")
                createdParams = createdParams + 1
                applied = applied + 1
                paramOk = True
            Catch
            End Try
        End If
        If Not paramOk Then
            skipped = skipped + 1
            skipList.AppendLine("  " & pName)
        End If
    End If
Next

' ── 6. 結果報告 ───────────────────────────────────────────────
Try
    RuleParametersOutput()
Catch
End Try
Try
    iLogicVb.UpdateWhenDone = True
Catch
End Try
Try
    ThisDoc.Document.Update2(True)
Catch
    Try
        ThisDoc.Document.Update()
    Catch
    End Try
End Try
Try
    InventorVb.DocumentUpdate()
Catch
End Try
Try
    ThisDoc.Document.Save()
Catch
End Try

Dim refreshedDocs As New System.Text.StringBuilder()
Dim missingDocs As New System.Text.StringBuilder()
Dim rootDir As String = System.IO.Path.GetDirectoryName(ThisDoc.Document.FullFileName)
Dim dependentDocs() As String = New String() {{"Pad.ipt", "Channel.ipt", "組合.iam", "a.dwg"}}

For Each depName As String In dependentDocs
    Dim depPath As String = System.IO.Path.Combine(rootDir, depName)
    If System.IO.File.Exists(depPath) Then
        Try
            Dim depDoc As Object = ThisApplication.Documents.Open(depPath, False)
            Try
                Dim depCustomProps As Object = depDoc.PropertySets.Item("Inventor User Defined Properties")
                For Each textName As String In textParams.Keys
                    Dim depExpectedText As String = textParams(textName)
                    Dim depWroteTextOk As Boolean = False
                    Try
                        depCustomProps.Item(textName).Value = depExpectedText
                        If CStr(depCustomProps.Item(textName).Value) = depExpectedText Then depWroteTextOk = True
                    Catch
                    End Try
                    If Not depWroteTextOk Then
                        Try
                            Try
                                depCustomProps.Item(textName).Delete()
                            Catch
                            End Try
                            depCustomProps.Add(depExpectedText, textName)
                            If CStr(depCustomProps.Item(textName).Value) = depExpectedText Then depWroteTextOk = True
                        Catch
                        End Try
                    End If
                    If Not depWroteTextOk Then
                        skipped = skipped + 1
                        skipList.AppendLine("  iProperty: " & depName & " / " & textName)
                    End If
                Next
            Catch
            End Try
            Try
                depDoc.Update2(True)
            Catch
                Try
                    depDoc.Update()
                Catch
                End Try
            End Try
            depDoc.Save()
            refreshedDocs.AppendLine("  " & depName)
        Catch
            skipped = skipped + 1
            skipList.AppendLine("  update: " & depName)
        End Try
    Else
        missingDocs.AppendLine("  " & depName)
    End If
Next

Dim report As New System.Text.StringBuilder()
report.AppendLine("[OK] 參數套用完成")
report.AppendLine()
report.AppendLine("  Designation ：" & designation)
report.AppendLine("  來源檔案   ：" & csvPath)
report.AppendLine()
report.AppendLine("  套用成功：" & applied.ToString() & " 個數值參數")
If createdParams > 0 Then
    report.AppendLine("  自動新增：" & createdParams.ToString() & " 個 User Parameters")
End If
report.AppendLine("  寫入文字：" & appliedText.ToString() & " 個 iProperties")
If watchedTextReport.Length > 0 Then
    report.AppendLine()
    report.AppendLine("  Value_Control.ipt 目前文字屬性：")
    report.Append(watchedTextReport.ToString())
End If
If skipped > 0 Then
    report.AppendLine("  略過（模型中無此參數）：" & skipped.ToString() & " 個")
    report.Append(skipList.ToString())
End If
If refreshedDocs.Length > 0 Then
    report.AppendLine()
    report.AppendLine("  已更新文件：")
    report.Append(refreshedDocs.ToString())
End If
If missingDocs.Length > 0 Then
    report.AppendLine()
    report.AppendLine("  找不到文件：")
    report.Append(missingDocs.ToString())
End If
System.Windows.Forms.MessageBox.Show(report.ToString(), "IEC - 匯入完成", System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Information)
End Sub
"""
