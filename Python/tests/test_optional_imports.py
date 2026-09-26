"""Calculation and discovery callers should not pay for optional renderers."""

from __future__ import annotations

import subprocess
import sys
from textwrap import dedent

import pytest


def _run_fresh(code: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-c", dedent(code)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize(
    "statement",
    [
        "import structural_lib",
        "from structural_lib.design.is456 import column",
        "from structural_lib import __main__ as cli; cli.main(['capabilities', '--json'])",
    ],
)
def test_calculation_and_cli_discovery_leave_renderers_unloaded(statement: str) -> None:
    _run_fresh(f"""\
        import sys
        {statement}
        import structural_lib
        assert {{'dxf_export', 'reports'}} <= set(dir(structural_lib))
        for name in ('ezdxf', 'jinja2', 'structural_lib.services.dxf_export', 'structural_lib.reports'):
            assert name not in sys.modules, name
        """)


def test_optional_root_exports_resolve_and_cache_the_existing_owners() -> None:
    _run_fresh("""\
        import importlib
        import structural_lib
        from structural_lib import dxf_export, reports
        assert dxf_export is importlib.import_module('structural_lib.services.dxf_export')
        assert reports is importlib.import_module('structural_lib.reports')
        assert structural_lib.dxf_export is dxf_export
        assert structural_lib.reports is reports
        assert callable(dxf_export.generate_beam_dxf)
        assert callable(reports.generate_html_report)
        """)


def test_missing_extras_preserve_calculation_import_and_output_fallbacks() -> None:
    _run_fresh("""\
        import importlib.abc
        import sys

        class MissingExtras(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] in {'ezdxf', 'jinja2'}:
                    raise ModuleNotFoundError(fullname, name=fullname)

        sys.meta_path.insert(0, MissingExtras())
        from structural_lib.design.is456 import column
        from structural_lib import dxf_export, reports
        assert not dxf_export.EZDXF_AVAILABLE
        try:
            dxf_export.check_ezdxf()
        except ImportError as exc:
            assert 'pip install ezdxf' in str(exc)
        else:
            raise AssertionError('DXF must explain its missing dependency')
        assert not reports.JINJA2_AVAILABLE
        html = reports.generate_html_report(
            {'inputs': {'b_mm': 300}, 'results': {}, 'is_ok': True},
            beam_id='B1',
        )
        assert 'B1' in html
        """)
