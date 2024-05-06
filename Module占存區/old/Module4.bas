Attribute VB_Name = "Module4"
Sub Type_01(ByVal fullString As String)
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim pi As Double
    Dim Support_Pipe_Size As String
    Dim Pipe_ThickNess_mm As String
    Dim Main_Pipe_Length As Double
    Dim Support_Pipe_Length As Double
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
          

    
    '給M42資料
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    

    letter = GetThirdPartOfString(fullString)
    letter = Right(letter, 1)
    

    
    'Main_Pipe
    Third_Length_export = Replace(GetThirdPartOfString(fullString), letter, "") * 100
        ' 處理主管與輔助管的編制:
            
            Select Case PipeSize
               Case 2
                Support_Pipe_Size = "'1.5"
                Pipe_ThickNess_mm = "SCH.80"
                L_Value = 70
                
               Case 3
                Support_Pipe_Size = "'2"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 93
               
               Case 4
                Support_Pipe_Size = "'3"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 139

               Case 6
                Support_Pipe_Size = "'4"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 186

               Case 8
                Support_Pipe_Size = "'6"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 271

               Case 10
                Support_Pipe_Size = "'8"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 353

               Case 12
                Support_Pipe_Size = "'8"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 370

               Case 14
                Support_Pipe_Size = "'10"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 473
                
               Case 16
                Support_Pipe_Size = "'10"
                Pipe_ThickNess_mm = "SCH.40"
                L_Value = 491

               Case 18
                Support_Pipe_Size = "'12"
                Pipe_ThickNess_mm = "STD.WT"
                L_Value = 572
                
                Case 20
                Support_Pipe_Size = "'12"
                Pipe_ThickNess_mm = "STD.WT"
                L_Value = 594

                Case 24
                Support_Pipe_Size = "'14"
                Pipe_ThickNess_mm = "STD.WT"
                L_Value = 677
                
                Case 28
                Support_Pipe_Size = "'16"
                Pipe_ThickNess_mm = "STD.WT"
                L_Value = 782
                
                Case 36
                Support_Pipe_Size = "'24"
                Pipe_ThickNess_mm = "STD.WT"
                L_Value = 1099

                
    Case Else
        Exit Sub
End Select
    
    '主管長度與副管長度演算
    
    '主管長度 - 通常為SUS304
        Main_Pipe_Length = L_Value + 100
        AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"

    '固有資訊傳入 - 主管 - 副管 - 底板
          '主管
            
            '副管長度 - 通常為C12
            Support_Pipe_Length = Third_Length_export - 100
          
          '評估上若副管長度小於等於0 則跳過
          If Support_Pipe_Length > 0 Then
            '副管長度 - 通常為C12
            '副管厚度字串導正為需求
            Pipe_ThickNess_mm = "SCH." & Replace(Pipe_ThickNess_mm, "S", "")
            Support_Pipe_Length = Third_Length_export - 100
            AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Support_Pipe_Length, "A53Gr.B"
           End If
    
    PipeSize = Replace(Support_Pipe_Size, "'", "")
    PerformActionByLetter letter, PipeSize
End Sub
Sub Type_05(ByVal fullString As String)
    '範例格式A : 20-L50-05L
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim SectionType As String
    Dim Section_Dim As String
    Dim Total_Length As Double

    
   
    Set ws = Worksheets("Weight_Analysis")
    
    '區分出角鐵尺寸
    PartString_Type = GetSecondPartOfString(fullString)
        Select Case PartString_Type
            
            Case "L50"
               The_Section_Size = "L50*50*6"
               SectionType = "Angle"
            Case "L65"
               The_Section_Size = "L65*65*6"
               SectionType = "Angle"
            Case "L75"
               The_Section_Size = "L75*75*9"
               SectionType = "Angle"
            End Select

    '區分出M42類型
        Support_05_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)
    '區分出長度"H"
         Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_05_Type_Choice_M42, "") * 100
         Section_Length_L = 130
         
       '轉換為部分必要需求 :
        letter = Support_05_Type_Choice_M42
        PipeSize = The_Section_Size

      
      
      '導入Function addSteelSectionEntry
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H + Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length
            PerformActionByLetter letter, PipeSize
End Sub
Sub Type_08(ByVal fullString As String)
    '範例格式A : 08-2B-1005G
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim pi As Double
    Dim SectionType As String
    Dim Section_Dim As String
    Dim Total_Length As Double
    Dim BoltSize As String
    Dim Support_Pipe_Size As String
    Dim Pipe_ThickNess_mm As String
    Dim Main_Pipe_Length As Double
    Dim Support_Pipe_Length As Double
    Dim Plate_Size_a As Double
    Dim Plate_Size_b As Double
    Dim Plate_Thickness As Double
    Dim Plate_Name As String
    
    
    Set ws_M42 = Worksheets("M_42_Table")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    Set Type_08_Table = Worksheets("For_08_Type_data")

    
    '給定管尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    '給定H&L 長度
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    
    '給M42資料
    letter = GetThirdPartOfString(fullString)
    letter = Right(letter, 1)
    
    '注意 以下給個H值為暫定
    Pipe_Length_H_part = Replace(Right(GetThirdPartOfString(fullString), 3), letter, "") * 100
    
    '主管長度 - 通常為SUS304
        
        ' 計算實際管子需求長度
        PipeSize = GetLookupValue(PipeSize)
        BpLength = 6
        SL = Replace(Left(Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 7, False), 4), "C", "")  'For the section Length
        BTLength = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:K"), 11, False) 'For the M42 Plate Thickness
        
        ' 計算管子厚度
            Select Case PipeSize
               Case 2
                Pipe_ThickNess_mm = "SCH.40"
                
               Case 3
                Pipe_ThickNess_mm = "SCH.40"
               
               Case 4
                Pipe_ThickNess_mm = "SCH.40"



    Case Else
        Exit Sub
End Select

    '固有資訊傳入 - 主管 - 鋼構 - Plate(wing) - Plate(STOPPER) - Plate(BASE PLATE) - Plate(TOP)


'導入鋼管
        Main_Pipe_Length = Pipe_Length_H_part - BpLength - SL / 2 - BTLength
        AddPipeEntry PipeSize, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
        
'導入鋼構

            The_Section_Size = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 7, False) 'N
            SectionType = "Channel"
       
'導入Function addSteelSectionEntry
            
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length

'導入Function PerformActionByLetter-M42
            
            PerformActionByLetter letter, PipeSize

'導入14-Tpye特有屬性 : Plate(STOPPER)_08Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 4, False) 'K
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 5, False) 'M
            Plate_Thickness = 6
            Plate_Name = "Plate(STOPPER)_08Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'導入14-Tpye特有屬性 : Plate(TOP)_08Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 6, False) 'B
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 6, False) 'B
            Plate_Thickness = 6
            Plate_Name = "Plate(TOP)_08Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

End Sub
Sub Type_09(ByVal fullString As String)
    ' 範例格式A : 09-2B-05B
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim pi As Double
    Dim Support_Pipe_Size As String
    Dim Pipe_ThickNess_mm As String
    Dim Main_Pipe_Length As Double
    Dim Support_Pipe_Length As Double
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")

    ' 給M42資料
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    letter = GetThirdPartOfString(fullString)
    letter = Right(letter, 1)

    ' Main_Pipe
    Third_Length_export = Replace(GetThirdPartOfString(fullString), letter, "") * 100
    
    ' 處理主管與輔助管的編制:
    Select Case PipeSize
        Case 2
            Support_Pipe_Size = "'2"
            Pipe_ThickNess_mm = "SCH.80"
            L_Value = 106
                
        Case 3
            Support_Pipe_Size = "'2"
            Pipe_ThickNess_mm = "SCH.40"
            L_Value = 93
               
        Case 4
            Support_Pipe_Size = "'2"
            Pipe_ThickNess_mm = "SCH.40"
            L_Value = 106

        Case Else
            Exit Sub
    End Select

    ' 主管長度與副管長度演算
    
    ' 固有資訊傳入 - 主管 - 副管 - 底板 - Machine Bolt
    
    ' 主管長度 - 通常為SUS304
    Main_Pipe_Length = L_Value + 100
    AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
            
    ' 副管長度 - 通常為C12
    Support_Pipe_Length = Third_Length_export - 100
          
    ' 評估上若副管長度小於等於0 則跳過
    If Support_Pipe_Length > 0 Then
        ' 副管長度 - 通常為C12
        ' 副管厚度字串導正為需求
        Pipe_ThickNess_mm = "SCH." & Replace(Pipe_ThickNess_mm, "S", "")
        Support_Pipe_Length = Third_Length_export - 100
        AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Support_Pipe_Length, "A53Gr.B"
    End If

    PipeSize = Replace(Support_Pipe_Size, "'", "")
    PerformActionByLetter letter, PipeSize
       
    ' 導入09-Tpye特有屬性 : Machine Bolt
    ' 填充數據
    i = GetNextRowInColumnB()
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "MACHINE BOLT"
        .Cells(i, "D").value = "1-5/8""""*150L"
        .Cells(i, "G").value = "A307Gr.B(熱浸鋅)"
        .Cells(i, "H").value = 1
        .Cells(i, "J").value = 20 ' 假設每個螺栓的單個重量是20（可以根據實際情況調整）
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "螺絲類"
    End With
End Sub
Sub Type_11(ByVal fullString As String)
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim pi As Double
    Dim Support_Pipe_Size As String
    Dim Pipe_ThickNess_mm As String
    Dim Main_Pipe_Length As Double
    Dim Support_Pipe_Length As Double
    Dim anotherbuttompipeSize As String
    Dim anotherbuttompipeThickNess_mm As String
    Dim anotherbuttompipelegth As Double
    
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
          

    '-------------------------------抽取區-------------------------------------------
    '給 Support Line Size "A" 數字
    PartString_Type = GetPartOfString(fullString, 2, "-")
    PipeSize = Replace(PartString_Type, "B", "")
    
    '抽取M42的標記
    letter = GetPartOfString(fullString, 3, "-")
    letter = Right(letter, 1)
    
    '抽取H值
    H_Value = Replace(GetPartOfString(fullString, 3, "-"), letter, "")
    
    '抽取"D"值 - Machine Bolt Length
    D_Value = GetPartOfString(fullString, 4, "-")
    
    
    ' 抽取L值
    Support_Pipe_Size = "'1.5"
    Pipe_ThickNess_mm = "SCH.80"
            
    Select Case PipeSize
        Case 2
        L_Value = 71
        Case 3
        L_Value = 81
        Case 4
        L_Value = 97
        Case 6
        L_Value = 129
        Case 8
        L_Value = 162
        Case 10
        L_Value = 195
    Case Else
        Exit Sub
    End Select
    '-------------------------------整理區-------------------------------------------
    'Note 4 - another buttom pipe
    MachineBoltLength = 300
    anotherbuttompipelegth = H_Value - 100 - (MachineBoltLength - 9)
    anotherbuttompipeSize = "2"
    anotherbuttompipeThickNess_mm = "SCH.80"
    'Spring dim
    If PipeSize <= 4 Then
        Spring_Matirial = "A229"
        Spring_Wire = "12"
        Spring_ID = "46"
        Spring_Active_Coils = "4"
        Spring_inactive_Coils = "2"
        Spring_constant = 25
        Spring_Free_Length = 100
        Spring_max_recommended_deflection = 22
    ElseIf PipeSize > 4 Then
        Spring_Matirial = "A229"
        Spring_Wire = "14"
        Spring_ID = "46"
        Spring_Active_Coils = "4"
        Spring_inactive_Coils = "2"
        Spring_constant = 42
        Spring_Free_Length = 115
        Spring_max_recommended_deflection = 24
    End If




    '-------------------------------導入區-------------------------------------------
    '主管長度 - 通常為SUS304
    Main_Pipe_Length = L_Value + 100
    AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
    '支管長度 - 通常為"A53Gr.B"
    AddPipeEntry anotherbuttompipeSize, anotherbuttompipeThickNess_mm, anotherbuttompipelegth, "A53Gr.B"
    ' 底板用
    PipeSize = Replace(Support_Pipe_Size, "'", "")
    PerformActionByLetter letter, PipeSize
    ' 導入11-Tpye特有屬性 : Machine Bolt
    i = GetNextRowInColumnB() '運用Function取得下一行的位置
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "MACHINE BOLT"
        .Cells(i, "D").value = "1-5/8""""*300L"
        .Cells(i, "G").value = "A307Gr.B(熱浸鋅)"
        .Cells(i, "H").value = 1
        .Cells(i, "J").value = 20 ' 假設每個螺栓的單個重量是20（可以根據實際情況調整）
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "螺絲類"
    End With
    i = GetNextRowInColumnB() '運用Function取得下一行的位置
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "washer"
        .Cells(i, "D").value = "92*9t*50"
        .Cells(i, "G").value = "A307Gr.B(熱浸鋅)"
        .Cells(i, "H").value = 2
        .Cells(i, "J").value = 1 ' 假設每個螺栓的單個重量是1（可以根據實際情況調整）
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "素材類"
    End With
    i = GetNextRowInColumnB() '運用Function取得下一行的位置
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "Spring"
        .Cells(i, "D").value = Spring_Wire & "W" & Spring_ID & "ID"
        .Cells(i, "G").value = Spring_Matirial
        .Cells(i, "H").value = 2
        .Cells(i, "J").value = 1 ' 假設每個螺栓的單個重量是1（可以根據實際情況調整）
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "素材類"
    End With
End Sub
Sub Type_14(ByVal fullString As String)
    '範例格式A : 14-2B-1005
    
    Dim PartString_Type As String ' 用於儲存分割後的字串部分
    Dim PipeSize As String ' 管尺寸字串，用於查找和計算
    Dim letter As String ' 可能用於儲存從字串提取的字母
    Dim pi As Double ' 圓周率，可能用於計算，通常用內建常量Math.Pi代替
    Dim SectionType As String ' 指定截面類型，如“Channel”
    Dim Section_Dim As String ' 截面尺寸，用於鋼構部分
    Dim Total_Length As Double ' 總長度，可能用於鋼構或板材的長度計算
    Dim BoltSize As String ' 螺栓尺寸，用於螺絲類的輸入
    Dim Support_Pipe_Size As String ' 支撐管尺寸，如果有的話
    Dim Pipe_ThickNess_mm As String ' 管壁厚度，用於計算或標識
    Dim Main_Pipe_Length As Double ' 主管長度，用於計算管材長度
    Dim Support_Pipe_Length As Double ' 支撐管長度，如果有的話
    '...
    ' 以下變量用於 MainAddPlate 過程
    Dim Plate_Size_a As Double ' 板材的長度尺寸
    Dim Plate_Size_b As Double ' 板材的寬度尺寸
    Dim Plate_Thickness As Double ' 板材的厚度
    Dim Plate_Name As String ' 板材的命名，用於標識不同板材
    
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    Set Type_14_Table = Worksheets("For_14_Type_data")

    
    '給定管尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    '給定H&L 長度
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '注意 以下給個H值為暫定
    Pipe_Length_H_part = Right(GetThirdPartOfString(fullString), 2) * 100
    
    '主管長度 - 通常為SUS304
        
        ' 計算實際管子需求長度
        PipeSize = GetLookupValue(PipeSize)
        BpLength = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
        SL = Replace(Left(Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 12, False), 4), "C", "")  'N
        BTLength = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
        ' 計算管子厚度
            Select Case PipeSize
               Case 2
                Pipe_ThickNess_mm = "SCH.40"
                
               Case 3
                Pipe_ThickNess_mm = "SCH.40"
               
               Case 4
                Pipe_ThickNess_mm = "SCH.40"

               Case 6
                Pipe_ThickNess_mm = "SCH.40"

               Case 8
                Pipe_ThickNess_mm = "SCH.40"

               Case 10
                Pipe_ThickNess_mm = "SCH.40"

               Case 12
                Pipe_ThickNess_mm = "STD.WT"


    Case Else
        Exit Sub
End Select

    '固有資訊傳入 - 主管 - 鋼構 - Plate(wing) - Plate(STOPPER) - Plate(BASE PLATE) - Plate(TOP)


'導入鋼管
        Main_Pipe_Length = Pipe_Length_H_part - BpLength - SL - BTLength
        AddPipeEntry PipeSize, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
        
'導入鋼構


            The_Section_Size = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 12, False)
            SectionType = "Channel"
       '導入Function addSteelSectionEntry
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length

'導入14-Tpye特有屬性 : Plate(wing)_14Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 9, False) 'Q
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 8, False) 'P
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
            Plate_Name = "Plate(wing)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'導入14-Tpye特有屬性 : Plate(STOPPER)_14Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 7, False) 'M
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 6, False) 'K
            Plate_Thickness = 6
            Plate_Name = "Plate(STOPPER)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'導入14-Tpye特有屬性 : Plate(BASE PLATE)_14Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 2, False) 'C
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 2, False) 'C
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
            Plate_Name = "Plate(BASE PLATE)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'導入14-Tpye特有屬性 : Plate(TOP)_14Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 11, False) 'C
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 11, False) 'C
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
            Plate_Name = "Plate(TOP)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
'導入14-Tpye特有屬性 : EXP.BOLT
' 填充數據
   BoltSize = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 10, False) 'J
 i = GetNextRowInColumnB()
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "EXP.BOLT"
        .Cells(i, "D").value = "'" & BoltSize & """"
        .Cells(i, "G").value = "SUS304"
        .Cells(i, "H").value = 4
        .Cells(i, "J").value = 1 ' 假設每個螺栓的單個重量是1（可以根據實際情況調整）
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "螺絲類"
    End With


End Sub
Sub Type_15(ByVal fullString As String)
    '範例格式A : 15-2B-1005
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim pi As Double
    Dim SectionType As String
    Dim Section_Dim As String
    Dim Total_Length As Double
    Dim BoltSize As String
    Dim Support_Pipe_Size As String
    Dim Pipe_ThickNess_mm As String
    Dim Main_Pipe_Length As Double
    Dim Support_Pipe_Length As Double
    
    ' 以下變量用於 MainAddPlate 過程
    Dim Plate_Size_a As Double ' 板材的長度尺寸
    Dim Plate_Size_b As Double ' 板材的寬度尺寸
    Dim Plate_Thickness As Double ' 板材的厚度
    Dim Plate_Name As String ' 板材的命名，用於標識不同板材
    
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    Set Type_15_Table = Worksheets("For_15_Type_data")

    
    '給定管尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    '給定H&L 長度
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '注意 以下給個H值為暫定
    Pipe_Length_H_part = Right(GetThirdPartOfString(fullString), 2) * 100
    
    '主管長度 - 通常為SUS304
        
        ' 計算實際管子需求長度
        PipeSize = GetLookupValue(PipeSize)
        BpLength = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
        SL = Replace(Left(Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:L"), 9, False), 4), "C", "")  'N
        BTLength = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
        ' 計算管子厚度
            Select Case PipeSize
               Case 2
                Pipe_ThickNess_mm = "SCH.40"
                
               Case 3
                Pipe_ThickNess_mm = "SCH.40"
               
               Case 4
                Pipe_ThickNess_mm = "SCH.40"

               Case 6
                Pipe_ThickNess_mm = "SCH.40"

               Case 8
                Pipe_ThickNess_mm = "SCH.40"

               Case 10
                Pipe_ThickNess_mm = "SCH.40"

               Case 12
                Pipe_ThickNess_mm = "STD.WT"


    Case Else
        Exit Sub
End Select

    '固有資訊傳入 - 主管 - 鋼構 - Plate(wing) - Plate(STOPPER) - Plate(BASE PLATE) - Plate(TOP)


'導入鋼管
        Main_Pipe_Length = Pipe_Length_H_part - BpLength - SL - BTLength
        AddPipeEntry PipeSize, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
        
'導入鋼構


               The_Section_Size = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 9, False) 'N
               SectionType = "Channel"
       '導入Function addSteelSectionEntry
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length

'導入15-Tpye特有屬性 : Plate(wing)_15Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 7, False) 'Q
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 6, False) 'P
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
            Plate_Name = "Plate(wing)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'導入15-Tpye特有屬性 : Plate(STOPPER)_15Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 5, False) 'M
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 4, False) 'K
            Plate_Thickness = 6
            Plate_Name = "Plate(STOPPER)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
'導入15-Tpye特有屬性 : Plate(BASE PLATE)_15Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 2, False) 'D
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 2, False) 'D
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
            Plate_Name = "Plate(BASE PLATE)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'導入15-Tpye特有屬性 : Plate(TOP)_15Type
' 填充數據
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 8, False) 'B
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 8, False) 'B
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
            Plate_Name = "Plate(TOP)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name


End Sub
Sub Type_16(ByVal fullString As String)
    Dim Support_Pipe_Size As String
    Dim Pipe_ThickNess_mm As String
    Dim Main_Pipe_Length As Double
    Dim Support_Pipe_Length As Double
    Dim Plate_Size_a As Double ' 板材的長度尺寸
    Dim Plate_Size_b As Double ' 板材的寬度尺寸
    Dim Plate_Thickness As Double ' 板材的厚度
    Dim Plate_Name As String ' 板材的命名，用於標識不同板材
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim Third_Length_export As Double

    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")

    PrintStepCalculator "Type_16 - 開始處理"

    PartString_Type = GetPartOfString(fullString, 2)
    PrintStepCalculator "Type_16 - 抽取第二部分字符串: " & PartString_Type

    PipeSize = Replace(PartString_Type, "B", "")
    PrintStepCalculator "Type_16 - 抽取管徑: " & PipeSize

    Third_Length_export = GetPartOfString(fullString, 3) * 100
    PrintStepCalculator "Type_16 - 抽取第三部分字符串: " & Third_Length_export

       ' 處理主管與輔助管的編制:
            
            Select Case PipeSize
               Case 2
                Support_Pipe_Size = "'1.5"
                Pipe_ThickNess_mm = "SCH.80"
                Plate_Size = 70
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 2, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
                
               Case 3
                Support_Pipe_Size = "'2"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 80
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 3, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
               
               Case 4
                Support_Pipe_Size = "'3"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 110
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 4, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 6
                Support_Pipe_Size = "'4"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 140
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 6, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 8
                Support_Pipe_Size = "'6"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 190
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 8, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 10
                Support_Pipe_Size = "'8"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 240
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 10, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 12
                Support_Pipe_Size = "'10"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 290
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 12, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 14
                Support_Pipe_Size = "'12"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 340
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 14, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
                
               Case 16
                Support_Pipe_Size = "'12"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 340
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 16, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 18
                Support_Pipe_Size = "'14"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 380
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 18, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
                
                Case 20
                Support_Pipe_Size = "'14"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 380
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 20, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

                Case 24
                Support_Pipe_Size = "'16"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 430
                PrintStepCalculator "Type_16 - 處理主管與輔助管的編制: 24, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
    Case Else
        Exit Sub
End Select

    PrintStepCalculator "Type_16 - 開始計算管道細節"
    Set PipeDetails = CalculatePipeDetails(PipeSize, "10S")
    
    PrintStepCalculator "Type_16 - 開始計算主要管道長度"
    Main_Pipe_Length = Round((PipeSize * 1.5 * 25.4) + (PipeDetails.Item("DiameterInch") / 2) + 100)

    PrintStepCalculator "Type_16 - 開始計算支撐管道長度"
    Support_Pipe_Length = Round(Third_Length_export - (PipeDetails.Item("DiameterInch") / 2) - 100 + 300)

    PrintStepCalculator "Type_16 - 開始進入添加管道細節 - 主管, 搬運細節 管道直徑 : " & Support_Pipe_Size & ", 管道厚度 : " & Pipe_ThickNess_mm & ", 管道長度 : " & Main_Pipe_Length
    AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"


    If Support_Pipe_Length > 0 Then
        Pipe_ThickNess_mm = "SCH." & Replace(Pipe_ThickNess_mm, "S", "")
        PrintStepCalculator "Type_16 - 開始進入添加管道細節 - 支撐管, 搬運細節 管道直徑 : " & Support_Pipe_Size & ", 管道厚度 : " & Pipe_ThickNess_mm & ", 管道長度 : " & Support_Pipe_Length
        AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Support_Pipe_Length, "A53Gr.B"
    Else
        PrintStepCalculator "Type_16 - 支撐管長度為0，不添加支撐管"
    End If

    PrintStepCalculator "Type_16 - 開始添加板材"
    Plate_Size_a = Plate_Size
    Plate_Size_b = Plate_Size
    Plate_Thickness = 6
    Plate_Name = "Plate"
    PrintStepCalculator "Type_16 - 開始添加板材 - 板材尺寸 : " & Plate_Size_a & " x " & Plate_Size_b & " x " & Plate_Thickness
    MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
    PrintStepCalculator "Type_16 - Plate added successfully"

End Sub
Sub Type_20(ByVal fullString As String)
    '範例格式A : 20-L50-05A
    ' ----------------------------------------------------------------------------------------
    ' |                             子程序 Type_20 功能描述                                   |
    ' | ------------------------------------------------------------------------------------- |
    ' | - 內容 : 處理特定格式的字符串，提取鋼構尺寸和類型資訊。                               |
    ' | - 內容列數總觀 : 提取鋼構尺寸 (Size)、類型 (Type)，計算長度 (Total_Length)。          |
    ' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)                               |
    ' |                       GetSectionDetails(PartString_Type)                              |
    ' |                       GetThirdPartOfString(fullString)                                |
    ' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)|
    ' | - 錯誤處理        :  檢查Fig類型的合法性。                                           |
    ' | -2023/12/26 : 判定為完成                                                              |
    ' ----------------------------------------------------------------------------------------
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Support_20_Type_Choice As String
    Dim Section_Length_H As Double
    Dim Details As SectionDetails
    Dim Total_Length As Double
    
    
    Set ws = Worksheets("Weight_Analysis")

    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' 區分出Fig類型
    Support_20_Type_Choice = Right(GetThirdPartOfString(fullString), 1)

    ' 錯誤處理
    If IsNumeric(Support_20_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If

    ' 區分出長度"H"
    Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_20_Type_Choice, "") * 100

    ' 導入 Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length


End Sub

Sub Type_21(ByVal fullString As String)
    '範例格式A : 21-L50-05A
    '範例格式B : 21-L50-05C-07
' ----------------------------------------------------------------------------------------
' |                             子程序 Type_21 功能描述                                     |
' | -------------------------------------------------------------------------------------   |
' | - 內容 : 處理特定格式的字符串並提取鋼構尺寸和類型資訊。                                 |
' | - 內容列數總觀 : 提取鋼構尺寸 (Size)、類型 (Type)，計算總長度 (Total_Length)。          |
' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)                                 |
' |                       GetSectionDetails (PartString_Type)                               |
' |                       GetThirdPartOfString (fullString)                                 |
' |                       GetFourthPartOfString(fullString)                                 |
' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length) |
' |                                                                                         |
' | - 錯誤處理         :  檢查鋼構匹配項、Fig類型合法性、數字格式、字數。                   |
' | -2023/12/26        :  判定為完成                                                        |
' ------------------------------------------------------------------------------------------

    ' 宣告變數
    Dim ws As Worksheet
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim PartString_Type As String
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim Support_21_Type_Choice As String
    Dim Details As SectionDetails

    Set ws = Worksheets("Weight_Analysis")

    ' ----------------------------------<<<Action area>>>------------------------------------------
    '----------------------------------------------------------------------------------------------
    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (錯誤處理)[鋼材] 檢查是否找到匹配項 @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
    
    
    
    '-----------------------------------------------------------------------------------

    ' 區分出Fig類型
    Support_21_Type_Choice = Right(GetThirdPartOfString(fullString), 1)

    ' (錯誤處理)[Fig類型或者M42] 檢查是否為數字 @ 514
    If IsNumeric(Support_21_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    
    '-----------------------------------------------------------------------------------
    
    ' 區分出長度"H"
    Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_21_Type_Choice, "") * 100
    

    ' (錯誤處理)[字數判讀] 檢查是否含3碼 @ 515
    If Len(GetThirdPartOfString(fullString)) < 3 Then
        Err.Raise Number:=vbObjectError + 515, _
                  Description:="Len Value < 3 " & fullString
    End If
    '-----------------------------------------------------------------------------------

    ' 區分出長度"L"
    Select Case Support_21_Type_Choice
        Case "A"
            Section_Length_L = 300
        Case "B"
            Section_Length_L = 500
        Case "C"
            Section_Length_L = GetFourthPartOfString(fullString) * 100
    End Select

   
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length

End Sub
   

Sub Type_22(ByVal fullString As String)
    '範例格式A : 22-L50-05A(L)
    '範例格式B : 21-L50-05(L)C-07
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim Support_22_Type_Choice As String
    Dim Support_22_Type_Choice_M42 As String
    Dim Type_22_Replace_A As String
    Dim Type_22_Replace_B As String
    Dim Details As SectionDetails
    Dim letter As String
    Dim PipeSize As String
 ' ----------------------------------------------------------------------------------------
' |                             子程序 Type_22 功能描述                                                                           |
' | -------------------------------------------------------------------------------------   |
' | - 內容 : 倒吊雙鋼構。                                                                                                                |
' | - 內容列數總觀 : (鋼構H) -> (鋼構V)。                                                                                 |
' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)                                              |
' |                       GetSectionDetails (PartString_Type)                                                           |
' |                       GetThirdPartOfString (fullString)                                                                  |
' |                       GetFourthPartOfString(fullString)                                                                 |
' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length) |
' |                                                                                                                                                          |
' | - 具有Second , Third , Forth 錯誤判讀                                                                                    |
' |                                                                                                                                                          |
' |                                                                                                                                                         |
' | -2023/12/26 : 判定為完成                                                                                                        |
' ----------------------------------------------------------------------------------------
   
    
    
    Set ws = Worksheets("Weight_Analysis")
    
    ' ----------------------------------<<<Action area>>>------------------------------------------
    '----------------------------------------------------------------------------------------------
    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (錯誤處理)[鋼材] 檢查是否找到匹配項 @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
                  
                  
                  
    '----------------------------------------------------------------------------------------------
    '區分出Fig類型
    Support_22_Type_Choice = Mid(Right(GetThirdPartOfString(fullString), 3), 1, 1)
    
    ' (錯誤處理)[特殊Fig類型] 檢查格式是否正確 @ 514
    If Not (Support_22_Type_Choice = "A" Or Support_22_Type_Choice = "B" Or Support_22_Type_Choice = "C") Then
        If Not (Left(Support_22_Type_Choice, 1) = "(" And Right(Support_22_Type_Choice, 1) = ")") Then
            Err.Raise Number:=vbObjectError + 514, _
                      Description:="Invalid format for Fig type in " & fullString
        End If
    End If
    '---------------------------------------------------------------------------------------------------------------
        
        
    '----------------------------------------------------------------------------------------------
    '區分出M-42類型
    Support_22_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)
    
    ' (錯誤處理)[M-42類型] 檢查格式是否正確 @ 514
    If Not Left(Right(GetThirdPartOfString(fullString), 2), 1) = ")" Or Not (Support_22_Type_Choice_M42 Like "[A-Za-z]") Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Invalid format for M-42 type in " & fullString
    End If

    '----------------------------------------------------------------------------------------------
    
    
    ' 區分出長度"H"
    '修剪出 Replace 邏輯 for 長度
        Type_22_Replace_A = "(" & Support_22_Type_Choice & ")"
        Type_22_Replace_B = Support_22_Type_Choice_M42
        Section_Length_H = Replace(Replace(GetThirdPartOfString(fullString), Type_22_Replace_A, ""), Type_22_Replace_B, "") * 100
        
    
    ' 區分出長度"L"
    Select Case Support_22_Type_Choice
        Case "A"
            Section_Length_L = 300
        Case "B"
            Section_Length_L = 500
        Case "C"
            Section_Length_L = GetFourthPartOfString(fullString) * 100
    End Select
      
      '轉換為部分必要需求 :
        letter = Support_22_Type_Choice_M42
        PipeSize = The_Section_Size
      
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
            PerformActionByLetter letter, PipeSize
      '導入Function addSteelSectionEntry
            
End Sub
Sub Type_23(ByVal fullString As String)
    '範例格式A : 23-L50-05A
    '範例格式B : 23-L50-05C-07
' ----------------------------------------------------------------------------------------
' |                             子程序 Type_23 功能描述                                     |
' | -------------------------------------------------------------------------------------   |
' | - 內容 : 倒吊雙鋼構。                                                                   |
' | - 內容列數總觀 : (鋼構H) -> (鋼構V)。                                                   |
' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)                                 |
' |                       GetSectionDetails (PartString_Type)                               |
' |                       GetThirdPartOfString (fullString)                                 |
' |                       GetFourthPartOfString(fullString)                                 |
' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length) |
' |                                                                                         |
' | - 具有Second , Third , Forth 錯誤判讀                                                   |
' |                                                                                         |
' |                                                                                         |
' | -2023/12/26 : 判定為完成                                                                |
' ----------------------------------------------------------------------------------------
    ' 宣告變數
    Dim ws As Worksheet
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim PartString_Type As String
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim Support_23_Type_Choice As String
    Dim Details As SectionDetails

    Set ws = Worksheets("Weight_Analysis")

    ' ----------------------------------<<<Action area>>>------------------------------------------
    '----------------------------------------------------------------------------------------------
    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (錯誤處理)[鋼材] 檢查是否找到匹配項 @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
    
    
    
    '-----------------------------------------------------------------------------------

    ' 區分出Fig類型
    Support_23_Type_Choice = Right(GetThirdPartOfString(fullString), 1)

    ' (錯誤處理)[Fig類型或者M42] 檢查是否為數字 @ 514
    If IsNumeric(Support_23_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    
    '-----------------------------------------------------------------------------------
    
    ' 區分出長度"H"
    Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_23_Type_Choice, "") * 100 + Mid(GetSecondPartOfString(fullString), 2, 99)
    

    ' (錯誤處理)[字數判讀] 檢查是否含3碼 @ 515
    If Len(GetThirdPartOfString(fullString)) < 3 Then
        Err.Raise Number:=vbObjectError + 515, _
                  Description:="Len Value < 3 " & fullString
    End If
    '-----------------------------------------------------------------------------------

    ' 區分出長度"L"
    Select Case Support_23_Type_Choice
        Case "A"
            Section_Length_L = 300
        Case "B"
            Section_Length_L = 500
        Case "C"
            Section_Length_L = GetFourthPartOfString(fullString) * 100
    End Select

   
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length

End Sub

Sub Type_24(ByVal fullString As String)
    '範例格式A : 24-L50-05

    ' ----------------------------------------------------------------------------------------
    ' |                             子程序 Type_24 功能描述                                   |
    ' | ------------------------------------------------------------------------------------- |
    ' | - 內容 : 解析特定格式的字符串，提取鋼構信息。                                         |
    ' | - 內容列數總觀 : 從字符串中提取鋼構尺寸(Size)和計算長度(Total_Length)。               |
    ' | - 用了哪幾個函數 :  GetSecondPartOfString(fullString)                                 |
    ' |                     GetSectionDetails(PartString_Type)                                |
    ' |                     GetThirdPartOfString(fullString)                                  |
    ' | - 用了哪幾個子程序:  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)|
    ' | - 錯誤處理        :  目前無特定錯誤處理。                                             |
    ' | - 日期            :  2023/12/26                                                       |
    ' ----------------------------------------------------------------------------------------
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Section_Length_H As Double
    Dim Details As SectionDetails
    Dim Total_Length As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' 區分出長度"H"
    Section_Length_H = GetThirdPartOfString(fullString) * 100

    ' 導入 Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length


End Sub

Sub Type_25(ByVal fullString As String)
    '範例格式A : 25-L50-0505A
     ' ----------------------------------------------------------------------------------------
    ' |                             子程序 Type_25 功能描述                                   |
    ' | ------------------------------------------------------------------------------------- |
    ' | - 內容 : 解析特定格式的字符串以處理鋼構信息。                                          |
    ' | - 內容列數總觀 : 提取鋼構的尺寸(Size)、類型(Type)，並計算長度(H, L)。                  |
    ' | - 用了哪幾個函數 : GetSecondPartOfString(fullString)、GetThirdPartOfString(fullString) |
    ' | - 用了哪幾個子程序 : AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)  |
    ' | - 錯誤處理 : 檢查鋼材匹配項和Fig類型的合法性。                                        |
    ' | - 日期 : 2023/12/26                                                                  |
    ' ----------------------------------------------------------------------------------------
      
    Dim ws As Worksheet
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim PartString_Type As String
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim Support_23_Type_Choice As String
    Dim Details As SectionDetails
    '範例格式B : 25-L50-0505C-0401
    
   
    Set ws = Worksheets("Weight_Analysis")
    
    
    
    '----------------------------------------------------------------------------------------------
    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (錯誤處理)[鋼材] 檢查是否找到匹配項 @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '區分出Fig類型
    Support_25_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' (錯誤處理)[Fig類型或者M42] 檢查是否為數字 @ 514
    If IsNumeric(Support_25_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '區分出"L"值
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '-----------------------------------------------------------------------------------
    
    
    '-----------------------------------------------------------------------------------
    '區分出"H"值
    Section_Length_H = Replace(Right(GetThirdPartOfString(fullString), 3), Support_25_Type_Choice, "") * 100

    '-----------------------------------------------------------------------------------

    


      

      
      
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length

End Sub
Sub Type_26(ByVal fullString As String)
    '範例格式A : 26-L50-0505A
     ' ----------------------------------------------------------------------------------------
    ' |                             子程序 Type_26 功能描述
    ' | -------------------------------------------------------------------------------------
    ' | - 內容 : 解析特定格式的字符串以處理鋼構信息。
    ' | - 內容列數總觀 : 提取鋼構的尺寸(Size)、類型(Type)，並計算長度(H, L)。
    ' | - 用了哪幾個函數 : GetSecondPartOfString(fullString)、GetThirdPartOfString(fullString)
    ' | - 用了哪幾個子程序 : AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
    ' | - 錯誤處理 : 檢查鋼材匹配項和Fig類型的合法性。
    ' | - 日期 : 2023/04/29
    ' ----------------------------------------------------------------------------------------
      
    Dim ws As Worksheet
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim PartString_Type As String
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim Support_26_Type_Choice As String
    Dim Details As SectionDetails
    '範例格式B : 26-L50-1005A
    
   
    Set ws = Worksheets("Weight_Analysis")
    
    
    
    '----------------------------------------------------------------------------------------------
    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (錯誤處理)[鋼材] 檢查是否找到匹配項 @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '區分出Fig類型
    Support_26_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' (錯誤處理)[Fig類型或者M42] 檢查是否為數字 @ 514
    If IsNumeric(Support_26_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '區分出"L"值
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '-----------------------------------------------------------------------------------
    
    
    '-----------------------------------------------------------------------------------
    '區分出"H"值
    Section_Length_H = Replace(Right(GetThirdPartOfString(fullString), 3), Support_26_Type_Choice, "") * 100 * 2

    '-----------------------------------------------------------------------------------
     
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
 
End Sub
Sub Type_27(ByVal fullString As String)
    '範例格式A : 27-L50-0505A-0402
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim SectionType As String
    Dim Section_Dim As String
    Dim Total_Length As Double

    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set Type_15_Table = Worksheets("For_15_Type_data")
    Set ws = Worksheets("Weight_Analysis")
    
        
                                  
        
    '區分出角鐵尺寸
    PartString_Type = GetSecondPartOfString(fullString)
        Select Case PartString_Type
            
            Case "L50"
               The_Angle_Size = "L50*50*6"
               SectionType = "Angle"
            Case "L75"
               The_Angle_Size = "L75*75*9"
               SectionType = "Angle"
            Case "L100"
               The_Angle_Size = "L100*100*10"
               SectionType = "Angle"
            
            Case "C100"
               The_Angle_Size = "C100*50*5"
               SectionType = "Channel"
            
            Case "H150"
               The_Angle_Size = "H150*150*10"
               SectionType = "H Beam"
            Case Else
                i = GetNextRowInColumnB()
                ws.Cells(i, "B").value = "-"
                Exit Sub
            
            End Select
            
                  

    '區分出M-42類型
        Support_27_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)

    '區分出長度"H"
        Section_Length_H_1 = Right(Replace(GetThirdPartOfString(fullString), Support_27_Type_Choice_M42, ""), 2) * 100
        Section_Length_H_2 = 15
        Section_Length_H = Section_Length_H_1 - Section_Length_H_2
        
        
    '區分出長度"L"
        Section_Length_L = Left(Replace(GetThirdPartOfString(fullString), Support_27_Type_Choice_M42, ""), 2) * 100
        

      '轉換為部分必要需求 :
        letter = Support_27_Type_Choice_M42
        PipeSize = The_Angle_Size
      
      '導入Function addSteelSectionEntry
            
            SectionType = SectionType
            Section_Dim = Replace(The_Angle_Size, Left(The_Angle_Size, 1), "")
            Total_Length = Section_Length_H + Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length
            PerformActionByLetter letter, PipeSize

 
 If SectionType = "H Beam" Then
 
 '如果是H Bean 類型 則使用以下
 '導入27-Tpye特有屬性 : Plate(Wing)_27Type
' 填充數據
            Plate_Size_a = 200
            Plate_Size_b = 100
            Plate_Thickness = 9
            Weight_calculator = Plate_Size_a / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '項次
                      .Cells(i, "C").value = "Plate(Wing)_27Type"
                      .Cells(i, "D").value = Plate_Thickness
                      .Cells(i, "E").value = Plate_Size_a
                      .Cells(i, "F").value = Plate_Size_b
                      .Cells(i, "G").value = "A36/SS400"
                      .Cells(i, "H").value = 1
                      .Cells(i, "J").value = Weight_calculator
                      .Cells(i, "K").value = Weight_calculator
                      .Cells(i, "L").value = "PC"
                      .Cells(i, "M").value = 1
                      .Cells(i, "O").value = 1
                      .Cells(i, "P").value = Weight_calculator
                      .Cells(i, "Q").value = "鋼板類"
                  End With
            
  Else
  End If
  
End Sub
Sub Type_28(ByVal fullString As String)
    ' 範例格式A : 28-L50-1005L

    ' 宣告變數
    Dim ws As Worksheet
    Dim ws_Pipe_Table As Worksheet
    Dim ws_M42 As Worksheet
    Dim PipeSize As String
    Dim letter As String
    Dim SectionType As String
    Dim Section_Dim As String
    Dim Total_Length As Double
    Dim PartString_Type As String
    Dim The_Section_Size As String
    Dim Section_Length_H As Double
    Dim Section_Length_H_1 As Double
    Dim Section_Length_H_2 As Double
    Dim Section_Length_L As Double
    Dim Support_30_Type_Choice As String
    Dim Details As SectionDetails

    ' 設置工作表引用
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    
    ' 區分出角鐵尺寸
    PartString_Type = GetSecondPartOfString(fullString)

    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' 如果未找到匹配項，則退出子程序
    End If

    '區分出M-42類型
        Support_28_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)
    
    ' 區分出 "H" 值
        Section_Length_H = Replace(Right(GetThirdPartOfString(fullString), 3), Support_28_Type_Choice_M42, "") * 100 * 2
    ' 區分出 "L" 值
        Section_Length_L = Left(GetThirdPartOfString(fullString), 2)
        
        letter = Support_28_Type_Choice_M42
        PipeSize = The_Section_Size
        
    ' 導入 Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
    PerformActionByLetter letter, PipeSize
End Sub
Sub Type_30(ByVal fullString As String)
    ' 範例格式A : 30-L50-0505A
    ' 範例格式B : 30-L50-0505A-0401

    ' 宣告變數
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim Section_Length_H As Double
    Dim Section_Length_H_1 As Double
    Dim Section_Length_H_2 As Double
    Dim Section_Length_L As Double
    Dim Support_30_Type_Choice As String
    Dim Details As SectionDetails

    ' 設置工作表引用
    Set ws = Worksheets("Weight_Analysis")

    ' 區分出角鐵尺寸
    PartString_Type = GetSecondPartOfString(fullString)

    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' 如果未找到匹配項，則退出子程序
    End If

    ' 區分出 Fig 類型
    Support_30_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    Select Case Support_30_Type_Choice
        Case "A"
            Section_Length_H = Left(GetThirdPartOfString(fullString), 2) * 100
        Case "B"
            Section_Length_H_1 = Left(GetThirdPartOfString(fullString), 2) * 100
            Section_Length_H_2 = 15
            Section_Length_H = Section_Length_H_1 - Section_Length_H_2
        Case Else
            Exit Sub
    End Select

    ' 區分出 "L" 值
    Section_Length_L = Replace(Right(GetThirdPartOfString(fullString), 3), Support_30_Type_Choice, "") * 100

    ' 導入 Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_31(ByVal fullString As String)
    '範例格式A : 31-L50-05A
    '範例格式B : 31-L50-05C-07
' ----------------------------------------------------------------------------------------
' |                             子程序 Type_31 功能描述
' | -------------------------------------------------------------------------------------
' | - 內容 : 倒吊雙鋼構。
' | - 內容列數總觀 : (鋼構H) -> (鋼構V)。
' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)
' |                       GetSectionDetails (PartString_Type)
' |                       GetThirdPartOfString (fullString)
' |                       GetFourthPartOfString(fullString)
' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
' |
' | - 具有Second , Third , Forth 錯誤判讀
' |
' |
' | -2024/04/29 : 判定為完成
' ----------------------------------------------------------------------------------------
    ' ----------------------------------<<<宣告變數>>>-----------------------------------------------------------------
    ' 宣告變數
    '# 本地定義的變量
    Dim ws As Worksheet                     ' 工作表參考，用於訪問和操作 "Weight_Analysis" 工作表
    Dim The_Section_Size As String          ' 用來存儲從 Details 結構中獲得的尺寸信息
    Dim SectionType As String               ' 用來存儲從 Details 結構中獲得的類型信息
    Dim Total_Length As Double              ' 用來計算和存儲鋼結構的總長度
    Dim Section_Length_H As Double          ' 用於存儲和計算鋼結構垂直部分的長度
    Dim Section_Length_L As Double          ' 用於存儲和計算鋼結構水平部分的長度
    Dim Support_31_Type_Choice As String    ' 用於存儲額外的分類選擇或類型選擇，可能來自用戶輸入或其他計算
    '# 從其他函數或子程序調用的變量
    Dim PartString_Type As String           ' 從 GetSecondPartOfString(fullString) 獲得的字符串部分
    Dim Details As SectionDetails           ' 從 GetSectionDetails(PartString_Type) 獲得的部件尺寸和類型
    Dim lengthStrH As String                ' 從 GetThirdPartOfString(fullString) 獲得的字符串，代表鋼結構高度部分
    Dim lengthStrL As String                ' 從 GetFourthPartOfString(fullString) 獲得的字符串，代表鋼結構長度部分（如果適用）


   '---------------------------------------------------------------------------------------------------------------------
 
    ' ----------------------------------<<<Action area>>>------------------------------------------
    '----------------------------------------------------------------------------------------------
    Set ws = Worksheets("Weight_Analysis")
    ' 區分出鋼構尺寸
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (錯誤處理)[鋼材] 檢查是否找到匹配項 @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
    
    
    
    '-----------------------------------------------------------------------------------
    ' 檢查 lengthStrH 是否足夠長且為數字
    If GetThirdPartOfString(fullString) >= 3 Then
        ' 從字符串中提取高度和長度部分
        lengthStrL = Left(GetThirdPartOfString(fullString), 2)
        lengthStrH = Right(GetThirdPartOfString(fullString), 2)
        
        ' 檢查是否全部為數字
        If IsNumeric(lengthStrH) And IsNumeric(lengthStrL) Then
            Section_Length_H = Val(lengthStrH) * 100 * 2 ' 假設每個單位表示100倍的長度, DENOTE DIMENSION "H" (IN 100 mm)
            Section_Length_L = Val(lengthStrL) * 100  ' 假設每個單位表示100倍的長度  DENOTE DIMENSION "L" (IN 100 mm)
        Else
            Err.Raise Number:=vbObjectError + 516, _
                      Description:="Non-numeric characters found in dimensions: " & fullString
        End If
    Else
        Err.Raise Number:=vbObjectError + 515, _
                  Description:="Length string is too short for valid processing: " & lengthStrH
    End If

   
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表

End Sub
Sub Type_32(ByVal fullString As String)
    '範例格式A : 32-L50-1005
    Dim SectionType As String
    Dim The_Section_Size As String ' 確保此變數已被定義
    Dim Total_Length As Double
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim Details As SectionDetails
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取部分字符串
    PartString_Type = GetSecondPartOfString(fullString)

    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)

    ' 更新 The_Section_Size 和 SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' 如果未找到匹配項，則退出子程序
    End If

    
    ' 區分出 "H" 值

    Section_Length_H = Right(GetThirdPartOfString(fullString), 2) * 100 * 2

    ' 區分出 "L" 值
    
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100

    ' 導入 Function addSteelSectionEntry
    SectionType = SectionType
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_33(ByVal fullString As String)
    ' 示例格式A: 33-L50-1005
    ' ----------------------------------------------------------------------------------------
' |                             子程序 Type_33 功能描述
' | -------------------------------------------------------------------------------------
' | - 內容 : 倒吊雙鋼構。
' | - 內容列數總觀 : (鋼構H) -> (鋼構V)。
' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)
' |                       GetSectionDetails (PartString_Type)
' |                       GetThirdPartOfString (fullString)
' |                       GetFourthPartOfString(fullString)
' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
' |
' | - 具有Second , Third , Forth 錯誤判讀
' |
' |
' | -2024/04/29 : 判定為完成
' ----------------------------------------------------------------------------------------
    ' ----------------------------------<<<宣告變數>>>-----------------------------------------------------------------
    '# 本地定義的變量
    Dim ws As Worksheet                     ' 工作表參考，用於訪問和操作 "Weight_Analysis" 工作表
    Dim The_Section_Size As String          ' 用來存儲從 Details 結構中獲得的尺寸信息
    Dim SectionType As String               ' 用來存儲從 Details 結構中獲得的類型信息
    Dim Total_Length As Double              ' 用來計算和存儲鋼結構的總長度
    Dim Section_Length_H As Double          ' 用於存儲和計算鋼結構垂直部分的長度
    Dim Section_Length_L As Double          ' 用於存儲和計算鋼結構水平部分的長度
    '# 從其他函數或子程序調用的變量
    Dim PartString_Type As String           ' 從 GetSecondPartOfString(fullString) 獲得的字符串部分
    Dim Details As SectionDetails           ' 從 GetSectionDetails(PartString_Type) 獲得的部件尺寸和類型

    ' 初始化工作表
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取部分字符串
    PartString_Type = GetSecondPartOfString(fullString)

    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)

    ' 更新 The_Section_Size 和 SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' 如果未找到匹配，退出子程序
    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub
    End If

    ' 計算H L長度
    Section_Length_H = Right(GetThirdPartOfString(fullString), 2) * 100
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100

    ' 計算總長度
    Total_Length = Section_Length_H + Section_Length_L

   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表
End Sub
Sub Type_34(ByVal fullString As String)
    ' 示例格式A: 34-L50-1005
    ' ----------------------------------------------------------------------------------------
' |                             子程序 Type_34 功能描述
' | -------------------------------------------------------------------------------------
' | - 內容 : 倒吊雙鋼構。
' | - 內容列數總觀 : (鋼構H) -> (鋼構V)。
' | - 用了哪幾個函數   :  GetSecondPartOfString(fullString)
' |                       GetSectionDetails (PartString_Type)
' |                       GetThirdPartOfString (fullString)
' |                       GetFourthPartOfString(fullString)
' | - 用了哪幾個子程序 :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
' |
' | - 具有Second , Third , Forth 錯誤判讀
' |
' |
' | -2024/04/29 : 判定為完成
' ----------------------------------------------------------------------------------------
    ' ----------------------------------<<<宣告變數>>>-----------------------------------------------------------------
    '# 本地定義的變量
    Dim ws As Worksheet                     ' 工作表參考，用於訪問和操作 "Weight_Analysis" 工作表
    Dim The_Section_Size As String          ' 用來存儲從 Details 結構中獲得的尺寸信息
    Dim SectionType As String               ' 用來存儲從 Details 結構中獲得的類型信息
    Dim Total_Length As Double              ' 用來計算和存儲鋼結構的總長度
    Dim Section_Length_H As Double          ' 用於存儲和計算鋼結構垂直部分的長度
    Dim Section_Length_L As Double          ' 用於存儲和計算鋼結構水平部分的長度
    '# 從其他函數或子程序調用的變量
    Dim PartString_Type As String           ' 從 GetSecondPartOfString(fullString) 獲得的字符串部分
    Dim Details As SectionDetails           ' 從 GetSectionDetails(PartString_Type) 獲得的部件尺寸和類型

    ' 初始化工作表
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取部分字符串
    PartString_Type = GetSecondPartOfString(fullString)

    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)

    ' 更新 The_Section_Size 和 SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' 如果未找到匹配，退出子程序
    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub
    End If

    ' 計算H L長度
    Section_Length_H = Right(GetThirdPartOfString(fullString), 2) * 100
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100

    ' 計算總長度
    Total_Length = Section_Length_H + Section_Length_L

   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表
End Sub
Sub Type_35(ByVal fullString As String)
    '範例格式A : 35-L50-05A
    '未驗證
    
    Dim SectionType As String
    Dim The_Section_Size As String ' 確保此變數已被定義
    Dim Total_Length As Double
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim Details As SectionDetails
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取第二部分字符串
    PartString_Type = GetSecondPartOfString(fullString)
    
    '區分出Fig類型
        Support_35_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
        
    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)

    ' 更新 The_Section_Size 和 SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' 如果未找到匹配項，則退出子程序
    End If

 ' 區分出 "H" 值
 Select Case Support_35_Type_Choice
    Case "A"
    
        Section_Length_H = Left(GetThirdPartOfString(fullString), 2) * 100
    Case "B"
        Section_Length_H = Left(GetThirdPartOfString(fullString), 2) * 100 * 2
    Case Else
        Exit Sub
    End Select
        
        
    ' 導入 Function addSteelSectionEntry
    SectionType = SectionType
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_37(ByVal fullString As String)
    '範例格式A : 37-C125-1200A-05
    '範例格式B : 37-C125-1200B-05
    
    Dim SectionType As String
    Dim The_Section_Size As String
    Dim Total_Length As Double
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim Details As SectionDetails
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim pi As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取第二部分字符串 - 第二部分取得槽鋼類別
    PartString_Type = GetSecondPartOfString(fullString)
    
    '區分出角度類型 - 從 fullString 中提取第三部分字符串
        Support_37_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' 區分出 "H" 值 - 從 fullString 中提取第三部分字符串 - 水平長第一部分
        Section_Length_H_1 = Replace(GetThirdPartOfString(fullString), Support_37_Type_Choice, "")
        
    ' 檢查是否存在第四部分字符串
    If IsFourthPartAvailable(fullString) Then
        ' 存在第四部分，從 fullString 中提取第四部分字符串 - 水平長第二部分
        Section_Length_H_2 = GetFourthPartOfString(fullString) * 100
    Else
        ' 第四部分不存在，設定預設值
        Section_Length_H_2 = 200
    End If
        
        
    '區分出角度區別
        'Angle_A = 30
        'Angle_B = 45
        
        If Support_37_Type_Choice = "A" Then
            Angle_Y = 60
            Angle_X = 30
        Else
            Angle_Y = 45
            Angle_X = 45
        End If
        
    ' 演算出L值 - 需四個步驟
        '必要值變數
            Section_Length = Replace(GetSecondPartOfString(fullString), Left(GetSecondPartOfString(fullString), 1), "")
            pi = 4 * Atn(1) ' 計算圓周率 π
            
            '第一步驟
                First_Step = Section_Length / 2 * Tan(Angle_Y * pi / 180)
            '第二步驟
                halfSection = Section_Length / 2
                Second_a_calculator = First_Step * First_Step
                Second_Step = Round(Sqr(Round(halfSection * halfSection) + Second_a_calculator))
            '第三步驟
                Third_a_calculator = Second_Step * Tan(Angle_X * pi / 180) * Second_Step * Tan(Angle_X * pi / 180)
                Third_b_calculator = Second_Step * Second_Step
                Third_Step = Round(Sqr(Third_a_calculator + Third_b_calculator))
            '第四步驟
                Forth_a_calculator = Section_Length_H_1 * Tan(Angle_X * pi / 180) * Section_Length_H_1 * Tan(Angle_X * pi / 180)
                Forth_b_calculator = Section_Length_H_1 * Section_Length_H_1
                Forth_Step = Round(Sqr(Forth_a_calculator + Forth_b_calculator))
            
            Section_Length_L = Round(Third_Step + Forth_Step)
     ' 演算出H值 -
                Section_Length_H = Section_Length_H_1 + Section_Length_H_2
                
                
    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)

    ' 更新 The_Section_Size 和 SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' 如果未找到匹配項，則退出子程序
    End If


        
        
    ' 導入 Function addSteelSectionEntry
    SectionType = SectionType
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_39(ByVal fullString As String)
    '範例格式A : 39-C100-800A
    '範例格式B : 39-C125-1200B-05
    
    Dim SectionType As String
    Dim The_Section_Size As String
    Dim Total_Length As Double
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim Details As SectionDetails
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    Dim pi As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取第二部分字符串 - 第二部分取得槽鋼類別
    PartString_Type = GetSecondPartOfString(fullString)
    
    '區分出角度類型 - 從 fullString 中提取第三部分字符串
        Support_39_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' 區分出 "H" 值 - 從 fullString 中提取第三部分字符串 - 水平長第一部分
        Section_Length_H_1 = Replace(GetThirdPartOfString(fullString), Support_39_Type_Choice, "")
        
    ' 檢查是否存在第四部分字符串
    If IsFourthPartAvailable(fullString) Then
        ' 存在第四部分，從 fullString 中提取第四部分字符串 - 水平長第二部分
        Section_Length_H_2 = GetFourthPartOfString(fullString) * 100
    Else
        ' 第四部分不存在，設定預設值
        Section_Length_H_2 = 200
    End If
        
        
    '區分出角度區別
        'Angle_A = 30
        'Angle_B = 45
        
        If Support_39_Type_Choice = "A" Then
            Angle_Y = 60
            Angle_X = 30
        Else
            Angle_Y = 45
            Angle_X = 45
        End If
        
    ' 演算出L值 - 需四個步驟
        '必要值變數
            Section_Length = Replace(GetSecondPartOfString(fullString), Left(GetSecondPartOfString(fullString), 1), "")
            pi = 4 * Atn(1) ' 計算圓周率 π
            
            '第一步驟
                First_Step = Section_Length / 2 * Tan(Angle_Y * pi / 180)
            '第二步驟
                halfSection = Section_Length / 2
                Second_a_calculator = First_Step * First_Step
                Second_Step = Round(Sqr(Round(halfSection * halfSection) + Second_a_calculator))
            '第三步驟
                Third_a_calculator = Second_Step * Tan(Angle_X * pi / 180) * Second_Step * Tan(Angle_X * pi / 180)
                Third_b_calculator = Second_Step * Second_Step
                Third_Step = Round(Sqr(Third_a_calculator + Third_b_calculator))
            '第四步驟
                Forth_a_calculator = Section_Length_H_1 * Tan(Angle_X * pi / 180) * Section_Length_H_1 * Tan(Angle_X * pi / 180)
                Forth_b_calculator = Section_Length_H_1 * Section_Length_H_1
                Forth_Step = Round(Sqr(Forth_a_calculator + Forth_b_calculator))
            
            Section_Length_L = Round(Third_Step + Forth_Step)
     ' 演算出H值 -
                Section_Length_H = Section_Length_H_1 + Section_Length_H_2
                
                
    ' 使用 GetSectionDetails 函數取代 Select Case
    Details = GetSectionDetails(PartString_Type)

    ' 更新 The_Section_Size 和 SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' 如果未找到匹配項，則退出子程序
    End If

   
   ' 導入 Function addSteelSectionEntry
        '第一個導入H值 <垂直> 向
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表
        '第二個導入L值 <水平> 向
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' 調用以添加鋼結構條目到工作表

End Sub
Sub Type_48(ByVal fullString As String)
    '範例格式A : 48-1/2B(A)
    '範例格式B : 48-1B
    
Dim ws As Worksheet                          ' Excel 工作表對象，用於引用和操作工作表中的數據
Dim PartString_Type As String          ' 用於存儲從 fullString 提取的第二部分字符串
Dim Plate_Name As String               ' 用於存儲生成的鋼板名稱，將在 MainAddPlate 子程序中使用

Dim MatL As String                                 ' 材料類型，可以是碳鋼、合金鋼或不銹鋼，根據括號內的標記確定
Dim Plate_Size_a As Double                ' 鋼板的長度，從 Plate_Size 字符串中提取並轉換為 Double 類型
Dim Plate_Size_b As Double                ' 鋼板的寬度，從 Plate_Size 字符串中提取並轉換為 Double 類型
Dim Plate_Thickness As Double          ' 鋼板的厚度，從 Plate_Size 字符串中提取並轉換為 Double 類型

Dim needValue() As Variant                   ' 用於存儲從 PartString_Type 中提取的包含括號的字符串部分的結果
Dim Value0 As String                                 ' 從 needValue(0) 提取出的字符串，移除 "B" 之後用於進一步處理
Dim Re_Size As Double                            ' 從 Value0 轉換或計算得到的尺寸值，用於決定 Plate_Size 的選擇

Dim Plate_Size As String                            ' 存儲鋼板尺寸的字符串，格式為 "長度*寬度*厚度"

    
    Set ws = Worksheets("Weight_Analysis")

    ' 從 fullString 中提取部分字符串
    PartString_Type = GetPartOfString(fullString, 2)
    
    ' 檢查是否存在括號，以確定是否可以正常提取部分
    ValueCondition = InStr(PartString_Type, "(")
    If ValueCondition > 0 Then
        needValue = ExtractParts(PartString_Type)
        ' 進行再處理 needvalue(0) ; "B"是無效的, 故得先刪除。1/2 & 3/4 & 1 1/2 Excel看不懂, 得先再處理
        Value0 = Replace(needValue(0), "B", "")
        ' 進行再處理 needvalue(1) ; 有3個條件 "None"= Carbon steel , "(A)" = Alloy steel , "(B)" = Stainless steel
        Select Case needValue(1)
            Case "(A)"
                MatL = "AS"
            Case "(B)"
                MatL = "SUS304"
            Case Else
                MatL = "A36/SS400"
        End Select
    Else
        Value0 = Replace(PartString_Type, "B", "")
        MatL = "A36/SS400" ' 沒有具體的材料標識，使用預設值
    End If
    
    Select Case Value0
        Case "1/2"
            Re_Size = 0.5
        Case "3/4"
            Re_Size = 0.75
        Case "1 1/2"
            Re_Size = 1.5
        Case Else
            Re_Size = Val(Value0)  ' 直接將字符串轉換為數值
    End Select
    
    If Re_Size <= 2 Then
        Plate_Size = "150*100*6"
    Else
        Plate_Size = "150*100*9"
    End If
    
    ' 切出需要的值給予MainAddPlate
    Plate_Size_a = Val(GetPartOfString(Plate_Size, 1, "*"))
    Plate_Size_b = Val(GetPartOfString(Plate_Size, 2, "*"))
    Plate_Thickness = Val(GetPartOfString(Plate_Size, 3, "*"))
    Plate_Name = "Plate_48Type"
    
    ' 導入 MainAddPlate
    MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name, MatL
End Sub

Sub Type_51(ByVal fullString As String)
    '範例格式A : 51-2B
    '2B  = Line Size

Dim Ssize As String
Dim M As String
Dim H As String

Dim MatL As String                                 ' 材料類型，可以是碳鋼、合金鋼或不銹鋼，根據括號內的標記確定
Dim Plate_Size_a As Double                ' 鋼板的長度，從 Plate_Size 字符串中提取並轉換為 Double 類型
Dim Plate_Size_b As Double                ' 鋼板的寬度，從 Plate_Size 字符串中提取並轉換為 Double 類型
Dim Plate_Thickness As Double          ' 鋼板的厚度，從 Plate_Size 字符串中提取並轉換為 Double 類型
Dim Plate_Name As String               ' 用於存儲生成的鋼板名稱，將在 MainAddPlate 子程序中使用
    
Dim SectionType As String
Dim The_Section_Size As String
Dim Total_Length As Double
    '------------------------抽取第二部分並抽出正確尺寸------------------------
    PartString_Type = GetPartOfString(fullString, 2)
    Line_Size = Replace(PartString_Type, "B", "")
    '------------------------判讀區域------------------------
    If Line_Size <= "3" Then
        M = "FlateBar"
        Ssize = "50*9"
    ElseIf Line_Size > "3" And Line_Size <= "6" Then
        M = "Angle"
        Ssize = "50*50*6"
    ElseIf Line_Size > "6" Then
        M = "Angle"
        Ssize = "65*65*6"
    End If
    '------------------------獲取H值------------------------
    Select Case Line_Size
        Case "3/4"
            H = "25"
        Case "1"
            H = "30"
        Case "1 1/2"
            H = "45"
        Case "2"
            H = "60"
        Case "2 1/2"
            H = "70"
        Case "3"
            H = "80"
        Case "4"
            H = "125"
        Case "5"
            H = "125"
        Case "6"
            H = "125"
        Case "8"
            H = "150"
        Case "10"
            H = "150"
        Case "12"
            H = "200"
        Case "14"
            H = "200"
        Case "16"
            H = "250"
        Case "18"
            H = "300"
        Case "20"
            H = "300"
        Case "24"
            H = "300"
    End Select

'------------------------分割出需要的值------------------------
    If M = "FlateBar" Then
            Plate_Size_a = Val(GetPartOfString(Ssize, 1, "*"))
            Plate_Size_b = Val(GetPartOfString(Ssize, 1, "*"))
            Plate_Thickness = Val(GetPartOfString(Ssize, 2, "*"))
            Plate_Name = "FlateBar"
            MatL = "A36/SS400"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
        ElseIf M = "Angle" Then
            The_Section_Size = Ssize
            SectionType = M
            Total_Length = H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
            MatL = "A36/SS400"
    End If


End Sub
Sub Type_52(ByVal fullString As String)
    '範例格式A : 52-2B(P)-A(A)-130-500
    '2B  = Line Size
    '(P) = Pad is Req'D
    'A   = D-80A Table "A" - Something write for insulation Thickness ( That was not our Problem )
            'if Symbol is " " then
            '   insulation thickness = 75 & lesser
            '   Height of shoe (mm)(Say hops)= 100
            'else if Symbol is "A" then
            '   insulation thickness = 80 THROUGH 125
            '   Height of shoe (mm)(Say hops)= 150
            'else if Symbol is "B" then
            '   insulation thickness = 130 THROUGH 175
            '   Height of shoe (mm)(Say hops)= 200
            'else if Symbol is "C" then
            '   insulation thickness = 180 THROUGH 225
            '   Height of shoe (mm)(Say hops)= 250
            'end if
    '(A) = D-80A Table "B" - Something write for Matirial (A) for Alloy steel ; (S) for Stainless steel
    '130 = HOPS = 130 IN MM IF ANY
    '500 = LOPS = 500 IN MM IF ANY
    
        ' 指定編號的含義：
        ' 52-2B(P)-A(A)-130-500：這是部件的設計編號，每部分的含義如下：
        ' 52：代表型號編號。
        ' 2B：代表線徑尺寸。
        ' P：需要特別注意，可能表示材料的特殊屬性或處理方式。
        ' A(A)：代表一個重要的分類或規格。
        ' 130-500：可能指部件的尺寸或與特定設計相關的參數。
        ' 修改 LOpS=500 (in mm) if any：如果有需要，可以修改 LOpS（管鞋長度）的標準值至 500 毫米。
        ' 修改 HOpS=130 (in mm) if any：如果有需要，可以修改 HOpS（管鞋高度）的標準值至 130 毫米。
        ' 參見 SHT D-80A 表 'A' 和表 'B'：具體細節或條款可以在文件的 D-80A 頁面的表 'A' 和表 'B' 中查找。
        ' 組件最大長度：
        ' 此部件的最大長度不應超過梁的寬度。
        ' HOpS 和 LOpS 的定義：
        ' HOpS：高度，指的是管鞋的高度。
        ' LOpS：長度，指的是管鞋的長度。
    
    ' 宣告變數
    Dim pi As Double
    Dim ws_For_52_Type_Table As Worksheet
    Dim Special_symbol_count As Integer
    Dim Hops_Value As Variant, Lops_Value As Variant
    Dim PipeSize As Variant, Pad_symbol As Variant
    Dim Insulation_Value As Variant, Material_Value As Variant
    Dim Plate_Size_a As Double, Plate_Size_b As Double, Plate_Thickness As Double
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Total_Length As Double
    Dim PartString_Type As String
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    
    ' 以下變量用於 MainAddPlate 過程
    Dim Plate_Name As String ' 板材的命名，用於標識不同板材
    

    '------------------------------------------第四部分判讀與分析------------------------------------------
    Special_symbol_count = CountCharacter(fullString, "-")  ' if fullstring = "52-2B(P)-A(A)-130-500" then Special_symbol_count = 4
    Select Case Special_symbol_count
        Case 1
        ' 他只有Type 52-2B   這種情況 需附加第二階段判讀 且insulation = 75 & lesser  hope = 130 lops = 500
            Hops_Value = GetFourthPartOfString(fullString)
            If Hops_Value = "N/A" Then
                Hops_Value = 150
                PipeSize = GetLookupValue(Replace(Type52_GetPipeSize(fullString), "B", ""))
                Pad_symbol = Type52_GetPadSymbol(fullString)
                Lops_Value = 500
            End If
        Case 2
        ' 他只有Type 52-2B(P)-"*(*)" 或者  Type 52-2B(P)-"*" 這種情況需附加第三階段判讀
            Hops_Value = GetFourthPartOfString(fullString)
            If Hops_Value = "N/A" Then
                Hops_Value = 150
                PipeSize = Type52_GetPipeSize(fullString)
                Pad_symbol = Type52_GetPadSymbol(fullString)
                Insulation_Value = Type52_GetInsulationValue(fullString)
                Matirial_Value = Type52_GetMaterialValue(fullString)
            End If
        Case 4
        ' 他有Type 52-2B(P)-A(A)-130-500 這種情況需附加第四階段判讀
            Hops_Value = GetFourthPartOfString(fullString)
            If Hops_Value = "N/A" Then
                Hops_Value = 150
                PipeSize = Type52_GetPipeSize(fullString)
                Pad_symbol = Type52_GetPadSymbol(fullString)
                Insulation_Value = Type52_GetInsulationValue(fullString)
                Matirial_Value = Type52_GetMaterialValue(fullString)
            Else
                Hops_Value = GetPartOfString(fullString, 4)
                Lops_Value = GetPartOfString(fullString, 5)
                PipeSize = Type52_GetPipeSize(fullString)
                Pad_symbol = Type52_GetPadSymbol(fullString)
                Insulation_Value = Type52_GetInsulationValue(fullString)
                Matirial_Value = Type52_GetMaterialValue(fullString)
            End If
            Lops_Value = GetFifthPartOfString(fullString)
            
        If Lops_Value = " " Then
            Lops_Value = 500
        End If
            If Hops_Value = " " Then
            Hops_Value = 150
        End If
    End Select
            
    If Pad_symbol <> "N/A" Then
    '------------------ pad專區-----------------------
    '區分出管徑-差異是Pad長
    '開始演算Pad的板子 - 圓周長=A  Pad長=B  Pad厚度=t
    'Pad長度 = Lops + 2E
    '若為10"以上 將會增添兩個U型PAD 52 & 66 都有
    '52與66的差異在於角鐵 IF < 10 則添加兩個40*40*5-150L的角鐵 Else if >= 10 則添加兩個40*40*5-150L的角鐵 <- 可知 角鐵的尺寸為不變
    '52是擁有角鐵 不管是10如何都有角鐵
    'Triago Calculator :
    'Set The Angle for 30 deg  = 30T_Angle
    '30T_Angle_Address = [x,y]
    '30T_x = (PipeDetails.item("DiameterInch") + (PipeDetail.Item("PipeThickness") * 2)) / 2 * Sin(radians(60))
    '30T_y = (PipeDetails.item("DiameterInch") + (PipeDetail.Item("PipeThickness") * 2)) / 2 * Sin(radians(30))
    'And I need 30T_y to know how to calculator The Plate_Y_max_Value
    'Plate_Y_max_Value = (PipeDetails.item("DiameterInch") + (PipeDetail.Item("PipeThickness") * 2)) / 2 + H_Beam_Y_Value - H_Beam_Thickness_Value*2
    'Plate_Size_a 指的是板子的短邊。為了計算這個，你需要計算一個大圓的周長。
    '這是透過取半徑（即 Pipe_dia_Size 和 Pipe_thickness 總和），將其加倍以獲得較大圓的直徑，然後乘以 pi 得出較大圓的周長來完成的。_
    'Plate_Size_b 表示板的較長邊緣。其計算公式為：Lops 加上兩倍 25，再加上兩倍 E。

    ' This is a highly intricate calculation that I need to delineate in detail :P.

    ' Plate_Size_a refers to the shorter edge of the plate. To compute this,
    'you calculate the circumference of a larger circle. This is done by taking the radius,
    'which is the sum of the Pipe_dia_Size and the Pipe_thickness,
    'doubling it to get the diameter of the larger circle, and then multiplying by pi to find the circumference of the larger circle.
    ' Plate_Size_b denotes the longer edge of the plate. The calculation for this is: Lops plus twice 25, added to twice E.
        Select Case Val(PipeSize)
            Case Is < 2
                Pipe_Thickness = 6
            Case 2 To 14
                Pipe_Thickness = 9
            Case 15 To 24
                Pipe_Thickness = 12
            Case Else
                Pipe_Thickness = 0 ' 可以設置一個默認值，以防 PipeSize 超出預期範圍
        End Select
            
            
            Set PipeDetails = CalculatePipeDetails(PipeSize, "10S")
            
            If PipeSize < 10 Then
                
            'Here for the Pipe Size < 10B
            PAD_Calculator_A = ((PipeDetails.Item("DiameterInch") / 2) + Pipe_Thickness * 2) * (4 * Atn(1)) '((該置放管直徑/2)+該管徑的厚度 *2)*(4*atn(1))
            PAD_Calculator_B = Type_GetTable66_E(PipeSize) * 2 + Lops_Value
            PAD_Calculator_t = Pipe_Thickness
            
            
            
            ElseIf GetLookupValue(Replace(PipeSize, "B", "")) >= 10 Then
            'Here for the Pipe Size >= 10B
            PAD_Calculator_A = ((PipeDetails.Item("DiameterInch") / 2) + Pipe_Thickness * 2) * (4 * Atn(1))
            PAD_Calculator_B = Type_GetTable66_E(PipeSize) * (2 + Lops_Value) + (25 * 2)
            PAD_Calculator_t = Pipe_Thickness
                
            End If
                
                
            'Pad Calculator
                Plate_Size_a = PAD_Calculator_A
                Plate_Size_b = PAD_Calculator_B
                Plate_Thickness = PAD_Calculator_t
                Plate_Name = "Pad_52Type"
                MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
    End If
    '------------------ 角鐵專區-----------------------
    '角鐵的尺寸為不變
    SectionType = "Angle"
    The_Section_Size = "40*40*5"
    Total_Length = 150
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
    '------------------ C專區-----------------------
    SectionType = "H Beam"
    The_Section_Size = Type52_GetTable66_C(PipeSize)
    Total_Length = Lops_Value
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
    
End Sub




Sub Type_108(ByVal fullString As String)
    Dim needValue As Variant
    
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim pi As Double
    
    '範例格式 : 108-1B-12E-A(S)
    'Need use GetFourthPartOfString
    '108=Type
    '1B =Denote Line Size "D"
    '12 =Denote Dimension "H" (IN 100mm)
    'E  =Denote the M42 Type
    'A  =分為Fig.A & Fig.B & Fig.C Lug Plate 的區別
    '(S)=材質區分
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
        
        '區分出尺吋 符合Line Size : "D"
            PartString_Type = GetSecondPartOfString(fullString)
            PipeSize = Replace(PartString_Type, "B", "")
          
          '區分出M42板類型
        letter = GetThirdPartOfString(fullString)
        letter = Right(letter, 1)
        
        '區分出"H"值並乘上100
        Main_Pipe_Length = Replace(GetThirdPartOfString(fullString), letter, "") * 100
        

        
        '區分出Fig number
        needValue = ExtractParts(GetFourthPartOfString(fullString))
        Fig_number = needValue(0)
                
                Select Case Fig_number
                Case "A"
                    Fig = "Fig_A"
                Case "B"
                    Fig = "Fig_B"
                Case "C"
                    Fig = "Fig_C"
                
                Case Else
                   Exit Sub
                End Select
        
        
        
        '區分出 材質
        Mtl = needValue(1)
            If Mtl = "" Then
                Mtl = "A36"
            Else
                Mtl = needValue(1)
                Select Case Mtl
                
                Case "(A)"
                    Mtl = "A36/SS400"
                Case "(S)"
                    Mtl = "SUS304"
                Case Else
                   Exit Sub
                End Select
        
        
        
            End If
        
        
        ' 具有雙向制約檢測
        ' 如果denote "D" = 3/4" H >1000 Then 1.5"_Sch80 else 1"_Sch80
        ' 如果denote "D" = 1" H >1000 Then 1.5"_Sch80 else 1"_Sch80
        ' 如果denote "D" = 1.5" H >1000 Then 2"_Sch40 else 1..5"_Sch80
        ' 如果denote "D" = 2" = 2"_Sch40
        
        '實際換算出 所需主管 與 主管厚度
     Select Case PipeSize
        Case "1/2"
            If Third_Length_export > 1001 Then
                Main_Pipe_Size = "1.5"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
            Else
                Main_Pipe_Size = "1"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
                
            End If
        Case "3/4"
            If Third_Length_export > 1001 Then
                Main_Pipe_Size = "1.5"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
            Else
                Main_Pipe_Size = "1"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
                
            End If
        
        Case "1"
            If Third_Length_export > 1001 Then
                Main_Pipe_Size = "1.5"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
            Else
                Main_Pipe_Size = "1"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
                
            End If
        
        Case "1-1/2"
            If Third_Length_export > 1001 Then
                Main_Pipe_Size = "2"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
            Else
                Main_Pipe_Size = "1.5"
                Main_Pipe_Thickness = "80S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
                
            End If
        
         Case "2"

                Main_Pipe_Size = "2"
                Main_Pipe_Thickness = "40S"
                Set MainPipeDetails = CalculatePipeDetails(Main_Pipe_Size, Main_Pipe_Thickness)
        End Select
   
   '導入式: 管 -> M42 -> 獨特板子
                  
           '管子導入式
                  i = GetNextRowInColumnB()
            With ws
                .Cells(i, "B").value = 1 '項次
                .Cells(i, "C").value = "Pipe" '品名
                .Cells(i, "D").value = Main_Pipe_Size & """" & "*" & "SCH" & Replace(Main_Pipe_Thickness, "S", "") '尺寸厚度
                .Cells(i, "E").value = Main_Pipe_Length - 100 '長度
                .Cells(i, "G").value = Mtl '材值
                .Cells(i, "H").value = 1 '數量
                .Cells(i, "I").value = MainPipeDetails.Item("WeightPerMeter") '每米重
                .Cells(i, "J").value = .Cells(i, "E").value / 1000 * .Cells(i, "I").value '單重
                .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value '重量小計
                .Cells(i, "L").value = "M"
                .Cells(i, "M").value = 1 '組數
                .Cells(i, "N").value = .Cells(i, "H").value * .Cells(i, "M").value * .Cells(i, "E").value / 1000 '長度小計 組數*數量*長度/1000
                .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
                .Cells(i, "Q").value = "素材類"
            End With
               
            'M42 導入式 :
            '重新演算
            PipeSize = Main_Pipe_Size
            PerformActionByLetter letter, PipeSize
            
            'Spacer Plate 選用
            Plate_Size = 120
            Plate_Size_b = 80
            Plate_Thickness = 6
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '項次
                      .Cells(i, "C").value = "Plate"
                      .Cells(i, "D").value = Plate_Thickness
                      .Cells(i, "E").value = Plate_Size
                      .Cells(i, "F").value = Plate_Size_b
                      .Cells(i, "G").value = Mtl
                      .Cells(i, "H").value = 1
                      .Cells(i, "J").value = Weight_calculator
                      .Cells(i, "K").value = Weight_calculator
                      .Cells(i, "L").value = "PC"
                      .Cells(i, "M").value = 1
                      .Cells(i, "O").value = 1
                      .Cells(i, "P").value = Weight_calculator
                      .Cells(i, "Q").value = "鋼板類"
                  End With
            


            '特殊板選用
            ' 給定定義特殊板 Fig.A = 108_Fig_A_Plate
            Select Case Fig
            Case "Fig_A"
            Plate_Size = 120
            Plate_Size_b = 100
            Plate_Thickness = 9
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '項次
                      .Cells(i, "C").value = "108_Fig_A_Plate"
                      .Cells(i, "D").value = Plate_Thickness
                      .Cells(i, "E").value = Plate_Size
                      .Cells(i, "F").value = Plate_Size_b
                      .Cells(i, "G").value = Mtl
                      .Cells(i, "H").value = 1
                      .Cells(i, "J").value = Weight_calculator
                      .Cells(i, "K").value = Weight_calculator
                      .Cells(i, "L").value = "PC"
                      .Cells(i, "M").value = 1
                      .Cells(i, "O").value = 1
                      .Cells(i, "P").value = Weight_calculator
                      .Cells(i, "Q").value = "鋼板類"
                  End With
             
             Case "Fig_B"
            Plate_Size = 120
            Plate_Size_b = 100
            Plate_Thickness = 9
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '項次
                      .Cells(i, "C").value = "108_Fig_B_Plate"
                      .Cells(i, "D").value = Plate_Thickness
                      .Cells(i, "E").value = Plate_Size
                      .Cells(i, "F").value = Plate_Size_b
                      .Cells(i, "G").value = Mtl
                      .Cells(i, "H").value = 1
                      .Cells(i, "J").value = Weight_calculator
                      .Cells(i, "K").value = Weight_calculator
                      .Cells(i, "L").value = "PC"
                      .Cells(i, "M").value = 1
                      .Cells(i, "O").value = 1
                      .Cells(i, "P").value = Weight_calculator
                      .Cells(i, "Q").value = "鋼板類"
                  End With
             
             Case "Fig_C"
            Plate_Size = 65
            Plate_Size_b = 210
            Plate_Thickness = 9
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '項次
                      .Cells(i, "C").value = "108_Fig_C_Plate"
                      .Cells(i, "D").value = Plate_Thickness
                      .Cells(i, "E").value = Plate_Size
                      .Cells(i, "F").value = Plate_Size_b
                      .Cells(i, "G").value = Mtl
                      .Cells(i, "H").value = 1
                      .Cells(i, "J").value = Weight_calculator
                      .Cells(i, "K").value = Weight_calculator
                      .Cells(i, "L").value = "PC"
                      .Cells(i, "M").value = 1
                      .Cells(i, "O").value = 1
                      .Cells(i, "P").value = Weight_calculator
                      .Cells(i, "Q").value = "鋼板類"
                  End With


            End Select

End Sub
