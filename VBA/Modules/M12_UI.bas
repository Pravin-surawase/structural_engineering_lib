Attribute VB_Name = "M12_UI"
Option Explicit

' ==========================================================================================
' Module:       M12_UI
' Description:  UI Event Handlers for Buttons and Controls.
'               Connects Sheet Buttons to Application Layer Logic.
' Dependencies: M11_AppLayer
' ==========================================================================================

' ------------------------------------------------------------------------------------------
' Button: [Run Design] on HOME Sheet
' ------------------------------------------------------------------------------------------
Public Sub Main_RunDesign()
    ' Log the action (optional, could be added later)
    ' Call the Application Layer
    M11_AppLayer.Run_BeamDesign
End Sub

' ------------------------------------------------------------------------------------------
' Button: [Clear Results] on HOME Sheet
' ------------------------------------------------------------------------------------------
Public Sub Main_Clear()
    Dim answer As VbMsgBoxResult
    answer = MsgBox("Are you sure you want to clear all design results?", vbYesNo + vbQuestion, "Confirm Clear")
    
    If answer = vbYes Then
        M11_AppLayer.Clear_Results
    End If
End Sub

' ------------------------------------------------------------------------------------------
' Button: [Import Data] on HOME Sheet
' ------------------------------------------------------------------------------------------
Public Sub Import_CSV()
    ' Call the Integration Layer
    M13_Integration.Import_ETABS_Data
End Sub

' ------------------------------------------------------------------------------------------
' Button: [Generate Schedule] on BEAM_DESIGN Sheet (or HOME)
' ------------------------------------------------------------------------------------------
Public Sub Main_GenerateSchedule()
    M14_Reporting.Generate_Beam_Schedule
End Sub

' ------------------------------------------------------------------------------------------
' Navigation Helpers (Optional)
' ------------------------------------------------------------------------------------------
Public Sub GoTo_Input()
    ThisWorkbook.Sheets("BEAM_INPUT").Activate
End Sub

Public Sub GoTo_Design()
    ThisWorkbook.Sheets("BEAM_DESIGN").Activate
End Sub

Public Sub GoTo_Home()
    ThisWorkbook.Sheets("HOME").Activate
End Sub
