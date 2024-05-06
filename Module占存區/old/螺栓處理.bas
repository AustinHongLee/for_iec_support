Attribute VB_Name = "螺栓處理"
Sub AddBoltEntry(PipeSize As Variant, Quantity As Integer)
    Dim ws As Worksheet
    Dim i As Long
    Dim BoltSize As String
    
    ' 設定對 "Weight_Analysis" 工作表的引用
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")
    ' 找到列 B 的下一個空白行
    i = GetNextRowInColumnB()

    If InStr(1, PipeSize, "*") > 0 Then
        ' 若PipeSize為特定格式的字符串
        BoltSize = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 9, False)
    Else
        ' 若PipeSize為數字
        PipeSize = GetLookupValue(PipeSize)
        BoltSize = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 10, False)
    End If


    ' 填充數據
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "EXP.BOLT"
        .Cells(i, "D").value = "'" & BoltSize & """"
        .Cells(i, "G").value = "SUS304"
        .Cells(i, "H").value = Quantity
        .Cells(i, "J").value = 1 ' 假設每個螺栓的單個重量是1（可以根據實際情況調整）
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "螺絲類"
    End With
End Sub
