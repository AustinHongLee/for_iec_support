Attribute VB_Name = "M42���O�{��"
Function PerformActionByLetter(letter As String, PipeSize As String) As String
    Dim Plate_Size As Double
    Dim Plate_Thickness As Double
    Dim Weight_calculator As Double
    Dim ws As Worksheet
    Dim Bolt_size As String
    Dim Section_Dim As String
    Dim Angle_Total_Length As Double
    
    Set ws = Worksheets("Weight_Analysis")
    Set ws_M42 = Worksheets("M_42_Table")

    ' �ھڶǤJ���r������������ʧ@
    Select Case letter
        Case "A"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "B"
            ' For Plate a, Plate d, and Bolt
            AddPlateEntry "a", PipeSize
            AddPlateEntry "d", PipeSize
            AddBoltEntry PipeSize, 4

        Case "C"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "D"
            ' For Plate a and Plate e
            AddPlateEntry "a", PipeSize
            AddPlateEntry "e", PipeSize

        Case "E"
            ' For Plate a, Plate d, and Bolt ,and Angle
            AddPlateEntry "a", PipeSize
            AddPlateEntry "d", PipeSize
            AddBoltEntry PipeSize, 4
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "F"
            ' For Plate a and Angle
            AddPlateEntry "a", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "G"
            ' For Plate b and Bolt
            AddPlateEntry "b", PipeSize
            AddBoltEntry PipeSize, 4

        Case "H"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "J"
            ' For Plate b and Bolt
            AddPlateEntry "b", PipeSize
            AddBoltEntry PipeSize, 4

        Case "K"
            ' For Plate a and Angle
            AddPlateEntry "a", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "L"
            ' For Plate c and Bolt
            AddPlateEntry "c", PipeSize
            AddBoltEntry PipeSize, 4

        Case "M"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "N"
            ' For Plate a and Angle
            AddPlateEntry "a", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case "P"
            ' For Plate c and Bolt
            AddPlateEntry "c", PipeSize
            AddBoltEntry PipeSize, 4
        Case "R"
            ' For Plate a
            AddPlateEntry "a", PipeSize

        Case "S"
            ' For Plate a, Plate e, and Angle
            AddPlateEntry "a", PipeSize
            AddPlateEntry "e", PipeSize
            Angle_Total_Length = 150
            Section_Dim = "40*40*5"
            AddSteelSectionEntry "Angle", Section_Dim, Angle_Total_Length, 2

        Case Else
            ' �p�G�ǤJ���r�����O�w�����r��
            PerformActionByLetter = "�S�������r���w�q�ʧ@�C"
    End Select
End Function

