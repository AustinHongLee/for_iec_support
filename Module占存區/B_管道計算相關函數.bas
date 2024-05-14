Attribute VB_Name = "B_管道計算相關函數"
Function CalculatePipeWeight(Pipe_Dn_inch As Double, Pipe_Weight_thickness_mm As Double) As Double
    Dim pi As Double
    pi = 4 * Atn(1)
    ' 計算公式
    CalculatePipeWeight = Round(((Pipe_Dn_inch - Pipe_Weight_thickness_mm) * pi / 1000 * 1 * Pipe_Weight_thickness_mm * 7.85), 2)
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


Sub AddPipeEntry(Pipe_Size As String, Pipe_Thickness As String, Pipe_Length As Double, material As String)
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
    If Pipe_Thickness = "STD" Then
        Pipe_Thickness = "STD.WT"
    ElseIf Pipe_Thickness <> "STD.WT" Then
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
                .Cells(i, "G").value = material '材值
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
