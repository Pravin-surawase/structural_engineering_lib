# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for batch design helpers."""

from __future__ import annotations

from structural_lib.services.batch import design_beams, design_beams_iter


def test_design_beams_iter_success() -> None:
    beams = [
        {
            "id": "B1",
            "width": 300,
            "depth": 500,
            "moment": 100,
            "shear": 50,
            "fck": 25,
            "fy": 500,
            "cover": 40,
        }
    ]

    outcome = next(iter(design_beams_iter(beams)))

    assert outcome["success"] is True
    data = outcome["data"]
    assert data["beam_id"] == "B1"
    assert data["design_succeeded"] is True
    assert data["is_safe"] is True
    assert data["status"] == "PASS"
    assert data["flexure"]["is_safe"] is True
    assert set(data["shear"]) == {
        "tau_v",
        "tau_c",
        "tau_c_max",
        "vus",
        "stirrup_spacing",
        "is_safe",
    }
    assert data["shear"]["is_safe"] is True
    assert data["evidence"]["status"] == "PASS"
    assert data["evidence"]["support_status"] == "SUPPORTED"
    assert data["evidence"]["calculation_identity"]


def test_design_beams_iter_unsafe_shear_is_a_completed_failure() -> None:
    outcome = next(
        iter(
            design_beams_iter(
                [
                    {
                        "id": "B-UNSAFE-SHEAR",
                        "width": 300,
                        "depth": 500,
                        "moment": 100,
                        "shear": 600,
                        "fck": 25,
                        "fy": 500,
                        "cover": 40,
                    }
                ]
            )
        )
    )

    assert outcome["success"] is True
    data = outcome["data"]
    assert data["design_succeeded"] is True
    assert data["flexure"]["is_safe"] is True
    assert data["shear"]["is_safe"] is False
    assert data["is_safe"] is False
    assert data["status"] == "FAIL"
    assert data["evidence"]["status"] == "FAIL"
    assert data["evidence"]["support_status"] == "SUPPORTED"
    assert all(
        data["shear"][field] is not None
        for field in ("tau_v", "tau_c", "tau_c_max", "stirrup_spacing")
    )


def test_design_beams_iter_error() -> None:
    beams = [
        {
            "id": "B2",
            "width": 300,
            "depth": 50,
            "moment": 100,
            "shear": 50,
            "cover": 60,
        }
    ]

    outcome = next(iter(design_beams_iter(beams)))

    assert outcome["success"] is False
    assert outcome["error"]["beam_id"] == "B2"


def test_design_beams_summary() -> None:
    beams = [
        {
            "id": "B1",
            "width": 300,
            "depth": 500,
            "moment": 100,
            "shear": 50,
        },
        {
            "id": "B2",
            "width": 300,
            "depth": 50,
            "moment": 100,
            "shear": 50,
            "cover": 60,
        },
        {
            "id": "B3",
            "width": 300,
            "depth": 500,
            "moment": 100,
            "shear": 600,
            "cover": 40,
        },
    ]

    result = design_beams(beams)

    assert result["summary"]["total"] == 3
    assert result["summary"]["passed"] == 1
    assert result["summary"]["failed"] == 2
    assert result["summary"]["status"] == "FAIL"
    assert result["summary"]["is_safe"] is False
    assert len(result["results"]) == 2
    assert len(result["errors"]) == 1
