#!/usr/bin/env python3
"""
Run VBA smoke tests via Excel automation (macOS).

This script opens an Excel workbook, runs one or more VBA macros,
and reports success/failure. It is intended for quick smoke validation
of VBA test suites, not full CI execution.

Default macro: Test_RunAll.RunAllVBATests
Default workbook: Excel/BeamDesignApp.xlsm
"""

from __future__ import annotations

import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List


DEFAULT_WORKBOOK = Path("Excel/BeamDesignApp.xlsm")
DEFAULT_MACROS = ["Test_RunAll.RunAllVBATests"]
DEFAULT_EXCEL_APP = "Microsoft Excel"
DEFAULT_LOG = Path("logs/vba_smoke_test.log")


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(message: str, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{_timestamp()}] {message}\n")


def _run_osascript(script: str, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["osascript", "-e", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _build_applescript(workbook_path: Path, macros: List[str], excel_app: str) -> str:
    macro_list = ", ".join([f'"{macro}"' for macro in macros])
    workbook_posix = workbook_path.resolve().as_posix()
    return f"""
    tell application "{excel_app}"
        set display alerts to false
        open (POSIX file "{workbook_posix}")
        set wb to active workbook
        repeat with macroName in {{{macro_list}}}
            run VB macro (contents of macroName)
        end repeat
        close wb saving no
    end tell
    """


def run_smoke_tests(
    workbook_path: Path, macros: List[str], excel_app: str, log_path: Path, timeout: int
) -> int:
    if sys.platform != "darwin":
        _log("Skipping VBA smoke tests: macOS required for Excel automation.", log_path)
        print("VBA smoke tests skipped: macOS required.")
        return 0

    if not workbook_path.exists():
        _log(f"Workbook not found: {workbook_path}", log_path)
        print(f"ERROR: Workbook not found: {workbook_path}")
        return 2

    script = _build_applescript(workbook_path, macros, excel_app)
    _log(
        f"Starting VBA smoke tests: workbook={workbook_path}, macros={macros}", log_path
    )

    try:
        result = _run_osascript(script, timeout=timeout)
    except subprocess.TimeoutExpired:
        _log("ERROR: VBA smoke tests timed out.", log_path)
        print("ERROR: VBA smoke tests timed out.")
        return 3

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        _log(
            f"ERROR: VBA smoke tests failed. stderr={stderr} stdout={stdout}", log_path
        )
        print("ERROR: VBA smoke tests failed.")
        if stderr:
            print(stderr)
        return 1

    _log("VBA smoke tests completed successfully.", log_path)
    print("VBA smoke tests completed successfully.")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run VBA smoke tests via Excel (macOS)."
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        default=DEFAULT_WORKBOOK,
        help="Path to macro-enabled workbook (default: Excel/BeamDesignApp.xlsm)",
    )
    parser.add_argument(
        "--macro",
        action="append",
        dest="macros",
        help="VBA macro to run (repeatable). Defaults to Test_RunAll.RunAllVBATests.",
    )
    parser.add_argument(
        "--excel-app",
        default=DEFAULT_EXCEL_APP,
        help="Excel application name (default: Microsoft Excel)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help="Log file path (default: logs/vba_smoke_test.log)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Timeout in seconds for running macros (default: 180)",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    macros = args.macros or DEFAULT_MACROS
    workbook_path = Path(args.workbook)
    return run_smoke_tests(
        workbook_path, macros, args.excel_app, args.log, args.timeout
    )


if __name__ == "__main__":
    raise SystemExit(main())
