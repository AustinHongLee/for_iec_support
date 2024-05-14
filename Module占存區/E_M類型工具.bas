Attribute VB_Name = "E_M類型工具"
Type PipeDimensions
    W As String
    L As String
End Type

Function M_47(ByVal PipeSize As String) As PipeDimensions
    Dim dimensions As PipeDimensions
    Dim line_size As Variant
    
    line_size = GetLookupValue(PipeSize)
    
    Select Case line_size
        Case 0.75
            dimensions.W = "50"
            dimensions.L = "83"
        Case 1
            dimensions.W = "50"
            dimensions.L = "105"
        Case 1.5
            dimensions.W = "50"
            dimensions.L = "152"
        Case 2
            dimensions.W = "50"
            dimensions.L = "190"
        Case 2.5
            dimensions.W = "50"
            dimensions.L = "229"
        Case 3
            dimensions.W = "50"
            dimensions.L = "279"
        Case 4
            dimensions.W = "50"
            dimensions.L = "359"
        Case 5
            dimensions.W = "50"
            dimensions.L = "444"
        Case 6
            dimensions.W = "50"
            dimensions.L = "529"
        Case 8
            dimensions.W = "80"
            dimensions.L = "688"
        Case 10
            dimensions.W = "80"
            dimensions.L = "858"
        Case 12
            dimensions.W = "80"
            dimensions.L = "1017"
        Case 14
            dimensions.W = "80"
            dimensions.L = "1117"
        Case 16
            dimensions.W = "80"
            dimensions.L = "1277"
        Case 18
            dimensions.W = "80"
            dimensions.L = "1436"
        Case 20
            dimensions.W = "90"
            dimensions.L = "1596"
        Case 24
            dimensions.W = "90"
            dimensions.L = "1915"
        Case 26
            dimensions.W = "90"
            dimensions.L = "2074"
        Case 28
            dimensions.W = "90"
            dimensions.L = "2234"
        Case 30
            dimensions.W = "90"
            dimensions.L = "2393"
        Case 32
            dimensions.W = "90"
            dimensions.L = "2553"
        Case 34
            dimensions.W = "110"
            dimensions.L = "2712"
        Case 36
            dimensions.W = "110"
            dimensions.L = "2872"
        Case 40
            dimensions.W = "110"
            dimensions.L = "3191"
        Case 42
            dimensions.W = "110"
            dimensions.L = "3350"
        Case Else
            dimensions.W = "Not found"
            dimensions.L = "Not found"
    End Select
    
    M_47 = dimensions
End Function

Sub TestM_47()
    Dim result As PipeDimensions
    Dim PipeSize As String
    
    PipeSize = "10B"
    result = M_47(PipeSize)
    
    MsgBox "W: " & result.W & ", L: " & result.L
End Sub

