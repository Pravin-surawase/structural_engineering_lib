import pytest


class _FakeText:
    def __init__(self, text: str, dxfattribs: dict):
        self.text = text
        self.dxfattribs = dxfattribs
        self.placement = None

    def set_placement(self, point, align=None):
        self.placement = (point, align)
        return self


class _FakeModelspace:
    def __init__(self):
        self.lines = []
        self.texts = []
        self.polylines = []
        self.circles = []

    def add_line(self, start, end, dxfattribs=None):
        self.lines.append((start, end, dxfattribs or {}))
        return None

    def add_text(self, text, dxfattribs=None):
        ent = _FakeText(text=text, dxfattribs=dxfattribs or {})
        self.texts.append(ent)
        return ent

    def add_lwpolyline(self, points, dxfattribs=None):
        self.polylines.append((points, dxfattribs or {}))
        return None

    def add_circle(self, center, radius, dxfattribs=None):
        self.circles.append((center, radius, dxfattribs or {}))
        return None


class _FakeLayers:
    def __init__(self):
        self.created = set()

    def add(self, name, color=None):
        # Mirror the real behavior: if already exists, raise DXFTableEntryError.
        if name in self.created:
            raise _FakeEzdxf.DXFTableEntryError("exists")
        self.created.add(name)


class _FakeDoc:
    def __init__(self):
        self.layers = _FakeLayers()
        self._msp = _FakeModelspace()
        self.units = None
        self.saved_to = None

    def modelspace(self):
        return self._msp

    def saveas(self, path):
        self.saved_to = path


class _FakeUnits:
    MM = "MM"


class _FakeTextEntityAlignment:
    TOP_CENTER = "TOP_CENTER"
    MIDDLE_CENTER = "MIDDLE_CENTER"
    LEFT = "LEFT"
    BOTTOM_CENTER = "BOTTOM_CENTER"


class _FakeEzdxf:
    class DXFTableEntryError(Exception):
        pass

    last_doc = None

    @staticmethod
    def new(version):
        assert version == "R2010"
        doc = _FakeDoc()
        _FakeEzdxf.last_doc = doc
        return doc


def test_check_ezdxf_raises_when_missing(monkeypatch):
    import structural_lib.dxf_export as dxf_export

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", False, raising=True)

    with pytest.raises(ImportError, match="ezdxf library not installed"):
        dxf_export.check_ezdxf()


def test_setup_layers_is_idempotent():
    # Calling setup_layers twice should not crash (second call hits "already exists" path).
    import structural_lib.dxf_export as dxf_export

    if not dxf_export.EZDXF_AVAILABLE:
        pytest.skip("ezdxf not installed")

    import ezdxf

    doc = ezdxf.new("R2010")
    dxf_export.setup_layers(doc)
    dxf_export.setup_layers(doc)

    for layer_name in dxf_export.LAYERS.keys():
        assert layer_name in doc.layers


def test_draw_rectangle_adds_four_lines():
    import structural_lib.dxf_export as dxf_export

    msp = _FakeModelspace()
    dxf_export.draw_rectangle(msp, 0, 0, 10, 5, layer="BEAM_OUTLINE")

    assert len(msp.lines) == 4
    assert all(line[2].get("layer") == "BEAM_OUTLINE" for line in msp.lines)


def test_draw_stirrup_adds_u_and_hooks():
    import structural_lib.dxf_export as dxf_export

    msp = _FakeModelspace()
    dxf_export.draw_stirrup(
        msp,
        x=100,
        y_bottom=0,
        width=300,
        height=500,
        cover=25,
        layer="REBAR_STIRRUP",
    )

    # 3 sides of U + 2 hook lines
    assert len(msp.lines) == 5
    assert all(line[2].get("layer") == "REBAR_STIRRUP" for line in msp.lines)


@pytest.mark.parametrize(
    "include_dimensions,include_annotations",
    [(True, True), (False, True), (True, False), (False, False)],
)
def test_generate_beam_dxf_runs_with_stubbed_ezdxf(
    monkeypatch, tmp_path, include_dimensions, include_annotations
):
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    # Stub ezdxf dependency surface.
    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    detailing = BeamDetailingResult(
        beam_id="B1",
        story="S1",
        b=300,
        D=500,
        span=4000,
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
        ],
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
            StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=2000),
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    out = tmp_path / "beam.dxf"
    returned = dxf_export.generate_beam_dxf(
        detailing,
        str(out),
        include_dimensions=include_dimensions,
        include_annotations=include_annotations,
        include_section_cuts=False,  # Disable section cuts for clean text assertions
    )

    assert returned == str(out)

    doc = _FakeEzdxf.last_doc
    assert doc is not None
    assert doc.units == _FakeUnits.MM
    assert doc.saved_to == str(out)

    # Setup layers should create all expected layers.
    assert set(dxf_export.LAYERS.keys()).issubset(doc.layers.created)

    # Beam outline always adds entities.
    assert len(doc._msp.lines) >= 4

    # Dimensions and annotations add TEXT entities; both together add several.
    if include_dimensions or include_annotations:
        assert len(doc._msp.texts) > 0
    else:
        # draw_beam_elevation itself adds no TEXT.
        assert len(doc._msp.texts) == 0


def test_dxf_export_cli_main_reads_json_and_writes(monkeypatch, tmp_path, capsys):
    import json

    import structural_lib.dxf_export as dxf_export
    import structural_lib.detailing as detailing

    # Prepare input JSON
    payload = {
        "beam_id": "B9",
        "story": "S3",
        "b": 250,
        "D": 500,
        "span": 6000,
        "cover": 30,
        "fck": 30,
        "fy": 500,
        "ast_start": 900,
        "ast_mid": 1200,
        "ast_end": 950,
    }
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "out.dxf"

    sentinel_detailing = object()

    def _fake_create_beam_detailing(**kwargs):
        # Ensure JSON values are wired through.
        assert kwargs["beam_id"] == payload["beam_id"]
        assert kwargs["story"] == payload["story"]
        assert kwargs["b"] == payload["b"]
        assert kwargs["D"] == payload["D"]
        assert kwargs["span"] == payload["span"]
        assert kwargs["cover"] == payload["cover"]
        assert kwargs["fck"] == payload["fck"]
        assert kwargs["fy"] == payload["fy"]
        assert kwargs["ast_start"] == payload["ast_start"]
        assert kwargs["ast_mid"] == payload["ast_mid"]
        assert kwargs["ast_end"] == payload["ast_end"]
        return sentinel_detailing

    def _fake_generate_beam_dxf(detailing_obj, output_path, **_):
        assert detailing_obj is sentinel_detailing
        assert output_path == str(out)
        return output_path

    monkeypatch.setattr(
        detailing, "create_beam_detailing", _fake_create_beam_detailing, raising=True
    )
    monkeypatch.setattr(
        dxf_export, "generate_beam_dxf", _fake_generate_beam_dxf, raising=True
    )

    # Drive CLI args
    monkeypatch.setattr(
        dxf_export,
        "__name__",
        "structural_lib.dxf_export",
        raising=False,
    )
    monkeypatch.setattr(
        __import__("sys"),
        "argv",
        ["dxf_export", str(inp), "-o", str(out)],
        raising=True,
    )

    dxf_export.main()

    captured = capsys.readouterr().out
    assert "DXF generated:" in captured
    assert str(out) in captured


def test_section_cuts_added_when_enabled(monkeypatch, tmp_path):
    """Test that section cut views are added when include_section_cuts=True."""
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    # Stub ezdxf dependency surface.
    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    detailing = BeamDetailingResult(
        beam_id="B1",
        story="S1",
        b=300,
        D=500,
        span=4000,
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
        ],
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
            StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=2000),
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    out = tmp_path / "beam_with_sections.dxf"
    dxf_export.generate_beam_dxf(
        detailing,
        str(out),
        include_dimensions=False,
        include_annotations=False,
        include_section_cuts=True,
    )

    doc = _FakeEzdxf.last_doc

    # Section cuts add circles (for rebars) and polylines (for stirrup outline)
    assert len(doc._msp.circles) > 0, "Section cuts should draw rebar circles"
    assert len(doc._msp.polylines) > 0, "Section cuts should draw stirrup polylines"

    # Section cuts add text labels (section titles, bar callouts)
    section_texts = [t.text for t in doc._msp.texts]
    assert any(
        "SECTION A-A" in t for t in section_texts
    ), "Should have Section A-A title"
    assert any(
        "SECTION B-B" in t for t in section_texts
    ), "Should have Section B-B title"


def test_multi_beam_layout_generates_combined_dxf(monkeypatch, tmp_path):
    """Test that generate_multi_beam_dxf creates a combined drawing."""
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    # Stub ezdxf dependency surface.
    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    # Create two test beams
    beam1 = BeamDetailingResult(
        beam_id="B1",
        story="S1",
        b=300,
        D=500,
        span=4000,
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
        ],
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
            StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=2000),
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    beam2 = BeamDetailingResult(
        beam_id="B2",
        story="S1",
        b=250,
        D=450,
        span=3500,
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            ),
            BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            ),
        ],
        bottom_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=100, layers=1
            ),
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=100, layers=1
            ),
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=875),
            StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=1750),
        ],
        ld_tension=550,
        ld_compression=450,
        lap_length=650,
        is_valid=True,
        remarks="OK",
    )

    out = tmp_path / "multi_beam.dxf"
    returned = dxf_export.generate_multi_beam_dxf(
        [beam1, beam2],
        str(out),
        columns=2,
        include_section_cuts=True,
    )

    assert returned == str(out)

    doc = _FakeEzdxf.last_doc
    assert doc is not None
    assert doc.saved_to == str(out)

    # Should have drawings for both beams
    # Each beam adds at least 4 lines for outline
    assert len(doc._msp.lines) >= 8, "Should have lines for both beams"

    # Should have circles for rebar in section cuts
    assert len(doc._msp.circles) > 0, "Should have rebar circles from section cuts"

    # Should have annotations for both beams
    texts = [t.text for t in doc._msp.texts]
    assert any("B1" in t for t in texts), "Should have B1 beam ID"
    assert any("B2" in t for t in texts), "Should have B2 beam ID"


def test_multi_beam_layout_rejects_empty_list(monkeypatch, tmp_path):
    """Test that generate_multi_beam_dxf raises error for empty list."""
    import structural_lib.dxf_export as dxf_export

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    out = tmp_path / "empty.dxf"
    with pytest.raises(ValueError, match="At least one beam"):
        dxf_export.generate_multi_beam_dxf([], str(out))


def test_multi_beam_layout_rejects_zero_columns(monkeypatch, tmp_path):
    """Test that generate_multi_beam_dxf raises error for columns < 1."""
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    beam = BeamDetailingResult(
        beam_id="B1",
        story="S1",
        b=300,
        D=500,
        span=4000,
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            )
        ],
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            )
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000)
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    out = tmp_path / "zero_cols.dxf"
    with pytest.raises(ValueError, match="columns must be >= 1"):
        dxf_export.generate_multi_beam_dxf([beam], str(out), columns=0)


def test_multi_beam_layout_mixed_sizes_no_overlap(monkeypatch, tmp_path):
    """Test that beams with different spans/widths don't overlap in grid layout."""
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    # Create beams with very different spans (5000 vs 3000)
    beam_large = BeamDetailingResult(
        beam_id="B1-LARGE",
        story="S1",
        b=350,
        D=600,
        span=5000,  # Large span
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            )
        ],
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            )
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000)
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    beam_small = BeamDetailingResult(
        beam_id="B2-SMALL",
        story="S1",
        b=200,
        D=400,
        span=3000,  # Small span
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        ],
        bottom_bars=[
            BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=1000)
        ],
        ld_tension=500,
        ld_compression=400,
        lap_length=600,
        is_valid=True,
        remarks="OK",
    )

    # Put both in same row (columns=2)
    out = tmp_path / "mixed_sizes.dxf"
    dxf_export.generate_multi_beam_dxf(
        [beam_large, beam_small],
        str(out),
        columns=2,
        col_spacing=500,
        include_section_cuts=True,
    )

    doc = _FakeEzdxf.last_doc
    assert doc is not None

    # Check that we have drawings for both beams
    texts = [t.text for t in doc._msp.texts]
    assert any("B1-LARGE" in t for t in texts), "Should have B1-LARGE"
    assert any("B2-SMALL" in t for t in texts), "Should have B2-SMALL"

    # --- Geometry overlap check ---
    # Find title text positions to verify no overlap between beams
    beam1_title = None
    beam2_title = None
    for t in doc._msp.texts:
        if "B1-LARGE" in t.text:
            beam1_title = t
        elif "B2-SMALL" in t.text:
            beam2_title = t

    assert beam1_title is not None and beam2_title is not None

    # Beam 1 (large) cell width with sections: span + 500 + b*2 + 200 + DIM_OFFSET + TEXT_HEIGHT + 20
    # = 5000 + 500 + 350 + 200 + 350 + 100 + 50 + 20 = 6570
    # Beam 2 should start at >= 6570 + col_spacing(500) = 7070
    beam1_x = beam1_title.placement[0][0]  # placement is ((x, y), align)
    beam2_x = beam2_title.placement[0][0]

    # Beam 2's x origin should be significantly greater than beam 1's x origin
    # At minimum: beam1_x + large_span + section_space + col_spacing
    min_expected_gap = 5000 + 500  # span + minimal section space
    assert (
        beam2_x >= beam1_x + min_expected_gap
    ), f"Beam 2 x={beam2_x} should be >= beam1_x({beam1_x}) + {min_expected_gap}"


# ============================================================================
# Q-014: Additional edge cases for DXF export
# ============================================================================


def test_multi_beam_layout_single_beam(monkeypatch, tmp_path):
    """Q-014: Single beam with columns=1 should work correctly."""
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    beam = BeamDetailingResult(
        beam_id="B-SINGLE",
        story="S1",
        b=250,
        D=450,
        span=3500,
        cover=35,
        top_bars=[
            BarArrangement(
                count=2, diameter=12, area_provided=226, spacing=100, layers=1
            )
        ],
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=100, layers=1
            )
        ],
        stirrups=[StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=800)],
        ld_tension=500,
        ld_compression=400,
        lap_length=600,
        is_valid=True,
        remarks="Single beam test",
    )

    out = tmp_path / "single_beam.dxf"
    dxf_export.generate_multi_beam_dxf([beam], str(out), columns=1)

    doc = _FakeEzdxf.last_doc
    assert doc is not None
    assert doc.saved_to == str(out)

    # Should have drawings for the single beam
    texts = [t.text for t in doc._msp.texts]
    assert any("B-SINGLE" in t for t in texts), "Should have B-SINGLE beam ID"


def test_multi_beam_layout_large_grid(monkeypatch, tmp_path):
    """Q-014: 12 beams in 3x4 grid should work without overlap."""
    import structural_lib.dxf_export as dxf_export
    from structural_lib.detailing import (
        BarArrangement,
        BeamDetailingResult,
        StirrupArrangement,
    )

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", True, raising=True)
    monkeypatch.setattr(dxf_export, "ezdxf", _FakeEzdxf, raising=False)
    monkeypatch.setattr(dxf_export, "units", _FakeUnits, raising=False)
    monkeypatch.setattr(
        dxf_export,
        "TextEntityAlignment",
        _FakeTextEntityAlignment,
        raising=False,
    )

    beams = []
    for i in range(12):
        beam = BeamDetailingResult(
            beam_id=f"B{i+1:02d}",
            story=f"S{(i % 3) + 1}",
            b=230 + (i * 10),  # Varying widths
            D=400 + (i * 20),  # Varying depths
            span=3000 + (i * 100),  # Varying spans
            cover=40,
            top_bars=[
                BarArrangement(
                    count=2, diameter=12, area_provided=226, spacing=100, layers=1
                )
            ],
            bottom_bars=[
                BarArrangement(
                    count=3, diameter=16, area_provided=603, spacing=100, layers=1
                )
            ],
            stirrups=[
                StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=800)
            ],
            ld_tension=500,
            ld_compression=400,
            lap_length=600,
            is_valid=True,
            remarks=f"Beam {i+1}",
        )
        beams.append(beam)

    out = tmp_path / "large_grid.dxf"
    dxf_export.generate_multi_beam_dxf(beams, str(out), columns=3)

    doc = _FakeEzdxf.last_doc
    assert doc is not None
    assert doc.saved_to == str(out)

    # Should have drawings for all 12 beams
    texts = [t.text for t in doc._msp.texts]
    for i in range(12):
        beam_id = f"B{i+1:02d}"
        assert any(beam_id in t for t in texts), f"Should have {beam_id} beam ID"

    # Should have a reasonable number of lines (at least 4 rectangle lines per beam)
    assert (
        len(doc._msp.lines) >= 12 * 4
    ), f"Expected at least 48 lines, got {len(doc._msp.lines)}"
