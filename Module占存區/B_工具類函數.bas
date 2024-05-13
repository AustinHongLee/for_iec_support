Attribute VB_Name = "B_工具類函數"
' Lenguage: Visual Basic
' coding = utf-8
' 1.GetLookupValue
' 2.GetPartOfString
' 3.CountCharacter
' 4.GetNextRowInColumnB
' 各種字符串分割函數（GetFirstPartOfString, GetSecondPartOfString, 等等）


Function GetLookupValue(value As Variant) As Variant
    ' ----------------------------------------------------------------------------------------
    ' |                             函數 GetLookupValue 功能描述
    ' | --------------------------------------------------------------------------------------
    ' | - 將傳入的值轉換為字符串。
    ' | - 檢查字符串是否包含小數點。
    ' | - 如果包含小數點，則檢查是否已經有單引號，如果沒有，則在前面添加單引號。
    ' | - 如果不包含小數點，則移除所有非數字字符，並嘗試將結果轉換為整數。
    ' | - 如果結果字符串為空，則返回 0 或一個預設的默認值。
    ' | - 適用於處理可能為數字或特殊格式字符串（如日期）的情況。
    ' ----------------------------------------------------------------------------------------

    ' 將值轉換為字符串
    Dim strValue As String
    strValue = CStr(value)

   If InStr(1, strValue, "/") > 0 Then
        Dim splitValues() As String
        splitValues = Split(strValue, "/")
        
        If UBound(splitValues) = 1 Then
            Dim A As Double, B As Double, A_sp As Variant
            A_sp = Split(splitValues(0), " ")
            
            If UBound(A_sp) = 1 Then
                A = CDbl(A_sp(1))
                B = CDbl(splitValues(1))
                If B <> 0 Then
                    GetLookupValue = CDbl(A_sp(0)) + A / B
                Else
                   Err.Raise vbObjectError + 513, "GetLookupValue Function", "Division by zero error"
                End If
            ElseIf UBound(A_sp) = 0 Then
                A = CDbl(A_sp(0))
                B = CDbl(splitValues(1))
                If B <> 0 Then
                    GetLookupValue = A / B
                Else
                   Err.Raise vbObjectError + 513, "GetLookupValue Function", "Division by zero error"
                End If
            Else
                Err.Raise vbObjectError + 515, "GetLookupValue Function", "Input format error"
            End If
        Else
            Err.Raise vbObjectError + 515, "GetLookupValue Function", "Value error"
        End If
        
    ElseIf InStr(1, strValue, ".") > 0 Then
        If InStr(1, strValue, "'") = 0 Then
            GetLookupValue = "'" & strValue
        Else
            GetLookupValue = strValue
        End If
    Else
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
            GetLookupValue = 0
        End If
    End If
End Function

Function GetPartOfString(fullstring As String, partIndex As Integer, Optional splitLogic As String = "-") As String
    Dim splitString As Variant
    PrintStepCalculator "[Tool_Function-GetPartOfString] - 開始執行切割區字元函數"
    PrintStepCalculator "[Tool_Function-GetPartOfString] - 目前的fullString是 : " & fullstring & "目前的區域數是 : " & partIndex & " 憑切割字元為 : " & splitLogic
    ' 使用 Split 函數按指定分隔符分割字符串
    splitString = Split(fullstring, splitLogic)
    
    ' 檢查 partIndex 是否有效（大於 0 且不超過分割後陣列的長度）
    If partIndex > 0 And partIndex <= UBound(splitString) + 1 Then
        GetPartOfString = splitString(partIndex - 1) ' 索引從 1 開始，陣列從 0 開始，所以要減 1
    Else
        GetPartOfString = "N/A" ' 如果索引無效，返回 "N/A"
    End If
End Function


Function CountCharacter(ByVal text As String, ByVal character As String) As Integer
    Dim count As Integer
    Dim i As Integer
    
    For i = 1 To Len(text)
        If Mid(text, i, 1) = character Then
            count = count + 1
        End If
    Next i
    
    CountCharacter = count
End Function

Function GetNextRowInColumnB() As Long
    Dim ws As Worksheet
    Dim lastRow As Long

    ' 設定對 "Weight_Analysis" 工作表的引用
    Set ws = Worksheets("Weight_Analysis")

    ' 找到第 B 列的最後一行
    lastRow = ws.Cells(ws.Rows.count, "B").End(xlUp).Row

    ' 返回下一行的行號
    GetNextRowInColumnB = lastRow + 1
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
Function CleanPipeSize(PipeSize As Variant) As String
    ' 用來進出管線計算用
    ' 移除字符"B"和引號，如果存在
    If InStr(PipeSize, "B") > 0 Then
        PipeSize = Replace(PipeSize, "B", "")
    End If
    ' 從GetLookupValue獲取實際的值
    PipeSize = GetLookupValue(PipeSize)
    If InStr(PipeSize, "'") > 0 Then
        PipeSize = Replace(PipeSize, "'", "")
    End If
    CleanPipeSize = PipeSize

End Function
