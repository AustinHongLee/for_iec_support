Attribute VB_Name = "Module3"
Sub CreateSheet_M42()
    Dim ws As Worksheet
    Dim sheetName As String
    sheetName = "M_42_Table"

    ' �ˬd�O�_�w�s�b�u�@��A�Y���s�b�h�s�W
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets(sheetName)
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add
        ws.Name = sheetName
    Else
        ws.Cells.Clear ' �p�G�u�@��w�s�b�A�M���Ҧ����e
    End If
    On Error GoTo 0
    
    ' �w�q���Y
    Dim headers As Variant
    headers = Array("Supporting pipe", "Supporting steel", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K")

    '�ۻs���
    Dim tableData As Variant
    tableData = Array( _
        Array("'1", "L50x50x6", 150, 180, 110, 290, 220, 200, 19, "'5/8", 9), _
        Array("'2", "L65x65x6", 150, 180, 110, 290, 220, 200, 19, "'5/8", 9), _
        Array("'3", "L65x65x6", 150, 180, 110, 290, 220, 200, 19, "'5/8", 9), _
        Array("'4", "L75x75x9", 230, 260, 190, 370, 300, 280, 19, "'5/8", 9), _
        Array("'5", "L100x100x10", 230, 260, 190, 370, 300, 280, 19, "'5/8", 9), _
        Array("'6", "L100x100x10", 230, 260, 190, 370, 300, 280, 19, "'5/8", 9), _
        Array("'8", "C125x65x6", 330, 380, 300, 490, 410, 380, 22, "'3/4", 16), _
        Array("'10", "C150x75x9", 330, 380, 300, 490, 410, 380, 22, "'3/4", 16), _
        Array("'12", "H150x150x7", 380, 500, 410, 560, 470, 430, 26, "'7/8", 16), _
        Array("'12", "H250x250x9", 380, 500, 410, 560, 470, 430, 26, "'7/8", 16) _
    )

    ' ��R���
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).value = headers(i)
    Next i
    
    ' ��R���
    Dim j As Integer
    For i = LBound(tableData) To UBound(tableData)
        For j = LBound(tableData(i)) To UBound(tableData(i))
            ws.Cells(i + 2, j + 1).value = tableData(i)(j)
        Next j
    Next i
    
    ' �榡��
    With ws
        .Range("A1:L1").Font.Bold = True
        .Range("A1:L1").Interior.Color = RGB(255, 255, 0) '����
        .Columns("A:L").AutoFit
    End With
End Sub




