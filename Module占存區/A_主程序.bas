Attribute VB_Name = "A_主程序"
' debug.print 開關
Global Const DEBUG_MODE As Boolean = True
Global globalPrintStep As Long
Sub List_to_Analysis()
    Dim ws As Worksheet
    Dim Row_max As Long
    Dim i As Long
    Dim fullstring As String
    Dim PartString_Type As String
    Dim headers As Variant
    Dim ii As Integer
    
    Set ws = Worksheets("List_Table")
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Weight_Analysis = Worksheets("Weight_Analysis")
    ' 標記運行時間
    ws.Cells(9, "F") = Now()
    ' 清除所有內容
    ws_M42.Cells.ClearContents
    
    ' 檢測是否有資訊若無則追加

    ' 定義列標題和對應的列號
    headers = Array(Array("A", "管支撐型號"), Array("B", "項次"), Array("C", "品名"), Array("D", "尺寸/厚度"), Array("E", "長度"), Array("F", "寬度"), Array("G", "材質"), Array("H", "數量"), Array("I", "每米重"), Array("J", "單重"), Array("K", "重量小計"), Array("L", "單位"), Array("M", "組數"), Array("N", "長度小計"), Array("O", "數量小計"), Array("P", "重量合計"), Array("Q", "屬性"))

    ' 遍歷數組並設置列標題
       With ws_Weight_Analysis
    For ii = LBound(headers) To UBound(headers)
        If .Cells(1, headers(ii)(0)).value <> headers(ii)(1) Then
            .Cells(1, headers(ii)(0)).value = headers(ii)(1)
        End If
    Next ii
        End With
    
    ' 修改了找尋最後一列的方法 or ws.Cells(1, "A").End(xlDown).Row
    Row_max = ws.Cells(ws.Rows.count, "A").End(xlUp).Row
    
    ' 主處理循環
    For i = 2 To Row_max
        fullstring = ws.Cells(i, "A").value
        PartString_Type = GetFirstPartOfString(fullstring)
        Last_row_main_Title = GetNextRowInColumnB()
        ws_Weight_Analysis.Cells(Last_row_main_Title, "A") = fullstring
        On Error GoTo ErrorHandler
Select Case PartString_Type
    Case "01"
        Type_01 fullstring
    ' Case "02"
        ' Type_02 fullString
    ' Case "03"
        ' Type_03 fullString
    ' Case "04"
        ' Type_04 fullString
     Case "05"
         Type_05 fullstring
    ' Case "06"
        ' Type_06 fullString
    ' Case "07"
        ' Type_07 fullString
     Case "08"
         Type_08 fullstring
     Case "09"
         Type_09 fullstring
    ' Case "10"
        ' Type_10 fullString
    Case "11"
        Type_11 fullstring
    ' Case "12"
        ' Type_12 fullString
    ' Case "13"
        ' Type_13 fullString
     Case "14"
         Type_14 fullstring
     Case "15"
         Type_15 fullstring
    Case "16"
        Type_16 fullstring
    ' Case "17"
        ' Type_17 fullString
    ' Case "18"
        ' Type_18 fullString
    ' Case "19"
        ' Type_19 fullString
     Case "20"
         Type_20 fullstring
     Case "21"
         Type_21 fullstring
     Case "22"
         Type_22 fullstring
     Case "23"
         Type_23 fullstring
     Case "24"
         Type_24 fullstring
     Case "25"
         Type_25 fullstring
     Case "26"
         Type_26 fullstring
     Case "27"
         Type_27 fullstring
     Case "28"
         Type_28 fullstring
    ' Case "29"
        ' Type_29 fullString
     Case "30"
         Type_30 fullstring
      Case "31"
         Type_31 fullstring
     Case "32"
         Type_32 fullstring
     Case "33"
         Type_33 fullstring
     Case "34"
         Type_34 fullstring
     Case "35"
         Type_35 fullstring
     Case "37"
         Type_37 fullstring
     Case "39"
         Type_39 fullstring
     Case "48"
         Type_48 fullstring
     Case "51"
         Type_51 fullstring
     Case "52"
         Type_52 fullstring
     Case "53"
         Type_53 fullstring
     Case "54"
         Type_54 fullstring
     Case "55"
         Type_55 fullstring
     Case "57"
         Type_57 fullstring
     Case "59"
         Type_59 fullstring
     'Case "60"
         'Type_60 fullString
      Case "66"
         Type_66 fullstring
      Case "67"
         Type_67 fullstring
      Case "80"
         Type_80 fullstring
      Case "85"
         Type_85 fullstring
      Case "86"
         Type_86 fullstring
      Case "87"
         Type_87 fullstring
    Case "102"
        Type_102 fullstring
    Case "108"
        Type_108 fullstring
    Case Else
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error"
        End Select
        On Error GoTo 0
ContinueLoop:
    Next i
    Exit Sub


ErrorHandler:
    If Err.Number = vbObjectError + 513 Then ' 513錯誤是說該值得第二段產生非邏輯上的錯誤
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error02"
    ElseIf Err.Number = vbObjectError + 514 Then '(錯誤處理)[Fig類型或者M42] 檢查是否找到匹配項，並判讀是否為數字或者中文 @ 514
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
        Debug.Print "[目前程序 : " & functionName & "]" & vbCrLf & "#Step " & globalPrintStep & "." & vbCrLf & "      time : " & formattedTime & vbCrLf
    End If
End Function































