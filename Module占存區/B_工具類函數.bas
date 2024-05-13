Attribute VB_Name = "B_�u�������"
' Lenguage: Visual Basic
' coding = utf-8
' 1.GetLookupValue
' 2.GetPartOfString
' 3.CountCharacter
' 4.GetNextRowInColumnB
' �U�ئr�Ŧ���Ψ�ơ]GetFirstPartOfString, GetSecondPartOfString, �����^


Function GetLookupValue(value As Variant) As Variant
    ' ----------------------------------------------------------------------------------------
    ' |                             ��� GetLookupValue �\��y�z
    ' | --------------------------------------------------------------------------------------
    ' | - �N�ǤJ�����ഫ���r�Ŧ�C
    ' | - �ˬd�r�Ŧ�O�_�]�t�p���I�C
    ' | - �p�G�]�t�p���I�A�h�ˬd�O�_�w�g����޸��A�p�G�S���A�h�b�e���K�[��޸��C
    ' | - �p�G���]�t�p���I�A�h�����Ҧ��D�Ʀr�r�šA�ù��ձN���G�ഫ����ơC
    ' | - �p�G���G�r�Ŧꬰ�šA�h��^ 0 �Τ@�ӹw�]���q�{�ȡC
    ' | - �A�Ω�B�z�i�ର�Ʀr�ίS��榡�r�Ŧ�]�p����^�����p�C
    ' ----------------------------------------------------------------------------------------

    ' �N���ഫ���r�Ŧ�
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
    PrintStepCalculator "[Tool_Function-GetPartOfString] - �}�l������ΰϦr�����"
    PrintStepCalculator "[Tool_Function-GetPartOfString] - �ثe��fullString�O : " & fullstring & "�ثe���ϰ�ƬO : " & partIndex & " �̤��Φr���� : " & splitLogic
    ' �ϥ� Split ��ƫ����w���j�Ť��Φr�Ŧ�
    splitString = Split(fullstring, splitLogic)
    
    ' �ˬd partIndex �O�_���ġ]�j�� 0 �B���W�L���Ϋ�}�C�����ס^
    If partIndex > 0 And partIndex <= UBound(splitString) + 1 Then
        GetPartOfString = splitString(partIndex - 1) ' ���ޱq 1 �}�l�A�}�C�q 0 �}�l�A�ҥH�n�� 1
    Else
        GetPartOfString = "N/A" ' �p�G���޵L�ġA��^ "N/A"
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

    ' �]�w�� "Weight_Analysis" �u�@���ޥ�
    Set ws = Worksheets("Weight_Analysis")

    ' ���� B �C���̫�@��
    lastRow = ws.Cells(ws.Rows.count, "B").End(xlUp).Row

    ' ��^�U�@�檺�渹
    GetNextRowInColumnB = lastRow + 1
End Function


Function ExtractParts(fourthString As String) As Variant
    
'����ƭt�d�װťX �@�Ӧr�� �t��"()"�� �ä��Φ�0�Ϊ�1
'�Ҧp : A(S) �h needvalue(0) = "A" needValue(1) = (S)
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
    ' �ΨӶi�X�޽u�p���
    ' �����r��"B"�M�޸��A�p�G�s�b
    If InStr(PipeSize, "B") > 0 Then
        PipeSize = Replace(PipeSize, "B", "")
    End If
    ' �qGetLookupValue�����ڪ���
    PipeSize = GetLookupValue(PipeSize)
    If InStr(PipeSize, "'") > 0 Then
        PipeSize = Replace(PipeSize, "'", "")
    End If
    CleanPipeSize = PipeSize

End Function
