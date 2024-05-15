Attribute VB_Name = "C_¿ûªO³B²z"
Sub MainAddPlate( _
    plate_size_a As Double, _
    plate_size_b As Double, _
    plate_thickness As Double, _
    plate_name As String, _
    Optional Plate_Material As String = "", _
    Optional Plate_qty As Double = 1, _
    Optional PlateBolt_switch As Boolean = False, _
    Optional PlateBolt_Length_x As Double = 0, _
    Optional PlateBolt_Length_y As Double = 0 _
)
    Dim Pipeline_Density As Double
    Dim weight As Double
    Dim i As Long
    Dim First_Value_Checking As Long
    Dim ws As Worksheet
    Dim bolt_length_join As String
    
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

    If PlateBolt_switch = True Then
        bolt_length_join = PlateBolt_Length_x & "x" & PlateBolt_Length_y & "x" & plate_thickness
    End If

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
        .Cells(i, "Q").value = "¿ûªOÃþ"
        .Cells(i, "R").value = bolt_length_join
    End With
End Sub


