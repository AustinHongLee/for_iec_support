Attribute VB_Name = "A_�D�{��"
' debug.print �}��
Global Const DEBUG_MODE As Boolean = False
Global globalPrintStep As Long
Sub List_to_Analysis()
    Dim ws As Worksheet
    Dim Row_max As Long
    Dim i As Long
    Dim fullString As String
    Dim PartString_Type As String
    Dim headers As Variant
    Dim ii As Integer
    
    Set ws = Worksheets("List_Table")
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Weight_Analysis = Worksheets("Weight_Analysis")
    ' �аO�B��ɶ�
    ws.Cells(9, "F") = Now()
    ' �M���Ҧ����e
    ws_M42.Cells.ClearContents
    
    ' �˴��O�_����T�Y�L�h�l�[

    ' �w�q�C���D�M�������C��
    headers = Array(Array("A", "�ޤ伵����"), Array("B", "����"), Array("C", "�~�W"), Array("D", "�ؤo/�p��"), Array("E", "����"), Array("F", "�e��"), Array("G", "����"), Array("H", "�ƶq"), Array("I", "�C�̭�"), Array("J", "�歫"), Array("K", "���q�p�p"), Array("L", "���"), Array("M", "�ռ�"), Array("N", "���פp�p"), Array("O", "�ƶq�p�p"), Array("P", "���q�X�p"), Array("Q", "�ݩ�"))

    ' �M���Ʋըó]�m�C���D
       With ws_Weight_Analysis
    For ii = LBound(headers) To UBound(headers)
        If .Cells(1, headers(ii)(0)).value <> headers(ii)(1) Then
            .Cells(1, headers(ii)(0)).value = headers(ii)(1)
        End If
    Next ii
        End With
    
    ' �ק�F��M�̫�@�C����k or ws.Cells(1, "A").End(xlDown).Row
    Row_max = ws.Cells(ws.Rows.count, "A").End(xlUp).Row
    
    ' �D�B�z�`��
    For i = 2 To Row_max
        fullString = ws.Cells(i, "A").value
        PartString_Type = GetFirstPartOfString(fullString)
        Last_row_main_Title = GetNextRowInColumnB()
        ws_Weight_Analysis.Cells(Last_row_main_Title, "A") = fullString
        On Error GoTo ErrorHandler
Select Case PartString_Type
    Case "01"
        Type_01 fullString
    ' Case "02"
        ' Type_02 fullString
    ' Case "03"
        ' Type_03 fullString
    ' Case "04"
        ' Type_04 fullString
     Case "05"
         Type_05 fullString
    ' Case "06"
        ' Type_06 fullString
    ' Case "07"
        ' Type_07 fullString
     Case "08"
         Type_08 fullString
     Case "09"
         Type_09 fullString
    ' Case "10"
        ' Type_10 fullString
    Case "11"
        Type_11 fullString
    ' Case "12"
        ' Type_12 fullString
    ' Case "13"
        ' Type_13 fullString
     Case "14"
         Type_14 fullString
     Case "15"
         Type_15 fullString
    Case "16"
        Type_16 fullString
    ' Case "17"
        ' Type_17 fullString
    ' Case "18"
        ' Type_18 fullString
    ' Case "19"
        ' Type_19 fullString
     Case "20"
         Type_20 fullString
     Case "21"
         Type_21 fullString
     Case "22"
         Type_22 fullString
     Case "23"
         Type_23 fullString
     Case "24"
         Type_24 fullString
     Case "25"
         Type_25 fullString
     Case "26"
         Type_26 fullString
     Case "27"
         Type_27 fullString
     Case "28"
         Type_28 fullString
    ' Case "29"
        ' Type_29 fullString
     Case "30"
         Type_30 fullString
      Case "31"
         Type_31 fullString
     Case "32"
         Type_32 fullString
     Case "33"
         Type_33 fullString
     Case "34"
         Type_34 fullString
     Case "35"
         Type_35 fullString
     Case "37"
         Type_37 fullString
     Case "39"
         Type_39 fullString
     Case "48"
         Type_48 fullString
     Case "51"
         Type_51 fullString
     Case "52"
         Type_52 fullString
     Case "53"
         Type_53 fullString
     Case "54"
         Type_54 fullString
     Case "55"
         Type_55 fullString
     Case "57"
         Type_57 fullString
    Case "108"
        Type_108 fullString
    Case Else
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error"
        End Select
        On Error GoTo 0
ContinueLoop:
    Next i
    Exit Sub


ErrorHandler:
    If Err.Number = vbObjectError + 513 Then ' 513���~�O���ӭȱo�ĤG�q���ͫD�޿�W�����~
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error02"
    ElseIf Err.Number = vbObjectError + 514 Then '(���~�B�z)[Fig�����Ϊ�M42] �ˬd�O�_���ǰt���A�çPŪ�O�_���Ʀr�Ϊ̤��� @ 514
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error03"
    Else
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error"
    End If
    Resume ContinueLoop
End Sub



Function PrintStepCalculator(functionName As String)
    If DEBUG_MODE Then
        globalPrintStep = globalPrintStep + 1
        Dim formattedTime As String
        formattedTime = Format(Now, "yyyy-mm-dd HH:nn:ss")
        Debug.Print "[�ثe�{�� : " & functionName & "]" & vbCrLf & "#Step " & globalPrintStep & "." & vbCrLf & "      time : " & formattedTime & vbCrLf
    End If
End Function































