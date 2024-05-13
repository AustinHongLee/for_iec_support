Attribute VB_Name = "C_鋼板處理"
Sub MainAddPlate(plate_size_a As Double, plate_size_b As Double, plate_thickness As Double, plate_name As String, Optional Plate_Material As String, Optional Plate_qty As Double)
 ' ----------------------------------------------------------------------------------------
' |                        程序 AddNewMaterial 功能描述                                  |
' | ------------------------------------------------------------------------------------- |
' | - 根據提供的材料尺寸和類型，計算新材料的重量。                                        |
' | - 使用預定義的材料密度，如果沒有指定材料類型，將使用默認材料。                        |
' | - 根據輸入的尺寸計算材料重量，並將計算結果填充到工作表的相應單元格中。                |
' | - 獲取下一個可用行以插入新數據，保持工作表的整潔和組織。                              |
' | - 檢查第一個值是否已存在，以確定是否從1開始編號或繼續序列。                           |
' | - 將計算和輸入的數據填充到工作表的特定列，以便進行重量分析。                          |
' | - 適用板類配分
' | - MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name.Plate_Material,Plate_qty
' ----------------------------------------------------------------------------------------
   
    
    
    Dim Pipeline_Density As Double
    Dim weight As Double
    Dim i As Long
    Dim First_Value_Checking As Long
    Dim ws As Worksheet
    Set ws = Worksheets("Weight_Analysis")
    '------Optional remake---
    If Plate_qty = 0 Then
        Plate_qty = 1
    End If
   
    If Plate_Material = "" Then
        Plate_Material = "A36/SS400"
    End If
    '-----------------------------
    Select Case Plate_Material
        Case "A36/SS400"
            Pipeline_Density = 7.85
        Case "SUS304"
            Pipeline_Density = 7.93
        Case "AS"
            Pipeline_Density = 7.82
    End Select
           

    weight = plate_size_a / 1000 * plate_size_b / 1000 * plate_thickness * Pipeline_Density
    

    i = GetNextRowInColumnB()


    If ws.Cells(i, "A").value <> "" Then
        First_Value_Checking = 1
    Else
        First_Value_Checking = ws.Cells(i - 1, "B").value + 1
    End If


    With ws
        .Cells(i, "B").value = First_Value_Checking
        .Cells(i, "C").value = plate_name
        .Cells(i, "D").value = plate_thickness
        .Cells(i, "E").value = plate_size_a
        .Cells(i, "F").value = plate_size_b
        .Cells(i, "G").value = Plate_Material
        .Cells(i, "H").value = Plate_qty
        .Cells(i, "J").value = weight
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "PC"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "鋼板類"
    End With
End Sub


Sub AddPlateEntry(PlateType As String, PipeSize As Variant)
    '負責運算M42的板子
    
    Dim ws_M42 As Worksheet
    Dim col_type As Integer
    Dim Plate_Size As Double
    Dim plate_thickness As Double
    Dim Weight_calculator As Double
    Dim plate_name As String
    Dim RequireDrilling As Boolean
    Dim ws As Worksheet
    Dim i As Long

    ' 設定對特定工作表的引用
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")

    ' 找到列 B 的最後一行，並為新數據準備下一行
    i = ws.Cells(ws.Rows.count, "B").End(xlUp).Row + 1

    ' 根據板子類型決定是否需要鑽孔
    Select Case PlateType
        Case "d", "b", "c"
            RequireDrilling = True
        Case Else
            RequireDrilling = False
    End Select
    ' 根據板子類型決定屬性(BXB EXE GXG CXC)
        Select Case PlateType
            Case "a"
                col_type = 3
            Case "b"
                col_type = 4
            Case "c"
                col_type = 4
            Case "d"
                col_type = 6
            Case "e"
                col_type = 8
        End Select
            
            
            
    ' 確定Plate的尺寸和厚度
    If InStr(1, PipeSize, "*") > 0 Then
        ' 若PipeSize為特定格式的字符串
        col_type = col_type - 1
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), col_type, False)
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 10, False)
    Else
        ' 若PipeSize為數字
        PipeSize = GetLookupValue(PipeSize)
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), col_type, False)
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 11, False)
    End If
    Weight_calculator = Plate_Size / 1000 * Plate_Size / 1000 * plate_thickness * 7.85

    ' 確定Plate名稱
    plate_name = "Plate_" & PlateType & IIf(RequireDrilling, "_需鑽孔", "_不需鑽孔")

    
    MainAddPlate Plate_Size, Plate_Size, plate_thickness, plate_name
    ' 填充數據
    ' With ws
        ' .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        ' .Cells(i, "C").value = Plate_Name
        ' .Cells(i, "D").value = Plate_Thickness
        ' .Cells(i, "E").value = Plate_Size
        ' .Cells(i, "F").value = Plate_Size
        ' .Cells(i, "G").value = "A36/SS400"
        ' .Cells(i, "H").value = 1
        ' .Cells(i, "J").value = Weight_calculator
        ' .Cells(i, "K").value = Weight_calculator
        ' .Cells(i, "L").value = "PC"
        ' .Cells(i, "M").value = 1
        ' .Cells(i, "O").value = 1
        ' .Cells(i, "P").value = Weight_calculator
        ' .Cells(i, "Q").value = "鋼板類"
    ' End With
End Sub
