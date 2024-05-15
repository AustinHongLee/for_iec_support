Attribute VB_Name = "X_M42底板程序"
Function PerformActionByLetter(letter As String, PipeSize As String) As String
    Dim Plate_Size As Double
    Dim plate_thickness As Double
    Dim Weight_calculator As Double
    Dim ws As Worksheet
    Dim Bolt_size As String
    Dim Section_Dim As String
    Dim Angle_Total_Length As Double
    
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")

    ' 根據傳入的字母執行相應的動作
    Select Case letter
        Case "A"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "B"
            ' For Plate a, Plate d, and Bolt
            AddPlateEntry "a", PipeSize
            AddPlateEntry "d", PipeSize
            AddBoltEntry PipeSize, 4

        Case "C"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "D"
            ' For Plate a and Plate e
            AddPlateEntry "a", PipeSize
            AddPlateEntry "e", PipeSize

        Case "E"
            ' For Plate a, Plate d, and Bolt ,and Angle
            AddPlateEntry "a", PipeSize
            AddPlateEntry "d", PipeSize
            AddBoltEntry PipeSize, 4
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "F"
            ' For Plate a and Angle
            AddPlateEntry "a", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "G"
            ' For Plate b and Bolt
            AddPlateEntry "b", PipeSize
            AddBoltEntry PipeSize, 4

        Case "H"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "J"
            ' For Plate b and Bolt
            AddPlateEntry "b", PipeSize
            AddBoltEntry PipeSize, 4

        Case "K"
            ' For Plate a and Angle
            AddPlateEntry "a", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "L"
            ' For Plate c and Bolt
            AddPlateEntry "c", PipeSize
            AddBoltEntry PipeSize, 4

        Case "M"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "N"
            ' For Plate a and Angle
            AddPlateEntry "a", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "P"
            ' For Plate c and Bolt
            AddPlateEntry "c", PipeSize
            AddBoltEntry PipeSize, 4
        Case "R"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "S"
            ' For Plate a, Plate e, and Angle
            AddPlateEntry "a", PipeSize
            AddPlateEntry "e", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case Else
            ' 如果傳入的字母不是預期的字母
            PerformActionByLetter = "沒有為此字母定義動作。"
    End Select
End Function

Sub AddPlateEntry(PlateType As String, PipeSize As Variant)
    '負責運算M42的板子
    
    Dim ws_M42 As Worksheet
    Dim col_type As Integer
    Dim Plate_Size As Double
    Dim plate_thickness As Double
    Dim Weight_calculator As Double
    Dim plate_name As String
    Dim RequireDrilling As Boolean
    Dim PlateBolt_Length_x As Double
    Dim PlateBolt_Length_y As Double
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
        Case "b", "c"
            col_type = 4
        Case "d"
            col_type = 6
        Case "e"
            col_type = 8
    End Select
            
    ' 確定Plate的尺寸和厚度
    If InStr(1, PipeSize, "*") > 0 Then ' this is about section type, different part just range()
        ' 若PipeSize為特定格式的字符串 判讀是否為Steel類別
        col_type = col_type - 1
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), col_type, False)
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 10, False)
        If RequireDrilling = True Then
            If PlateType = "b" Or PlateType = "c" Then
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 4, False) ' get col=4 D
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 4, False) ' same as x
            Else
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 6, False) ' get col=6 F
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 6, False) ' same as x
            End If
        End If
    Else
        ' 若PipeSize為數字
        PipeSize = GetLookupValue(PipeSize)
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), col_type, False)
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 11, False)
        If RequireDrilling = True Then
            If PlateType = "b" Or PlateType = "c" Then
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 5, False) ' get col=5 E
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 5, False) ' same as x
            Else
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 7, False) ' get col=7 G
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 7, False) ' same as x
            End If
        End If
    End If
    Weight_calculator = Plate_Size / 1000 * Plate_Size / 1000 * plate_thickness * 7.85

    ' 確定Plate名稱
    plate_name = "Plate_" & PlateType & IIf(RequireDrilling, "_需鑽孔", "_不需鑽孔")
    
    ' 若需鑽孔則需要給予Bolt_Length
    If RequireDrilling = True Then
        MainAddPlate Plate_Size, Plate_Size, plate_thickness, plate_name, , , True, PlateBolt_Length_x, PlateBolt_Length_y
    Else
        MainAddPlate Plate_Size, Plate_Size, plate_thickness, plate_name
    End If
End Sub
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
