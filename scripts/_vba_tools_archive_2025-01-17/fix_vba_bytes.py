#!/usr/bin/env python3
"""
VBA Byte Fixer - Fix encoding issues in VBA files
Replaces problematic UTF-8 bytes with valid ASCII equivalents

ARCHIVE METADATA:
  Archive Date: 2025-01-17
  Project: ETABS Export VBA Validation
  Status: COMPLETED WORK - All files fixed
  Location: scripts/_vba_tools_archive_2025-01-17/
  
  Why Archived:
    - Task completed: Fixed 10 corrupted bytes in 2 VBA files
    - mod_Types.bas position 634: 1 byte (0xb7 middle-dot → period)
    - mod_Validation.bas position 2602: 9 bytes (0xd7 multiplication → asterisk)
    - All ETABS modules now have clean encoding
    
  Reusability: MEDIUM
    - Use for byte-level encoding corruption
    - Rare issue but impossible to fix manually
    - Fixes: 0xb7, 0xd7, 0xf7 Latin-1 bytes
    
  See: README_ARCHIVE.md for full documentation
  Validation Report: ../../VALIDATION_COMPLETE.md
"""

import sys
from pathlib import Path


def fix_vba_bytes(filepath: str) -> bool:
    """Fix problematic bytes in a VBA file"""
    try:
        with open(filepath, 'rb') as f:
            content = bytearray(f.read())
    except Exception as e:
        print(f"❌ Could not read {filepath}: {e}")
        return False
    
    original_len = len(content)
    
    # Define problematic byte sequences and their replacements
    replacements = [
        # Middle-dot (·) and other Unicode bullets represented as single bytes
        # These appear when UTF-8 encoding is broken
        (b'\xb7', b'.'),       # Middle dot → period
        (b'\xd7', b'*'),       # Multiplication sign → asterisk
        (b'\xb5', b'u'),       # Micro sign → u (for micrometers)
        (b'\xf1', b'n'),       # N with tilde → n
        (b'\xf3', b'o'),       # O with acute → o
        (b'\xf9', b'u'),       # U with grave → u
    ]
    
    changes = 0
    for bad_byte, good_byte in replacements:
        while bad_byte in content:
            idx = content.find(bad_byte)
            if idx >= 0:
                content[idx:idx+len(bad_byte)] = good_byte
                changes += 1
    
    if changes == 0:
        print(f"  ✅ {Path(filepath).name} - No problematic bytes found")
        return True
    
    # Write back
    try:
        with open(filepath, 'wb') as f:
            f.write(content)
        
        print(f"  ✅ {Path(filepath).name} - Fixed {changes} problematic byte(s)")
        return True
    
    except Exception as e:
        print(f"  ❌ {Path(filepath).name} - Could not write: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("VBA Byte Fixer")
        print("=" * 60)
        print("\nUsage:")
        print("  python fix_vba_bytes.py <file.bas>        - Fix single file")
        print("  python fix_vba_bytes.py <directory>       - Fix all .bas files")
        print("\nExample:")
        print("  python fix_vba_bytes.py VBA/ETABS_Export/mod_Types.bas")
        print("  python fix_vba_bytes.py VBA/ETABS_Export/")
        return 1
    
    target = sys.argv[1]
    path = Path(target)
    
    print("\n🔧 VBA Byte Fixer")
    print("=" * 60)
    
    if path.is_file() and path.suffix == '.bas':
        # Single file
        success = fix_vba_bytes(target)
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
            if not fix_vba_bytes(str(bas_file)):
                all_success = False
        
        print("\n" + "=" * 60)
        if all_success:
            print("✅ All files processed successfully!")
            return 0
        else:
            print("❌ Some files had errors")
            return 1
    
    else:
        print(f"❌ File not found or not a .bas file: {target}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
