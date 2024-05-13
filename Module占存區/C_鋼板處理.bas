Attribute VB_Name = "C_���O�B�z"
Sub MainAddPlate(plate_size_a As Double, plate_size_b As Double, plate_thickness As Double, plate_name As String, Optional Plate_Material As String, Optional Plate_qty As Double)
 ' ----------------------------------------------------------------------------------------
' |                        �{�� AddNewMaterial �\��y�z                                  |
' | ------------------------------------------------------------------------------------- |
' | - �ھڴ��Ѫ����Ƥؤo�M�����A�p��s���ƪ����q�C                                        |
' | - �ϥιw�w�q�����ƱK�סA�p�G�S�����w���������A�N�ϥ��q�{���ơC                        |
' | - �ھڿ�J���ؤo�p����ƭ��q�A�ñN�p�⵲�G��R��u�@�������椸�椤�C                |
' | - ����U�@�ӥi�Φ�H���J�s�ƾڡA�O���u�@�����M��´�C                              |
' | - �ˬd�Ĥ@�ӭȬO�_�w�s�b�A�H�T�w�O�_�q1�}�l�s�����~��ǦC�C                           |
' | - �N�p��M��J���ƾڶ�R��u�@���S�w�C�A�H�K�i�歫�q���R�C                          |
' | - �A�ΪO���t��
' | - MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name.Plate_Material,Plate_qty
' ----------------------------------------------------------------------------------------
   
    
    
    Dim Pipeline_Density As Double
    Dim weight As Double
    Dim i As Long
    Dim First_Value_Checking As Long
    Dim ws As Worksheet
    Set ws = Worksheets("Weight_Analysis")
    '------Optional remake---
    If Plate_qty = 0 Then
        Plate_qty = 1
    End If
   
    If Plate_Material = "" Then
        Plate_Material = "A36/SS400"
    End If
    '-----------------------------
    Select Case Plate_Material
        Case "A36/SS400"
            Pipeline_Density = 7.85
        Case "SUS304"
            Pipeline_Density = 7.93
        Case "AS"
            Pipeline_Density = 7.82
    End Select
           

    weight = plate_size_a / 1000 * plate_size_b / 1000 * plate_thickness * Pipeline_Density
    

    i = GetNextRowInColumnB()


    If ws.Cells(i, "A").value <> "" Then
        First_Value_Checking = 1
    Else
        First_Value_Checking = ws.Cells(i - 1, "B").value + 1
    End If


    With ws
        .Cells(i, "B").value = First_Value_Checking
        .Cells(i, "C").value = plate_name
        .Cells(i, "D").value = plate_thickness
        .Cells(i, "E").value = plate_size_a
        .Cells(i, "F").value = plate_size_b
        .Cells(i, "G").value = Plate_Material
        .Cells(i, "H").value = Plate_qty
        .Cells(i, "J").value = weight
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "PC"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "���O��"
    End With
End Sub


Sub AddPlateEntry(PlateType As String, PipeSize As Variant)
    '�t�d�B��M42���O�l
    
    Dim ws_M42 As Worksheet
    Dim col_type As Integer
    Dim Plate_Size As Double
    Dim plate_thickness As Double
    Dim Weight_calculator As Double
    Dim plate_name As String
    Dim RequireDrilling As Boolean
    Dim ws As Worksheet
    Dim i As Long

    ' �]�w��S�w�u�@���ޥ�
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")

    ' ���C B ���̫�@��A�ì��s�ƾڷǳƤU�@��
    i = ws.Cells(ws.Rows.count, "B").End(xlUp).Row + 1

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
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("B:L"), 10, False)
    Else
        ' �YPipeSize���Ʀr
        PipeSize = GetLookupValue(PipeSize)
        Plate_Size = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), col_type, False)
        plate_thickness = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:L"), 11, False)
    End If
    Weight_calculator = Plate_Size / 1000 * Plate_Size / 1000 * plate_thickness * 7.85

    ' �T�wPlate�W��
    plate_name = "Plate_" & PlateType & IIf(RequireDrilling, "_���p��", "_�����p��")

    
    MainAddPlate Plate_Size, Plate_Size, plate_thickness, plate_name
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
