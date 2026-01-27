# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for rebar validation helpers."""

from __future__ import annotations

from structural_lib.rebar import apply_rebar_config, validate_rebar_config


def test_validate_rebar_config_ok() -> None:
    beam = {"b_mm": 300, "D_mm": 500, "cover_mm": 40}
    config = {"bar_count": 3, "bar_dia_mm": 16}

    report = validate_rebar_config(beam, config)

    assert report.ok is True
    assert report.details["bar_count"] == 3


def test_apply_rebar_config_ok() -> None:
    beam = {"b_mm": 300, "D_mm": 500, "cover_mm": 40, "span_mm": 5000}
    config = {"bar_count": 3, "bar_dia_mm": 16}

    result = apply_rebar_config(beam, config)

    assert result["success"] is True
    assert len(result["geometry"]["rebars"]) == 3
    assert result["geometry"]["stirrups"]


def test_validate_rebar_config_error() -> None:
    beam = {"b_mm": 300, "D_mm": 500, "cover_mm": 40}
    config = {"bar_count": 0, "bar_dia_mm": 16}

    report = validate_rebar_config(beam, config)

    assert report.ok is False
    assert report.errors
