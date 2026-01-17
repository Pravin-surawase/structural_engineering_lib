Attribute VB_Name = "mod_Connection"
Option Explicit

'==============================================================================
' ETABS Connection Module
' Handles connecting to ETABS via COM API
'==============================================================================

' Connect to ETABS - try attach first, launch if needed
Public Function ConnectToETABS() As Object
    On Error GoTo LaunchETABS

    Dim helper As Object
    Set helper = CreateObject("ETABSv1.Helper")

    If helper Is Nothing Then
        LogError "Cannot create ETABSv1.Helper object"
        LogError "Is ETABS installed?"
        Set ConnectToETABS = Nothing
        Exit Function
    End If

    ' Try to attach to running instance
    LogInfo "Attempting to attach to running ETABS..."
    Dim etabs As Object
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")

    If Not etabs Is Nothing Then
        LogInfo "? Attached to running ETABS instance"

        ' Verify we can access the model
        Dim modelPath As String
        modelPath = etabs.SapModel.GetModelFilename

        If Len(modelPath) > 0 Then
            LogInfo "Model loaded: " & modelPath
        Else
            LogWarning "ETABS is running but no model is loaded"
        End If

        Set ConnectToETABS = etabs
        Exit Function
    End If

LaunchETABS:
    ' Launch new instance if attach failed
    On Error GoTo LaunchError

    LogInfo "No running instance found, launching ETABS..."
    Set etabs = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")

    If etabs Is Nothing Then
        LogError "Failed to launch ETABS"
        Set ConnectToETABS = Nothing
        Exit Function
    End If

    LogInfo "? Launched new ETABS instance"
    LogWarning "No model loaded - you may need to open a model in ETABS"

    Set ConnectToETABS = etabs
    Exit Function

LaunchError:
    LogError "Failed to launch ETABS: " & Err.Description
    Set ConnectToETABS = Nothing
End Function

' Validate connection is still alive
Public Function ValidateConnection(etabs As Object) As Boolean
    On Error Resume Next

    Dim test As String
    test = etabs.SapModel.GetModelFilename

    If Err.Number = 0 Then
        ValidateConnection = True
    Else
        LogWarning "Connection validation failed: " & Err.Description
        ValidateConnection = False
    End If
End Function

' Get ETABS version
Public Function GetETABSVersion(helper As Object) As String
    On Error Resume Next

    Dim version As Long
    version = helper.GetOAPIVersionNumber

    If Err.Number <> 0 Then
        GetETABSVersion = "Unknown"
        LogWarning "Cannot determine ETABS version"
    Else
        GetETABSVersion = "v" & CStr(version)
        LogInfo "ETABS OAPI Version: " & GetETABSVersion
    End If
End Function

' Check if model is loaded and has frames
Public Function ValidateModelReady(sapModel As Object) As Boolean
    On Error Resume Next
    
    ' Check model exists
    Dim modelPath As String
    modelPath = sapModel.GetModelFilename
    
    If Err.Number <> 0 Or Len(modelPath) = 0 Then
        LogError "No model loaded in ETABS"
        ValidateModelReady = False
        Exit Function
    End If
    
    LogInfo "Model: " & modelPath
    
    ' Check for frames
    Dim frameCount As Long
    Dim frameNames() As String
    Dim ret As Long
    
    ret = sapModel.FrameObj.GetNameList(frameCount, frameNames)
    
    If Err.Number <> 0 Or ret <> 0 Then
        LogWarning "Cannot get frame count"
    ElseIf frameCount = 0 Then
        LogWarning "Model has no frame objects"
    Else
        LogInfo "Model has " & frameCount & " frame objects"
    End If
    
    ValidateModelReady = True
End Function

' Safe API call wrapper with retry
Public Function SafeAPICall(ByRef etabs As Object, _
                           operationName As String, _
                           Optional maxRetries As Integer = 3) As Boolean
    Dim retryCount As Integer

    For retryCount = 1 To maxRetries
        On Error Resume Next
        Err.Clear

        ' Validate connection
        If Not ValidateConnection(etabs) Then
            LogWarning operationName & ": Connection lost, attempting reconnect..."
            Set etabs = ConnectToETABS()

            If etabs Is Nothing Then
                LogError operationName & ": Reconnection failed"
                SafeAPICall = False
                Exit Function
            End If
        End If

        ' Connection is valid
        SafeAPICall = True
        Exit Function
    Next

    LogError operationName & ": Max retries exceeded"
    SafeAPICall = False
End Function
