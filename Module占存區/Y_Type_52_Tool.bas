Attribute VB_Name = "Y_Type_52_Tool"
Function Type52_GetPipeSize(ByVal fullstring As String) As String
    Dim Second_Part_needValue_list As Variant
    PrintStepCalculator "[Type52_GetPipeSize] - �}��Ū���޽u�ؤo�P�O"
    If InStr(GetPartOfString(fullstring, 2), "(") > 0 Then
        PrintStepCalculator "[Type52_GetPipeSize] - �o�{�̭��æ�Pad�r�� �����"
        Second_Part_needValue_list = ExtractParts(GetPartOfString(fullstring, 2))
        Type52_GetPipeSize = Second_Part_needValue_list(0)
    Else
        Type52_GetPipeSize = GetPartOfString(fullstring, 2)
    End If
End Function

Function Type52_GetPadSymbol(ByVal fullstring As String) As String
    Dim Second_Part_needValue_list As Variant

    If InStr(GetPartOfString(fullstring, 2), "(") > 0 Then
        Second_Part_needValue_list = ExtractParts(GetPartOfString(fullstring, 2))
        Type52_GetPadSymbol = Second_Part_needValue_list(1)
    Else
        Type52_GetPadSymbol = "N/A"
    End If
End Function
Function Type52_GetMaterialValue(ByVal fullstring As String) As String
    Dim Third_Part_value As String
    Dim Third_Part_needValue_list As Variant

    Third_Part_value = GetPartOfString(fullstring, 3)
    If Third_Part_value = " " Then
        Type52_GetMaterialValue = "A36/SS400"
    Else
        If InStr(Third_Part_value, "(") > 0 Then

            Third_Part_needValue_list = ExtractParts(Third_Part_value)
            Select Case Third_Part_needValue_list(1)
                Case "(A)"
                    Type52_GetMaterialValue = "AS"
                Case "(S)"
                    Type52_GetMaterialValue = "SUS304"
                Case " "
                    Type52_GetMaterialValue = "A36/SS400"
            End Select
        Else
            Type52_GetMaterialValue = "A36/SS400"
        End If
    End If
End Function
Function Type52_GetInsulationValue(ByVal fullstring As String) As Integer
    Dim Third_Part_value As String
    Dim Third_Part_needValue_list As Variant

    Third_Part_value = GetPartOfString(fullstring, 3)
    If Third_Part_value = " " Then
        GetInsulationValue = 75
    Else
        If InStr(Third_Part_value, "(") > 0 Then

            Third_Part_needValue_list = ExtractParts(Third_Part_value)
            Select Case Third_Part_needValue_list(0)
                Case "A"
                    Type52_GetInsulationValue = 80
                Case "B"
                    Type52_GetInsulationValue = 130
                Case "C"
                    Type52_GetInsulationValue = 180
                Case " "
                    Type52_GetInsulationValue = 75
            End Select
        Else

            Select Case Third_Part_value
                Case "A"
                    Type52_GetInsulationValue = 80
                Case "B"
                    Type52_GetInsulationValue = 130
                Case "C"
                    Type52_GetInsulationValue = 180
                Case " "
                    Type52_GetInsulationValue = 75
            End Select
        End If
    End If
End Function
Function Type52_GetTable66_A(PipeSize) As Variant
    Select Case PipeSize
        Case 0.5 To 8
            Type52_GetTable66_A = 100
        Case 10 To 14
            Type52_GetTable66_A = 130
        Case 16 To 20
            Type52_GetTable66_A = 250
        Case 22 To 40
            Type52_GetTable66_A = 300
    End Select
End Function

Function Type52_GetTable66_B(PipeSize) As Variant
    Select Case PipeSize
        Case 0.5 To 8
            Type52_GetTable66_B = 0
        Case 10 To 14
            Type52_GetTable66_B = 9
        Case 16 To 40
            Type52_GetTable66_B = 12
    End Select
End Function

Function Type52_GetTable66_C(PipeSize) As String
    PrintStepCalculator "[Type52_GetTable66_C] - �}��D-80���PŪ'C'��"
    ' �̫��ˬd �i��A�B�z
    PipeSize = CleanPipeSize(PipeSize)
    Select Case PipeSize
        Case 0.5 To 8
            Type52_GetTable66_C = "200*100*5.5" ' Hbeam
        Case 10 To 14
            Type52_GetTable66_C = "200*200*8"
        Case 16 To 40
            Type52_GetTable66_C = "FB12"
    End Select
End Function

Function Type_GetTable66_D(PipeSize As Variant) As Variant
    ' �M��PipeSize�����D�Ʀr�r�šA�H�K���T����
    PipeSize = CleanPipeSize(PipeSize)

    ' �ھ��ഫ�᪺�Ʀr�j�p��ܹ�������^��
    Select Case PipeSize
        Case 0.5 To 2.5
            Type_GetTable66_D = 150
        Case 3 To 8
            Type_GetTable66_D = 250
        Case 10 To 40
            Type_GetTable66_D = 250
        Case Else
            Type_GetTable66_D = "Error: Invalid size"  ' �K�[���~�B�z�H�����L�Ŀ�J
    End Select
End Function




Function Type_GetTable66_E(PipeSize) As Variant
    Select Case PipeSize
        Case 1.5 To 2
            Type_GetTable66_E = 0
        Case 2 To 40
            Type_GetTable66_E = 50
    End Select
End Function
Function Type52_GetTable66_HopesPlate(PipeSize) As Variant
    
    Select Case PipeSize
        Case 10
            Type52_GetTable66_HopesPlate = 68.25
        Case 12
            Type52_GetTable66_HopesPlate = 76.2
         Case 14
            Type52_GetTable66_HopesPlate = 88.9
        Case 16
            Type52_GetTable66_HopesPlate = 101.6
        Case 18
            Type52_GetTable66_HopesPlate = 114.3
        Case 20
            Type52_GetTable66_HopesPlate = 127
        Case 22 To 40
            Type52_GetTable66_HopesPlate = 152.4
    End Select

End Function
