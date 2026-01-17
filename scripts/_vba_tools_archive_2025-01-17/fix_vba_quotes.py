#!/usr/bin/env python3
"""
VBA Quote Fixer - Convert curly/smart quotes to straight quotes
Handles the most common encoding issues in VBA files

ARCHIVE METADATA:
  Archive Date: 2025-01-17
  Project: ETABS Export VBA Validation
  Status: COMPLETED WORK - All files fixed
  Location: scripts/_vba_tools_archive_2025-01-17/
  
  Why Archived:
    - Task completed: Fixed 468+ Unicode quote issues across 10 VBA files
    - mod_Setup_Installer.bas: 265 replacements
    - Test_ETABS_Export.bas: 203 replacements
    - All ETABS modules now have correct ASCII quotes (0x22)
    
  Reusability: HIGH
    - Use for any VBA project with Unicode quote issues
    - Common when copy-pasting from web/Word/PDF
    - Fixes: curly quotes → straight quotes, emoji → ASCII
    
  See: README_ARCHIVE.md for full documentation
  Validation Report: ../../VALIDATION_COMPLETE.md
"""

import sys
from pathlib import Path


def fix_vba_quotes(filepath: str) -> bool:
    """Fix curly quotes in a VBA file"""
    try:
        # Read with error handling
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read {filepath}: {e}")
        return False
    
    original_content = content
    
    # Map of problematic characters to replacements
    # Focus on the characters the validator is actually detecting
    replacements = {
        '\u201C': '"',  # Left double quote (") → straight quote
        '\u201D': '"',  # Right double quote (") → straight quote
        '\u2018': "'",  # Left single quote (') → straight quote
        '\u2019': "'",  # Right single quote (') → straight quote
        '–': '-',       # En dash → hyphen
        '—': '-',       # Em dash → hyphen
        '·': '.',       # Middle dot → period
        '′': "'",       # Prime → single quote
        '→': '->',      # Arrow → dash-gt
        '✓': '[OK]',    # Checkmark → [OK]
        '✗': '[FAIL]',  # X mark → [FAIL]
    }
    
    for bad_char, good_char in replacements.items():
        if bad_char in content:
            content = content.replace(bad_char, good_char)
    
    # Check if changes were made
    if content == original_content:
        print(f"  ✅ {Path(filepath).name} - No changes needed")
        return True
    
    # Write back
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Count changes
        changes = sum(original_content.count(bad) for bad in replacements.keys())
        print(f"  ✅ {Path(filepath).name} - Fixed {changes} quote(s)")
        return True
    
    except Exception as e:
        print(f"  ❌ {Path(filepath).name} - Could not write: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("VBA Quote Fixer")
        print("=" * 60)
        print("\nUsage:")
        print("  python fix_vba_quotes.py <file.bas>        - Fix single file")
        print("  python fix_vba_quotes.py <directory>       - Fix all .bas files")
        print("\nExample:")
        print("  python fix_vba_quotes.py VBA/ETABS_Export/mod_Main.bas")
        print("  python fix_vba_quotes.py VBA/ETABS_Export/")
        return 1
    
    target = sys.argv[1]
    path = Path(target)
    
    print("\n🔧 VBA Quote Fixer")
    print("=" * 60)
    
    if path.is_file() and path.suffix == '.bas':
        # Single file
        success = fix_vba_quotes(target)
        return 0 if success else 1
    
    elif path.is_dir():
        # Directory
        bas_files = sorted(path.glob('*.bas'))
        
        if not bas_files:
            print(f"❌ No .bas files found in {path}")
            return 1
        
        print(f"\n📂 Found {len(bas_files)} VBA files")
        print("-" * 60)
        
        all_success = True
        for bas_file in bas_files:
            if not fix_vba_quotes(str(bas_file)):
                all_success = False
        
        print("\n" + "=" * 60)
        if all_success:
            print("✅ All files fixed successfully!")
            return 0
        else:
            print("❌ Some files had errors")
            return 1
    
    else:
        print(f"❌ File not found or not a .bas file: {target}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
