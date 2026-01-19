#!/usr/bin/env python3
"""
VBA Quote Detector - Detect all types of quotes in VBA files
Shows hex values and character codes

ARCHIVE METADATA:
  Archive Date: 2025-01-17
  Project: ETABS Export VBA Validation
  Status: DIAGNOSTIC TOOL - Used to verify fixes
  Location: scripts/_vba_tools_archive_2025-01-17/

  Why Archived:
    - Specialized debugging tool for hex-level analysis
    - Used to verify fix_vba_quotes.py worked correctly
    - Confirmed all 10 ETABS files have correct ASCII quotes (0x22)
    - Not needed for daily VBA work

  Reusability: LOW (specialized)
    - Use to verify quote fixes at byte level
    - Debugging invisible Unicode characters
    - Proof that encoding is correct

  See: README_ARCHIVE.md for full documentation
  Validation Report: ../../VALIDATION_COMPLETE.md
"""

import sys
from pathlib import Path


def check_quotes_hex(filepath: str) -> bool:
    """Check for different types of quotes by hex value"""
    try:
        with open(filepath, "rb") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read {filepath}: {e}")
        return False

    # Search for different quote byte sequences (UTF-8 encoded)
    quotes_found = {
        b"\xe2\x80\x9c": 'Left double quote (" | U+201C | UTF-8: e2 80 9c)',
        b"\xe2\x80\x9d": 'Right double quote (" | U+201D | UTF-8: e2 80 9d)',
        b"\xe2\x80\x98": "Left single quote (' | U+2018 | UTF-8: e2 80 98)",
        b"\xe2\x80\x99": "Right single quote (' | U+2019 | UTF-8: e2 80 99)",
        b"\x22": 'Straight quote (" | U+0022 | UTF-8: 22)',
        b"\xb7": "Middle dot (· | U+00B7 | UTF-8: b7)",
        b"\xd7": "Multiplication sign (× | U+00D7 | UTF-8: d7)",
        b"\xe2\x86\x92": "Arrow (→ | U+2192 | UTF-8: e2 86 92)",
    }

    found = {}
    for byte_seq, description in quotes_found.items():
        count = content.count(byte_seq)
        if count > 0:
            found[description] = count

    if found:
        print(f"  {Path(filepath).name}:")
        for desc, count in found.items():
            print(f"    - {desc}: {count}")
        return True
    else:
        print(f"  {Path(filepath).name}: No special quotes found")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("VBA Quote Hex Detector")
        print("=" * 70)
        print("\nUsage:")
        print("  python check_quotes_hex.py <file.bas>    - Check single file")
        print("  python check_quotes_hex.py <directory>   - Check all .bas files")
        print("\nExample:")
        print("  python check_quotes_hex.py VBA/ETABS_Export/mod_Main.bas")
        print("  python check_quotes_hex.py VBA/ETABS_Export/")
        return 1

    target = sys.argv[1]
    path = Path(target)

    print("\n🔎 VBA Quote Hex Detector")
    print("=" * 70)

    if path.is_file() and path.suffix == ".bas":
        # Single file
        check_quotes_hex(target)
        return 0

    elif path.is_dir():
        # Directory
        bas_files = sorted(path.glob("*.bas"))

        if not bas_files:
            print(f"❌ No .bas files found in {path}")
            return 1

        print(f"\n📂 Analyzing {len(bas_files)} VBA files")
        print("-" * 70)

        for bas_file in bas_files:
            check_quotes_hex(str(bas_file))

        print("\n" + "=" * 70)
        return 0

    else:
        print(f"❌ File not found or not a .bas file: {target}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
