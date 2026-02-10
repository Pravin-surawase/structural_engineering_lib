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
    assert data["status"] in {"PASS", "FAIL"}
    assert "flexure" in data


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
    ]

    result = design_beams(beams)

    assert result["summary"]["total"] == 2
    assert result["summary"]["failed"] == 1
    assert len(result["results"]) == 1
    assert len(result["errors"]) == 1
