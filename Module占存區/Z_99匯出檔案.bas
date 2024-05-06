Attribute VB_Name = "Z_99匯出檔案"
Private Sub Workbook_AfterSave(ByVal Success As Boolean)
    
    If Success Then
        Dim vbComp As VBIDE.VBComponent
        Dim SaveFolder As String
        SaveFolder = "C:\Users\a0976\OneDrive\AutoLisp 學習與公式架構\專案類別 - 繪製\My_Anysis_Support_for_iec"

        For Each vbComp In ThisWorkbook.VBProject.VBComponents
            If vbComp.Type = vbext_ct_StdModule Then
                ' 只導出標準模塊
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

    SaveFolder = "C:\Users\a0976\Desktop\新增資料夾 (3)\for_iec_support\Module占存區" ' 更改為您的導出文件夾

    For Each vbComp In ThisWorkbook.VBProject.VBComponents
        If vbComp.Type = vbext_ct_StdModule Then
            ' 生成文件路徑
            sFilePath = SaveFolder & "\" & vbComp.Name & ".bas"

            ' 導出模塊
            vbComp.Export sFilePath

            ' 重新打開文件並以二進位模式讀取內容
            nFileNum = FreeFile
            Open sFilePath For Binary Access Read As #nFileNum
            sContent = StrConv(InputB(LOF(nFileNum), #nFileNum), vbUnicode)
            Close #nFileNum

            ' 以 UTF-8 格式保存
            SaveAsUTF8 sContent, sFilePath
        End If
    Next vbComp

    MsgBox "所有標準模塊已導出到 " & SaveFolder
End Sub



Function SaveAsUTF8(sContent As String, sFilePath As String)
    Dim nFileNum As Integer
    Dim baBuffer() As Byte

    ' 轉換字符串到 UTF-8
    baBuffer = StrConv(sContent, vbFromUnicode)

    ' 寫入文件
    nFileNum = FreeFile
    Open sFilePath For Binary Access Write As #nFileNum
    Put #nFileNum, , baBuffer
    Close #nFileNum
End Function

Sub GenerateUpdateLog()  '負責創立更新日誌
    Dim logFilePath As String
    Dim fileNo As Integer
    Dim moduleContent As String

    ' 設置日誌文件的路徑
    logFilePath = ThisWorkbook.Path & "\Update_Log.txt"

    ' 檢查文件是否存在，如果存在則刪除
    If Dir(logFilePath) <> "" Then
        Kill logFilePath
    End If

    ' 從模塊獲取內容
    moduleContent = GetModuleContent("Module6")

    ' 將內容寫入新的文件
    fileNo = FreeFile
    Open logFilePath For Output As fileNo
    Print #fileNo, moduleContent
    Close fileNo

    MsgBox "更新日誌已生成於: " & logFilePath, vbInformation, "日誌生成"
End Sub

Function GetModuleContent(moduleName As String) As String '負責創立更新日誌
    Dim vbComp As Object
    Dim codeLine As String
    Dim moduleContent As String

    ' 循環通過所有的 VBA 模塊
    For Each vbComp In ThisWorkbook.VBProject.VBComponents
        If vbComp.Name = moduleName Then
            ' 獲取模塊的所有代碼行
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


