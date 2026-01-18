Attribute VB_Name = "INSTRUCTIONS_AddReference"
Option Explicit

'==============================================================================
' INSTRUCTIONS: How to Add ETABS Type Library Reference
'==============================================================================
'
' The legacy code works because it uses EARLY BINDING with ETABS type library.
' Your current Excel file uses LATE BINDING (As Object) which doesn't work
' for FrameObj methods.
'
' TO FIX:
' -------
' 1. In Excel VBA Editor, go to: Tools → References
'
' 2. Click "Browse" button
'
' 3. Navigate to your ETABS installation folder, typically:
'    C:\Program Files\Computers and Structures\ETABS 21\ETABS.exe
'    (or similar path for your ETABS version)
'
' 4. Select ETABS.exe and click "Open"
'
' 5. You should see "ETABS XX Object Library" now checked
'
' 6. Click "OK"
'
' 7. Now the legacy-style code will work!
'
' AFTER ADDING REFERENCE:
' -----------------------
' Change your variable declarations from:
'   Dim sapModel As Object
' To:
'   Dim sapModel As ETABSv1.cSapModel
'
' This enables IntelliSense and fixes the Error #430 issues.
'
'==============================================================================

Sub ShowInstructions()
    MsgBox "INSTRUCTIONS: Add ETABS Type Library Reference" & vbCrLf & vbCrLf & _
           "1. Tools → References" & vbCrLf & _
           "2. Browse → Find ETABS.exe in Program Files" & vbCrLf & _
           "3. Check 'ETABS Object Library'" & vbCrLf & _
           "4. OK" & vbCrLf & vbCrLf & _
           "Then the legacy code patterns will work!", _
           vbInformation, "Setup Instructions"
End Sub

Sub TestAfterAddingReference()
    On Error GoTo NeedsReference
    
    ' This will only work AFTER adding the reference
    Dim myHelper As Object  ' Can't use early binding without reference visible to this code
    Dim myETABSObject As Object
    Dim mySapModel As Object
    
    Set myHelper = CreateObject("ETABSv1.Helper")
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    ' Test FrameObj.GetNameList
    Dim NumberNames As Long
    Dim MyName() As String
    Dim ret As Long
    
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    If ret = 0 And NumberNames > 0 Then
        MsgBox "SUCCESS!" & vbCrLf & vbCrLf & _
               "FrameObj.GetNameList now works!" & vbCrLf & _
               "Found " & NumberNames & " frames" & vbCrLf & vbCrLf & _
               "You can now use the full export code.", _
               vbInformation, "Test Passed"
    Else
        MsgBox "FrameObj.GetNameList returned ret=" & ret & vbCrLf & _
               "This shouldn't happen after adding reference.", _
               vbExclamation
    End If
    Exit Sub
    
NeedsReference:
    MsgBox "Error #" & Err.Number & ": " & Err.Description & vbCrLf & vbCrLf & _
           "Please add ETABS type library reference:" & vbCrLf & _
           "Tools → References → Browse for ETABS.exe", _
           vbCritical, "Reference Required"
End Sub
