Attribute VB_Name = "Module1"
' 自定義類型 SectionDetails，用於存儲部件的尺寸和類型
Type SectionDetails
    Size As String
    Type As String
End Type
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
    ' 標記運行時間
    ws.Cells(4, "F") = Now()
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
    
    ' 修改了找尋最後一列的方法
    Row_max = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    ' 主處理循環
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
     Case "52"
         Type_52 fullString
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
    If Err.Number = vbObjectError + 513 Then ' 513錯誤是說該值得第二段產生非邏輯上的錯誤
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error02"
    ElseIf Err.Number = vbObjectError + 514 Then '(錯誤處理)[Fig類型或者M42] 檢查是否找到匹配項，並判讀是否為數字或者中文 @ 514
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error03"
    Else
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error"
    End If
    Resume ContinueLoop
End Sub


Function GetFirstPartOfString(fullString As String) As String
    Dim splitString As Variant
    Dim firstPart As String
    
    splitString = Split(fullString, "-") ' 使用"-"作為分隔符來分割字符串
    
    If UBound(splitString) >= 1 Then ' 確保有足夠的分隔符
        firstPart = splitString(0) ' 獲取分割後數組的第一個元素，即第一個"-"之前的值
    Else
        firstPart = "N/A" ' 如果沒有足夠的分隔符，設置一個錯誤消息或默認值
    End If

    GetFirstPartOfString = firstPart
End Function


Function GetSecondPartOfString(fullString As String) As String
    Dim splitString As Variant
    Dim secondPart As String
    
    splitString = Split(fullString, "-") ' 使用"-"作為分隔符來分割字符串
    
    If UBound(splitString) >= 1 Then ' 確保有足夠的分隔符
        secondPart = splitString(1) ' 獲取分割後數組的第二個元素，即第一個和第二個"-"之間的值
    Else
        secondPart = "N/A" ' 如果沒有足夠的分隔符，設置一個錯誤消息或默認值
    End If

    GetSecondPartOfString = secondPart
End Function

Function GetThirdPartOfString(fullString As String) As String
    Dim splitString As Variant
    splitString = Split(fullString, "-") ' 使用 "-" 來分割字符串

    If UBound(splitString) >= 2 Then ' 確保有足夠的分隔符
        GetThirdPartOfString = splitString(2) ' 第三部分
    Else
        GetThirdPartOfString = "N/A" ' 如果沒有足夠的分隔符，設置一個錯誤消息或默認值
    End If
End Function
Function GetFourthPartOfString(fullString As String) As String
    Dim splitString As Variant
    splitString = Split(fullString, "-") ' 使用 "-" 來分割字符串

    If UBound(splitString) >= 3 Then ' 確保有足夠的分隔符
        GetFourthPartOfString = splitString(3) ' 第四部分
    Else
        GetFourthPartOfString = "N/A" ' 如果沒有足夠的分隔符，設置一個錯誤消息或默認值
    End If
End Function
Function GetFifthPartOfString(fullString As String) As String
    Dim splitString As Variant
    splitString = Split(fullString, "-") ' 使用 "-" 來分割字符串

    If UBound(splitString) >= 4 Then ' 確保有足夠的分隔符
        GetFifthPartOfString = splitString(4) ' 第五部分
    Else
        GetFifthPartOfString = "N/A" ' 如果沒有足夠的分隔符，設置一個錯誤消息或默認值
    End If
End Function

Function IsFourthPartAvailable(ByVal fullString As String) As Boolean
    Dim parts() As String
    parts = Split(fullString, "-") ' 使用連字符分隔字符串
    
    ' 如果分割後的數組長度大於或等於 4，則表示存在第四部分
    If UBound(parts) >= 3 Then
        IsFourthPartAvailable = True
    Else
        IsFourthPartAvailable = False
    End If
End Function

Function GetNextRowInColumnB() As Long
    Dim ws As Worksheet
    Dim lastRow As Long

    ' 設定對 "Weight_Analysis" 工作表的引用
    Set ws = Worksheets("Weight_Analysis")

    ' 找到第 B 列的最後一行
    lastRow = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row

    ' 返回下一行的行號
    GetNextRowInColumnB = lastRow + 1
End Function
Function GetPartOfString(fullString As String, partIndex As Integer, Optional splitLogic As String = "-") As String
    Dim splitString As Variant
    
    ' 使用 Split 函數按指定分隔符分割字符串
    splitString = Split(fullString, splitLogic)
    
    ' 檢查 partIndex 是否有效（大於 0 且不超過分割後陣列的長度）
    If partIndex > 0 And partIndex <= UBound(splitString) + 1 Then
        GetPartOfString = splitString(partIndex - 1) ' 索引從 1 開始，陣列從 0 開始，所以要減 1
    Else
        GetPartOfString = "N/A" ' 如果索引無效，返回 "N/A"
    End If
End Function


Function CalculatePipeWeight(Pipe_Dn_inch As Double, Pipe_Weight_thickness_mm As Double) As Double
    Dim pi As Double
    pi = 4 * Atn(1)
    ' 計算公式
    CalculatePipeWeight = Round(((Pipe_Dn_inch - Pipe_Weight_thickness_mm) * pi / 1000 * 1 * Pipe_Weight_thickness_mm * 7.85), 2)
End Function
Function GetLookupValue(value As Variant) As Variant
    ' ----------------------------------------------------------------------------------------
    ' |                             函數 GetLookupValue 功能描述                             |
    ' | ------------------------------------------------------------------------------------- |
    ' | - 將傳入的值轉換為字符串。                                                           |
    ' | - 檢查字符串是否包含小數點。                                                         |
    ' | - 如果包含小數點，則檢查是否已經有單引號，如果沒有，則在前面添加單引號。              |
    ' | - 如果不包含小數點，則移除所有非數字字符，並嘗試將結果轉換為整數。                   |
    ' | - 如果結果字符串為空，則返回 0 或一個預設的默認值。                                  |
    ' | - 適用於處理可能為數字或特殊格式字符串（如日期）的情況。                             |
    ' ----------------------------------------------------------------------------------------

    ' 將值轉換為字符串
    Dim strValue As String
    strValue = CStr(value)

    ' 檢查字符串是否包含 "/"
    If InStr(1, strValue, "/") > 0 Then
        ' 包含 "/", 分割字符串
        Dim splitValues() As String
        splitValues = Split(strValue, "/")
        
        ' 計算 A/B
        If UBound(splitValues) = 1 Then
            Dim A As Double
            Dim B As Double
            
            A = CDbl(splitValues(0))
            B = CDbl(splitValues(1))
            
            ' 確保不除以零
            If B <> 0 Then
                GetLookupValue = A / B
            Else
               Err.Raise vbObjectError + 513, "GetLookupValue Function", "Division by zero error"
            End If
        Else
            Err.Raise vbObjectError + 515, "GetLookupValue Function", "Value error"
        End If
        
    ' 否則，按照原有邏輯處理
    ElseIf InStr(1, strValue, ".") > 0 Then
        ' 如果有小數點，保持為字符串
        If InStr(1, strValue, "'") = 0 Then
            GetLookupValue = "'" & strValue
        Else
            GetLookupValue = strValue
        End If
    Else
        ' 沒有小數點，嘗試去除非數字字符後轉換成整數
        Dim numericValue As String
        numericValue = ""
        Dim i As Integer
        For i = 1 To Len(strValue)
            If IsNumeric(Mid(strValue, i, 1)) Then
                numericValue = numericValue & Mid(strValue, i, 1)
            End If
        Next i

        If Len(numericValue) > 0 Then
            GetLookupValue = CInt(numericValue)
        Else
            GetLookupValue = 0 ' 或設置一個合理的默認值
        End If
    End If
End Function



Function CalculatePipeDetails(PipeSize As Variant, PipeThickness As Variant) As Collection
' ------------------------------------------------------------------------------------------------------------------
' |                                                 CalculatePipeDetails 函數詳解                                   |
' | --------------------------------------------------------------------------------------------------------------- |
' | 設定對 "Pipe_Table" 工作表的引用:                                                                               |
' | 此函數首先設定對 "Pipe_Table" 工作表的引用，這是後續查找操作的數據來源。                                        |
' | 使用 GetLookupValue 獲取查找值:                                                                                 |
' | 調用 GetLookupValue 函數，傳入 Pipe_Size（"10"）作為參數。                                                      |
' | 函數檢查 Pipe_Size 是否含小數點。在這個例子中，它是整數 "10"，所以將非數字字符移除，最終得到整數 10 作為查找值。|
' | 獲取管道直徑（英寸）:                                                                                           |
' | 使用 Excel 的 VLOOKUP 函數，以前面獲得的查找值（10）在 "Pipe_Table" 工作表的範圍 "B:R" 中尋找對應的直徑（英寸）。|
' | 找到 Pipe_Thickness 的列位置:                                                                                   |
' | 使用 Excel 的 MATCH 函數在 "Pipe_Table" 工作表的 "B3:R3" 範圍中尋找修改後的 Pipe_Thickness（"40S"）的列位置。   |
' | 獲取厚度（毫米）:                                                                                               |
' | 再次使用 VLOOKUP 函數，以同樣的查找值（10）和剛剛找到的列位置在 "Pipe_Table" 工作表中獲取對應的厚度（毫米）。   |
' | 計算管道每米的重量:                                                                                             |
' | 調用 CalculatePipeWeight 函數，傳入管道的直徑（英寸）和厚度（毫米）。這個函數根據公式計算出管道的每米重量。     |
' | 將計算結果添加到集合:                                                                                           |
' | 管道的直徑（英寸）、厚度（毫米）和每米重量被添加到一個新的集合 PipeDetails 中。這個集合會用專門的鍵來標記每個值，如 "DiameterInch"、"PipeThickness" 和 "PerWeight"。|
' | 返回管道細節集合:                                                                                               |
' | 最後，CalculatePipeDetails 函數將包含了管道細節的 PipeDetails 集合返回給 AddPipeEntry 子程序。                  |
' ------------------------------------------------------------------------------------------------------------------|

    
    

    ' 初始化一個新的集合來存儲管道的細節
    Dim PipeDetails As New Collection

    ' 宣告變數用於存儲計算結果
    Dim PipeDiameterInch As Double
    Dim PipeThicknessColumn As Long
    Dim PipeThickness_mm As Double
    Dim TotalWeight As Double
    Dim LookupValue As Variant
    
    ' 確定有沒有漏網之魚 "B" 一起進來
     If InStr(1, PipeSize, "B") > 0 Then
        PipeSize = Replace(PipeSize, "B", "")
    End If
    
    ' 設置工作表引用，"Pipe_Table" 存儲管道尺寸和重量的數據
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    
    ' 使用 GetLookupValue 函數獲取查找值
    LookupValue = GetLookupValue(PipeSize)

    ' 使用 VLOOKUP 函數根據查找值獲取管道的直徑（英寸）
    PipeDiameterInch = ws_Pipe_Table.Application.WorksheetFunction.VLookup(LookupValue, ws_Pipe_Table.Range("B:R"), 2, False)

    ' 使用 MATCH 函數找到 Pipe_Thickness 在工作表中的列位置
    PipeThicknessColumn = ws_Pipe_Table.Application.WorksheetFunction.Match(PipeThickness, ws_Pipe_Table.Range("B3:R3"), 0)

    ' 再次使用 VLOOKUP 函數獲取對應的厚度（毫米）
    PipeThickness_mm = ws_Pipe_Table.Application.WorksheetFunction.VLookup(LookupValue, ws_Pipe_Table.Range("B:R"), PipeThicknessColumn, False)

    ' 調用 CalculatePipeWeight 函數計算管道每米的重量
    TotalWeight = CalculatePipeWeight(CDbl(PipeDiameterInch), CDbl(PipeThickness_mm))

    ' 將計算出的直徑、厚度和每米重量添加到集合中
    PipeDetails.Add PipeDiameterInch, "DiameterInch"
    PipeDetails.Add PipeThickness_mm, "PipeThickness"
    PipeDetails.Add TotalWeight, "PerWeight"

    ' 返回包含管道細節的集合
    Set CalculatePipeDetails = PipeDetails
End Function



Function ExtractParts(fourthString As String) As Variant
    
'此函數負責修剪出 一個字串 含有"()"的 並切割成0或者1
'例如 : A(S) 則 needvalue(0) = "A" needValue(1) = (S)
'needValue = ExtractParts("A(S)")
    Dim openParenPos As Integer
    openParenPos = InStr(fourthString, "(")
    
    If openParenPos > 0 Then
        Dim partBeforeParen As String
        Dim partWithParen As String

        partBeforeParen = Left(fourthString, openParenPos - 1)
        partWithParen = Mid(fourthString, openParenPos)

        ExtractParts = Array(partBeforeParen, partWithParen)
    Else
        ExtractParts = Array(fourthString, "")
    End If
End Function
Function CalculateAngleDetail(Angle_A As Variant, Angle_B As Variant, Thickness As Variant) As Double
    ' Const density As Double = 7.85 ' 鋼鐵的密度，單位: kg/dm3
    ' Dim singleWeight As Double
    ' Dim A As Double, B As Double, t As Double

    ' ' 嘗試將參數轉換為 Double 類型
    ' On Error Resume Next
    ' A = CDbl(Angle_A)
    ' B = CDbl(Angle_B)
    ' t = CDbl(Thickness)
    ' If Err.Number <> 0 Then
        ' CalculateAngleDetail = 0 ' 如果轉換失敗，返回 0
        ' Exit Function
    ' End If
    ' On Error GoTo 0

    ' ' 確保 t 的值適合進行計算
    ' If t <= 0 Then
        ' CalculateAngleDetail = 0 ' 如果 t 小於或等於 0，返回 0
        ' Exit Function
    ' End If

    ' ' 計算單重
    ' singleWeight = (((A * t) + (B * t) - (t * t)) * density) / 1000
    
    ' ' 返回計算結果
    ' CalculateAngleDetail = singleWeight
End Function

Sub AddPlateEntry(PlateType As String, PipeSize As Variant)
    '負責運算M42的板子
    
    Dim ws_M42 As Worksheet
    Dim col_type As Integer
    Dim Plate_Size As Double
    Dim Plate_Thickness As Double
    Dim Weight_calculator As Double
    Dim Plate_Name As String
    Dim RequireDrilling As Boolean
    Dim ws As Worksheet
    Dim i As Long

    ' 設定對特定工作表的引用
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")

    ' 找到列 B 的最後一行，並為新數據準備下一行
    i = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row + 1

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
        Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 10, False)
    Else
        ' 若PipeSize為數字
        PipeSize = GetLookupValue(PipeSize)
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), col_type, False)
        Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 11, False)
    End If
    Weight_calculator = Plate_Size / 1000 * Plate_Size / 1000 * Plate_Thickness * 7.85

    ' 確定Plate名稱
    Plate_Name = "Plate_" & PlateType & IIf(RequireDrilling, "_需鑽孔", "_不需鑽孔")

    
    MainAddPlate Plate_Size, Plate_Size, Plate_Thickness, Plate_Name
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


Sub AddSteelSectionEntry(SectionType As String, Section_Dim As String, Total_Length As Double, Optional Steel_Qty As Double)
    Dim ws As Worksheet
    Dim i As Long
    Dim SectionWeight As Double
    

    '規整數量
    
    If Steel_Qty = 0 Then
        Steel_Qty = 1
    End If
    
    ' 設定對各鋼種工作表的引用
    Set ws = Worksheets("Weight_Analysis")
    Set ws_HBeam = Worksheets("For_HBeam_Weight_Table")
    Set ws_Channel = Worksheets("For_Channel_Weight_Table")
    Set ws_Angle = Worksheets("For_Angle_Weight_Table")

    ' 參照重量
    Select Case SectionType
        Case "Angle"
            SectionWeight = Application.WorksheetFunction.VLookup(Section_Dim, ws_Angle.Range("C:G"), 5, False)
        Case "Channel"
            SectionWeight = Application.WorksheetFunction.VLookup(Section_Dim, ws_Channel.Range("D:H"), 5, False)
        Case "H Beam"
            SectionWeight = Application.WorksheetFunction.VLookup(Section_Dim, ws_HBeam.Range("E:H"), 4, False)
        Case Else
            SectionWeight = 0 ' IF NO THEN 0
    End Select

    ' 找到第 B 列的下一個空白行
    i = GetNextRowInColumnB()
     With ws
    ' 如果
    If .Cells(i, "A").value <> "" Then
    First_Value_Checking = 1
    Else
    First_Value_Checking = .Cells(i - 1, "B").value + 1
    End If
    ' 填充數據
   
        .Cells(i, "B").value = First_Value_Checking
        .Cells(i, "C").value = SectionType
        .Cells(i, "D").value = Section_Dim
        .Cells(i, "E").value = Total_Length
        .Cells(i, "G").value = "A36/SS400"
        .Cells(i, "H").value = Steel_Qty
        .Cells(i, "I").value = SectionWeight
        .Cells(i, "J").value = .Cells(i, "E").value / 1000 * .Cells(i, "I").value
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value '重量小計
        .Cells(i, "L").value = "M"
        .Cells(i, "M").value = 1
        .Cells(i, "N").value = .Cells(i, "M").value * .Cells(i, "E").value / 1000 * .Cells(i, "H").value
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "素材類"
    End With
End Sub

Sub AddPipeEntry(Pipe_Size As String, Pipe_Thickness As String, Pipe_Length As Double, Material As String)
    Dim i As Integer
    
    
' ----------------------------------------------------------------------------------------
' |                             子程序 AddPipeEntry 執行流程:                             |
' | ------------------------------------------------------------------------------------- |
' | 1. 輸入參數                                                                          |
' |    - Pipe_Size: "10"                                                                 |
' |    - Pipe_Thickness: "SCH.40"                                                        |
' |    - Pipe_Length: 1000                                                               |
' |    - Material: "SUS304"                                                              |
' |                                                                                      |
' | 2. 設定工作表引用                                                                    |
' |    - 引用 "Weight_Analysis" 工作表。                                                  |
' |                                                                                      |
' | 3. 處理管道厚度                                                                      |
' |    - 檢查 Pipe_Thickness 是否為 "STD.WT"。                                           |
' |    - 將 "SCH.40" 轉換為 "40S"。                                                      |
' |                                                                                      |
' | 4. 找到下一個空白行                                                                  |
' |    - 調用 GetNextRowInColumnB 函數找到 "Weight_Analysis" 中第 B 列的下一個空白行。    |
' |                                                                                      |
' | 5. 調用 CalculatePipeDetails 函數                                                    |
' |    - 使用 "10" 和 "40S" 作為參數。                                                    |
' |                                                                                      |
' | 6. CalculatePipeDetails 函數                                                         |
' |    - 設定對 "Pipe_Table" 的引用。                                                    |
' |    - 使用 GetLookupValue 獲取查找值。                                                |
' |    - 使用 VLOOKUP 獲取管道直徑（英寸）。                                             |
' |    - 使用 MATCH 找到 Pipe_Thickness 的列位置。                                        |
' |    - 再次使用 VLOOKUP 獲取厚度（毫米）。                                             |
' |    - 調用 CalculatePipeWeight 計算每米重量。                                         |
' |    - 將直徑、厚度和每米重量添加到集合中。                                            |
' |    - 返回集合給 AddPipeEntry。                                                        |
' |                                                                                      |
' | 7. 填充工作表數據                                                                   |
' |    - 在 "Weight_Analysis" 工作表中填充數據。                                         |
' |    - 包括品名、尺寸、厚度、長度、材質、數量等。                                       |
' |                                                                                      |
' | 8. 結束                                                                              |
' |    - 子程序完成，工作表更新。                                                        |
' ----------------------------------------------------------------------------------------

    
    
    
    Set ws = Worksheets("Weight_Analysis")
    
    '特定標題
    Pipe_ThickNess_For_Title = Pipe_Thickness
   ' 可能性 "SCH.80"
    
    If Pipe_Thickness <> "STD.WT" Then
        Pipe_Thickness = Replace(Pipe_Thickness, "SCH.", "") & "S"
    Else
        Pipe_Thickness = Pipe_Thickness
    End If
    
    
    ' 找到第 B 列的下一個空白行
    i = GetNextRowInColumnB()
     With ws
    ' 演算項次是否為1或其他
    If .Cells(i, "A").value <> "" Then
    First_Value_Checking = 1
    Else
    First_Value_Checking = .Cells(i - 1, "B").value + 1
    End If
'讀取相關管直徑 厚度 每米重量
     
   Set PipeDetails = CalculatePipeDetails(Pipe_Size, Pipe_Thickness)
    
    ' 填充數據
   
                .Cells(i, "B").value = First_Value_Checking
                .Cells(i, "C").value = "Pipe" '品名
                .Cells(i, "D").value = Pipe_Size & """" & "*" & Pipe_ThickNess_For_Title '尺寸厚度
                .Cells(i, "E").value = Pipe_Length '長度
                .Cells(i, "G").value = Material '材值
                .Cells(i, "H").value = 1 '數量
                .Cells(i, "I").value = PipeDetails.Item("PerWeight") '每米重
                .Cells(i, "J").value = .Cells(i, "E").value / 1000 * .Cells(i, "I").value '單重
                .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value '重量小計
                .Cells(i, "L").value = "M"
                .Cells(i, "M").value = 1 '組數
                .Cells(i, "N").value = .Cells(i, "H").value * .Cells(i, "M").value * .Cells(i, "E").value / 1000 '長度小計 組數*數量*長度/1000
                .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
                .Cells(i, "Q").value = "素材類"
    End With
End Sub
'------------------------------------------------------------------------------------------------------





Function GetSectionDetails(PartString_Type As String) As SectionDetails
' 自定義類型 SectionDetails，用於存儲部件的尺寸和類型

' ----------------------------------------------------------------------------------------
' |                             函數 GetSectionDetails 功能描述                          |
' | ------------------------------------------------------------------------------------- |
' | - 根據傳入的 PartString_Type （部件型號字符串）判斷部件的尺寸和類型。                |
' | - 使用 Select Case 結構根據不同的 PartString_Type 案例賦予不同的尺寸和類型。        |
' | - PartString_Type 是從 另外的子程序中讀取的特定部件型號代碼。                        |
' | - 每個 Case 對應一種特定的部件型號，並賦予相應的尺寸和類型。                         |
' | - 函數返回一個自定義類型 SectionDetails，包含了 Size（尺寸）和 Type（類型）。       |
' | - 如果未找到對應的 PartString_Type，將返回一個包含空字符串的 SectionDetails。         |
' | - 此函數可用於基於部件型號快速獲取相關的尺寸和類型資訊。                             |


' ----------------------------------------------------------------------------------------


    
    
    ' 創建一個 SectionDetails 類型的變數來存儲結果
    Dim Details As SectionDetails
    
    ' 根據傳入的 PartString_Type 進行判斷，並賦予相對應的尺寸和類型
    Select Case PartString_Type
        Case "L50"
           Details.Size = "L50*50*6"
           Details.Type = "Angle"
        Case "L65"
           Details.Size = "L65*65*6"
           Details.Type = "Angle"
        Case "L75"
           Details.Size = "L75*75*9"
           Details.Type = "Angle"
        Case "C100"
           Details.Size = "C100*50*5"
           Details.Type = "Channel"
        Case "C125"
           Details.Size = "C125*65*6"
           Details.Type = "Channel"
        Case "C150"
           Details.Size = "C150*75*9"
           Details.Type = "Channel"
        Case "C180"
           Details.Size = "C180*75*7"
           Details.Type = "Channel"
        Case "H150"
           Details.Size = "H150*150*10"
           Details.Type = "H Beam"
        Case "H250"
           Details.Size = "H250*125*6"
           Details.Type = "H Beam"
        ' ... 更多案例可以根據需要添加
        Case Else
            ' 如果沒有匹配的案例，返回一個空的結構
            Details.Size = ""
            Details.Type = ""
    End Select
    
    ' 將包含結果的 Details 結構返回給調用者
    GetSectionDetails = Details
End Function


Sub MainAddPlate(Plate_Size_a As Double, Plate_Size_b As Double, Plate_Thickness As Double, Plate_Name As String, Optional Plate_Material As String)
 ' ----------------------------------------------------------------------------------------
' |                        程序 AddNewMaterial 功能描述                                  |
' | ------------------------------------------------------------------------------------- |
' | - 根據提供的材料尺寸和類型，計算新材料的重量。                                        |
' | - 使用預定義的材料密度，如果沒有指定材料類型，將使用默認材料。                        |
' | - 根據輸入的尺寸計算材料重量，並將計算結果填充到工作表的相應單元格中。                |
' | - 獲取下一個可用行以插入新數據，保持工作表的整潔和組織。                              |
' | - 檢查第一個值是否已存在，以確定是否從1開始編號或繼續序列。                           |
' | - 將計算和輸入的數據填充到工作表的特定列，以便進行重量分析。                          |
' | - 適用板類配分                                                                        |
' ----------------------------------------------------------------------------------------
   
    
    
    Dim Pipeline_Density As Double
    Dim weight As Double
    Dim i As Long
    Dim First_Value_Checking As Long
    Dim ws As Worksheet
    Set ws = Worksheets("Weight_Analysis")
    
   
    If Plate_Material = "" Then
        Plate_Material = "A36/SS400"
    End If
    
    Select Case Plate_Material
        Case "A36/SS400"
            Pipeline_Density = 7.85
        Case "SUS304"
            Pipeline_Density = 7.93
        Case "AS"
            Pipeline_Density = 7.82
    End Select
           

    weight = Plate_Size_a / 1000 * Plate_Size_b / 1000 * Plate_Thickness * Pipeline_Density
    

    i = GetNextRowInColumnB()


    If ws.Cells(i, "A").value <> "" Then
        First_Value_Checking = 1
    Else
        First_Value_Checking = ws.Cells(i - 1, "B").value + 1
    End If


    With ws
        .Cells(i, "B").value = First_Value_Checking
        .Cells(i, "C").value = Plate_Name
        .Cells(i, "D").value = Plate_Thickness
        .Cells(i, "E").value = Plate_Size_a
        .Cells(i, "F").value = Plate_Size_b
        .Cells(i, "G").value = Plate_Material
        .Cells(i, "H").value = 1
        .Cells(i, "J").value = weight
        .Cells(i, "K").value = weight
        .Cells(i, "L").value = "PC"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = 1
        .Cells(i, "P").value = weight
        .Cells(i, "Q").value = "鋼板類"
    End With
End Sub
