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
          

    
    '��M42���
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    

    letter = GetThirdPartOfString(fullString)
    letter = Right(letter, 1)
    

    
    'Main_Pipe
    Third_Length_export = Replace(GetThirdPartOfString(fullString), letter, "") * 100
        ' �B�z�D�޻P���U�ު��s��:
            
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
    
    '�D�ު��׻P�ƺު��׺t��
    
    '�D�ު��� - �q�`��SUS304
        Main_Pipe_Length = L_Value + 100
        AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"

    '�T����T�ǤJ - �D�� - �ƺ� - ���O
          '�D��
            
            '�ƺު��� - �q�`��C12
            Support_Pipe_Length = Third_Length_export - 100
          
          '�����W�Y�ƺު��פp�󵥩�0 �h���L
          If Support_Pipe_Length > 0 Then
            '�ƺު��� - �q�`��C12
            '�ƺޫp�צr��ɥ����ݨD
            Pipe_ThickNess_mm = "SCH." & Replace(Pipe_ThickNess_mm, "S", "")
            Support_Pipe_Length = Third_Length_export - 100
            AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Support_Pipe_Length, "A53Gr.B"
           End If
    
    PipeSize = Replace(Support_Pipe_Size, "'", "")
    PerformActionByLetter letter, PipeSize
End Sub
Sub Type_05(ByVal fullString As String)
    '�d�Ү榡A : 20-L50-05L
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim letter As String
    Dim SectionType As String
    Dim Section_Dim As String
    Dim Total_Length As Double

    
   
    Set ws = Worksheets("Weight_Analysis")
    
    '�Ϥ��X���K�ؤo
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

    '�Ϥ��XM42����
        Support_05_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)
    '�Ϥ��X����"H"
         Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_05_Type_Choice_M42, "") * 100
         Section_Length_L = 130
         
       '�ഫ���������n�ݨD :
        letter = Support_05_Type_Choice_M42
        PipeSize = The_Section_Size

      
      
      '�ɤJFunction addSteelSectionEntry
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H + Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length
            PerformActionByLetter letter, PipeSize
End Sub
Sub Type_08(ByVal fullString As String)
    '�d�Ү榡A : 08-2B-1005G
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

    
    '���w�ޤؤo
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    '���wH&L ����
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    
    '��M42���
    letter = GetThirdPartOfString(fullString)
    letter = Right(letter, 1)
    
    '�`�N �H�U����H�Ȭ��ȩw
    Pipe_Length_H_part = Replace(Right(GetThirdPartOfString(fullString), 3), letter, "") * 100
    
    '�D�ު��� - �q�`��SUS304
        
        ' �p���ںޤl�ݨD����
        PipeSize = GetLookupValue(PipeSize)
        BpLength = 6
        SL = Replace(Left(Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 7, False), 4), "C", "")  'For the section Length
        BTLength = Application.WorksheetFunction.VLookup(PipeSize, ws_M42.Range("A:K"), 11, False) 'For the M42 Plate Thickness
        
        ' �p��ޤl�p��
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

    '�T����T�ǤJ - �D�� - ���c - Plate(wing) - Plate(STOPPER) - Plate(BASE PLATE) - Plate(TOP)


'�ɤJ����
        Main_Pipe_Length = Pipe_Length_H_part - BpLength - SL / 2 - BTLength
        AddPipeEntry PipeSize, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
        
'�ɤJ���c

            The_Section_Size = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 7, False) 'N
            SectionType = "Channel"
       
'�ɤJFunction addSteelSectionEntry
            
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length

'�ɤJFunction PerformActionByLetter-M42
            
            PerformActionByLetter letter, PipeSize

'�ɤJ14-Tpye�S���ݩ� : Plate(STOPPER)_08Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 4, False) 'K
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 5, False) 'M
            Plate_Thickness = 6
            Plate_Name = "Plate(STOPPER)_08Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'�ɤJ14-Tpye�S���ݩ� : Plate(TOP)_08Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 6, False) 'B
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_08_Table.Range("A:G"), 6, False) 'B
            Plate_Thickness = 6
            Plate_Name = "Plate(TOP)_08Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

End Sub
Sub Type_09(ByVal fullString As String)
    ' �d�Ү榡A : 09-2B-05B
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

    ' ��M42���
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    letter = GetThirdPartOfString(fullString)
    letter = Right(letter, 1)

    ' Main_Pipe
    Third_Length_export = Replace(GetThirdPartOfString(fullString), letter, "") * 100
    
    ' �B�z�D�޻P���U�ު��s��:
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

    ' �D�ު��׻P�ƺު��׺t��
    
    ' �T����T�ǤJ - �D�� - �ƺ� - ���O - Machine Bolt
    
    ' �D�ު��� - �q�`��SUS304
    Main_Pipe_Length = L_Value + 100
    AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
            
    ' �ƺު��� - �q�`��C12
    Support_Pipe_Length = Third_Length_export - 100
          
    ' �����W�Y�ƺު��פp�󵥩�0 �h���L
    If Support_Pipe_Length > 0 Then
        ' �ƺު��� - �q�`��C12
        ' �ƺޫp�צr��ɥ����ݨD
        Pipe_ThickNess_mm = "SCH." & Replace(Pipe_ThickNess_mm, "S", "")
        Support_Pipe_Length = Third_Length_export - 100
        AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Support_Pipe_Length, "A53Gr.B"
    End If

    PipeSize = Replace(Support_Pipe_Size, "'", "")
    PerformActionByLetter letter, PipeSize
       
    ' �ɤJ09-Tpye�S���ݩ� : Machine Bolt
    ' ��R�ƾ�
    i = GetNextRowInColumnB()
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "MACHINE BOLT"
        .Cells(i, "D").value = "1-5/8""""*150L"
        .Cells(i, "G").value = "A307Gr.B(�����N)"
        .Cells(i, "H").value = 1
        .Cells(i, "J").value = 20 ' ���]�C�����ꪺ��ӭ��q�O20�]�i�H�ھڹ�ڱ��p�վ�^
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
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
          

    '-------------------------------�����-------------------------------------------
    '�� Support Line Size "A" �Ʀr
    PartString_Type = GetPartOfString(fullString, 2, "-")
    PipeSize = Replace(PartString_Type, "B", "")
    
    '���M42���аO
    letter = GetPartOfString(fullString, 3, "-")
    letter = Right(letter, 1)
    
    '���H��
    H_Value = Replace(GetPartOfString(fullString, 3, "-"), letter, "")
    
    '���"D"�� - Machine Bolt Length
    D_Value = GetPartOfString(fullString, 4, "-")
    
    
    ' ���L��
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
    '-------------------------------��z��-------------------------------------------
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




    '-------------------------------�ɤJ��-------------------------------------------
    '�D�ު��� - �q�`��SUS304
    Main_Pipe_Length = L_Value + 100
    AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
    '��ު��� - �q�`��"A53Gr.B"
    AddPipeEntry anotherbuttompipeSize, anotherbuttompipeThickNess_mm, anotherbuttompipelegth, "A53Gr.B"
    ' ���O��
    PipeSize = Replace(Support_Pipe_Size, "'", "")
    PerformActionByLetter letter, PipeSize
    ' �ɤJ11-Tpye�S���ݩ� : Machine Bolt
    i = GetNextRowInColumnB() '�B��Function���o�U�@�檺��m
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "MACHINE BOLT"
        .Cells(i, "D").value = "1-5/8""""*300L"
        .Cells(i, "G").value = "A307Gr.B(�����N)"
        .Cells(i, "H").value = 1
        .Cells(i, "J").value = 20 ' ���]�C�����ꪺ��ӭ��q�O20�]�i�H�ھڹ�ڱ��p�վ�^
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
    End With
    i = GetNextRowInColumnB() '�B��Function���o�U�@�檺��m
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "washer"
        .Cells(i, "D").value = "92*9t*50"
        .Cells(i, "G").value = "A307Gr.B(�����N)"
        .Cells(i, "H").value = 2
        .Cells(i, "J").value = 1 ' ���]�C�����ꪺ��ӭ��q�O1�]�i�H�ھڹ�ڱ��p�վ�^
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
    End With
    i = GetNextRowInColumnB() '�B��Function���o�U�@�檺��m
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "Spring"
        .Cells(i, "D").value = Spring_Wire & "W" & Spring_ID & "ID"
        .Cells(i, "G").value = Spring_Matirial
        .Cells(i, "H").value = 2
        .Cells(i, "J").value = 1 ' ���]�C�����ꪺ��ӭ��q�O1�]�i�H�ھڹ�ڱ��p�վ�^
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
    End With
End Sub
Sub Type_14(ByVal fullString As String)
    '�d�Ү榡A : 14-2B-1005
    
    Dim PartString_Type As String ' �Ω��x�s���Ϋ᪺�r�곡��
    Dim PipeSize As String ' �ޤؤo�r��A�Ω�d��M�p��
    Dim letter As String ' �i��Ω��x�s�q�r�괣�����r��
    Dim pi As Double ' ��P�v�A�i��Ω�p��A�q�`�Τ��ر`�qMath.Pi�N��
    Dim SectionType As String ' ���w�I�������A�p��Channel��
    Dim Section_Dim As String ' �I���ؤo�A�Ω���c����
    Dim Total_Length As Double ' �`���סA�i��Ω���c�ΪO�������׭p��
    Dim BoltSize As String ' ����ؤo�A�Ω�����������J
    Dim Support_Pipe_Size As String ' �伵�ޤؤo�A�p�G������
    Dim Pipe_ThickNess_mm As String ' �޾��p�סA�Ω�p��μ���
    Dim Main_Pipe_Length As Double ' �D�ު��סA�Ω�p��ާ�����
    Dim Support_Pipe_Length As Double ' �伵�ު��סA�p�G������
    '...
    ' �H�U�ܶq�Ω� MainAddPlate �L�{
    Dim Plate_Size_a As Double ' �O�������פؤo
    Dim Plate_Size_b As Double ' �O�����e�פؤo
    Dim Plate_Thickness As Double ' �O�����p��
    Dim Plate_Name As String ' �O�����R�W�A�Ω���Ѥ��P�O��
    
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    Set Type_14_Table = Worksheets("For_14_Type_data")

    
    '���w�ޤؤo
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    '���wH&L ����
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '�`�N �H�U����H�Ȭ��ȩw
    Pipe_Length_H_part = Right(GetThirdPartOfString(fullString), 2) * 100
    
    '�D�ު��� - �q�`��SUS304
        
        ' �p���ںޤl�ݨD����
        PipeSize = GetLookupValue(PipeSize)
        BpLength = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
        SL = Replace(Left(Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 12, False), 4), "C", "")  'N
        BTLength = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
        ' �p��ޤl�p��
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

    '�T����T�ǤJ - �D�� - ���c - Plate(wing) - Plate(STOPPER) - Plate(BASE PLATE) - Plate(TOP)


'�ɤJ����
        Main_Pipe_Length = Pipe_Length_H_part - BpLength - SL - BTLength
        AddPipeEntry PipeSize, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
        
'�ɤJ���c


            The_Section_Size = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 12, False)
            SectionType = "Channel"
       '�ɤJFunction addSteelSectionEntry
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length

'�ɤJ14-Tpye�S���ݩ� : Plate(wing)_14Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 9, False) 'Q
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 8, False) 'P
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
            Plate_Name = "Plate(wing)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'�ɤJ14-Tpye�S���ݩ� : Plate(STOPPER)_14Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 7, False) 'M
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 6, False) 'K
            Plate_Thickness = 6
            Plate_Name = "Plate(STOPPER)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'�ɤJ14-Tpye�S���ݩ� : Plate(BASE PLATE)_14Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 2, False) 'C
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 2, False) 'C
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
            Plate_Name = "Plate(BASE PLATE)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'�ɤJ14-Tpye�S���ݩ� : Plate(TOP)_14Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 11, False) 'C
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 11, False) 'C
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 5, False) 'F
            Plate_Name = "Plate(TOP)_14Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
'�ɤJ14-Tpye�S���ݩ� : EXP.BOLT
' ��R�ƾ�
   BoltSize = Application.WorksheetFunction.VLookup(PipeSize, Type_14_Table.Range("A:L"), 10, False) 'J
 i = GetNextRowInColumnB()
    With ws
        .Cells(i, "B").value = .Cells(i - 1, "B").value + 1
        .Cells(i, "C").value = "EXP.BOLT"
        .Cells(i, "D").value = "'" & BoltSize & """"
        .Cells(i, "G").value = "SUS304"
        .Cells(i, "H").value = 4
        .Cells(i, "J").value = 1 ' ���]�C�����ꪺ��ӭ��q�O1�]�i�H�ھڹ�ڱ��p�վ�^
        .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value
        .Cells(i, "L").value = "SET"
        .Cells(i, "M").value = 1
        .Cells(i, "O").value = .Cells(i, "M").value * .Cells(i, "H").value
        .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
        .Cells(i, "Q").value = "������"
    End With


End Sub
Sub Type_15(ByVal fullString As String)
    '�d�Ү榡A : 15-2B-1005
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
    
    ' �H�U�ܶq�Ω� MainAddPlate �L�{
    Dim Plate_Size_a As Double ' �O�������פؤo
    Dim Plate_Size_b As Double ' �O�����e�פؤo
    Dim Plate_Thickness As Double ' �O�����p��
    Dim Plate_Name As String ' �O�����R�W�A�Ω���Ѥ��P�O��
    
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    Set Type_15_Table = Worksheets("For_15_Type_data")

    
    '���w�ޤؤo
    PartString_Type = GetSecondPartOfString(fullString)
    PipeSize = Replace(PartString_Type, "B", "")
    '���wH&L ����
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '�`�N �H�U����H�Ȭ��ȩw
    Pipe_Length_H_part = Right(GetThirdPartOfString(fullString), 2) * 100
    
    '�D�ު��� - �q�`��SUS304
        
        ' �p���ںޤl�ݨD����
        PipeSize = GetLookupValue(PipeSize)
        BpLength = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
        SL = Replace(Left(Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:L"), 9, False), 4), "C", "")  'N
        BTLength = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
        ' �p��ޤl�p��
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

    '�T����T�ǤJ - �D�� - ���c - Plate(wing) - Plate(STOPPER) - Plate(BASE PLATE) - Plate(TOP)


'�ɤJ����
        Main_Pipe_Length = Pipe_Length_H_part - BpLength - SL - BTLength
        AddPipeEntry PipeSize, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"
        
'�ɤJ���c


               The_Section_Size = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 9, False) 'N
               SectionType = "Channel"
       '�ɤJFunction addSteelSectionEntry
            SectionType = SectionType
            Section_Dim = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length

'�ɤJ15-Tpye�S���ݩ� : Plate(wing)_15Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 7, False) 'Q
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 6, False) 'P
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
            Plate_Name = "Plate(wing)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'�ɤJ15-Tpye�S���ݩ� : Plate(STOPPER)_15Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 5, False) 'M
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 4, False) 'K
            Plate_Thickness = 6
            Plate_Name = "Plate(STOPPER)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
'�ɤJ15-Tpye�S���ݩ� : Plate(BASE PLATE)_15Type
' ��R�ƾ�
            PipeSize = GetLookupValue(PipeSize)
            Plate_Size_a = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 2, False) 'D
            Plate_Size_b = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 2, False) 'D
            Plate_Thickness = Application.WorksheetFunction.VLookup(PipeSize, Type_15_Table.Range("A:I"), 3, False) 'F
            Plate_Name = "Plate(BASE PLATE)_15Type"
            MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name

'�ɤJ15-Tpye�S���ݩ� : Plate(TOP)_15Type
' ��R�ƾ�
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
    Dim Plate_Size_a As Double ' �O�������פؤo
    Dim Plate_Size_b As Double ' �O�����e�פؤo
    Dim Plate_Thickness As Double ' �O�����p��
    Dim Plate_Name As String ' �O�����R�W�A�Ω���Ѥ��P�O��
    Dim PartString_Type As String
    Dim PipeSize As String
    Dim Third_Length_export As Double

    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")

    PrintStepCalculator "Type_16 - �}�l�B�z"

    PartString_Type = GetPartOfString(fullString, 2)
    PrintStepCalculator "Type_16 - ����ĤG�����r�Ŧ�: " & PartString_Type

    PipeSize = Replace(PartString_Type, "B", "")
    PrintStepCalculator "Type_16 - ����ޮ|: " & PipeSize

    Third_Length_export = GetPartOfString(fullString, 3) * 100
    PrintStepCalculator "Type_16 - ����ĤT�����r�Ŧ�: " & Third_Length_export

       ' �B�z�D�޻P���U�ު��s��:
            
            Select Case PipeSize
               Case 2
                Support_Pipe_Size = "'1.5"
                Pipe_ThickNess_mm = "SCH.80"
                Plate_Size = 70
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 2, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
                
               Case 3
                Support_Pipe_Size = "'2"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 80
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 3, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
               
               Case 4
                Support_Pipe_Size = "'3"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 110
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 4, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 6
                Support_Pipe_Size = "'4"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 140
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 6, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 8
                Support_Pipe_Size = "'6"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 190
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 8, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 10
                Support_Pipe_Size = "'8"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 240
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 10, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 12
                Support_Pipe_Size = "'10"
                Pipe_ThickNess_mm = "SCH.40"
                Plate_Size = 290
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 12, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 14
                Support_Pipe_Size = "'12"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 340
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 14, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
                
               Case 16
                Support_Pipe_Size = "'12"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 340
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 16, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

               Case 18
                Support_Pipe_Size = "'14"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 380
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 18, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
                
                Case 20
                Support_Pipe_Size = "'14"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 380
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 20, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size

                Case 24
                Support_Pipe_Size = "'16"
                Pipe_ThickNess_mm = "STD.WT"
                Plate_Size = 430
                PrintStepCalculator "Type_16 - �B�z�D�޻P���U�ު��s��: 24, Support_Pipe_Size: " & Support_Pipe_Size & ", Pipe_ThickNess_mm: " & Pipe_ThickNess_mm & ", Plate_Size: " & Plate_Size
    Case Else
        Exit Sub
End Select

    PrintStepCalculator "Type_16 - �}�l�p��޹D�Ӹ`"
    Set PipeDetails = CalculatePipeDetails(PipeSize, "10S")
    
    PrintStepCalculator "Type_16 - �}�l�p��D�n�޹D����"
    Main_Pipe_Length = Round((PipeSize * 1.5 * 25.4) + (PipeDetails.Item("DiameterInch") / 2) + 100)

    PrintStepCalculator "Type_16 - �}�l�p��伵�޹D����"
    Support_Pipe_Length = Round(Third_Length_export - (PipeDetails.Item("DiameterInch") / 2) - 100 + 300)

    PrintStepCalculator "Type_16 - �}�l�i�J�K�[�޹D�Ӹ` - �D��, �h�B�Ӹ` �޹D���| : " & Support_Pipe_Size & ", �޹D�p�� : " & Pipe_ThickNess_mm & ", �޹D���� : " & Main_Pipe_Length
    AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Main_Pipe_Length, "SUS304"


    If Support_Pipe_Length > 0 Then
        Pipe_ThickNess_mm = "SCH." & Replace(Pipe_ThickNess_mm, "S", "")
        PrintStepCalculator "Type_16 - �}�l�i�J�K�[�޹D�Ӹ` - �伵��, �h�B�Ӹ` �޹D���| : " & Support_Pipe_Size & ", �޹D�p�� : " & Pipe_ThickNess_mm & ", �޹D���� : " & Support_Pipe_Length
        AddPipeEntry Support_Pipe_Size, Pipe_ThickNess_mm, Support_Pipe_Length, "A53Gr.B"
    Else
        PrintStepCalculator "Type_16 - �伵�ު��׬�0�A���K�[�伵��"
    End If

    PrintStepCalculator "Type_16 - �}�l�K�[�O��"
    Plate_Size_a = Plate_Size
    Plate_Size_b = Plate_Size
    Plate_Thickness = 6
    Plate_Name = "Plate"
    PrintStepCalculator "Type_16 - �}�l�K�[�O�� - �O���ؤo : " & Plate_Size_a & " x " & Plate_Size_b & " x " & Plate_Thickness
    MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name
    PrintStepCalculator "Type_16 - Plate added successfully"

End Sub
Sub Type_20(ByVal fullString As String)
    '�d�Ү榡A : 20-L50-05A
    ' ----------------------------------------------------------------------------------------
    ' |                             �l�{�� Type_20 �\��y�z                                   |
    ' | ------------------------------------------------------------------------------------- |
    ' | - ���e : �B�z�S�w�榡���r�Ŧ�A�������c�ؤo�M������T�C                               |
    ' | - ���e�C���`�[ : �������c�ؤo (Size)�B���� (Type)�A�p����� (Total_Length)�C          |
    ' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)                               |
    ' |                       GetSectionDetails(PartString_Type)                              |
    ' |                       GetThirdPartOfString(fullString)                                |
    ' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)|
    ' | - ���~�B�z        :  �ˬdFig�������X�k�ʡC                                           |
    ' | -2023/12/26 : �P�w������                                                              |
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

    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' �Ϥ��XFig����
    Support_20_Type_Choice = Right(GetThirdPartOfString(fullString), 1)

    ' ���~�B�z
    If IsNumeric(Support_20_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If

    ' �Ϥ��X����"H"
    Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_20_Type_Choice, "") * 100

    ' �ɤJ Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length


End Sub

Sub Type_21(ByVal fullString As String)
    '�d�Ү榡A : 21-L50-05A
    '�d�Ү榡B : 21-L50-05C-07
' ----------------------------------------------------------------------------------------
' |                             �l�{�� Type_21 �\��y�z                                     |
' | -------------------------------------------------------------------------------------   |
' | - ���e : �B�z�S�w�榡���r�Ŧ�ô������c�ؤo�M������T�C                                 |
' | - ���e�C���`�[ : �������c�ؤo (Size)�B���� (Type)�A�p���`���� (Total_Length)�C          |
' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)                                 |
' |                       GetSectionDetails (PartString_Type)                               |
' |                       GetThirdPartOfString (fullString)                                 |
' |                       GetFourthPartOfString(fullString)                                 |
' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length) |
' |                                                                                         |
' | - ���~�B�z         :  �ˬd���c�ǰt���BFig�����X�k�ʡB�Ʀr�榡�B�r�ơC                   |
' | -2023/12/26        :  �P�w������                                                        |
' ------------------------------------------------------------------------------------------

    ' �ŧi�ܼ�
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
    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (���~�B�z)[����] �ˬd�O�_���ǰt�� @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
    
    
    
    '-----------------------------------------------------------------------------------

    ' �Ϥ��XFig����
    Support_21_Type_Choice = Right(GetThirdPartOfString(fullString), 1)

    ' (���~�B�z)[Fig�����Ϊ�M42] �ˬd�O�_���Ʀr @ 514
    If IsNumeric(Support_21_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    
    '-----------------------------------------------------------------------------------
    
    ' �Ϥ��X����"H"
    Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_21_Type_Choice, "") * 100
    

    ' (���~�B�z)[�r�ƧPŪ] �ˬd�O�_�t3�X @ 515
    If Len(GetThirdPartOfString(fullString)) < 3 Then
        Err.Raise Number:=vbObjectError + 515, _
                  Description:="Len Value < 3 " & fullString
    End If
    '-----------------------------------------------------------------------------------

    ' �Ϥ��X����"L"
    Select Case Support_21_Type_Choice
        Case "A"
            Section_Length_L = 300
        Case "B"
            Section_Length_L = 500
        Case "C"
            Section_Length_L = GetFourthPartOfString(fullString) * 100
    End Select

   
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length

End Sub
   

Sub Type_22(ByVal fullString As String)
    '�d�Ү榡A : 22-L50-05A(L)
    '�d�Ү榡B : 21-L50-05(L)C-07
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
' |                             �l�{�� Type_22 �\��y�z                                                                           |
' | -------------------------------------------------------------------------------------   |
' | - ���e : �˦Q�����c�C                                                                                                                |
' | - ���e�C���`�[ : (���cH) -> (���cV)�C                                                                                 |
' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)                                              |
' |                       GetSectionDetails (PartString_Type)                                                           |
' |                       GetThirdPartOfString (fullString)                                                                  |
' |                       GetFourthPartOfString(fullString)                                                                 |
' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length) |
' |                                                                                                                                                          |
' | - �㦳Second , Third , Forth ���~�PŪ                                                                                    |
' |                                                                                                                                                          |
' |                                                                                                                                                         |
' | -2023/12/26 : �P�w������                                                                                                        |
' ----------------------------------------------------------------------------------------
   
    
    
    Set ws = Worksheets("Weight_Analysis")
    
    ' ----------------------------------<<<Action area>>>------------------------------------------
    '----------------------------------------------------------------------------------------------
    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (���~�B�z)[����] �ˬd�O�_���ǰt�� @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
                  
                  
                  
    '----------------------------------------------------------------------------------------------
    '�Ϥ��XFig����
    Support_22_Type_Choice = Mid(Right(GetThirdPartOfString(fullString), 3), 1, 1)
    
    ' (���~�B�z)[�S��Fig����] �ˬd�榡�O�_���T @ 514
    If Not (Support_22_Type_Choice = "A" Or Support_22_Type_Choice = "B" Or Support_22_Type_Choice = "C") Then
        If Not (Left(Support_22_Type_Choice, 1) = "(" And Right(Support_22_Type_Choice, 1) = ")") Then
            Err.Raise Number:=vbObjectError + 514, _
                      Description:="Invalid format for Fig type in " & fullString
        End If
    End If
    '---------------------------------------------------------------------------------------------------------------
        
        
    '----------------------------------------------------------------------------------------------
    '�Ϥ��XM-42����
    Support_22_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)
    
    ' (���~�B�z)[M-42����] �ˬd�榡�O�_���T @ 514
    If Not Left(Right(GetThirdPartOfString(fullString), 2), 1) = ")" Or Not (Support_22_Type_Choice_M42 Like "[A-Za-z]") Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Invalid format for M-42 type in " & fullString
    End If

    '----------------------------------------------------------------------------------------------
    
    
    ' �Ϥ��X����"H"
    '�װťX Replace �޿� for ����
        Type_22_Replace_A = "(" & Support_22_Type_Choice & ")"
        Type_22_Replace_B = Support_22_Type_Choice_M42
        Section_Length_H = Replace(Replace(GetThirdPartOfString(fullString), Type_22_Replace_A, ""), Type_22_Replace_B, "") * 100
        
    
    ' �Ϥ��X����"L"
    Select Case Support_22_Type_Choice
        Case "A"
            Section_Length_L = 300
        Case "B"
            Section_Length_L = 500
        Case "C"
            Section_Length_L = GetFourthPartOfString(fullString) * 100
    End Select
      
      '�ഫ���������n�ݨD :
        letter = Support_22_Type_Choice_M42
        PipeSize = The_Section_Size
      
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
            PerformActionByLetter letter, PipeSize
      '�ɤJFunction addSteelSectionEntry
            
End Sub
Sub Type_23(ByVal fullString As String)
    '�d�Ү榡A : 23-L50-05A
    '�d�Ү榡B : 23-L50-05C-07
' ----------------------------------------------------------------------------------------
' |                             �l�{�� Type_23 �\��y�z                                     |
' | -------------------------------------------------------------------------------------   |
' | - ���e : �˦Q�����c�C                                                                   |
' | - ���e�C���`�[ : (���cH) -> (���cV)�C                                                   |
' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)                                 |
' |                       GetSectionDetails (PartString_Type)                               |
' |                       GetThirdPartOfString (fullString)                                 |
' |                       GetFourthPartOfString(fullString)                                 |
' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length) |
' |                                                                                         |
' | - �㦳Second , Third , Forth ���~�PŪ                                                   |
' |                                                                                         |
' |                                                                                         |
' | -2023/12/26 : �P�w������                                                                |
' ----------------------------------------------------------------------------------------
    ' �ŧi�ܼ�
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
    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (���~�B�z)[����] �ˬd�O�_���ǰt�� @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
    
    
    
    '-----------------------------------------------------------------------------------

    ' �Ϥ��XFig����
    Support_23_Type_Choice = Right(GetThirdPartOfString(fullString), 1)

    ' (���~�B�z)[Fig�����Ϊ�M42] �ˬd�O�_���Ʀr @ 514
    If IsNumeric(Support_23_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    
    '-----------------------------------------------------------------------------------
    
    ' �Ϥ��X����"H"
    Section_Length_H = Replace(GetThirdPartOfString(fullString), Support_23_Type_Choice, "") * 100 + Mid(GetSecondPartOfString(fullString), 2, 99)
    

    ' (���~�B�z)[�r�ƧPŪ] �ˬd�O�_�t3�X @ 515
    If Len(GetThirdPartOfString(fullString)) < 3 Then
        Err.Raise Number:=vbObjectError + 515, _
                  Description:="Len Value < 3 " & fullString
    End If
    '-----------------------------------------------------------------------------------

    ' �Ϥ��X����"L"
    Select Case Support_23_Type_Choice
        Case "A"
            Section_Length_L = 300
        Case "B"
            Section_Length_L = 500
        Case "C"
            Section_Length_L = GetFourthPartOfString(fullString) * 100
    End Select

   
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length

End Sub

Sub Type_24(ByVal fullString As String)
    '�d�Ү榡A : 24-L50-05

    ' ----------------------------------------------------------------------------------------
    ' |                             �l�{�� Type_24 �\��y�z                                   |
    ' | ------------------------------------------------------------------------------------- |
    ' | - ���e : �ѪR�S�w�榡���r�Ŧ�A�������c�H���C                                         |
    ' | - ���e�C���`�[ : �q�r�Ŧꤤ�������c�ؤo(Size)�M�p�����(Total_Length)�C               |
    ' | - �ΤF���X�Ө�� :  GetSecondPartOfString(fullString)                                 |
    ' |                     GetSectionDetails(PartString_Type)                                |
    ' |                     GetThirdPartOfString(fullString)                                  |
    ' | - �ΤF���X�Ӥl�{��:  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)|
    ' | - ���~�B�z        :  �ثe�L�S�w���~�B�z�C                                             |
    ' | - ���            :  2023/12/26                                                       |
    ' ----------------------------------------------------------------------------------------
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim The_Section_Size As String
    Dim SectionType As String
    Dim Section_Length_H As Double
    Dim Details As SectionDetails
    Dim Total_Length As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' �Ϥ��X����"H"
    Section_Length_H = GetThirdPartOfString(fullString) * 100

    ' �ɤJ Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length


End Sub

Sub Type_25(ByVal fullString As String)
    '�d�Ү榡A : 25-L50-0505A
     ' ----------------------------------------------------------------------------------------
    ' |                             �l�{�� Type_25 �\��y�z                                   |
    ' | ------------------------------------------------------------------------------------- |
    ' | - ���e : �ѪR�S�w�榡���r�Ŧ�H�B�z���c�H���C                                          |
    ' | - ���e�C���`�[ : �������c���ؤo(Size)�B����(Type)�A�íp�����(H, L)�C                  |
    ' | - �ΤF���X�Ө�� : GetSecondPartOfString(fullString)�BGetThirdPartOfString(fullString) |
    ' | - �ΤF���X�Ӥl�{�� : AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)  |
    ' | - ���~�B�z : �ˬd�����ǰt���MFig�������X�k�ʡC                                        |
    ' | - ��� : 2023/12/26                                                                  |
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
    '�d�Ү榡B : 25-L50-0505C-0401
    
   
    Set ws = Worksheets("Weight_Analysis")
    
    
    
    '----------------------------------------------------------------------------------------------
    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (���~�B�z)[����] �ˬd�O�_���ǰt�� @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '�Ϥ��XFig����
    Support_25_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' (���~�B�z)[Fig�����Ϊ�M42] �ˬd�O�_���Ʀr @ 514
    If IsNumeric(Support_25_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '�Ϥ��X"L"��
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '-----------------------------------------------------------------------------------
    
    
    '-----------------------------------------------------------------------------------
    '�Ϥ��X"H"��
    Section_Length_H = Replace(Right(GetThirdPartOfString(fullString), 3), Support_25_Type_Choice, "") * 100

    '-----------------------------------------------------------------------------------

    


      

      
      
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length

End Sub
Sub Type_26(ByVal fullString As String)
    '�d�Ү榡A : 26-L50-0505A
     ' ----------------------------------------------------------------------------------------
    ' |                             �l�{�� Type_26 �\��y�z
    ' | -------------------------------------------------------------------------------------
    ' | - ���e : �ѪR�S�w�榡���r�Ŧ�H�B�z���c�H���C
    ' | - ���e�C���`�[ : �������c���ؤo(Size)�B����(Type)�A�íp�����(H, L)�C
    ' | - �ΤF���X�Ө�� : GetSecondPartOfString(fullString)�BGetThirdPartOfString(fullString)
    ' | - �ΤF���X�Ӥl�{�� : AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
    ' | - ���~�B�z : �ˬd�����ǰt���MFig�������X�k�ʡC
    ' | - ��� : 2023/04/29
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
    '�d�Ү榡B : 26-L50-1005A
    
   
    Set ws = Worksheets("Weight_Analysis")
    
    
    
    '----------------------------------------------------------------------------------------------
    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (���~�B�z)[����] �ˬd�O�_���ǰt�� @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '�Ϥ��XFig����
    Support_26_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' (���~�B�z)[Fig�����Ϊ�M42] �ˬd�O�_���Ʀr @ 514
    If IsNumeric(Support_26_Type_Choice) Then
        Err.Raise Number:=vbObjectError + 514, _
                  Description:="Numeric value found where text was expected for " & fullString
    End If
    '-----------------------------------------------------------------------------------

    
    '-----------------------------------------------------------------------------------
    '�Ϥ��X"L"��
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100
    '-----------------------------------------------------------------------------------
    
    
    '-----------------------------------------------------------------------------------
    '�Ϥ��X"H"��
    Section_Length_H = Replace(Right(GetThirdPartOfString(fullString), 3), Support_26_Type_Choice, "") * 100 * 2

    '-----------------------------------------------------------------------------------
     
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
 
End Sub
Sub Type_27(ByVal fullString As String)
    '�d�Ү榡A : 27-L50-0505A-0402
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
    
        
                                  
        
    '�Ϥ��X���K�ؤo
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
            
                  

    '�Ϥ��XM-42����
        Support_27_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)

    '�Ϥ��X����"H"
        Section_Length_H_1 = Right(Replace(GetThirdPartOfString(fullString), Support_27_Type_Choice_M42, ""), 2) * 100
        Section_Length_H_2 = 15
        Section_Length_H = Section_Length_H_1 - Section_Length_H_2
        
        
    '�Ϥ��X����"L"
        Section_Length_L = Left(Replace(GetThirdPartOfString(fullString), Support_27_Type_Choice_M42, ""), 2) * 100
        

      '�ഫ���������n�ݨD :
        letter = Support_27_Type_Choice_M42
        PipeSize = The_Angle_Size
      
      '�ɤJFunction addSteelSectionEntry
            
            SectionType = SectionType
            Section_Dim = Replace(The_Angle_Size, Left(The_Angle_Size, 1), "")
            Total_Length = Section_Length_H + Section_Length_L
            AddSteelSectionEntry SectionType, Section_Dim, Total_Length
            PerformActionByLetter letter, PipeSize

 
 If SectionType = "H Beam" Then
 
 '�p�G�OH Bean ���� �h�ϥΥH�U
 '�ɤJ27-Tpye�S���ݩ� : Plate(Wing)_27Type
' ��R�ƾ�
            Plate_Size_a = 200
            Plate_Size_b = 100
            Plate_Thickness = 9
            Weight_calculator = Plate_Size_a / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '����
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
                      .Cells(i, "Q").value = "���O��"
                  End With
            
  Else
  End If
  
End Sub
Sub Type_28(ByVal fullString As String)
    ' �d�Ү榡A : 28-L50-1005L

    ' �ŧi�ܼ�
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

    ' �]�m�u�@��ޥ�
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
    
    ' �Ϥ��X���K�ؤo
    PartString_Type = GetSecondPartOfString(fullString)

    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' �p�G�����ǰt���A�h�h�X�l�{��
    End If

    '�Ϥ��XM-42����
        Support_28_Type_Choice_M42 = Right(GetThirdPartOfString(fullString), 1)
    
    ' �Ϥ��X "H" ��
        Section_Length_H = Replace(Right(GetThirdPartOfString(fullString), 3), Support_28_Type_Choice_M42, "") * 100 * 2
    ' �Ϥ��X "L" ��
        Section_Length_L = Left(GetThirdPartOfString(fullString), 2)
        
        letter = Support_28_Type_Choice_M42
        PipeSize = The_Section_Size
        
    ' �ɤJ Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
    PerformActionByLetter letter, PipeSize
End Sub
Sub Type_30(ByVal fullString As String)
    ' �d�Ү榡A : 30-L50-0505A
    ' �d�Ү榡B : 30-L50-0505A-0401

    ' �ŧi�ܼ�
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

    ' �]�m�u�@��ޥ�
    Set ws = Worksheets("Weight_Analysis")

    ' �Ϥ��X���K�ؤo
    PartString_Type = GetSecondPartOfString(fullString)

    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' �p�G�����ǰt���A�h�h�X�l�{��
    End If

    ' �Ϥ��X Fig ����
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

    ' �Ϥ��X "L" ��
    Section_Length_L = Replace(Right(GetThirdPartOfString(fullString), 3), Support_30_Type_Choice, "") * 100

    ' �ɤJ Function addSteelSectionEntry
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_31(ByVal fullString As String)
    '�d�Ү榡A : 31-L50-05A
    '�d�Ү榡B : 31-L50-05C-07
' ----------------------------------------------------------------------------------------
' |                             �l�{�� Type_31 �\��y�z
' | -------------------------------------------------------------------------------------
' | - ���e : �˦Q�����c�C
' | - ���e�C���`�[ : (���cH) -> (���cV)�C
' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)
' |                       GetSectionDetails (PartString_Type)
' |                       GetThirdPartOfString (fullString)
' |                       GetFourthPartOfString(fullString)
' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
' |
' | - �㦳Second , Third , Forth ���~�PŪ
' |
' |
' | -2024/04/29 : �P�w������
' ----------------------------------------------------------------------------------------
    ' ----------------------------------<<<�ŧi�ܼ�>>>-----------------------------------------------------------------
    ' �ŧi�ܼ�
    '# ���a�w�q���ܶq
    Dim ws As Worksheet                     ' �u�@��ѦҡA�Ω�X�ݩM�ާ@ "Weight_Analysis" �u�@��
    Dim The_Section_Size As String          ' �ΨӦs�x�q Details ���c����o���ؤo�H��
    Dim SectionType As String               ' �ΨӦs�x�q Details ���c����o�������H��
    Dim Total_Length As Double              ' �Ψӭp��M�s�x�����c���`����
    Dim Section_Length_H As Double          ' �Ω�s�x�M�p������c��������������
    Dim Section_Length_L As Double          ' �Ω�s�x�M�p������c��������������
    Dim Support_31_Type_Choice As String    ' �Ω�s�x�B�~��������ܩ�������ܡA�i��ӦۥΤ��J�Ψ�L�p��
    '# �q��L��ƩΤl�{�ǽեΪ��ܶq
    Dim PartString_Type As String           ' �q GetSecondPartOfString(fullString) ��o���r�Ŧ곡��
    Dim Details As SectionDetails           ' �q GetSectionDetails(PartString_Type) ��o������ؤo�M����
    Dim lengthStrH As String                ' �q GetThirdPartOfString(fullString) ��o���r�Ŧ�A�N������c���׳���
    Dim lengthStrL As String                ' �q GetFourthPartOfString(fullString) ��o���r�Ŧ�A�N������c���׳����]�p�G�A�Ρ^


   '---------------------------------------------------------------------------------------------------------------------
 
    ' ----------------------------------<<<Action area>>>------------------------------------------
    '----------------------------------------------------------------------------------------------
    Set ws = Worksheets("Weight_Analysis")
    ' �Ϥ��X���c�ؤo
    PartString_Type = GetSecondPartOfString(fullString)
    Details = GetSectionDetails(PartString_Type)
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' (���~�B�z)[����] �ˬd�O�_���ǰt�� @ 513
    If The_Section_Size = "" And SectionType = "" Then
        Err.Raise Number:=vbObjectError + 513, _
                  Description:="No matching item found for " & fullString
    End If
    '-----------------------------------------------------------------------------------
    
    
    
    '-----------------------------------------------------------------------------------
    ' �ˬd lengthStrH �O�_�������B���Ʀr
    If GetThirdPartOfString(fullString) >= 3 Then
        ' �q�r�Ŧꤤ�������שM���׳���
        lengthStrL = Left(GetThirdPartOfString(fullString), 2)
        lengthStrH = Right(GetThirdPartOfString(fullString), 2)
        
        ' �ˬd�O�_�������Ʀr
        If IsNumeric(lengthStrH) And IsNumeric(lengthStrL) Then
            Section_Length_H = Val(lengthStrH) * 100 * 2 ' ���]�C�ӳ����100��������, DENOTE DIMENSION "H" (IN 100 mm)
            Section_Length_L = Val(lengthStrL) * 100  ' ���]�C�ӳ����100��������  DENOTE DIMENSION "L" (IN 100 mm)
        Else
            Err.Raise Number:=vbObjectError + 516, _
                      Description:="Non-numeric characters found in dimensions: " & fullString
        End If
    Else
        Err.Raise Number:=vbObjectError + 515, _
                  Description:="Length string is too short for valid processing: " & lengthStrH
    End If

   
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��

End Sub
Sub Type_32(ByVal fullString As String)
    '�d�Ү榡A : 32-L50-1005
    Dim SectionType As String
    Dim The_Section_Size As String ' �T�O���ܼƤw�Q�w�q
    Dim Total_Length As Double
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim Details As SectionDetails
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' �q fullString �����������r�Ŧ�
    PartString_Type = GetSecondPartOfString(fullString)

    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)

    ' ��s The_Section_Size �M SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' �p�G�����ǰt���A�h�h�X�l�{��
    End If

    
    ' �Ϥ��X "H" ��

    Section_Length_H = Right(GetThirdPartOfString(fullString), 2) * 100 * 2

    ' �Ϥ��X "L" ��
    
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100

    ' �ɤJ Function addSteelSectionEntry
    SectionType = SectionType
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_33(ByVal fullString As String)
    ' �ܨҮ榡A: 33-L50-1005
    ' ----------------------------------------------------------------------------------------
' |                             �l�{�� Type_33 �\��y�z
' | -------------------------------------------------------------------------------------
' | - ���e : �˦Q�����c�C
' | - ���e�C���`�[ : (���cH) -> (���cV)�C
' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)
' |                       GetSectionDetails (PartString_Type)
' |                       GetThirdPartOfString (fullString)
' |                       GetFourthPartOfString(fullString)
' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
' |
' | - �㦳Second , Third , Forth ���~�PŪ
' |
' |
' | -2024/04/29 : �P�w������
' ----------------------------------------------------------------------------------------
    ' ----------------------------------<<<�ŧi�ܼ�>>>-----------------------------------------------------------------
    '# ���a�w�q���ܶq
    Dim ws As Worksheet                     ' �u�@��ѦҡA�Ω�X�ݩM�ާ@ "Weight_Analysis" �u�@��
    Dim The_Section_Size As String          ' �ΨӦs�x�q Details ���c����o���ؤo�H��
    Dim SectionType As String               ' �ΨӦs�x�q Details ���c����o�������H��
    Dim Total_Length As Double              ' �Ψӭp��M�s�x�����c���`����
    Dim Section_Length_H As Double          ' �Ω�s�x�M�p������c��������������
    Dim Section_Length_L As Double          ' �Ω�s�x�M�p������c��������������
    '# �q��L��ƩΤl�{�ǽեΪ��ܶq
    Dim PartString_Type As String           ' �q GetSecondPartOfString(fullString) ��o���r�Ŧ곡��
    Dim Details As SectionDetails           ' �q GetSectionDetails(PartString_Type) ��o������ؤo�M����

    ' ��l�Ƥu�@��
    Set ws = Worksheets("Weight_Analysis")

    ' �q fullString �����������r�Ŧ�
    PartString_Type = GetSecondPartOfString(fullString)

    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)

    ' ��s The_Section_Size �M SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' �p�G�����ǰt�A�h�X�l�{��
    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub
    End If

    ' �p��H L����
    Section_Length_H = Right(GetThirdPartOfString(fullString), 2) * 100
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100

    ' �p���`����
    Total_Length = Section_Length_H + Section_Length_L

   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��
End Sub
Sub Type_34(ByVal fullString As String)
    ' �ܨҮ榡A: 34-L50-1005
    ' ----------------------------------------------------------------------------------------
' |                             �l�{�� Type_34 �\��y�z
' | -------------------------------------------------------------------------------------
' | - ���e : �˦Q�����c�C
' | - ���e�C���`�[ : (���cH) -> (���cV)�C
' | - �ΤF���X�Ө��   :  GetSecondPartOfString(fullString)
' |                       GetSectionDetails (PartString_Type)
' |                       GetThirdPartOfString (fullString)
' |                       GetFourthPartOfString(fullString)
' | - �ΤF���X�Ӥl�{�� :  AddSteelSectionEntry(SectionType, The_Section_Size, Total_Length)
' |
' | - �㦳Second , Third , Forth ���~�PŪ
' |
' |
' | -2024/04/29 : �P�w������
' ----------------------------------------------------------------------------------------
    ' ----------------------------------<<<�ŧi�ܼ�>>>-----------------------------------------------------------------
    '# ���a�w�q���ܶq
    Dim ws As Worksheet                     ' �u�@��ѦҡA�Ω�X�ݩM�ާ@ "Weight_Analysis" �u�@��
    Dim The_Section_Size As String          ' �ΨӦs�x�q Details ���c����o���ؤo�H��
    Dim SectionType As String               ' �ΨӦs�x�q Details ���c����o�������H��
    Dim Total_Length As Double              ' �Ψӭp��M�s�x�����c���`����
    Dim Section_Length_H As Double          ' �Ω�s�x�M�p������c��������������
    Dim Section_Length_L As Double          ' �Ω�s�x�M�p������c��������������
    '# �q��L��ƩΤl�{�ǽեΪ��ܶq
    Dim PartString_Type As String           ' �q GetSecondPartOfString(fullString) ��o���r�Ŧ곡��
    Dim Details As SectionDetails           ' �q GetSectionDetails(PartString_Type) ��o������ؤo�M����

    ' ��l�Ƥu�@��
    Set ws = Worksheets("Weight_Analysis")

    ' �q fullString �����������r�Ŧ�
    PartString_Type = GetSecondPartOfString(fullString)

    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)

    ' ��s The_Section_Size �M SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    ' �p�G�����ǰt�A�h�X�l�{��
    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub
    End If

    ' �p��H L����
    Section_Length_H = Right(GetThirdPartOfString(fullString), 2) * 100
    Section_Length_L = Left(GetThirdPartOfString(fullString), 2) * 100

    ' �p���`����
    Total_Length = Section_Length_H + Section_Length_L

   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��
End Sub
Sub Type_35(ByVal fullString As String)
    '�d�Ү榡A : 35-L50-05A
    '������
    
    Dim SectionType As String
    Dim The_Section_Size As String ' �T�O���ܼƤw�Q�w�q
    Dim Total_Length As Double
    Dim ws As Worksheet
    Dim PartString_Type As String
    Dim Details As SectionDetails
    Dim Section_Length_H As Double
    Dim Section_Length_L As Double
    
    Set ws = Worksheets("Weight_Analysis")

    ' �q fullString �������ĤG�����r�Ŧ�
    PartString_Type = GetSecondPartOfString(fullString)
    
    '�Ϥ��XFig����
        Support_35_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
        
    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)

    ' ��s The_Section_Size �M SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' �p�G�����ǰt���A�h�h�X�l�{��
    End If

 ' �Ϥ��X "H" ��
 Select Case Support_35_Type_Choice
    Case "A"
    
        Section_Length_H = Left(GetThirdPartOfString(fullString), 2) * 100
    Case "B"
        Section_Length_H = Left(GetThirdPartOfString(fullString), 2) * 100 * 2
    Case Else
        Exit Sub
    End Select
        
        
    ' �ɤJ Function addSteelSectionEntry
    SectionType = SectionType
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_37(ByVal fullString As String)
    '�d�Ү榡A : 37-C125-1200A-05
    '�d�Ү榡B : 37-C125-1200B-05
    
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

    ' �q fullString �������ĤG�����r�Ŧ� - �ĤG�������o�ѿ����O
    PartString_Type = GetSecondPartOfString(fullString)
    
    '�Ϥ��X�������� - �q fullString �������ĤT�����r�Ŧ�
        Support_37_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' �Ϥ��X "H" �� - �q fullString �������ĤT�����r�Ŧ� - �������Ĥ@����
        Section_Length_H_1 = Replace(GetThirdPartOfString(fullString), Support_37_Type_Choice, "")
        
    ' �ˬd�O�_�s�b�ĥ|�����r�Ŧ�
    If IsFourthPartAvailable(fullString) Then
        ' �s�b�ĥ|�����A�q fullString �������ĥ|�����r�Ŧ� - �������ĤG����
        Section_Length_H_2 = GetFourthPartOfString(fullString) * 100
    Else
        ' �ĥ|�������s�b�A�]�w�w�]��
        Section_Length_H_2 = 200
    End If
        
        
    '�Ϥ��X���װϧO
        'Angle_A = 30
        'Angle_B = 45
        
        If Support_37_Type_Choice = "A" Then
            Angle_Y = 60
            Angle_X = 30
        Else
            Angle_Y = 45
            Angle_X = 45
        End If
        
    ' �t��XL�� - �ݥ|�ӨB�J
        '���n���ܼ�
            Section_Length = Replace(GetSecondPartOfString(fullString), Left(GetSecondPartOfString(fullString), 1), "")
            pi = 4 * Atn(1) ' �p���P�v �k
            
            '�Ĥ@�B�J
                First_Step = Section_Length / 2 * Tan(Angle_Y * pi / 180)
            '�ĤG�B�J
                halfSection = Section_Length / 2
                Second_a_calculator = First_Step * First_Step
                Second_Step = Round(Sqr(Round(halfSection * halfSection) + Second_a_calculator))
            '�ĤT�B�J
                Third_a_calculator = Second_Step * Tan(Angle_X * pi / 180) * Second_Step * Tan(Angle_X * pi / 180)
                Third_b_calculator = Second_Step * Second_Step
                Third_Step = Round(Sqr(Third_a_calculator + Third_b_calculator))
            '�ĥ|�B�J
                Forth_a_calculator = Section_Length_H_1 * Tan(Angle_X * pi / 180) * Section_Length_H_1 * Tan(Angle_X * pi / 180)
                Forth_b_calculator = Section_Length_H_1 * Section_Length_H_1
                Forth_Step = Round(Sqr(Forth_a_calculator + Forth_b_calculator))
            
            Section_Length_L = Round(Third_Step + Forth_Step)
     ' �t��XH�� -
                Section_Length_H = Section_Length_H_1 + Section_Length_H_2
                
                
    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)

    ' ��s The_Section_Size �M SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' �p�G�����ǰt���A�h�h�X�l�{��
    End If


        
        
    ' �ɤJ Function addSteelSectionEntry
    SectionType = SectionType
    The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
    Total_Length = Section_Length_H + Section_Length_L
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
End Sub
Sub Type_39(ByVal fullString As String)
    '�d�Ү榡A : 39-C100-800A
    '�d�Ү榡B : 39-C125-1200B-05
    
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

    ' �q fullString �������ĤG�����r�Ŧ� - �ĤG�������o�ѿ����O
    PartString_Type = GetSecondPartOfString(fullString)
    
    '�Ϥ��X�������� - �q fullString �������ĤT�����r�Ŧ�
        Support_39_Type_Choice = Right(GetThirdPartOfString(fullString), 1)
    
    ' �Ϥ��X "H" �� - �q fullString �������ĤT�����r�Ŧ� - �������Ĥ@����
        Section_Length_H_1 = Replace(GetThirdPartOfString(fullString), Support_39_Type_Choice, "")
        
    ' �ˬd�O�_�s�b�ĥ|�����r�Ŧ�
    If IsFourthPartAvailable(fullString) Then
        ' �s�b�ĥ|�����A�q fullString �������ĥ|�����r�Ŧ� - �������ĤG����
        Section_Length_H_2 = GetFourthPartOfString(fullString) * 100
    Else
        ' �ĥ|�������s�b�A�]�w�w�]��
        Section_Length_H_2 = 200
    End If
        
        
    '�Ϥ��X���װϧO
        'Angle_A = 30
        'Angle_B = 45
        
        If Support_39_Type_Choice = "A" Then
            Angle_Y = 60
            Angle_X = 30
        Else
            Angle_Y = 45
            Angle_X = 45
        End If
        
    ' �t��XL�� - �ݥ|�ӨB�J
        '���n���ܼ�
            Section_Length = Replace(GetSecondPartOfString(fullString), Left(GetSecondPartOfString(fullString), 1), "")
            pi = 4 * Atn(1) ' �p���P�v �k
            
            '�Ĥ@�B�J
                First_Step = Section_Length / 2 * Tan(Angle_Y * pi / 180)
            '�ĤG�B�J
                halfSection = Section_Length / 2
                Second_a_calculator = First_Step * First_Step
                Second_Step = Round(Sqr(Round(halfSection * halfSection) + Second_a_calculator))
            '�ĤT�B�J
                Third_a_calculator = Second_Step * Tan(Angle_X * pi / 180) * Second_Step * Tan(Angle_X * pi / 180)
                Third_b_calculator = Second_Step * Second_Step
                Third_Step = Round(Sqr(Third_a_calculator + Third_b_calculator))
            '�ĥ|�B�J
                Forth_a_calculator = Section_Length_H_1 * Tan(Angle_X * pi / 180) * Section_Length_H_1 * Tan(Angle_X * pi / 180)
                Forth_b_calculator = Section_Length_H_1 * Section_Length_H_1
                Forth_Step = Round(Sqr(Forth_a_calculator + Forth_b_calculator))
            
            Section_Length_L = Round(Third_Step + Forth_Step)
     ' �t��XH�� -
                Section_Length_H = Section_Length_H_1 + Section_Length_H_2
                
                
    ' �ϥ� GetSectionDetails ��ƨ��N Select Case
    Details = GetSectionDetails(PartString_Type)

    ' ��s The_Section_Size �M SectionType
    The_Section_Size = Details.Size
    SectionType = Details.Type

    If The_Section_Size = "" And SectionType = "" Then
        Exit Sub ' �p�G�����ǰt���A�h�h�X�l�{��
    End If

   
   ' �ɤJ Function addSteelSectionEntry
        '�Ĥ@�ӾɤJH�� <����> �V
            The_Section_Size = Replace(The_Section_Size, Left(The_Section_Size, 1), "")
            Total_Length = Section_Length_H
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��
        '�ĤG�ӾɤJL�� <����> �V
            Total_Length = Section_Length_L
            AddSteelSectionEntry SectionType, The_Section_Size, Total_Length    ' �եΥH�K�[�����c���ب�u�@��

End Sub
Sub Type_48(ByVal fullString As String)
    '�d�Ү榡A : 48-1/2B(A)
    '�d�Ү榡B : 48-1B
    
Dim ws As Worksheet                          ' Excel �u�@���H�A�Ω�ޥΩM�ާ@�u�@�����ƾ�
Dim PartString_Type As String          ' �Ω�s�x�q fullString �������ĤG�����r�Ŧ�
Dim Plate_Name As String               ' �Ω�s�x�ͦ������O�W�١A�N�b MainAddPlate �l�{�Ǥ��ϥ�

Dim MatL As String                                 ' ���������A�i�H�O�ҿ��B�X�����Τ��׿��A�ھڬA�������аO�T�w
Dim Plate_Size_a As Double                ' ���O�����סA�q Plate_Size �r�Ŧꤤ�������ഫ�� Double ����
Dim Plate_Size_b As Double                ' ���O���e�סA�q Plate_Size �r�Ŧꤤ�������ഫ�� Double ����
Dim Plate_Thickness As Double          ' ���O���p�סA�q Plate_Size �r�Ŧꤤ�������ഫ�� Double ����

Dim needValue() As Variant                   ' �Ω�s�x�q PartString_Type ���������]�t�A�����r�Ŧ곡�������G
Dim Value0 As String                                 ' �q needValue(0) �����X���r�Ŧ�A���� "B" ����Ω�i�@�B�B�z
Dim Re_Size As Double                            ' �q Value0 �ഫ�έp��o�쪺�ؤo�ȡA�Ω�M�w Plate_Size �����

Dim Plate_Size As String                            ' �s�x���O�ؤo���r�Ŧ�A�榡�� "����*�e��*�p��"

    
    Set ws = Worksheets("Weight_Analysis")

    ' �q fullString �����������r�Ŧ�
    PartString_Type = GetPartOfString(fullString, 2)
    
    ' �ˬd�O�_�s�b�A���A�H�T�w�O�_�i�H���`��������
    ValueCondition = InStr(PartString_Type, "(")
    If ValueCondition > 0 Then
        needValue = ExtractParts(PartString_Type)
        ' �i��A�B�z needvalue(0) ; "B"�O�L�Ī�, �G�o���R���C1/2 & 3/4 & 1 1/2 Excel�ݤ���, �o���A�B�z
        Value0 = Replace(needValue(0), "B", "")
        ' �i��A�B�z needvalue(1) ; ��3�ӱ��� "None"= Carbon steel , "(A)" = Alloy steel , "(B)" = Stainless steel
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
        MatL = "A36/SS400" ' �S�����骺���Ƽ��ѡA�ϥιw�]��
    End If
    
    Select Case Value0
        Case "1/2"
            Re_Size = 0.5
        Case "3/4"
            Re_Size = 0.75
        Case "1 1/2"
            Re_Size = 1.5
        Case Else
            Re_Size = Val(Value0)  ' �����N�r�Ŧ��ഫ���ƭ�
    End Select
    
    If Re_Size <= 2 Then
        Plate_Size = "150*100*6"
    Else
        Plate_Size = "150*100*9"
    End If
    
    ' ���X�ݭn���ȵ���MainAddPlate
    Plate_Size_a = Val(GetPartOfString(Plate_Size, 1, "*"))
    Plate_Size_b = Val(GetPartOfString(Plate_Size, 2, "*"))
    Plate_Thickness = Val(GetPartOfString(Plate_Size, 3, "*"))
    Plate_Name = "Plate_48Type"
    
    ' �ɤJ MainAddPlate
    MainAddPlate Plate_Size_a, Plate_Size_b, Plate_Thickness, Plate_Name, MatL
End Sub

Sub Type_51(ByVal fullString As String)
    '�d�Ү榡A : 51-2B
    '2B  = Line Size

Dim Ssize As String
Dim M As String
Dim H As String

Dim MatL As String                                 ' ���������A�i�H�O�ҿ��B�X�����Τ��׿��A�ھڬA�������аO�T�w
Dim Plate_Size_a As Double                ' ���O�����סA�q Plate_Size �r�Ŧꤤ�������ഫ�� Double ����
Dim Plate_Size_b As Double                ' ���O���e�סA�q Plate_Size �r�Ŧꤤ�������ഫ�� Double ����
Dim Plate_Thickness As Double          ' ���O���p�סA�q Plate_Size �r�Ŧꤤ�������ഫ�� Double ����
Dim Plate_Name As String               ' �Ω�s�x�ͦ������O�W�١A�N�b MainAddPlate �l�{�Ǥ��ϥ�
    
Dim SectionType As String
Dim The_Section_Size As String
Dim Total_Length As Double
    '------------------------����ĤG�����é�X���T�ؤo------------------------
    PartString_Type = GetPartOfString(fullString, 2)
    Line_Size = Replace(PartString_Type, "B", "")
    '------------------------�PŪ�ϰ�------------------------
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
    '------------------------���H��------------------------
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

'------------------------���ΥX�ݭn����------------------------
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
    '�d�Ү榡A : 52-2B(P)-A(A)-130-500
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
    
        ' ���w�s�����t�q�G
        ' 52-2B(P)-A(A)-130-500�G�o�O���󪺳]�p�s���A�C�������t�q�p�U�G
        ' 52�G�N�����s���C
        ' 2B�G�N��u�|�ؤo�C
        ' P�G�ݭn�S�O�`�N�A�i���ܧ��ƪ��S���ݩʩγB�z�覡�C
        ' A(A)�G�N��@�ӭ��n�������γW��C
        ' 130-500�G�i������󪺤ؤo�λP�S�w�]�p�������ѼơC
        ' �ק� LOpS=500 (in mm) if any�G�p�G���ݭn�A�i�H�ק� LOpS�]�޾c���ס^���зǭȦ� 500 �@�̡C
        ' �ק� HOpS=130 (in mm) if any�G�p�G���ݭn�A�i�H�ק� HOpS�]�޾c���ס^���зǭȦ� 130 �@�̡C
        ' �Ѩ� SHT D-80A �� 'A' �M�� 'B'�G����Ӹ`�α��ڥi�H�b��� D-80A �������� 'A' �M�� 'B' ���d��C
        ' �ե�̤j���סG
        ' �����󪺳̤j���פ����W�L�窺�e�סC
        ' HOpS �M LOpS ���w�q�G
        ' HOpS�G���סA�����O�޾c�����סC
        ' LOpS�G���סA�����O�޾c�����סC
    
    ' �ŧi�ܼ�
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
    
    ' �H�U�ܶq�Ω� MainAddPlate �L�{
    Dim Plate_Name As String ' �O�����R�W�A�Ω���Ѥ��P�O��
    

    '------------------------------------------�ĥ|�����PŪ�P���R------------------------------------------
    Special_symbol_count = CountCharacter(fullString, "-")  ' if fullstring = "52-2B(P)-A(A)-130-500" then Special_symbol_count = 4
    Select Case Special_symbol_count
        Case 1
        ' �L�u��Type 52-2B   �o�ر��p �ݪ��[�ĤG���q�PŪ �Binsulation = 75 & lesser  hope = 130 lops = 500
            Hops_Value = GetFourthPartOfString(fullString)
            If Hops_Value = "N/A" Then
                Hops_Value = 150
                PipeSize = GetLookupValue(Replace(Type52_GetPipeSize(fullString), "B", ""))
                Pad_symbol = Type52_GetPadSymbol(fullString)
                Lops_Value = 500
            End If
        Case 2
        ' �L�u��Type 52-2B(P)-"*(*)" �Ϊ�  Type 52-2B(P)-"*" �o�ر��p�ݪ��[�ĤT���q�PŪ
            Hops_Value = GetFourthPartOfString(fullString)
            If Hops_Value = "N/A" Then
                Hops_Value = 150
                PipeSize = Type52_GetPipeSize(fullString)
                Pad_symbol = Type52_GetPadSymbol(fullString)
                Insulation_Value = Type52_GetInsulationValue(fullString)
                Matirial_Value = Type52_GetMaterialValue(fullString)
            End If
        Case 4
        ' �L��Type 52-2B(P)-A(A)-130-500 �o�ر��p�ݪ��[�ĥ|���q�PŪ
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
    '------------------ pad�M��-----------------------
    '�Ϥ��X�ޮ|-�t���OPad��
    '�}�l�t��Pad���O�l - ��P��=A  Pad��=B  Pad�p��=t
    'Pad���� = Lops + 2E
    '�Y��10"�H�W �N�|�W�K���U��PAD 52 & 66 ����
    '52�P66���t���b���K IF < 10 �h�K�[���40*40*5-150L�����K Else if >= 10 �h�K�[���40*40*5-150L�����K <- �i�� ���K���ؤo������
    '52�O�֦����K ���ެO10�p�󳣦����K
    'Triago Calculator :
    'Set The Angle for 30 deg  = 30T_Angle
    '30T_Angle_Address = [x,y]
    '30T_x = (PipeDetails.item("DiameterInch") + (PipeDetail.Item("PipeThickness") * 2)) / 2 * Sin(radians(60))
    '30T_y = (PipeDetails.item("DiameterInch") + (PipeDetail.Item("PipeThickness") * 2)) / 2 * Sin(radians(30))
    'And I need 30T_y to know how to calculator The Plate_Y_max_Value
    'Plate_Y_max_Value = (PipeDetails.item("DiameterInch") + (PipeDetail.Item("PipeThickness") * 2)) / 2 + H_Beam_Y_Value - H_Beam_Thickness_Value*2
    'Plate_Size_a �����O�O�l���u��C���F�p��o�ӡA�A�ݭn�p��@�Ӥj�ꪺ�P���C
    '�o�O�z�L���b�|�]�Y Pipe_dia_Size �M Pipe_thickness �`�M�^�A�N��[���H��o���j�ꪺ���|�A�M�᭼�H pi �o�X���j�ꪺ�P���ӧ������C_
    'Plate_Size_b ��ܪO��������t�C��p�⤽�����GLops �[�W�⭿ 25�A�A�[�W�⭿ E�C

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
                Pipe_Thickness = 0 ' �i�H�]�m�@���q�{�ȡA�H�� PipeSize �W�X�w���d��
        End Select
            
            
            Set PipeDetails = CalculatePipeDetails(PipeSize, "10S")
            
            If PipeSize < 10 Then
                
            'Here for the Pipe Size < 10B
            PAD_Calculator_A = ((PipeDetails.Item("DiameterInch") / 2) + Pipe_Thickness * 2) * (4 * Atn(1)) '((�Ӹm��ު��|/2)+�Ӻޮ|���p�� *2)*(4*atn(1))
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
    '------------------ ���K�M��-----------------------
    '���K���ؤo������
    SectionType = "Angle"
    The_Section_Size = "40*40*5"
    Total_Length = 150
    AddSteelSectionEntry SectionType, The_Section_Size, Total_Length
    '------------------ C�M��-----------------------
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
    
    '�d�Ү榡 : 108-1B-12E-A(S)
    'Need use GetFourthPartOfString
    '108=Type
    '1B =Denote Line Size "D"
    '12 =Denote Dimension "H" (IN 100mm)
    'E  =Denote the M42 Type
    'A  =����Fig.A & Fig.B & Fig.C Lug Plate ���ϧO
    '(S)=����Ϥ�
    
    Set ws_M42 = Worksheets("Weight_Analysis")
    Set ws_Pipe_Table = Worksheets("Pipe_Table")
    Set ws = Worksheets("Weight_Analysis")
        
        '�Ϥ��X�ئT �ŦXLine Size : "D"
            PartString_Type = GetSecondPartOfString(fullString)
            PipeSize = Replace(PartString_Type, "B", "")
          
          '�Ϥ��XM42�O����
        letter = GetThirdPartOfString(fullString)
        letter = Right(letter, 1)
        
        '�Ϥ��X"H"�Ȩí��W100
        Main_Pipe_Length = Replace(GetThirdPartOfString(fullString), letter, "") * 100
        

        
        '�Ϥ��XFig number
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
        
        
        
        '�Ϥ��X ����
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
        
        
        ' �㦳���V����˴�
        ' �p�Gdenote "D" = 3/4" H >1000 Then 1.5"_Sch80 else 1"_Sch80
        ' �p�Gdenote "D" = 1" H >1000 Then 1.5"_Sch80 else 1"_Sch80
        ' �p�Gdenote "D" = 1.5" H >1000 Then 2"_Sch40 else 1..5"_Sch80
        ' �p�Gdenote "D" = 2" = 2"_Sch40
        
        '��ڴ���X �һݥD�� �P �D�ޫp��
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
   
   '�ɤJ��: �� -> M42 -> �W�S�O�l
                  
           '�ޤl�ɤJ��
                  i = GetNextRowInColumnB()
            With ws
                .Cells(i, "B").value = 1 '����
                .Cells(i, "C").value = "Pipe" '�~�W
                .Cells(i, "D").value = Main_Pipe_Size & """" & "*" & "SCH" & Replace(Main_Pipe_Thickness, "S", "") '�ؤo�p��
                .Cells(i, "E").value = Main_Pipe_Length - 100 '����
                .Cells(i, "G").value = Mtl '����
                .Cells(i, "H").value = 1 '�ƶq
                .Cells(i, "I").value = MainPipeDetails.Item("WeightPerMeter") '�C�̭�
                .Cells(i, "J").value = .Cells(i, "E").value / 1000 * .Cells(i, "I").value '�歫
                .Cells(i, "K").value = .Cells(i, "J").value * .Cells(i, "H").value '���q�p�p
                .Cells(i, "L").value = "M"
                .Cells(i, "M").value = 1 '�ռ�
                .Cells(i, "N").value = .Cells(i, "H").value * .Cells(i, "M").value * .Cells(i, "E").value / 1000 '���פp�p �ռ�*�ƶq*����/1000
                .Cells(i, "P").value = .Cells(i, "M").value * .Cells(i, "K").value
                .Cells(i, "Q").value = "������"
            End With
               
            'M42 �ɤJ�� :
            '���s�t��
            PipeSize = Main_Pipe_Size
            PerformActionByLetter letter, PipeSize
            
            'Spacer Plate ���
            Plate_Size = 120
            Plate_Size_b = 80
            Plate_Thickness = 6
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '����
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
                      .Cells(i, "Q").value = "���O��"
                  End With
            


            '�S��O���
            ' ���w�w�q�S��O Fig.A = 108_Fig_A_Plate
            Select Case Fig
            Case "Fig_A"
            Plate_Size = 120
            Plate_Size_b = 100
            Plate_Thickness = 9
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '����
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
                      .Cells(i, "Q").value = "���O��"
                  End With
             
             Case "Fig_B"
            Plate_Size = 120
            Plate_Size_b = 100
            Plate_Thickness = 9
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '����
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
                      .Cells(i, "Q").value = "���O��"
                  End With
             
             Case "Fig_C"
            Plate_Size = 65
            Plate_Size_b = 210
            Plate_Thickness = 9
            Weight_calculator = Plate_Size / 1000 * Plate_Size_b / 1000 * Plate_Thickness * 7.85

            i = GetNextRowInColumnB()
                  With ws
                      .Cells(i, "B").value = .Cells(i - 1, "B").value + 1 '����
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
                      .Cells(i, "Q").value = "���O��"
                  End With


            End Select

End Sub
