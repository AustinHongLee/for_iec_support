Attribute VB_Name = "�ǳƳQ���N�����"
Function GetFirstPartOfString(fullString As String) As String
    Dim splitString As Variant
    Dim firstPart As String
    
    splitString = Split(fullString, "-") ' �ϥ�"-"�@�����j�ŨӤ��Φr�Ŧ�
    
    If UBound(splitString) >= 1 Then ' �T�O�����������j��
        firstPart = splitString(0) ' ������Ϋ�Ʋժ��Ĥ@�Ӥ����A�Y�Ĥ@��"-"���e����
    Else
        firstPart = "N/A" ' �p�G�S�����������j�šA�]�m�@�ӿ��~�������q�{��
    End If

    GetFirstPartOfString = firstPart
End Function


Function GetSecondPartOfString(fullString As String) As String
    Dim splitString As Variant
    Dim secondPart As String
    
    splitString = Split(fullString, "-") ' �ϥ�"-"�@�����j�ŨӤ��Φr�Ŧ�
    
    If UBound(splitString) >= 1 Then ' �T�O�����������j��
        secondPart = splitString(1) ' ������Ϋ�Ʋժ��ĤG�Ӥ����A�Y�Ĥ@�өM�ĤG��"-"��������
    Else
        secondPart = "N/A" ' �p�G�S�����������j�šA�]�m�@�ӿ��~�������q�{��
    End If

    GetSecondPartOfString = secondPart
End Function

Function GetThirdPartOfString(fullString As String) As String
    Dim splitString As Variant
    splitString = Split(fullString, "-") ' �ϥ� "-" �Ӥ��Φr�Ŧ�

    If UBound(splitString) >= 2 Then ' �T�O�����������j��
        GetThirdPartOfString = splitString(2) ' �ĤT����
    Else
        GetThirdPartOfString = "N/A" ' �p�G�S�����������j�šA�]�m�@�ӿ��~�������q�{��
    End If
End Function
Function GetFourthPartOfString(fullString As String) As String
    Dim splitString As Variant
    splitString = Split(fullString, "-") ' �ϥ� "-" �Ӥ��Φr�Ŧ�

    If UBound(splitString) >= 3 Then ' �T�O�����������j��
        GetFourthPartOfString = splitString(3) ' �ĥ|����
    Else
        GetFourthPartOfString = "N/A" ' �p�G�S�����������j�šA�]�m�@�ӿ��~�������q�{��
    End If
End Function
Function GetFifthPartOfString(fullString As String) As String
    Dim splitString As Variant
    splitString = Split(fullString, "-") ' �ϥ� "-" �Ӥ��Φr�Ŧ�

    If UBound(splitString) >= 4 Then ' �T�O�����������j��
        GetFifthPartOfString = splitString(4) ' �Ĥ�����
    Else
        GetFifthPartOfString = "N/A" ' �p�G�S�����������j�šA�]�m�@�ӿ��~�������q�{��
    End If
End Function

Function IsFourthPartAvailable(ByVal fullString As String) As Boolean
    Dim parts() As String
    parts = Split(fullString, "-") ' �ϥγs�r�Ť��j�r�Ŧ�
    
    ' �p�G���Ϋ᪺�Ʋժ��פj��ε��� 4�A�h��ܦs�b�ĥ|����
    If UBound(parts) >= 3 Then
        IsFourthPartAvailable = True
    Else
        IsFourthPartAvailable = False
    End If
End Function

Function CalculateAngleDetail(Angle_A As Variant, Angle_B As Variant, Thickness As Variant) As Double
    ' Const density As Double = 7.85 ' ���K���K�סA���: kg/dm3
    ' Dim singleWeight As Double
    ' Dim A As Double, B As Double, t As Double

    ' ' ���ձN�Ѽ��ഫ�� Double ����
    ' On Error Resume Next
    ' A = CDbl(Angle_A)
    ' B = CDbl(Angle_B)
    ' t = CDbl(Thickness)
    ' If Err.Number <> 0 Then
        ' CalculateAngleDetail = 0 ' �p�G�ഫ���ѡA��^ 0
        ' Exit Function
    ' End If
    ' On Error GoTo 0

    ' ' �T�O t ���ȾA�X�i��p��
    ' If t <= 0 Then
        ' CalculateAngleDetail = 0 ' �p�G t �p��ε��� 0�A��^ 0
        ' Exit Function
    ' End If

    ' ' �p��歫
    ' singleWeight = (((A * t) + (B * t) - (t * t)) * density) / 1000
    
    ' ' ��^�p�⵲�G
    ' CalculateAngleDetail = singleWeight
End Function
