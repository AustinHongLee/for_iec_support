Attribute VB_Name = "B_�޹D�p��������"
Function CalculatePipeWeight(Pipe_Dn_inch As Double, Pipe_Weight_thickness_mm As Double) As Double
    Dim pi As Double
    pi = 4 * Atn(1)
    ' �p�⤽��
    CalculatePipeWeight = Round(((Pipe_Dn_inch - Pipe_Weight_thickness_mm) * pi / 1000 * 1 * Pipe_Weight_thickness_mm * 7.85), 2)
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


Sub AddPipeEntry(Pipe_Size As String, Pipe_Thickness As String, Pipe_Length As Double, material As String)
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
    If Pipe_Thickness = "STD" Then
        Pipe_Thickness = "STD.WT"
    ElseIf Pipe_Thickness <> "STD.WT" Then
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
                .Cells(i, "G").value = material '����
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
