Attribute VB_Name = "Module1"
' �۩w�q���� SectionDetails�A�Ω�s�x���󪺤ؤo�M����
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
    ' �аO�B��ɶ�
    ws.Cells(4, "F") = Now()
    ' �M���Ҧ����e
    ws_M42.Cells.ClearContents
    
    ' �˴��O�_����T�Y�L�h�l�[

    ' �w�q�C���D�M�������C��
    headers = Array(Array("A", "�ޤ伵����"), Array("B", "����"), Array("C", "�~�W"), Array("D", "�ؤo/�p��"), Array("E", "����"), Array("F", "�e��"), Array("G", "����"), Array("H", "�ƶq"), Array("I", "�C�̭�"), Array("J", "�歫"), Array("K", "���q�p�p"), Array("L", "���"), Array("M", "�ռ�"), Array("N", "���פp�p"), Array("O", "�ƶq�p�p"), Array("P", "���q�X�p"), Array("Q", "�ݩ�"))

    ' �M���Ʋըó]�m�C���D
       With ws_Weight_Analysis
    For ii = LBound(headers) To UBound(headers)
        If .Cells(1, headers(ii)(0)).value <> headers(ii)(1) Then
            .Cells(1, headers(ii)(0)).value = headers(ii)(1)
        End If
    Next ii
        End With
    
    ' �ק�F��M�̫�@�C����k
    Row_max = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    ' �D�B�z�`��
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
    If Err.Number = vbObjectError + 513 Then ' 513���~�O���ӭȱo�ĤG�q���ͫD�޿�W�����~
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error02"
    ElseIf Err.Number = vbObjectError + 514 Then '(���~�B�z)[Fig�����Ϊ�M42] �ˬd�O�_���ǰt���A�çPŪ�O�_���Ʀr�Ϊ̤��� @ 514
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error03"
    Else
        ws_Weight_Analysis.Cells(Last_row_main_Title, "B") = "Error"
    End If
    Resume ContinueLoop
End Sub


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

Function GetNextRowInColumnB() As Long
    Dim ws As Worksheet
    Dim lastRow As Long

    ' �]�w�� "Weight_Analysis" �u�@���ޥ�
    Set ws = Worksheets("Weight_Analysis")

    ' ���� B �C���̫�@��
    lastRow = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row

    ' ��^�U�@�檺�渹
    GetNextRowInColumnB = lastRow + 1
End Function
Function GetPartOfString(fullString As String, partIndex As Integer, Optional splitLogic As String = "-") As String
    Dim splitString As Variant
    
    ' �ϥ� Split ��ƫ����w���j�Ť��Φr�Ŧ�
    splitString = Split(fullString, splitLogic)
    
    ' �ˬd partIndex �O�_���ġ]�j�� 0 �B���W�L���Ϋ�}�C�����ס^
    If partIndex > 0 And partIndex <= UBound(splitString) + 1 Then
        GetPartOfString = splitString(partIndex - 1) ' ���ޱq 1 �}�l�A�}�C�q 0 �}�l�A�ҥH�n�� 1
    Else
        GetPartOfString = "N/A" ' �p�G���޵L�ġA��^ "N/A"
    End If
End Function


Function CalculatePipeWeight(Pipe_Dn_inch As Double, Pipe_Weight_thickness_mm As Double) As Double
    Dim pi As Double
    pi = 4 * Atn(1)
    ' �p�⤽��
    CalculatePipeWeight = Round(((Pipe_Dn_inch - Pipe_Weight_thickness_mm) * pi / 1000 * 1 * Pipe_Weight_thickness_mm * 7.85), 2)
End Function
Function GetLookupValue(value As Variant) As Variant
    ' ----------------------------------------------------------------------------------------
    ' |                             ��� GetLookupValue �\��y�z                             |
    ' | ------------------------------------------------------------------------------------- |
    ' | - �N�ǤJ�����ഫ���r�Ŧ�C                                                           |
    ' | - �ˬd�r�Ŧ�O�_�]�t�p���I�C                                                         |
    ' | - �p�G�]�t�p���I�A�h�ˬd�O�_�w�g����޸��A�p�G�S���A�h�b�e���K�[��޸��C              |
    ' | - �p�G���]�t�p���I�A�h�����Ҧ��D�Ʀr�r�šA�ù��ձN���G�ഫ����ơC                   |
    ' | - �p�G���G�r�Ŧꬰ�šA�h��^ 0 �Τ@�ӹw�]���q�{�ȡC                                  |
    ' | - �A�Ω�B�z�i�ର�Ʀr�ίS��榡�r�Ŧ�]�p����^�����p�C                             |
    ' ----------------------------------------------------------------------------------------

    ' �N���ഫ���r�Ŧ�
    Dim strValue As String
    strValue = CStr(value)

    ' �ˬd�r�Ŧ�O�_�]�t "/"
    If InStr(1, strValue, "/") > 0 Then
        ' �]�t "/", ���Φr�Ŧ�
        Dim splitValues() As String
        splitValues = Split(strValue, "/")
        
        ' �p�� A/B
        If UBound(splitValues) = 1 Then
            Dim A As Double
            Dim B As Double
            
            A = CDbl(splitValues(0))
            B = CDbl(splitValues(1))
            
            ' �T�O�����H�s
            If B <> 0 Then
                GetLookupValue = A / B
            Else
               Err.Raise vbObjectError + 513, "GetLookupValue Function", "Division by zero error"
            End If
        Else
            Err.Raise vbObjectError + 515, "GetLookupValue Function", "Value error"
        End If
        
    ' �_�h�A���ӭ즳�޿�B�z
    ElseIf InStr(1, strValue, ".") > 0 Then
        ' �p�G���p���I�A�O�����r�Ŧ�
        If InStr(1, strValue, "'") = 0 Then
            GetLookupValue = "'" & strValue
        Else
            GetLookupValue = strValue
        End If
    Else
        ' �S���p���I�A���եh���D�Ʀr�r�ū��ഫ�����
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
            GetLookupValue = 0 ' �γ]�m�@�ӦX�z���q�{��
        End If
    End If
End Function



Function CalculatePipeDetails(PipeSize As Variant, PipeThickness As Variant) As Collection
' ------------------------------------------------------------------------------------------------------------------
' |                                                 CalculatePipeDetails ��ƸԸ�                                   |
' | --------------------------------------------------------------------------------------------------------------- |
' | �]�w�� "Pipe_Table" �u�@���ޥ�:                                                                               |
' | ����ƭ����]�w�� "Pipe_Table" �u�@���ޥΡA�o�O����d��ާ@���ƾڨӷ��C                                        |
' | �ϥ� GetLookupValue ����d���:                                                                                 |
' | �ե� GetLookupValue ��ơA�ǤJ Pipe_Size�]"10"�^�@���ѼơC                                                      |
' | ����ˬd Pipe_Size �O�_�t�p���I�C�b�o�ӨҤl���A���O��� "10"�A�ҥH�N�D�Ʀr�r�Ų����A�̲ױo���� 10 �@���d��ȡC|
' | ����޹D���|�]�^�o�^:                                                                                           |
' | �ϥ� Excel �� VLOOKUP ��ơA�H�e����o���d��ȡ]10�^�b "Pipe_Table" �u�@���d�� "B:R" ���M����������|�]�^�o�^�C|
' | ��� Pipe_Thickness ���C��m:                                                                                   |
' | �ϥ� Excel �� MATCH ��Ʀb "Pipe_Table" �u�@�� "B3:R3" �d�򤤴M��ק�᪺ Pipe_Thickness�]"40S"�^���C��m�C   |
' | ����p�ס]�@�̡^:                                                                                               |
' | �A���ϥ� VLOOKUP ��ơA�H�P�˪��d��ȡ]10�^�M����쪺�C��m�b "Pipe_Table" �u�@������������p�ס]�@�̡^�C   |
' | �p��޹D�C�̪����q:                                                                                             |
' | �ե� CalculatePipeWeight ��ơA�ǤJ�޹D�����|�]�^�o�^�M�p�ס]�@�̡^�C�o�Ө�Ʈھڤ����p��X�޹D���C�̭��q�C     |
' | �N�p�⵲�G�K�[�춰�X:                                                                                           |
' | �޹D�����|�]�^�o�^�B�p�ס]�@�̡^�M�C�̭��q�Q�K�[��@�ӷs�����X PipeDetails ���C�o�Ӷ��X�|�αM������ӼаO�C�ӭȡA�p "DiameterInch"�B"PipeThickness" �M "PerWeight"�C|
' | ��^�޹D�Ӹ`���X:                                                                                               |
' | �̫�ACalculatePipeDetails ��ƱN�]�t�F�޹D�Ӹ`�� PipeDetails ���X��^�� AddPipeEntry �l�{�ǡC                  |
' ------------------------------------------------------------------------------------------------------------------|

    
    

    ' ��l�Ƥ@�ӷs�����X�Ӧs�x�޹D���Ӹ`
    Dim PipeDetails As New Collection

    ' �ŧi�ܼƥΩ�s�x�p�⵲�G
    Dim PipeDiameterInch As Double
    Dim PipeThicknessColumn As Long
    Dim PipeThickness_mm As Double
    Dim TotalWeight As Double
    Dim LookupValue As Variant
    
    ' �T�w���S���|������ "B" �@�_�i��
     If InStr(1, PipeSize, "B") > 0 Then
        PipeSize = Replace(PipeSize, "B", "")
    End If
    
    ' �]�m�u�@��ޥΡA"Pipe_Table" �s�x�޹D�ؤo�M���q���ƾ�
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    
    ' �ϥ� GetLookupValue �������d���
    LookupValue = GetLookupValue(PipeSize)

    ' �ϥ� VLOOKUP ��Ʈھڬd�������޹D�����|�]�^�o�^
    PipeDiameterInch = ws_Pipe_Table.Application.WorksheetFunction.VLookup(LookupValue, ws_Pipe_Table.Range("B:R"), 2, False)

    ' �ϥ� MATCH ��Ƨ�� Pipe_Thickness �b�u�@�����C��m
    PipeThicknessColumn = ws_Pipe_Table.Application.WorksheetFunction.Match(PipeThickness, ws_Pipe_Table.Range("B3:R3"), 0)

    ' �A���ϥ� VLOOKUP �������������p�ס]�@�̡^
    PipeThickness_mm = ws_Pipe_Table.Application.WorksheetFunction.VLookup(LookupValue, ws_Pipe_Table.Range("B:R"), PipeThicknessColumn, False)

    ' �ե� CalculatePipeWeight ��ƭp��޹D�C�̪����q
    TotalWeight = CalculatePipeWeight(CDbl(PipeDiameterInch), CDbl(PipeThickness_mm))

    ' �N�p��X�����|�B�p�שM�C�̭��q�K�[�춰�X��
    PipeDetails.Add PipeDiameterInch, "DiameterInch"
    PipeDetails.Add PipeThickness_mm, "PipeThickness"
    PipeDetails.Add TotalWeight, "PerWeight"

    ' ��^�]�t�޹D�Ӹ`�����X
    Set CalculatePipeDetails = PipeDetails
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

Sub AddPlateEntry(PlateType As String, PipeSize As Variant)
    '�t�d�B��M42���O�l
    
    Dim ws_M42 As Worksheet
    Dim col_type As Integer
    Dim Plate_Size As Double
    Dim Plate_Thickness As Double
    Dim Weight_calculator As Double
    Dim Plate_Name As String
    Dim RequireDrilling As Boolean
    Dim ws As Worksheet
    Dim i As Long

    ' �]�w��S�w�u�@���ޥ�
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")

    ' ���C B ���̫�@��A�ì��s�ƾڷǳƤU�@��
    i = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row + 1

    ' �ھڪO�l�����M�w�O�_�ݭn�p��
    Select Case PlateType
        Case "d", "b", "c"
            RequireDrilling = True
        Case Else
            RequireDrilling = False
    End Select
    ' �ھڪO�l�����M�w�ݩ�(BXB EXE GXG CXC)
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
            
            
            
    ' �T�wPlate���ؤo�M�p��
    If InStr(1, PipeSize, "*") > 0 Then
        ' �YPipeSize���S�w�榡���r�Ŧ�
        col_type = col_type - 1
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), col_type, False)
        Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 10, False)
    Else
        ' �YPipeSize���Ʀr
        PipeSize = GetLookupValue(PipeSize)
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), col_type, False)
        Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 11, False)
    End If
    Weight_calculator = Plate_Size / 1000 * Plate_Size / 1000 * Plate_Thickness * 7.85

    ' �T�wPlate�W��
    Plate_Name = "Plate_" & PlateType & IIf(RequireDrilling, "_���p��", "_�����p��")

    
    MainAddPlate Plate_Size, Plate_Size, Plate_Thickness, Plate_Name
    ' ��R�ƾ�
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
        ' .Cells(i, "Q").value = "���O��"
    ' End With
End Sub

Sub AddBoltEntry(PipeSize As Variant, Quantity As Integer)
    Dim ws As Worksheet
    Dim i As Long
    Dim BoltSize As String
    
    ' �]�w�� "Weight_Analysis" �u�@���ޥ�
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")
    ' ���C B ���U�@�Ӫťզ�
    i = GetNextRowInColumnB()

    If InStr(1, PipeSize, "*") > 0 Then
        ' �YPipeSize���S�w�榡���r�Ŧ�
        BoltSize = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 9, False)
    Else
        ' �YPipeSize���Ʀr
        PipeSize = GetLookupValue(PipeSize)
        BoltSize = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 10, False)
    End If


    ' ��R�ƾ�
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "EXP.BOLT"
        .Cells(i, "D").value = "'" & BoltSize & """"
        .Cells(i, "G").value = "SUS304"
        .Cells(i, "H").value = Quantity
        .Cells(i, "J").value = 1 ' ���]�C�����ꪺ��ӭ��q�O1�]�i�H�ھڹ�ڱ��p�վ�^
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
    End With
End Sub


Sub AddSteelSectionEntry(SectionType As String, Section_Dim As String, Total_Length As Double, Optional Steel_Qty As Double)
    Dim ws As Worksheet
    Dim i As Long
    Dim SectionWeight As Double
    

    '�W��ƶq
    
    If Steel_Qty = 0 Then
        Steel_Qty = 1
    End If
    
    ' �]�w��U���ؤu�@���ޥ�
    Set ws = Worksheets("Weight_Analysis")
    Set ws_HBeam = Worksheets("For_HBeam_Weight_Table")
    Set ws_Channel = Worksheets("For_Channel_Weight_Table")
    Set ws_Angle = Worksheets("For_Angle_Weight_Table")

    ' �ѷӭ��q
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

    ' ���� B �C���U�@�Ӫťզ�
    i = GetNextRowInColumnB()
     With ws
    ' �p�G
    If .Cells(i, "A").value <> "" Then
    First_Value_Checking = 1
    Else
    First_Value_Checking = .Cells(i - 1, "B").value + 1
    End If
    ' ��R�ƾ�
   
        .Cells(i, "B").value = First_Value_Checking
        .Cells(i, "C").value = SectionType
        .Cells(i, "D").value = Section_Dim
        .Cells(i, "E").value = Total_Length
        .Cells(i, "G").value = "A36/SS400"
        .Cells(i, "H").value = Steel_Qty
        .Cells(i, "I").value = SectionWeight
        .Cells(i, "J").value = .Cells(i, "E").value / 1000 * .Cells(i, "I").value
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value '���q�p�p
        .Cells(i, "L").value = "M"
        .Cells(i, "M").value = 1
        .Cells(i, "N").value = .Cells(i, "M").value * .Cells(i, "E").value / 1000 * .Cells(i, "H").value
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
    End With
End Sub

Sub AddPipeEntry(Pipe_Size As String, Pipe_Thickness As String, Pipe_Length As Double, Material As String)
    Dim i As Integer
    
    
' ----------------------------------------------------------------------------------------
' |                             �l�{�� AddPipeEntry ����y�{:                             |
' | ------------------------------------------------------------------------------------- |
' | 1. ��J�Ѽ�                                                                          |
' |    - Pipe_Size: "10"                                                                 |
' |    - Pipe_Thickness: "SCH.40"                                                        |
' |    - Pipe_Length: 1000                                                               |
' |    - Material: "SUS304"                                                              |
' |                                                                                      |
' | 2. �]�w�u�@��ޥ�                                                                    |
' |    - �ޥ� "Weight_Analysis" �u�@��C                                                  |
' |                                                                                      |
' | 3. �B�z�޹D�p��                                                                      |
' |    - �ˬd Pipe_Thickness �O�_�� "STD.WT"�C                                           |
' |    - �N "SCH.40" �ഫ�� "40S"�C                                                      |
' |                                                                                      |
' | 4. ���U�@�Ӫťզ�                                                                  |
' |    - �ե� GetNextRowInColumnB ��Ƨ�� "Weight_Analysis" ���� B �C���U�@�Ӫťզ�C    |
' |                                                                                      |
' | 5. �ե� CalculatePipeDetails ���                                                    |
' |    - �ϥ� "10" �M "40S" �@���ѼơC                                                    |
' |                                                                                      |
' | 6. CalculatePipeDetails ���                                                         |
' |    - �]�w�� "Pipe_Table" ���ޥΡC                                                    |
' |    - �ϥ� GetLookupValue ����d��ȡC                                                |
' |    - �ϥ� VLOOKUP ����޹D���|�]�^�o�^�C                                             |
' |    - �ϥ� MATCH ��� Pipe_Thickness ���C��m�C                                        |
' |    - �A���ϥ� VLOOKUP ����p�ס]�@�̡^�C                                             |
' |    - �ե� CalculatePipeWeight �p��C�̭��q�C                                         |
' |    - �N���|�B�p�שM�C�̭��q�K�[�춰�X���C                                            |
' |    - ��^���X�� AddPipeEntry�C                                                        |
' |                                                                                      |
' | 7. ��R�u�@��ƾ�                                                                   |
' |    - �b "Weight_Analysis" �u�@����R�ƾڡC                                         |
' |    - �]�A�~�W�B�ؤo�B�p�סB���סB����B�ƶq���C                                       |
' |                                                                                      |
' | 8. ����                                                                              |
' |    - �l�{�ǧ����A�u�@���s�C                                                        |
' ----------------------------------------------------------------------------------------

    
    
    
    Set ws = Worksheets("Weight_Analysis")
    
    '�S�w���D
    Pipe_ThickNess_For_Title = Pipe_Thickness
   ' �i��� "SCH.80"
    
    If Pipe_Thickness <> "STD.WT" Then
        Pipe_Thickness = Replace(Pipe_Thickness, "SCH.", "") & "S"
    Else
        Pipe_Thickness = Pipe_Thickness
    End If
    
    
    ' ���� B �C���U�@�Ӫťզ�
    i = GetNextRowInColumnB()
     With ws
    ' �t�ⶵ���O�_��1�Ψ�L
    If .Cells(i, "A").value <> "" Then
    First_Value_Checking = 1
    Else
    First_Value_Checking = .Cells(i - 1, "B").value + 1
    End If
'Ū�������ު��| �p�� �C�̭��q
     
   Set PipeDetails = CalculatePipeDetails(Pipe_Size, Pipe_Thickness)
    
    ' ��R�ƾ�
   
                .Cells(i, "B").value = First_Value_Checking
                .Cells(i, "C").value = "Pipe" '�~�W
                .Cells(i, "D").value = Pipe_Size & """" & "*" & Pipe_ThickNess_For_Title '�ؤo�p��
                .Cells(i, "E").value = Pipe_Length '����
                .Cells(i, "G").value = Material '����
                .Cells(i, "H").value = 1 '�ƶq
                .Cells(i, "I").value = PipeDetails.Item("PerWeight") '�C�̭�
                .Cells(i, "J").value = .Cells(i, "E").value / 1000 * .Cells(i, "I").value '�歫
                .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value '���q�p�p
                .Cells(i, "L").value = "M"
                .Cells(i, "M").value = 1 '�ռ�
                .Cells(i, "N").value = .Cells(i, "H").value * .Cells(i, "M").value * .Cells(i, "E").value / 1000 '���פp�p �ռ�*�ƶq*����/1000
                .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
                .Cells(i, "Q").value = "������"
    End With
End Sub
'------------------------------------------------------------------------------------------------------





Function GetSectionDetails(PartString_Type As String) As SectionDetails
' �۩w�q���� SectionDetails�A�Ω�s�x���󪺤ؤo�M����

' ----------------------------------------------------------------------------------------
' |                             ��� GetSectionDetails �\��y�z                          |
' | ------------------------------------------------------------------------------------- |
' | - �ھڶǤJ�� PartString_Type �]���󫬸��r�Ŧ�^�P�_���󪺤ؤo�M�����C                |
' | - �ϥ� Select Case ���c�ھڤ��P�� PartString_Type �רҽᤩ���P���ؤo�M�����C        |
' | - PartString_Type �O�q �t�~���l�{�Ǥ�Ū�����S�w���󫬸��N�X�C                        |
' | - �C�� Case �����@�دS�w�����󫬸��A�ýᤩ�������ؤo�M�����C                         |
' | - ��ƪ�^�@�Ӧ۩w�q���� SectionDetails�A�]�t�F Size�]�ؤo�^�M Type�]�����^�C       |
' | - �p�G���������� PartString_Type�A�N��^�@�ӥ]�t�Ŧr�Ŧꪺ SectionDetails�C         |
' | - ����ƥi�Ω��󳡥󫬸��ֳt����������ؤo�M������T�C                             |


' ----------------------------------------------------------------------------------------


    
    
    ' �Ыؤ@�� SectionDetails �������ܼƨӦs�x���G
    Dim Details As SectionDetails
    
    ' �ھڶǤJ�� PartString_Type �i��P�_�A�ýᤩ�۹������ؤo�M����
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
        ' ... ��h�רҥi�H�ھڻݭn�K�[
        Case Else
            ' �p�G�S���ǰt���רҡA��^�@�ӪŪ����c
            Details.Size = ""
            Details.Type = ""
    End Select
    
    ' �N�]�t���G�� Details ���c��^���եΪ�
    GetSectionDetails = Details
End Function


Sub MainAddPlate(Plate_Size_a As Double, Plate_Size_b As Double, Plate_Thickness As Double, Plate_Name As String, Optional Plate_Material As String)
 ' ----------------------------------------------------------------------------------------
' |                        �{�� AddNewMaterial �\��y�z                                  |
' | ------------------------------------------------------------------------------------- |
' | - �ھڴ��Ѫ����Ƥؤo�M�����A�p��s���ƪ����q�C                                        |
' | - �ϥιw�w�q�����ƱK�סA�p�G�S�����w���������A�N�ϥ��q�{���ơC                        |
' | - �ھڿ�J���ؤo�p����ƭ��q�A�ñN�p�⵲�G��R��u�@�������椸�椤�C                |
' | - ����U�@�ӥi�Φ�H���J�s�ƾڡA�O���u�@�����M��´�C                              |
' | - �ˬd�Ĥ@�ӭȬO�_�w�s�b�A�H�T�w�O�_�q1�}�l�s�����~��ǦC�C                           |
' | - �N�p��M��J���ƾڶ�R��u�@���S�w�C�A�H�K�i�歫�q���R�C                          |
' | - �A�ΪO���t��                                                                        |
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
        .Cells(i, "Q").value = "���O��"
    End With
End Sub
