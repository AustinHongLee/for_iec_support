Attribute VB_Name = "鋼材處理"
' 自定義類型 SectionDetails，用於存儲部件的尺寸和類型
Type SectionDetails
    Size As String
    Type As String
End Type

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

