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
    ' 負責處理M42板子的數據輸入
    
    ' 宣告變數
    Dim ws_M42 As Worksheet ' 儲存M_42_Table工作表的引用
    Dim col_type As Integer ' 用於存儲板子類型的對應列索引
    Dim Plate_Size As Double ' 用於存儲板子的大小
    Dim plate_thickness As Double ' 用於存儲板子的厚度
    Dim Weight_calculator As Double ' 用於計算板子的重量
    Dim plate_name As String ' 用於存儲板子的名稱
    Dim RequireDrilling As Boolean ' 用於標記是否需要鑽孔
    Dim PlateBolt_Length_x As Double ' 用於存儲板子在x方向上的螺栓長度
    Dim PlateBolt_Length_y As Double ' 用於存儲板子在y方向上的螺栓長度
    Dim ws As Worksheet ' 儲存Weight_Analysis工作表的引用
    Dim i As Long ' 用於存儲新數據輸入的行號
    Dim PlateBolt_Bolt_hole As Double
    Dim PlateBolt_Bolt_Size As String

    ' 設定對特定工作表的引用
    Set ws = Worksheets("Weight_Analysis") ' 引用Weight_Analysis工作表
    Set ws_M42 = Worksheets("M_42_Table") ' 引用M_42_Table工作表

    ' 找到列 B 的最後一行，並為新數據準備下一行
    i = ws.Cells(ws.Rows.count, "B").End(xlUp).Row + 1

    ' 根據板子類型決定是否需要鑽孔
    Select Case PlateType
        Case "d", "b", "c"
            RequireDrilling = True ' 當板子類型為 d, b 或 c 時，需要鑽孔
        Case Else
            RequireDrilling = False ' 其他類型的板子不需要鑽孔
    End Select
    
    ' 根據板子類型決定屬性(BXB EXE GXG CXC)
    Select Case PlateType
        Case "a"
            col_type = 3 ' 類型 a 對應第 3 列
        Case "b", "c"
            col_type = 4 ' 類型 b 和 c 對應第 4 列
        Case "d"
            col_type = 6 ' 類型 d 對應第 6 列
        Case "e"
            col_type = 8 ' 類型 e 對應第 8 列
    End Select
            
    ' 確定板子的尺寸和厚度
    If InStr(1, PipeSize, "*") > 0 Then ' 若PipeSize包含 "*" 字符
        ' 處理特定格式的字符串（例如鋼類別）
        col_type = col_type - 1 ' 列索引減 1
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), col_type, False) ' 查找板子的大小
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 10, False) ' 查找板子的厚度
        ' 若需要鑽孔，則獲取螺栓長度
        If RequireDrilling = True Then
            If PlateType = "b" Or PlateType = "c" Then
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 4, False) ' 查找列 4 的值
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 4, False) ' 查找列 4 的值（與 x 相同）
            Else
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 6, False) ' 查找列 6 的值
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 6, False) ' 查找列 6 的值（與 x 相同）
            End If
            PlateBolt_Bolt_hole = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 8, False) ' Type double
            PlateBolt_Bolt_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 9, False) ' Type String
            
        End If
    Else
        ' 若PipeSize為數字
        PipeSize = GetLookupValue(PipeSize) ' 獲取對應的查找值
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), col_type, False) ' 查找板子的大小
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 11, False) ' 查找板子的厚度
        
        ' 若需要鑽孔，則獲取螺栓長度
        If RequireDrilling = True Then
            If PlateType = "b" Or PlateType = "c" Then
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 5, False) ' 查找列 5 的值
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 5, False) ' 查找列 5 的值（與 x 相同）
            Else
                PlateBolt_Length_x = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 7, False) ' 查找列 7 的值
                PlateBolt_Length_y = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 7, False) ' 查找列 7 的值（與 x 相同）
            End If
        
        PlateBolt_Bolt_hole = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 9, False) ' Type double
        PlateBolt_Bolt_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 10, False) ' Type String
        End If
    End If
    
    ' 計算板子的重量
    Weight_calculator = Plate_Size / 1000 * Plate_Size / 1000 * plate_thickness * 7.85

    ' 確定板子的名稱
    plate_name = "Plate_" & PlateType & IIf(RequireDrilling, "_需鑽孔", "_不需鑽孔")
    
    ' 若需鑽孔則需要給予螺栓長度
    If RequireDrilling = True Then
        MainAddPlate Plate_Size, Plate_Size, plate_thickness, plate_name, , , True, PlateBolt_Length_x, PlateBolt_Length_y, PlateBolt_Bolt_hole, PlateBolt_Bolt_Size
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
