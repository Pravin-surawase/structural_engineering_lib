Attribute VB_Name = "Example_Usage"
'===============================================================================
' Example_Usage.bas
' Purpose: Worked examples for IS 456 RC Beam Design (flexure + shear)
' Notes: Assumes library modules M01–M08 are imported or StructEngLib.xlam is loaded
'===============================================================================
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

Public Sub Example_Flexure_150kNm()
    Dim res As FlexureResult
    ' Inputs: b=230 mm, d=450 mm, D=500 mm, Mu=150 kN·m, fck=25, fy=500
    res = Design_Singly_Reinforced(230, 450, 500, 150, 25, 500)

    Debug.Print "Flexure example (150 kNm, M25/Fe500)"
    Debug.Print "Mu_lim (kN·m): "; res.Mu_Lim
    Debug.Print "Ast_required (mm^2): "; res.Ast_Required
    Debug.Print "Pt_provided (%): "; res.Pt_Provided
    Debug.Print "Xu (mm): "; res.Xu
    Debug.Print "Status: "; IIf(res.IsSafe, "SAFE", "UNSAFE"); " - "; res.ErrorMessage
End Sub

Public Sub Example_Flexure_MinSteel()
    Dim res As FlexureResult
    ' Inputs: very small Mu => expect Ast_min to govern
    res = Design_Singly_Reinforced(230, 450, 500, 5, 20, 415)

    Debug.Print "Flexure example (Min steel governed)"
    Debug.Print "Ast_required (mm^2): "; res.Ast_Required
    Debug.Print "Status: "; IIf(res.IsSafe, "SAFE", "UNSAFE"); " - "; res.ErrorMessage
End Sub

Public Sub Example_Shear_100kN()
    Dim res As ShearResult
    ' Inputs: b=230 mm, d=450 mm, Vu=100 kN, fck=20, fy=415, Asv=100.5 mm^2 (2-legged 8mm), pt=1.0%
    res = Design_Shear(100, 230, 450, 20, 415, 100.5, 1)

    Debug.Print "Shear example (100 kN, M20/Fe415, pt=1%)"
    Debug.Print "Tv (N/mm^2): "; res.Tv
    Debug.Print "Tc (N/mm^2): "; res.Tc
    Debug.Print "Tc_max (N/mm^2): "; res.Tc_max
    Debug.Print "Vus (kN): "; res.Vus
    Debug.Print "Spacing (mm): "; res.Spacing
    Debug.Print "Status: "; IIf(res.IsSafe, "SAFE", "UNSAFE"); " - "; res.Remarks
End Sub

Public Sub Example_Shear_Unsafe()
    Dim res As ShearResult
    ' Inputs to force τv > τc,max
    res = Design_Shear(300, 230, 450, 20, 415, 100.5, 1)

    Debug.Print "Shear example (unsafe section)"
    Debug.Print "Tv (N/mm^2): "; res.Tv
    Debug.Print "Tc_max (N/mm^2): "; res.Tc_max
    Debug.Print "Status: "; IIf(res.IsSafe, "SAFE", "UNSAFE"); " - "; res.Remarks
End Sub
