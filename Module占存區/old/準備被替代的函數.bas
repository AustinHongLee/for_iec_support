Attribute VB_Name = "準備被替代的函數"
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
