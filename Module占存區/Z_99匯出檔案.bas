Attribute VB_Name = "Z_99�ץX�ɮ�"
Private Sub Workbook_AfterSave(ByVal Success As Boolean)
    
    If Success Then
        Dim vbComp As VBIDE.VBComponent
        Dim SaveFolder As String
        SaveFolder = "C:\Users\a0976\OneDrive\AutoLisp �ǲ߻P�����[�c\�M�����O - ø�s\My_Anysis_Support_for_iec"

        For Each vbComp In ThisWorkbook.VBProject.VBComponents
            If vbComp.Type = vbext_ct_StdModule Then
                ' �u�ɥX�зǼҶ�
                vbComp.Export SaveFolder & "\" & vbComp.Name & ".bas"
            End If
        Next vbComp
    End If
End Sub

Sub ExportAllStandardModules()
    Dim vbComp As VBIDE.VBComponent
    Dim SaveFolder As String
    Dim sContent As String
    Dim sFilePath As String
    Dim nFileNum As Integer

    SaveFolder = "C:\Users\a0976\Desktop\�s�W��Ƨ� (3)\for_iec_support\Module�e�s��" ' ��אּ�z���ɥX���

    For Each vbComp In ThisWorkbook.VBProject.VBComponents
        If vbComp.Type = vbext_ct_StdModule Then
            ' �ͦ������|
            sFilePath = SaveFolder & "\" & vbComp.Name & ".bas"

            ' �ɥX�Ҷ�
            vbComp.Export sFilePath

            ' ���s���}���åH�G�i��Ҧ�Ū�����e
            nFileNum = FreeFile
            Open sFilePath For Binary Access Read As #nFileNum
            sContent = StrConv(InputB(LOF(nFileNum), #nFileNum), vbUnicode)
            Close #nFileNum

            ' �H UTF-8 �榡�O�s
            SaveAsUTF8 sContent, sFilePath
        End If
    Next vbComp

    MsgBox "�Ҧ��зǼҶ��w�ɥX�� " & SaveFolder
End Sub



Function SaveAsUTF8(sContent As String, sFilePath As String)
    Dim nFileNum As Integer
    Dim baBuffer() As Byte

    ' �ഫ�r�Ŧ�� UTF-8
    baBuffer = StrConv(sContent, vbFromUnicode)

    ' �g�J���
    nFileNum = FreeFile
    Open sFilePath For Binary Access Write As #nFileNum
    Put #nFileNum, , baBuffer
    Close #nFileNum
End Function

Sub GenerateUpdateLog()  '�t�d�Хߧ�s��x
    Dim logFilePath As String
    Dim fileNo As Integer
    Dim moduleContent As String

    ' �]�m��x��󪺸��|
    logFilePath = ThisWorkbook.Path & "\Update_Log.txt"

    ' �ˬd���O�_�s�b�A�p�G�s�b�h�R��
    If Dir(logFilePath) <> "" Then
        Kill logFilePath
    End If

    ' �q�Ҷ�������e
    moduleContent = GetModuleContent("Module6")

    ' �N���e�g�J�s�����
    fileNo = FreeFile
    Open logFilePath For Output As fileNo
    Print #fileNo, moduleContent
    Close fileNo

    MsgBox "��s��x�w�ͦ���: " & logFilePath, vbInformation, "��x�ͦ�"
End Sub

Function GetModuleContent(moduleName As String) As String '�t�d�Хߧ�s��x
    Dim vbComp As Object
    Dim codeLine As String
    Dim moduleContent As String

    ' �`���q�L�Ҧ��� VBA �Ҷ�
    For Each vbComp In ThisWorkbook.VBProject.VBComponents
        If vbComp.Name = moduleName Then
            ' ����Ҷ����Ҧ��N�X��
            With vbComp.CodeModule
                For i = 1 To .CountOfLines
                    codeLine = .Lines(i, 1)
                    moduleContent = moduleContent & codeLine & vbCrLf
                Next i
            End With
        End If
    Next vbComp

    GetModuleContent = moduleContent
End Function
Sub clear_contents()
    Dim ws As Worksheet
    Dim Clear_Rng As Range
    Dim lastRow As Long

    Set ws = Worksheets("List_Table")
    
    ' Find the last row with data in column A
    lastRow = ws.Cells(ws.Rows.count, "A").End(xlUp).Row
    
    ' Set the range to clear
    Set Clear_Rng = ws.Range("A2:A" & lastRow)
    
    ' Clear the contents of the defined range
    Clear_Rng.ClearContents
End Sub


