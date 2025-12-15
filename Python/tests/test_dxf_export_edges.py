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

    def add_line(self, start, end, dxfattribs=None):
        self.lines.append((start, end, dxfattribs or {}))
        return None

    def add_text(self, text, dxfattribs=None):
        ent = _FakeText(text=text, dxfattribs=dxfattribs or {})
        self.texts.append(ent)
        return ent


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
