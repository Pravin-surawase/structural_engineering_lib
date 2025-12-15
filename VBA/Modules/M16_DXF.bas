Attribute VB_Name = "M16_DXF"
'@Module: M16_DXF
'@Description: DXF File Export for Structural Drawings
'@Reference: IS 456:2000, SP 34:1987, AutoCAD DXF Reference
'@Version: 0.8.0
'@Date: 2025-12-11
'
' PURPOSE:
'   Native VBA DXF writer for generating structural engineering drawings.
'   Creates standard AutoCAD-compatible DXF files (R12 format).
'
' CAD LAYER STANDARDS (IS/SP 34 Drawing Practices):
'   BEAM_OUTLINE    - Cyan (4)    - Beam section boundary
'   REBAR_MAIN      - Red (1)     - Main reinforcement bars
'   REBAR_STIRRUP   - Green (3)   - Stirrups/shear links
'   DIMENSIONS      - Yellow (2)  - Dimension lines
'   TEXT_CALLOUT    - White (7)   - Bar callouts, labels
'   CENTERLINE      - Magenta (6) - Center lines (CENTER linetype)
'   CONCRETE_HATCH  - Gray (8)    - Concrete section hatching
'   COVER_LINE      - Blue (5)    - Cover lines
'
' DRAWING TYPES:
'   1. Beam Cross-Section (showing rebar arrangement)
'   2. Longitudinal Section (showing main bars + stirrup spacing)
'   3. Stirrup Detail (single stirrup with dimensions)
'
Option Explicit

' ============================================================================
' CONSTANTS - DXF Codes and Layer Properties
' ============================================================================

' DXF Group Codes
Private Const GC_ENTITY_TYPE As Integer = 0
Private Const GC_LAYER As Integer = 8
Private Const GC_COLOR As Integer = 62
Private Const GC_LINETYPE As Integer = 6
Private Const GC_X1 As Integer = 10
Private Const GC_Y1 As Integer = 20
Private Const GC_X2 As Integer = 11
Private Const GC_Y2 As Integer = 21
Private Const GC_RADIUS As Integer = 40
Private Const GC_TEXT_HEIGHT As Integer = 40
Private Const GC_TEXT_VALUE As Integer = 1
Private Const GC_START_ANGLE As Integer = 50
Private Const GC_END_ANGLE As Integer = 51

' AutoCAD Color Index (ACI)
Public Const ACI_RED As Integer = 1
Public Const ACI_YELLOW As Integer = 2
Public Const ACI_GREEN As Integer = 3
Public Const ACI_CYAN As Integer = 4
Public Const ACI_BLUE As Integer = 5
Public Const ACI_MAGENTA As Integer = 6
Public Const ACI_WHITE As Integer = 7
Public Const ACI_GRAY As Integer = 8

' Layer Names (Standard Structural)
Public Const LAYER_BEAM_OUTLINE As String = "BEAM_OUTLINE"
Public Const LAYER_REBAR_MAIN As String = "REBAR_MAIN"
Public Const LAYER_REBAR_STIRRUP As String = "REBAR_STIRRUP"
Public Const LAYER_DIMENSIONS As String = "DIMENSIONS"
Public Const LAYER_TEXT_CALLOUT As String = "TEXT_CALLOUT"
Public Const LAYER_CENTERLINE As String = "CENTERLINE"
Public Const LAYER_COVER_LINE As String = "COVER_LINE"

' Drawing Scale (1 unit = 1 mm)
Private Const SCALE_FACTOR As Double = 1#

' ============================================================================
' TYPE DEFINITIONS
' ============================================================================

' DXF Drawing Context
Public Type DXFContext
    FilePath As String
    FileNum As Integer
    IsOpen As Boolean
    EntityCount As Long
    MinX As Double
    MinY As Double
    MaxX As Double
    MaxY As Double
End Type

' Point in 2D
Public Type Point2D
    X As Double
    Y As Double
End Type

' ============================================================================
' MODULE-LEVEL VARIABLES
' ============================================================================

Private m_Context As DXFContext

' ============================================================================
' DXF FILE MANAGEMENT
' ============================================================================

'@Description: Initialize a new DXF file
'@Param filePath: Full path to the DXF file
'@Returns: True if successful
Public Function DXF_Initialize(ByVal filePath As String) As Boolean
    On Error GoTo ErrorHandler
    
    ' Close any existing file
    If m_Context.IsOpen Then
        DXF_Close
    End If
    
    ' Initialize context
    m_Context.FilePath = filePath
    m_Context.FileNum = FreeFile()
    m_Context.EntityCount = 0
    m_Context.MinX = 1E+30
    m_Context.MinY = 1E+30
    m_Context.MaxX = -1E+30
    m_Context.MaxY = -1E+30
    
    ' Open file for output
    Open filePath For Output As #m_Context.FileNum
    m_Context.IsOpen = True
    
    ' Write DXF header
    Call WriteHeader
    
    ' Write layer table
    Call WriteTables
    
    ' Start entities section
    Call WriteLine(GC_ENTITY_TYPE, "SECTION")
    Call WriteLine(2, "ENTITIES")
    
    DXF_Initialize = True
    Exit Function
    
ErrorHandler:
    DXF_Initialize = False
End Function

'@Description: Close the DXF file and finalize
Public Sub DXF_Close()
    On Error Resume Next
    
    If Not m_Context.IsOpen Then Exit Sub
    
    ' End entities section
    Call WriteLine(GC_ENTITY_TYPE, "ENDSEC")
    
    ' Write EOF
    Call WriteLine(GC_ENTITY_TYPE, "EOF")
    
    ' Close file
    Close #m_Context.FileNum
    m_Context.IsOpen = False
    
    ' Note: DXF R12 doesn't support re-writing header after entities.
    ' Extents are tracked in m_Context.MinX/Y, MaxX/Y for reference.
    ' For proper extents, use DXF R2000+ format or post-process the file.
End Sub

'@Description: Write DXF header section
Private Sub WriteHeader()
    Call WriteLine(GC_ENTITY_TYPE, "SECTION")
    Call WriteLine(2, "HEADER")
    
    ' AutoCAD version (AC1009 = R12)
    Call WriteLine(9, "$ACADVER")
    Call WriteLine(1, "AC1009")
    
    ' Drawing units (decimal)
    Call WriteLine(9, "$LUNITS")
    Call WriteLine(70, "2")
    
    ' Unit precision
    Call WriteLine(9, "$LUPREC")
    Call WriteLine(70, "2")
    
    ' Insertion base point
    Call WriteLine(9, "$INSBASE")
    Call WriteLine(GC_X1, "0.0")
    Call WriteLine(GC_Y1, "0.0")
    Call WriteLine(30, "0.0")
    
    ' Drawing extents - use generous defaults for typical beam drawings
    ' Note: DXF R12 writes header first, so we use placeholder values.
    ' Most CAD software will recalculate extents on file open (ZOOM EXTENTS).
    ' For scaled 1:10 drawings of beams up to 10m span, 2000x1000 units is sufficient.
    Call WriteLine(9, "$EXTMIN")
    Call WriteLine(GC_X1, "-100.0")
    Call WriteLine(GC_Y1, "-100.0")
    Call WriteLine(30, "0.0")
    
    Call WriteLine(9, "$EXTMAX")
    Call WriteLine(GC_X1, "2000.0")
    Call WriteLine(GC_Y1, "1000.0")
    Call WriteLine(30, "0.0")
    
    Call WriteLine(GC_ENTITY_TYPE, "ENDSEC")
End Sub

'@Description: Write tables section with layers and linetypes
Private Sub WriteTables()
    Call WriteLine(GC_ENTITY_TYPE, "SECTION")
    Call WriteLine(2, "TABLES")
    
    ' Linetype table
    Call WriteLinetypeTable
    
    ' Layer table
    Call WriteLayerTable
    
    Call WriteLine(GC_ENTITY_TYPE, "ENDSEC")
End Sub

'@Description: Write linetype definitions
Private Sub WriteLinetypeTable()
    Call WriteLine(GC_ENTITY_TYPE, "TABLE")
    Call WriteLine(2, "LTYPE")
    Call WriteLine(70, "3")
    
    ' CONTINUOUS linetype
    Call WriteLine(GC_ENTITY_TYPE, "LTYPE")
    Call WriteLine(2, "CONTINUOUS")
    Call WriteLine(70, "0")
    Call WriteLine(3, "Solid line")
    Call WriteLine(72, "65")
    Call WriteLine(73, "0")
    Call WriteLine(GC_TEXT_HEIGHT, "0.0")
    
    ' CENTER linetype
    Call WriteLine(GC_ENTITY_TYPE, "LTYPE")
    Call WriteLine(2, "CENTER")
    Call WriteLine(70, "0")
    Call WriteLine(3, "Center ____ _ ____ _ ____")
    Call WriteLine(72, "65")
    Call WriteLine(73, "4")
    Call WriteLine(GC_TEXT_HEIGHT, "50.8")
    Call WriteLine(49, "31.75")
    Call WriteLine(49, "-6.35")
    Call WriteLine(49, "6.35")
    Call WriteLine(49, "-6.35")
    
    ' DASHED linetype
    Call WriteLine(GC_ENTITY_TYPE, "LTYPE")
    Call WriteLine(2, "DASHED")
    Call WriteLine(70, "0")
    Call WriteLine(3, "Dashed __ __ __ __")
    Call WriteLine(72, "65")
    Call WriteLine(73, "2")
    Call WriteLine(GC_TEXT_HEIGHT, "19.05")
    Call WriteLine(49, "12.7")
    Call WriteLine(49, "-6.35")
    
    Call WriteLine(GC_ENTITY_TYPE, "ENDTAB")
End Sub

'@Description: Write layer definitions for structural drawing
Private Sub WriteLayerTable()
    Call WriteLine(GC_ENTITY_TYPE, "TABLE")
    Call WriteLine(2, "LAYER")
    Call WriteLine(70, "7")  ' Number of layers (0 + 6 structural)
    
    ' Layer 0 (default)
    Call WriteLayerDef "0", ACI_WHITE, "CONTINUOUS"
    
    ' Structural layers
    Call WriteLayerDef LAYER_BEAM_OUTLINE, ACI_CYAN, "CONTINUOUS"
    Call WriteLayerDef LAYER_REBAR_MAIN, ACI_RED, "CONTINUOUS"
    Call WriteLayerDef LAYER_REBAR_STIRRUP, ACI_GREEN, "CONTINUOUS"
    Call WriteLayerDef LAYER_DIMENSIONS, ACI_YELLOW, "CONTINUOUS"
    Call WriteLayerDef LAYER_TEXT_CALLOUT, ACI_WHITE, "CONTINUOUS"
    Call WriteLayerDef LAYER_CENTERLINE, ACI_MAGENTA, "CENTER"
    Call WriteLayerDef LAYER_COVER_LINE, ACI_BLUE, "DASHED"
    
    Call WriteLine(GC_ENTITY_TYPE, "ENDTAB")
End Sub

'@Description: Write a single layer definition
Private Sub WriteLayerDef(ByVal layerName As String, ByVal color As Integer, ByVal lineType As String)
    Call WriteLine(GC_ENTITY_TYPE, "LAYER")
    Call WriteLine(2, layerName)
    Call WriteLine(70, "0")
    Call WriteLine(GC_COLOR, CStr(color))
    Call WriteLine(GC_LINETYPE, lineType)
End Sub

'@Description: Write a line to DXF file
Private Sub WriteLine(ByVal groupCode As Integer, ByVal value As String)
    Print #m_Context.FileNum, Format(groupCode, "0")
    Print #m_Context.FileNum, value
End Sub

' ============================================================================
' DXF PRIMITIVE ENTITIES
' ============================================================================

'@Description: Draw a line entity
'@Param x1, y1: Start point
'@Param x2, y2: End point
'@Param layer: Layer name
Public Sub DXF_Line(ByVal x1 As Double, ByVal y1 As Double, _
                   ByVal x2 As Double, ByVal y2 As Double, _
                   ByVal layer As String)
    If Not m_Context.IsOpen Then Exit Sub
    
    Call WriteLine(GC_ENTITY_TYPE, "LINE")
    Call WriteLine(GC_LAYER, layer)
    Call WriteLine(GC_X1, Format(x1, "0.00"))
    Call WriteLine(GC_Y1, Format(y1, "0.00"))
    Call WriteLine(30, "0.0")
    Call WriteLine(GC_X2, Format(x2, "0.00"))
    Call WriteLine(GC_Y2, Format(y2, "0.00"))
    Call WriteLine(31, "0.0")
    
    m_Context.EntityCount = m_Context.EntityCount + 1
    Call UpdateExtents(x1, y1)
    Call UpdateExtents(x2, y2)
End Sub

'@Description: Draw a circle entity (for rebar cross-section)
'@Param cx, cy: Center point
'@Param radius: Circle radius
'@Param layer: Layer name
Public Sub DXF_Circle(ByVal cx As Double, ByVal cy As Double, _
                     ByVal radius As Double, ByVal layer As String)
    If Not m_Context.IsOpen Then Exit Sub
    
    Call WriteLine(GC_ENTITY_TYPE, "CIRCLE")
    Call WriteLine(GC_LAYER, layer)
    Call WriteLine(GC_X1, Format(cx, "0.00"))
    Call WriteLine(GC_Y1, Format(cy, "0.00"))
    Call WriteLine(30, "0.0")
    Call WriteLine(GC_RADIUS, Format(radius, "0.00"))
    
    m_Context.EntityCount = m_Context.EntityCount + 1
    Call UpdateExtents(cx - radius, cy - radius)
    Call UpdateExtents(cx + radius, cy + radius)
End Sub

'@Description: Draw a filled circle (solid hatch for rebar)
'@Param cx, cy: Center point
'@Param radius: Circle radius
'@Param layer: Layer name
Public Sub DXF_FilledCircle(ByVal cx As Double, ByVal cy As Double, _
                           ByVal radius As Double, ByVal layer As String)
    If Not m_Context.IsOpen Then Exit Sub
    
    ' Draw outline circle
    Call DXF_Circle(cx, cy, radius, layer)
    
    ' For R12, we'll draw concentric circles to simulate fill
    Dim r As Double
    r = radius * 0.7
    Do While r > 0.5
        Call DXF_Circle(cx, cy, r, layer)
        r = r - 1
    Loop
End Sub

'@Description: Draw an arc entity
'@Param cx, cy: Center point
'@Param radius: Arc radius
'@Param startAngle: Start angle in degrees
'@Param endAngle: End angle in degrees
'@Param layer: Layer name
Public Sub DXF_Arc(ByVal cx As Double, ByVal cy As Double, _
                  ByVal radius As Double, _
                  ByVal startAngle As Double, ByVal endAngle As Double, _
                  ByVal layer As String)
    If Not m_Context.IsOpen Then Exit Sub
    
    Call WriteLine(GC_ENTITY_TYPE, "ARC")
    Call WriteLine(GC_LAYER, layer)
    Call WriteLine(GC_X1, Format(cx, "0.00"))
    Call WriteLine(GC_Y1, Format(cy, "0.00"))
    Call WriteLine(30, "0.0")
    Call WriteLine(GC_RADIUS, Format(radius, "0.00"))
    Call WriteLine(GC_START_ANGLE, Format(startAngle, "0.00"))
    Call WriteLine(GC_END_ANGLE, Format(endAngle, "0.00"))
    
    m_Context.EntityCount = m_Context.EntityCount + 1
End Sub

'@Description: Draw text entity
'@Param x, y: Insertion point
'@Param height: Text height
'@Param text: Text string
'@Param layer: Layer name
'@Param rotation: Rotation angle (default 0)
Public Sub DXF_Text(ByVal X As Double, ByVal Y As Double, _
                   ByVal height As Double, ByVal text As String, _
                   ByVal layer As String, _
                   Optional ByVal rotation As Double = 0)
    If Not m_Context.IsOpen Then Exit Sub
    
    Call WriteLine(GC_ENTITY_TYPE, "TEXT")
    Call WriteLine(GC_LAYER, layer)
    Call WriteLine(GC_X1, Format(X, "0.00"))
    Call WriteLine(GC_Y1, Format(Y, "0.00"))
    Call WriteLine(30, "0.0")
    Call WriteLine(GC_TEXT_HEIGHT, Format(height, "0.00"))
    Call WriteLine(GC_TEXT_VALUE, text)
    If rotation <> 0 Then
        Call WriteLine(GC_START_ANGLE, Format(rotation, "0.00"))
    End If
    
    m_Context.EntityCount = m_Context.EntityCount + 1
    Call UpdateExtents(X, Y)
End Sub

'@Description: Draw a rectangle (4 lines)
'@Param x, y: Bottom-left corner
'@Param width, height: Rectangle dimensions
'@Param layer: Layer name
Public Sub DXF_Rectangle(ByVal X As Double, ByVal Y As Double, _
                        ByVal width As Double, ByVal height As Double, _
                        ByVal layer As String)
    If Not m_Context.IsOpen Then Exit Sub
    
    ' Bottom
    Call DXF_Line(X, Y, X + width, Y, layer)
    ' Right
    Call DXF_Line(X + width, Y, X + width, Y + height, layer)
    ' Top
    Call DXF_Line(X + width, Y + height, X, Y + height, layer)
    ' Left
    Call DXF_Line(X, Y + height, X, Y, layer)
End Sub

'@Description: Draw a polyline (series of connected lines)
'@Param points: Array of Point2D
'@Param closed: Close the polyline
'@Param layer: Layer name
Public Sub DXF_Polyline(ByRef points() As Point2D, _
                       ByVal closed As Boolean, _
                       ByVal layer As String)
    If Not m_Context.IsOpen Then Exit Sub
    
    Dim i As Long
    Dim n As Long
    n = UBound(points)
    
    For i = LBound(points) To n - 1
        Call DXF_Line(points(i).X, points(i).Y, _
                     points(i + 1).X, points(i + 1).Y, layer)
    Next i
    
    If closed And n >= 2 Then
        Call DXF_Line(points(n).X, points(n).Y, _
                     points(LBound(points)).X, points(LBound(points)).Y, layer)
    End If
End Sub

'@Description: Update drawing extents
Private Sub UpdateExtents(ByVal X As Double, ByVal Y As Double)
    If X < m_Context.MinX Then m_Context.MinX = X
    If Y < m_Context.MinY Then m_Context.MinY = Y
    If X > m_Context.MaxX Then m_Context.MaxX = X
    If Y > m_Context.MaxY Then m_Context.MaxY = Y
End Sub

' ============================================================================
' STRUCTURAL DRAWING COMPONENTS
' ============================================================================

'@Description: Draw a stirrup (rectangular with hooks)
'@Param cx, cy: Center of stirrup
'@Param width: Internal width (B - 2*cover)
'@Param height: Internal height (D - 2*cover)
'@Param barDia: Stirrup bar diameter
'@Param hookLength: 135-degree hook length (typically 10*dia)
Public Sub DXF_Stirrup(ByVal cx As Double, ByVal cy As Double, _
                      ByVal width As Double, ByVal height As Double, _
                      ByVal barDia As Double, _
                      Optional ByVal hookLength As Double = 0)
    
    Dim halfW As Double, halfH As Double
    Dim r As Double  ' Bend radius
    
    halfW = width / 2
    halfH = height / 2
    r = 2 * barDia  ' Minimum bend radius = 2*dia for stirrups
    
    If hookLength = 0 Then hookLength = 10 * barDia
    
    ' Draw outer rectangle with rounded corners
    ' Bottom
    Call DXF_Line(cx - halfW + r, cy - halfH, cx + halfW - r, cy - halfH, LAYER_REBAR_STIRRUP)
    ' Right
    Call DXF_Line(cx + halfW, cy - halfH + r, cx + halfW, cy + halfH - r, LAYER_REBAR_STIRRUP)
    ' Top
    Call DXF_Line(cx + halfW - r, cy + halfH, cx - halfW + r, cy + halfH, LAYER_REBAR_STIRRUP)
    ' Left
    Call DXF_Line(cx - halfW, cy + halfH - r, cx - halfW, cy - halfH + r, LAYER_REBAR_STIRRUP)
    
    ' Corner arcs (90 degrees each)
    Call DXF_Arc(cx - halfW + r, cy - halfH + r, r, 180, 270, LAYER_REBAR_STIRRUP)  ' Bottom-left
    Call DXF_Arc(cx + halfW - r, cy - halfH + r, r, 270, 360, LAYER_REBAR_STIRRUP)  ' Bottom-right
    Call DXF_Arc(cx + halfW - r, cy + halfH - r, r, 0, 90, LAYER_REBAR_STIRRUP)     ' Top-right
    Call DXF_Arc(cx - halfW + r, cy + halfH - r, r, 90, 180, LAYER_REBAR_STIRRUP)   ' Top-left
    
    ' Draw 135-degree hooks at top (standard per IS 456)
    Dim hookAngle As Double
    hookAngle = hookLength * 0.707  ' cos(45)
    
    ' Left hook (going inward-down at 135 degrees)
    Call DXF_Line(cx - halfW + r, cy + halfH, _
                 cx - halfW + r + hookAngle, cy + halfH - hookAngle, LAYER_REBAR_STIRRUP)
    
    ' Right hook
    Call DXF_Line(cx + halfW - r, cy + halfH, _
                 cx + halfW - r - hookAngle, cy + halfH - hookAngle, LAYER_REBAR_STIRRUP)
End Sub

'@Description: Draw rebar cross-section in beam section view
'@Param cx, cy: Center of bar
'@Param barDia: Bar diameter in mm
'@Param filled: Draw as filled circle
Public Sub DXF_RebarSection(ByVal cx As Double, ByVal cy As Double, _
                           ByVal barDia As Double, _
                           Optional ByVal filled As Boolean = True)
    Dim radius As Double
    radius = barDia / 2
    
    If filled Then
        Call DXF_FilledCircle(cx, cy, radius, LAYER_REBAR_MAIN)
    Else
        Call DXF_Circle(cx, cy, radius, LAYER_REBAR_MAIN)
    End If
End Sub

'@Description: Draw dimension line (horizontal or vertical)
'@Param x1, y1: First point
'@Param x2, y2: Second point
'@Param offset: Offset distance for dimension line
'@Param textHeight: Height of dimension text
Public Sub DXF_Dimension(ByVal x1 As Double, ByVal y1 As Double, _
                        ByVal x2 As Double, ByVal y2 As Double, _
                        ByVal offset As Double, _
                        Optional ByVal textHeight As Double = 25)
    
    Dim length As Double
    Dim midX As Double, midY As Double
    Dim isHorizontal As Boolean
    Dim dimText As String
    
    ' Determine if horizontal or vertical
    isHorizontal = (Abs(y2 - y1) < 0.01)
    
    If isHorizontal Then
        length = Abs(x2 - x1)
        midX = (x1 + x2) / 2
        midY = y1 + offset
        
        ' Extension lines
        Call DXF_Line(x1, y1, x1, y1 + offset * 0.9, LAYER_DIMENSIONS)
        Call DXF_Line(x2, y2, x2, y2 + offset * 0.9, LAYER_DIMENSIONS)
        
        ' Dimension line
        Call DXF_Line(x1, midY, x2, midY, LAYER_DIMENSIONS)
        
        ' Arrow heads (simple lines)
        Call DXF_Line(x1, midY, x1 + textHeight * 0.3, midY + textHeight * 0.15, LAYER_DIMENSIONS)
        Call DXF_Line(x1, midY, x1 + textHeight * 0.3, midY - textHeight * 0.15, LAYER_DIMENSIONS)
        Call DXF_Line(x2, midY, x2 - textHeight * 0.3, midY + textHeight * 0.15, LAYER_DIMENSIONS)
        Call DXF_Line(x2, midY, x2 - textHeight * 0.3, midY - textHeight * 0.15, LAYER_DIMENSIONS)
    Else
        length = Abs(y2 - y1)
        midX = x1 + offset
        midY = (y1 + y2) / 2
        
        ' Extension lines
        Call DXF_Line(x1, y1, x1 + offset * 0.9, y1, LAYER_DIMENSIONS)
        Call DXF_Line(x2, y2, x2 + offset * 0.9, y2, LAYER_DIMENSIONS)
        
        ' Dimension line
        Call DXF_Line(midX, y1, midX, y2, LAYER_DIMENSIONS)
        
        ' Arrow heads
        Call DXF_Line(midX, y1, midX + textHeight * 0.15, y1 + textHeight * 0.3, LAYER_DIMENSIONS)
        Call DXF_Line(midX, y1, midX - textHeight * 0.15, y1 + textHeight * 0.3, LAYER_DIMENSIONS)
        Call DXF_Line(midX, y2, midX + textHeight * 0.15, y2 - textHeight * 0.3, LAYER_DIMENSIONS)
        Call DXF_Line(midX, y2, midX - textHeight * 0.15, y2 - textHeight * 0.3, LAYER_DIMENSIONS)
    End If
    
    ' Dimension text
    dimText = Format(length, "0")
    If isHorizontal Then
        Call DXF_Text(midX - textHeight, midY + textHeight * 0.3, textHeight, dimText, LAYER_DIMENSIONS)
    Else
        Call DXF_Text(midX + textHeight * 0.3, midY, textHeight, dimText, LAYER_DIMENSIONS, 90)
    End If
End Sub

' ============================================================================
' COMPLETE DRAWING FUNCTIONS
' ============================================================================

'@Description: Generate complete beam cross-section drawing
'@Param filePath: Output DXF file path
'@Param B: Beam width (mm)
'@Param D: Beam depth (mm)
'@Param cover: Clear cover (mm)
'@Param topBars: Array of top bar diameters
'@Param bottomBars: Array of bottom bar diameters
'@Param stirrupDia: Stirrup diameter (mm)
'@Returns: True if successful
Public Function Draw_BeamSection(ByVal filePath As String, _
                                ByVal B As Double, ByVal D As Double, _
                                ByVal cover As Double, _
                                ByRef topBars() As Double, _
                                ByRef bottomBars() As Double, _
                                ByVal stirrupDia As Double) As Boolean
    On Error GoTo ErrorHandler
    
    Dim success As Boolean
    Dim i As Long
    Dim nTop As Long, nBottom As Long
    Dim spacing As Double
    Dim X As Double, Y As Double
    Dim effectiveCover As Double
    
    ' Initialize DXF file
    success = DXF_Initialize(filePath)
    If Not success Then GoTo ErrorHandler
    
    ' Calculate effective cover (to center of bar)
    effectiveCover = cover + stirrupDia
    
    ' Origin at bottom-left of beam
    Dim originX As Double, originY As Double
    originX = 50  ' Margin
    originY = 50
    
    ' Draw beam outline
    Call DXF_Rectangle(originX, originY, B, D, LAYER_BEAM_OUTLINE)
    
    ' Draw cover lines (dashed)
    Call DXF_Rectangle(originX + cover, originY + cover, _
                      B - 2 * cover, D - 2 * cover, LAYER_COVER_LINE)
    
    ' Draw stirrup
    Call DXF_Stirrup(originX + B / 2, originY + D / 2, _
                    B - 2 * cover - stirrupDia, D - 2 * cover - stirrupDia, _
                    stirrupDia)
    
    ' Draw center lines
    Call DXF_Line(originX + B / 2, originY - 20, originX + B / 2, originY + D + 20, LAYER_CENTERLINE)
    
    ' Draw bottom bars
    nBottom = UBound(bottomBars) - LBound(bottomBars) + 1
    If nBottom > 0 Then
        Y = originY + effectiveCover + bottomBars(LBound(bottomBars)) / 2
        
        If nBottom = 1 Then
            ' Single bar: center it
            X = originX + B / 2
            Call DXF_RebarSection(X, Y, bottomBars(LBound(bottomBars)), True)
        Else
            ' Multiple bars: correct spacing = (B - 2*effectiveCover - bar_dia) / (n - 1)
            ' This gives center-to-center spacing with first/last bar at half-dia from cover
            Dim avgBarDiaBottom As Double
            avgBarDiaBottom = bottomBars(LBound(bottomBars))  ' Use first bar diameter
            Dim availableWidthBottom As Double
            availableWidthBottom = B - 2 * effectiveCover - avgBarDiaBottom
            spacing = availableWidthBottom / (nBottom - 1)
            
            X = originX + effectiveCover + bottomBars(LBound(bottomBars)) / 2
            For i = LBound(bottomBars) To UBound(bottomBars)
                Call DXF_RebarSection(X, Y, bottomBars(i), True)
                If i < UBound(bottomBars) Then
                    X = X + spacing
                End If
            Next i
        End If
    End If
    
    ' Draw top bars
    nTop = UBound(topBars) - LBound(topBars) + 1
    If nTop > 0 Then
        Y = originY + D - effectiveCover - topBars(LBound(topBars)) / 2
        
        If nTop = 1 Then
            ' Single bar: center it
            X = originX + B / 2
            Call DXF_RebarSection(X, Y, topBars(LBound(topBars)), True)
        Else
            ' Multiple bars: correct spacing = (B - 2*effectiveCover - bar_dia) / (n - 1)
            Dim avgBarDiaTop As Double
            avgBarDiaTop = topBars(LBound(topBars))  ' Use first bar diameter
            Dim availableWidthTop As Double
            availableWidthTop = B - 2 * effectiveCover - avgBarDiaTop
            spacing = availableWidthTop / (nTop - 1)
            
            X = originX + effectiveCover + topBars(LBound(topBars)) / 2
            For i = LBound(topBars) To UBound(topBars)
                Call DXF_RebarSection(X, Y, topBars(i), True)
                If i < UBound(topBars) Then
                    X = X + spacing
                End If
            Next i
        End If
    End If
    
    ' Add dimensions
    Call DXF_Dimension(originX, originY, originX + B, originY, -40)  ' Width
    Call DXF_Dimension(originX, originY, originX, originY + D, -40)  ' Depth
    
    ' Add title
    Call DXF_Text(originX, originY - 80, 30, "BEAM SECTION", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX, originY - 110, 20, B & " x " & D & " mm", LAYER_TEXT_CALLOUT)
    
    ' Close file
    Call DXF_Close
    
    Draw_BeamSection = True
    Exit Function
    
ErrorHandler:
    If m_Context.IsOpen Then DXF_Close
    Draw_BeamSection = False
End Function

'@Description: Generate beam longitudinal section drawing
'@Param filePath: Output DXF file path
'@Param length: Beam length (mm)
'@Param D: Beam depth (mm)
'@Param cover: Clear cover (mm)
'@Param topBarDia: Top bar diameter
'@Param bottomBarDia: Bottom bar diameter
'@Param stirrupDia: Stirrup diameter
'@Param stirrupSpacing: Stirrup spacing
'@Returns: True if successful
Public Function Draw_BeamLongitudinal(ByVal filePath As String, _
                                     ByVal length As Double, ByVal D As Double, _
                                     ByVal cover As Double, _
                                     ByVal topBarDia As Double, _
                                     ByVal bottomBarDia As Double, _
                                     ByVal stirrupDia As Double, _
                                     ByVal stirrupSpacing As Double) As Boolean
    On Error GoTo ErrorHandler
    
    Dim success As Boolean
    Dim i As Long
    Dim nStirrups As Long
    Dim X As Double, Y As Double
    Dim effectiveCover As Double
    Dim scale As Double
    
    ' Scale factor for drawing (1:10 for typical beams)
    scale = 0.1
    
    ' Initialize DXF file
    success = DXF_Initialize(filePath)
    If Not success Then GoTo ErrorHandler
    
    effectiveCover = cover + stirrupDia
    
    ' Origin
    Dim originX As Double, originY As Double
    originX = 50
    originY = 50
    
    ' Scaled dimensions
    Dim sLength As Double, sD As Double
    sLength = length * scale
    sD = D * scale
    
    ' Draw beam outline
    Call DXF_Rectangle(originX, originY, sLength, sD, LAYER_BEAM_OUTLINE)
    
    ' Draw top bar (single line representation)
    Y = originY + sD - (effectiveCover + topBarDia / 2) * scale
    Call DXF_Line(originX + cover * scale, Y, originX + sLength - cover * scale, Y, LAYER_REBAR_MAIN)
    
    ' Draw bottom bar
    Y = originY + (effectiveCover + bottomBarDia / 2) * scale
    Call DXF_Line(originX + cover * scale, Y, originX + sLength - cover * scale, Y, LAYER_REBAR_MAIN)
    
    ' Draw stirrups (with guard against zero/small spacing)
    If stirrupSpacing >= 25 Then
        nStirrups = Int((length - 2 * cover) / stirrupSpacing)
        If nStirrups > 500 Then nStirrups = 500  ' Safety cap
        X = originX + cover * scale
        
        For i = 0 To nStirrups
            Call DXF_Line(X, originY + cover * scale, X, originY + sD - cover * scale, LAYER_REBAR_STIRRUP)
            X = X + stirrupSpacing * scale
            If X > originX + sLength - cover * scale Then Exit For
        Next i
    End If
    
    ' Draw center line
    Call DXF_Line(originX - 20, originY + sD / 2, originX + sLength + 20, originY + sD / 2, LAYER_CENTERLINE)
    
    ' Add dimensions
    Call DXF_Dimension(originX, originY, originX + sLength, originY, -30)
    Call DXF_Dimension(originX, originY, originX, originY + sD, -30)
    
    ' Add stirrup spacing dimension
    If nStirrups > 1 Then
        X = originX + cover * scale
        Call DXF_Text(X + stirrupSpacing * scale / 2 - 15, originY + sD + 20, 15, _
                     stirrupDia & "T @ " & stirrupSpacing & " c/c", LAYER_TEXT_CALLOUT)
    End If
    
    ' Add title
    Call DXF_Text(originX, originY - 60, 25, "BEAM LONGITUDINAL SECTION", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX, originY - 85, 18, "Scale 1:" & Format(1 / scale, "0"), LAYER_TEXT_CALLOUT)
    
    ' Close file
    Call DXF_Close
    
    Draw_BeamLongitudinal = True
    Exit Function
    
ErrorHandler:
    If m_Context.IsOpen Then DXF_Close
    Draw_BeamLongitudinal = False
End Function

'@Description: Generate complete beam detailing drawing (section + elevation)
'@Param filePath: Output DXF file path
'@Param result: BeamDetailingResult from M15_Detailing
'@Returns: True if successful
Public Function Draw_BeamDetailing(ByVal filePath As String, _
                                  ByRef result As BeamDetailingResult) As Boolean
    On Error GoTo ErrorHandler
    
    Dim success As Boolean
    Dim topBars() As Double
    Dim bottomBars() As Double
    Dim i As Long
    Dim nTop As Long, nBottom As Long
    
    ' Initialize DXF file
    success = DXF_Initialize(filePath)
    If Not success Then GoTo ErrorHandler
    
    ' Use mid-span bars for section view (typical for sagging moment section)
    nTop = result.top_mid.count
    nBottom = result.bottom_mid.count
    
    ' Guard against zero bars
    If nTop < 1 Then nTop = 1
    If nBottom < 1 Then nBottom = 1
    
    ' Prepare bar arrays
    ReDim topBars(0 To nTop - 1)
    ReDim bottomBars(0 To nBottom - 1)
    
    For i = 0 To nTop - 1
        topBars(i) = result.top_mid.diameter
    Next i
    
    For i = 0 To nBottom - 1
        bottomBars(i) = result.bottom_mid.diameter
    Next i
    
    ' Origin for section view
    Dim secX As Double, secY As Double
    secX = 50
    secY = 400
    
    ' Draw section view
    Call DrawSectionAtPoint(secX, secY, result.b, result.D, _
                           result.cover, topBars, bottomBars, _
                           result.stirrup_mid.diameter)
    
    ' Origin for longitudinal view
    Dim longX As Double, longY As Double
    longX = 50
    longY = 50
    
    ' Use actual span from result (or default if not set)
    Dim actualSpan As Double
    actualSpan = result.span
    If actualSpan <= 0 Then actualSpan = 3000  ' Default fallback
    
    ' Draw longitudinal view with actual span and zoned stirrups
    Call DrawLongitudinalWithZones(longX, longY, actualSpan, result)
    
    ' Add bar schedule using actual zones
    Call DrawBarScheduleFromResult(secX + result.b + 100, secY, result)
    
    ' Close file
    Call DXF_Close
    
    Draw_BeamDetailing = True
    Exit Function
    
ErrorHandler:
    If m_Context.IsOpen Then DXF_Close
    Draw_BeamDetailing = False
End Function

'@Description: Draw section view at specified point
Private Sub DrawSectionAtPoint(ByVal originX As Double, ByVal originY As Double, _
                              ByVal B As Double, ByVal D As Double, _
                              ByVal cover As Double, _
                              ByRef topBars() As Double, _
                              ByRef bottomBars() As Double, _
                              ByVal stirrupDia As Double)
    
    Dim i As Long
    Dim nTop As Long, nBottom As Long
    Dim spacing As Double
    Dim X As Double, Y As Double
    Dim effectiveCover As Double
    
    effectiveCover = cover + stirrupDia
    
    ' Draw beam outline
    Call DXF_Rectangle(originX, originY, B, D, LAYER_BEAM_OUTLINE)
    
    ' Draw cover lines
    Call DXF_Rectangle(originX + cover, originY + cover, _
                      B - 2 * cover, D - 2 * cover, LAYER_COVER_LINE)
    
    ' Draw stirrup
    Call DXF_Stirrup(originX + B / 2, originY + D / 2, _
                    B - 2 * cover - stirrupDia, D - 2 * cover - stirrupDia, _
                    stirrupDia)
    
    ' Draw center line
    Call DXF_Line(originX + B / 2, originY - 15, originX + B / 2, originY + D + 15, LAYER_CENTERLINE)
    
    ' Draw bottom bars
    nBottom = UBound(bottomBars) - LBound(bottomBars) + 1
    If nBottom > 0 Then
        Y = originY + effectiveCover + bottomBars(LBound(bottomBars)) / 2
        
        If nBottom = 1 Then
            ' Single bar: center it
            X = originX + B / 2
            Call DXF_RebarSection(X, Y, bottomBars(LBound(bottomBars)))
        Else
            ' Multiple bars: correct spacing is center-to-center distance
            ' Clear width between bars = B - 2*effectiveCover - sum(bar_dias)
            ' But since we draw at centers, spacing = (B - 2*effectiveCover - bar_dia) / (n - 1)
            ' This places first bar center at effectiveCover + bar_dia/2 from edge
            Dim avgBarDiaBot As Double
            avgBarDiaBot = bottomBars(LBound(bottomBars))  ' Use first bar diameter
            Dim availWidthBot As Double
            availWidthBot = B - 2 * effectiveCover - avgBarDiaBot
            spacing = availWidthBot / (nBottom - 1)
            
            X = originX + effectiveCover + bottomBars(LBound(bottomBars)) / 2
            For i = LBound(bottomBars) To UBound(bottomBars)
                Call DXF_RebarSection(X, Y, bottomBars(i))
                If i < UBound(bottomBars) Then X = X + spacing
            Next i
        End If
    End If
    
    ' Draw top bars
    nTop = UBound(topBars) - LBound(topBars) + 1
    If nTop > 0 Then
        Y = originY + D - effectiveCover - topBars(LBound(topBars)) / 2
        
        If nTop = 1 Then
            ' Single bar: center it
            X = originX + B / 2
            Call DXF_RebarSection(X, Y, topBars(LBound(topBars)))
        Else
            ' Multiple bars: correct spacing includes bar diameter deduction
            ' spacing = (B - 2*effectiveCover - bar_dia) / (n - 1)
            Dim avgBarDiaTop As Double
            avgBarDiaTop = topBars(LBound(topBars))  ' Use first bar diameter
            Dim availWidthTop As Double
            availWidthTop = B - 2 * effectiveCover - avgBarDiaTop
            spacing = availWidthTop / (nTop - 1)
            
            X = originX + effectiveCover + topBars(LBound(topBars)) / 2
            For i = LBound(topBars) To UBound(topBars)
                Call DXF_RebarSection(X, Y, topBars(i))
                If i < UBound(topBars) Then X = X + spacing
            Next i
        End If
    End If
    
    ' Add dimensions
    Call DXF_Dimension(originX, originY, originX + B, originY, -35)
    Call DXF_Dimension(originX, originY, originX, originY + D, -35)
    
    ' Add title
    Call DXF_Text(originX, originY - 60, 20, "SECTION A-A", LAYER_TEXT_CALLOUT)
End Sub

'@Description: Draw longitudinal view at specified point
Private Sub DrawLongitudinalAtPoint(ByVal originX As Double, ByVal originY As Double, _
                                   ByVal length As Double, ByVal D As Double, _
                                   ByVal cover As Double, _
                                   ByVal topBarDia As Double, _
                                   ByVal bottomBarDia As Double, _
                                   ByVal stirrupDia As Double, _
                                   ByVal stirrupSpacing As Double)
    
    Dim i As Long
    Dim nStirrups As Long
    Dim X As Double, Y As Double
    Dim effectiveCover As Double
    Dim scale As Double
    
    scale = 0.1  ' 1:10 scale
    effectiveCover = cover + stirrupDia
    
    Dim sLength As Double, sD As Double
    sLength = length * scale
    sD = D * scale
    
    ' Draw beam outline
    Call DXF_Rectangle(originX, originY, sLength, sD, LAYER_BEAM_OUTLINE)
    
    ' Draw top bar
    Y = originY + sD - (effectiveCover + topBarDia / 2) * scale
    Call DXF_Line(originX + cover * scale, Y, originX + sLength - cover * scale, Y, LAYER_REBAR_MAIN)
    
    ' Draw bottom bar
    Y = originY + (effectiveCover + bottomBarDia / 2) * scale
    Call DXF_Line(originX + cover * scale, Y, originX + sLength - cover * scale, Y, LAYER_REBAR_MAIN)
    
    ' Draw stirrups (with guard against zero/small spacing)
    If stirrupSpacing >= 25 Then
        nStirrups = Int((length - 2 * cover) / stirrupSpacing)
        If nStirrups > 500 Then nStirrups = 500  ' Safety cap
        X = originX + cover * scale
        
        For i = 0 To nStirrups
            Call DXF_Line(X, originY + cover * scale, X, originY + sD - cover * scale, LAYER_REBAR_STIRRUP)
            X = X + stirrupSpacing * scale
            If X > originX + sLength - cover * scale Then Exit For
        Next i
    End If
    
    ' Draw center line
    Call DXF_Line(originX - 15, originY + sD / 2, originX + sLength + 15, originY + sD / 2, LAYER_CENTERLINE)
    
    ' Add dimensions
    Call DXF_Dimension(originX, originY, originX + sLength, originY, -25)
    
    ' Add stirrup callout
    Call DXF_Text(originX + sLength / 2 - 40, originY + sD + 15, 12, _
                 stirrupDia & "T @ " & stirrupSpacing & " c/c", LAYER_TEXT_CALLOUT)
    
    ' Add title
    Call DXF_Text(originX, originY - 45, 20, "LONGITUDINAL SECTION", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX, originY - 65, 12, "Scale 1:10", LAYER_TEXT_CALLOUT)
End Sub

'@Description: Draw longitudinal view with zoned stirrups
Private Sub DrawLongitudinalWithZones(ByVal originX As Double, ByVal originY As Double, _
                                     ByVal span As Double, _
                                     ByRef result As BeamDetailingResult)
    
    Dim i As Long
    Dim X As Double, Y As Double
    Dim effectiveCover As Double
    Dim scale As Double
    
    scale = 0.1  ' 1:10 scale
    effectiveCover = result.cover + result.stirrup_mid.diameter
    
    Dim sLength As Double, sD As Double
    sLength = span * scale
    sD = result.D * scale
    
    ' Draw beam outline
    Call DXF_Rectangle(originX, originY, sLength, sD, LAYER_BEAM_OUTLINE)
    
    ' Draw top bar (use maximum of start/mid/end)
    Dim topDia As Double
    topDia = result.top_mid.diameter
    If result.top_start.diameter > topDia Then topDia = result.top_start.diameter
    If result.top_end.diameter > topDia Then topDia = result.top_end.diameter
    
    Y = originY + sD - (effectiveCover + topDia / 2) * scale
    Call DXF_Line(originX + result.cover * scale, Y, originX + sLength - result.cover * scale, Y, LAYER_REBAR_MAIN)
    
    ' Draw bottom bar
    Dim botDia As Double
    botDia = result.bottom_mid.diameter
    If result.bottom_start.diameter > botDia Then botDia = result.bottom_start.diameter
    If result.bottom_end.diameter > botDia Then botDia = result.bottom_end.diameter
    
    Y = originY + (effectiveCover + botDia / 2) * scale
    Call DXF_Line(originX + result.cover * scale, Y, originX + sLength - result.cover * scale, Y, LAYER_REBAR_MAIN)
    
    ' Draw stirrups in zones
    Dim zoneStartX As Double, zoneEndX As Double
    Dim nStirrups As Long
    Dim maxIterations As Long
    Dim iterCount As Long
    Const MIN_SPACING As Double = 25  ' Minimum 25mm spacing to prevent infinite loops
    
    maxIterations = 500  ' Safety cap
    
    ' Start zone (typically 20% of span) - starts at cover, ends at cover + zone_length
    zoneStartX = originX + result.cover * scale
    zoneEndX = zoneStartX + result.stirrup_start.zone_length * scale
    If result.stirrup_start.spacing >= MIN_SPACING Then
        X = zoneStartX
        iterCount = 0
        Do While X <= zoneEndX And iterCount < maxIterations
            Call DXF_Line(X, originY + result.cover * scale, X, originY + sD - result.cover * scale, LAYER_REBAR_STIRRUP)
            X = X + result.stirrup_start.spacing * scale
            iterCount = iterCount + 1
        Loop
    End If
    
    ' Mid zone (typically 60% of span)
    zoneStartX = zoneEndX
    zoneEndX = zoneStartX + result.stirrup_mid.zone_length * scale
    If result.stirrup_mid.spacing >= MIN_SPACING Then
        X = zoneStartX
        iterCount = 0
        Do While X <= zoneEndX And iterCount < maxIterations
            Call DXF_Line(X, originY + result.cover * scale, X, originY + sD - result.cover * scale, LAYER_REBAR_STIRRUP)
            X = X + result.stirrup_mid.spacing * scale
            iterCount = iterCount + 1
        Loop
    End If
    
    ' End zone (typically 20% of span)
    zoneStartX = zoneEndX
    zoneEndX = originX + sLength - result.cover * scale
    If result.stirrup_end.spacing >= MIN_SPACING Then
        X = zoneStartX
        iterCount = 0
        Do While X <= zoneEndX And iterCount < maxIterations
            Call DXF_Line(X, originY + result.cover * scale, X, originY + sD - result.cover * scale, LAYER_REBAR_STIRRUP)
            X = X + result.stirrup_end.spacing * scale
            iterCount = iterCount + 1
        Loop
    End If
    
    ' Draw center line
    Call DXF_Line(originX - 15, originY + sD / 2, originX + sLength + 15, originY + sD / 2, LAYER_CENTERLINE)
    
    ' Add dimensions
    Call DXF_Dimension(originX, originY, originX + sLength, originY, -25)
    
    ' Add stirrup callouts for each zone
    Dim calloutY As Double
    calloutY = originY + sD + 15
    
    ' Start zone callout
    Call DXF_Text(originX + result.stirrup_start.zone_length * scale * 0.3, calloutY, 10, _
                 result.stirrup_start.diameter & "T@" & result.stirrup_start.spacing, LAYER_TEXT_CALLOUT)
    
    ' Mid zone callout
    Call DXF_Text(originX + (result.stirrup_start.zone_length + result.stirrup_mid.zone_length * 0.4) * scale, calloutY, 10, _
                 result.stirrup_mid.diameter & "T@" & result.stirrup_mid.spacing, LAYER_TEXT_CALLOUT)
    
    ' End zone callout
    Call DXF_Text(originX + (result.stirrup_start.zone_length + result.stirrup_mid.zone_length + result.stirrup_end.zone_length * 0.3) * scale, calloutY, 10, _
                 result.stirrup_end.diameter & "T@" & result.stirrup_end.spacing, LAYER_TEXT_CALLOUT)
    
    ' Add title
    Call DXF_Text(originX, originY - 45, 20, "LONGITUDINAL SECTION", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX, originY - 65, 12, "Span: " & span & " mm  Scale 1:10", LAYER_TEXT_CALLOUT)
End Sub

'@Description: Draw bar schedule table using actual BeamDetailingResult
Private Sub DrawBarScheduleFromResult(ByVal originX As Double, ByVal originY As Double, _
                                     ByRef result As BeamDetailingResult)
    
    Dim Y As Double
    Dim rowHeight As Double
    Dim colWidths(0 To 4) As Double
    
    rowHeight = 25
    colWidths(0) = 60   ' Mark
    colWidths(1) = 50   ' Dia
    colWidths(2) = 50   ' No.
    colWidths(3) = 80   ' Zone
    colWidths(4) = 100  ' Shape
    
    Dim totalWidth As Double
    totalWidth = colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + colWidths(4)
    
    ' Title
    Call DXF_Text(originX, originY + rowHeight * 8, 18, "BAR SCHEDULE", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX, originY + rowHeight * 7.3, 12, "Beam: " & result.beam_id & " (" & result.b & "x" & result.D & ")", LAYER_TEXT_CALLOUT)
    
    Y = originY + rowHeight * 6
    
    ' Header row
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "MARK", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "DIA", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, "NO.", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "ZONE", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "SHAPE", LAYER_TEXT_CALLOUT)
    
    ' Bottom bars - mid-span (main tension)
    Y = Y - rowHeight
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "A", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & result.bottom_mid.diameter, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(result.bottom_mid.count), LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "MID", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STRAIGHT", LAYER_TEXT_CALLOUT)
    
    ' Top bars - support (main tension at supports)
    Y = Y - rowHeight
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "B", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & result.top_start.diameter, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(result.top_start.count), LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "START", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STRAIGHT", LAYER_TEXT_CALLOUT)
    
    ' Top bars - end support
    Y = Y - rowHeight
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "C", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & result.top_end.diameter, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(result.top_end.count), LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "END", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STRAIGHT", LAYER_TEXT_CALLOUT)
    
    ' Stirrups - start zone
    Y = Y - rowHeight
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "D", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & result.stirrup_start.diameter, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(result.stirrup_start.legs) & "L", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "@" & result.stirrup_start.spacing, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STIRRUP", LAYER_TEXT_CALLOUT)
    
    ' Stirrups - mid zone
    Y = Y - rowHeight
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "E", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & result.stirrup_mid.diameter, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(result.stirrup_mid.legs) & "L", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "@" & result.stirrup_mid.spacing, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STIRRUP", LAYER_TEXT_CALLOUT)
End Sub

'@Description: Draw bar schedule table (legacy - for simple input)
Private Sub DrawBarSchedule(ByVal originX As Double, ByVal originY As Double, _
                           ByVal topDia As Double, ByVal topCount As Long, _
                           ByVal botDia As Double, ByVal botCount As Long, _
                           ByVal stirrupDia As Double, ByVal stirrupSpacing As Double)
    
    Dim Y As Double
    Dim rowHeight As Double
    Dim colWidths(0 To 4) As Double
    
    rowHeight = 25
    colWidths(0) = 60   ' Mark
    colWidths(1) = 50   ' Dia
    colWidths(2) = 50   ' No.
    colWidths(3) = 80   ' Length
    colWidths(4) = 100  ' Shape
    
    Dim totalWidth As Double
    totalWidth = colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + colWidths(4)
    
    ' Title
    Call DXF_Text(originX, originY + rowHeight * 4, 18, "BAR SCHEDULE", LAYER_TEXT_CALLOUT)
    
    Y = originY + rowHeight * 3
    
    ' Header row
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "MARK", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "DIA", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, "NO.", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "LENGTH", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "SHAPE", LAYER_TEXT_CALLOUT)
    
    ' Data rows
    Y = Y - rowHeight
    
    ' Top bars
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "A", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & topDia, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(topCount), LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "-", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STRAIGHT", LAYER_TEXT_CALLOUT)
    
    Y = Y - rowHeight
    
    ' Bottom bars
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "B", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & botDia, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, CStr(botCount), LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "-", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STRAIGHT", LAYER_TEXT_CALLOUT)
    
    Y = Y - rowHeight
    
    ' Stirrups
    Call DXF_Rectangle(originX, Y, totalWidth, rowHeight, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + 5, Y + 5, 12, "C", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + 5, Y + 5, 12, "T" & stirrupDia, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + 5, Y + 5, 12, "-", LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + 5, Y + 5, 12, "@" & stirrupSpacing, LAYER_TEXT_CALLOUT)
    Call DXF_Text(originX + colWidths(0) + colWidths(1) + colWidths(2) + colWidths(3) + 5, Y + 5, 12, "STIRRUP", LAYER_TEXT_CALLOUT)
End Sub

' ============================================================================
' UTILITY FUNCTIONS
' ============================================================================

'@Description: Get the entity count of current drawing
Public Function DXF_GetEntityCount() As Long
    DXF_GetEntityCount = m_Context.EntityCount
End Function

'@Description: Check if DXF file is currently open
Public Function DXF_IsOpen() As Boolean
    DXF_IsOpen = m_Context.IsOpen
End Function

