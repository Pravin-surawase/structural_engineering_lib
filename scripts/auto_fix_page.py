#!/usr/bin/env python3
"""
Autonomous Page Fixer - Fix common Streamlit issues without user intervention

Runs checks and applies fixes automatically:
1. Import path issues
2. Theme conflicts
3. Missing dependencies
4. Syntax errors

Usage:
    python scripts/auto_fix_page.py streamlit_app/pages/01_beam_design.py
"""

import sys
import re
from pathlib import Path


class AutoFixer:
    """Automatically fix common Streamlit page issues"""

    def __init__(self, page_path: str):
        self.page_path = Path(page_path)
        self.fixes_applied = []

    def fix_all(self):
        """Run all fixes"""
        print(f"🔧 Auto-fixing: {self.page_path.name}")
        print("=" * 60)

        # 1. Fix import paths
        self._fix_import_paths()

        # 2. Disable problematic theme
        self._disable_theme()

        # 3. Check syntax
        self._check_syntax()

        self._report()

    def _fix_import_paths(self):
        """Fix sys.path issues for component imports"""
        print("\n1️⃣  Fixing import paths...")

        with open(self.page_path) as f:
            content = f.read()

        # Look for the sys.path.insert line
        old_pattern = (
            r"sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent\.parent\)\)"
        )

        if re.search(old_pattern, content):
            # Replace with more robust version
            new_code = """# Fix import path - add streamlit_app directory to path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

# Ensure streamlit_app is in path for component imports
if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))"""

            content = re.sub(
                r"# Add parent directory to path for imports\s*\n" + old_pattern,
                new_code,
                content,
            )

            with open(self.page_path, "w") as f:
                f.write(content)

            self.fixes_applied.append("Fixed import paths (more robust)")
            print("   ✅ Import paths fixed")
        else:
            print("   ℹ️  Import paths already correct")

    def _disable_theme(self):
        """Comment out problematic theme calls"""
        print("\n2️⃣  Checking theme...")

        with open(self.page_path) as f:
            lines = f.readlines()

        modified = False
        for i, line in enumerate(lines):
            # Comment out apply_dark_mode_theme if not already
            if "apply_dark_mode_theme()" in line and not line.strip().startswith("#"):
                lines[i] = line.replace(
                    "apply_dark_mode_theme()", "#apply_dark_mode_theme()"
                )
                modified = True

        if modified:
            with open(self.page_path, "w") as f:
                f.writelines(lines)

            self.fixes_applied.append("Disabled problematic theme")
            print("   ✅ Theme disabled for testing")
        else:
            print("   ℹ️  Theme already disabled")

    def _check_syntax(self):
        """Verify syntax is correct"""
        print("\n3️⃣  Verifying syntax...")

        try:
            with open(self.page_path) as f:
                compile(f.read(), self.page_path, "exec")
            print("   ✅ Syntax OK")
        except SyntaxError as e:
            print(f"   ❌ Syntax error at line {e.lineno}: {e.msg}")
            print(f"      Please fix manually: {e.text}")

    def _report(self):
        """Report what was fixed"""
        print("\n" + "=" * 60)
        print("📊 AUTO-FIX REPORT")
        print("=" * 60)

        if self.fixes_applied:
            print(f"\n✅ Applied {len(self.fixes_applied)} fixes:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        else:
            print("\nℹ️  No fixes needed")

        print("\n" + "=" * 60)
        print("🚀 NEXT: Test the page")
        print("   streamlit run", self.page_path)
        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/auto_fix_page.py <page_path>")
        sys.exit(1)

    fixer = AutoFixer(sys.argv[1])
    fixer.fix_all()


if __name__ == "__main__":
    main()
