Attribute VB_Name = "C_�����B�z"
' �۩w�q���� SectionDetails�A�Ω�s�x���󪺤ؤo�M����
Type SectionDetails
    Size As String
    Type As String
End Type

Sub AddSteelSectionEntry(SectionType As String, Section_Dim As String, Total_Length As Double, Optional Steel_Qty As Double, Optional Matirial_S As String)
    Dim ws As Worksheet
    Dim i As Long
    Dim SectionWeight As Double
    PrintStepCalculator "[AddSteelSectionEntry] - �B��AddSteelSectionEntry ���c�p�⭫�q�P��X "

    '�W��ƶq
    
    If Steel_Qty = 0 Then
        Steel_Qty = 1
        PrintStepCalculator "[AddSteelSectionEntry] - ���c�ƶq�� : " & Steel_Qty & "��"
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
    ' ���c����
    If Matirial_S = "" Then
        Matirial_S = "A36/SS400"
    End If
    
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
    PrintStepCalculator "[AddSteelSectionEntry] - �}�l��X�ƾڶi���"
        .Cells(i, "B").value = First_Value_Checking
        .Cells(i, "C").value = SectionType
        .Cells(i, "D").value = Section_Dim
        .Cells(i, "E").value = Total_Length
        .Cells(i, "G").value = Matirial_S
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


Function GetSectionDetails(PartString_Type As String, Optional Type_First As String) As SectionDetails
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
PrintStepCalculator "[GetSectionDetails] - �B��GetSectionDetails ����key���c��� "

    ' �Ыؤ@�� SectionDetails �������ܼƨӦs�x���G
    Dim Details As SectionDetails
    
    ' �ھڶǤJ�� PartString_Type �i��P�_�A�ýᤩ�۹������ؤo�M����
    Select Case PartString_Type
        ' Angle types
        Case "L50"
           Details.Size = "L50*50*6"
           Details.Type = "Angle"
        Case "L65"
           Details.Size = "L65*65*6"
           Details.Type = "Angle"
        Case "L75"
           Details.Size = "L75*75*9"
           Details.Type = "Angle"
        Case "L80"
           Details.Size = "L80*80*8"
           Details.Type = "Angle"
        Case "L90"
           Details.Size = "L90*90*9"
           Details.Type = "Angle"
        Case "L100"
           Details.Size = "L100*100*10"
           Details.Type = "Angle"
        Case "L110"
           Details.Size = "L110*110*10"
           Details.Type = "Angle"
        Case "L120"
           Details.Size = "L120*120*11"
           Details.Type = "Angle"
        Case "L130"
           Details.Size = "L130*130*12"
           Details.Type = "Angle"
        Case "L140"
           Details.Size = "L140*140*13"
           Details.Type = "Angle"
        Case "L150"
           Details.Size = "L150*150*14"
           Details.Type = "Angle"
        Case "L160"
           Details.Size = "L160*160*15"
           Details.Type = "Angle"
        Case "L180"
           Details.Size = "L180*180*16"
           Details.Type = "Angle"

        ' Channel types
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
        Case "C200"
           Details.Size = "C200*80*7.5"
           Details.Type = "Channel"
        Case "C250"
           Details.Size = "C250*90*8"
           Details.Type = "Channel"
        Case "C300"
           Details.Size = "C300*100*8.5"
           Details.Type = "Channel"
        Case "C350"
           Details.Size = "C350*100*9"
           Details.Type = "Channel"
        Case "C400"
           Details.Size = "C400*150*10"
           Details.Type = "Channel"
        Case "C450"
           Details.Size = "C450*150*11"
           Details.Type = "Channel"
        Case "C500"
           Details.Size = "C500*200*12"
           Details.Type = "Channel"

        ' H Beam types
         Case "H100"
           Details.Size = "H100*100*6"
           Details.Type = "H Beam"
         Case "H125"
           Details.Size = "H125*125*6.5"
           Details.Type = "H Beam"
        Case "H150"
          If Type_First = "" Then
            Details.Size = "H150*150*10"
            Details.Type = "H Beam"
          Else ' for the type 37
            Details.Size = "H150*150*7"
            Details.Type = "H Beam"
           End If
        Case "H250"
           Details.Size = "H250*125*6"
           Details.Type = "H Beam"
        Case "H300"
           Details.Size = "H300*150*6.5"
           Details.Type = "H Beam"
        Case "H350"
           Details.Size = "H350*175*7"
           Details.Type = "H Beam"
        Case "H400"
           Details.Size = "H400*200*8"
           Details.Type = "H Beam"
        Case "H450"
           Details.Size = "H450*200*9"
           Details.Type = "H Beam"
        Case "H500"
           Details.Size = "H500*250*10"
           Details.Type = "H Beam"
        Case "H550"
           Details.Size = "H550*300*11"
           Details.Type = "H Beam"
        Case "H600"
           Details.Size = "H600*300*12"
           Details.Type = "H Beam"

        ' Default case
        Case Else
            ' �p�G�S���ǰt���רҡA��^�@�ӪŪ����c
            Details.Size = ""
            Details.Type = ""
    End Select
    
    ' �N�]�t���G�� Details ���c��^���եΪ�
    GetSectionDetails = Details
End Function



