#!/usr/bin/env python3
"""
Unified session management CLI.

Consolidates: start_session.py, end_session.py, update_handoff.py, check_session_docs.py

USAGE:
    python scripts/session.py start [--quick] [--no-add]
    python scripts/session.py end [--fix] [--quick]
    python scripts/session.py handoff
    python scripts/session.py check
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
SESSION_LOG = REPO_ROOT / "docs" / "SESSION_LOG.md"
TASKS_MD = REPO_ROOT / "docs" / "TASKS.md"
PYPROJECT = REPO_ROOT / "Python" / "pyproject.toml"
NEXT_BRIEF = REPO_ROOT / "docs" / "planning" / "next-session-brief.md"

DATE_RE = re.compile(r"##\s+(\d{4}-\d{2}-\d{2})\s+—\s+Session")
HANDOFF_START = "<!-- HANDOFF:START -->"
HANDOFF_END = "<!-- HANDOFF:END -->"
HANDOFF_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
COMMIT_HASH_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{7,40})(?![0-9a-fA-F])")


def _python_exe() -> str:
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.exists() else sys.executable


def _run_script(script_name: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    script = REPO_ROOT / "scripts" / script_name
    if not script.exists():
        return subprocess.CompletedProcess([], 1, "", f"Script not found: {script_name}")
    cmd = [_python_exe(), str(script), *args]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout)


# ─── Start Session ───────────────────────────────────────────────────────────


def get_version() -> str:
    try:
        content = PYPROJECT.read_text()
        match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
        return match.group(1) if match else "unknown"
    except Exception:
        return "unknown"


def get_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], cwd=REPO_ROOT,
            capture_output=True, text=True,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def get_uncommitted_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT,
            capture_output=True, text=True,
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return "Clean working tree" if not lines else f"{len(lines)} uncommitted change(s)"
    except Exception:
        return "Unable to check"


def check_session_log_entry() -> tuple[bool, str]:
    today_str = date.today().strftime("%Y-%m-%d")
    try:
        content = SESSION_LOG.read_text()
        if re.search(rf"^##\s+{re.escape(today_str)}\b", content, re.MULTILINE):
            return True, f"Entry exists for {today_str}"
        return False, f"No entry for {today_str}"
    except Exception as e:
        return False, f"Error reading SESSION_LOG: {e}"


def add_session_log_entry() -> bool:
    today_str = date.today().strftime("%Y-%m-%d")
    skeleton_lines = [
        "",
        f"## {today_str} — Session",
        "",
        "### Summary",
        "-",
        "",
        "### PRs Merged",
        "| PR | Summary |",
        "|----|---------|",
        "| #XX | - |",
        "",
        "### Key Deliverables",
        "-",
        "",
        "### Notes",
        "-",
        "",
    ]
    try:
        content = SESSION_LOG.read_text()
        lines = content.split("\n")
        insert_index = None
        for i, line in enumerate(lines):
            if line.strip() == "---" and i > 2:
                insert_index = i + 1
                break
        if insert_index is None:
            insert_index = 5
        new_lines = lines[:insert_index] + skeleton_lines + lines[insert_index:]
        SESSION_LOG.write_text("\n".join(new_lines))
        return True
    except Exception as e:
        print(f"  Error adding entry: {e}")
        return False


def get_active_tasks() -> list[tuple[str, str, str]]:
    try:
        content = TASKS_MD.read_text()
        active_match = re.search(r"## 🔴 Active\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if not active_match:
            return [("", "No Active section found", "")]
        active_section = active_match.group(1)
        tasks = []
        for line in active_section.split("\n"):
            match = re.match(
                r"\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)", line
            )
            if match:
                task_id = match.group(1).strip()
                task_desc = match.group(2).strip()
                status = match.group(4).strip()
                hint = ""
                status_lower = status.lower()
                if any(kw in status_lower for kw in ("human", "waiting", "manual")):
                    hint = "BLOCKER - requires human"
                elif "⏳" in status:
                    hint = "waiting"
                tasks.append((task_id, task_desc, hint))
        return tasks if tasks else [("", "No active tasks in table", "")]
    except Exception as e:
        return [("", f"Error reading TASKS.md: {e}", "")]


def get_key_blocker() -> Optional[str]:
    for task_id, desc, hint in get_active_tasks():
        if "BLOCKER" in hint:
            return f"{task_id}: {desc}"
    return None


def run_handoff_check(skip_tests: bool = True) -> tuple[bool, str]:
    try:
        args = ["--skip-tests"] if skip_tests else []
        result = _run_script("check_handoff_ready.py", *args, timeout=240)
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        if "All checks passed" in output:
            return True, "All handoff checks passed"
        issues = [line.strip() for line in output.split("\n") if "❌" in line or "⚠️" in line]
        return False, "\n".join(issues) if issues else "Some checks failed"
    except Exception as e:
        return False, f"Error running handoff check: {e}"


def cmd_start(args: argparse.Namespace) -> int:
    version = get_version()
    branch = get_branch()
    uncommitted = get_uncommitted_status()

    print()
    print("=" * 60)
    print("🚀 SESSION START")
    print("=" * 60)
    print()
    print(f"  Version:  v{version}")
    print(f"  Branch:   {branch}")
    print(f"  Date:     {date.today().strftime('%Y-%m-%d')}")
    print(f"  Git:      {uncommitted}")
    print()

    # Check/add SESSION_LOG entry
    print("📝 Session Log:")
    has_entry, entry_msg = check_session_log_entry()
    if has_entry:
        print(f"  ✅ {entry_msg}")
    else:
        print(f"  ⚠️  {entry_msg}")
        if not args.no_add:
            print("  📝 Adding skeleton entry...")
            if add_session_log_entry():
                print("  ✅ Entry added to SESSION_LOG.md")
            else:
                print("  ❌ Failed to add entry")
    print()

    # Active tasks
    print("📋 Active Tasks:")
    tasks = get_active_tasks()
    for task_id, desc, hint in tasks:
        if task_id:
            suffix = f" ({hint})" if hint else ""
            print(f"  • {task_id}: {desc}{suffix}")
        else:
            print(f"  • {desc}")

    blocker = get_key_blocker()
    if blocker:
        print()
        print(f"  ⚠️  Key Blocker: {blocker}")
    print()

    # Handoff checks
    print("🔍 Doc Freshness:")
    passed, check_msg = run_handoff_check(skip_tests=args.quick)
    if passed:
        print(f"  ✅ {check_msg}")
    else:
        for line in check_msg.split("\n"):
            print(f"  {line}")
    print()

    print("=" * 60)
    if blocker:
        print(f"⚠️  Blocker detected: {blocker}")
        print("   → Ask user to resolve, or pick from Up Next in TASKS.md")
    else:
        print("Ready to work! Pick a task from Active or Up Next.")
    print()
    print("🧭 Automation lookup: .venv/bin/python scripts/find_automation.py \"your task\"")
    print("📚 Context routing: scripts/automation-map.json (context_docs per task)")
    print("📖 Read first: docs/handoff.md → docs/agent-bootstrap.md → docs/ai-context-pack.md")
    print("=" * 60)
    print()
    return 0


# ─── End Session ─────────────────────────────────────────────────────────────


def get_uncommitted_changes() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT,
            capture_output=True, text=True,
        )
        if not result.stdout.strip():
            return []
        return [line.strip() for line in result.stdout.strip().split("\n")]
    except Exception:
        return []


def check_session_log_complete() -> tuple[bool, list[str]]:
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    today_display = today.strftime("%B %d, %Y")
    issues: list[str] = []

    try:
        content = SESSION_LOG.read_text()
        if today_str not in content and today_display not in content:
            issues.append("No entry for today")
            return False, issues

        lines = content.split("\n")
        in_today = False
        has_focus = False
        has_completed = False

        for line in lines:
            if today_str in line or today_display in line:
                in_today = True
            elif in_today and line.startswith("## Session:"):
                break
            elif in_today:
                if "**Focus:**" in line and "<!--" not in line:
                    if len(line.split("**Focus:**")[1].strip()) > 5:
                        has_focus = True
                if "**Completed:**" in line:
                    has_completed = True
                if has_completed and line.strip().startswith("-") and len(line.strip()) > 2:
                    if "<!--" not in line:
                        has_completed = True

        if not has_focus:
            issues.append("SESSION_LOG: Focus not filled in")
        if not has_completed:
            issues.append("SESSION_LOG: No completed items listed")

        return len(issues) == 0, issues
    except Exception as e:
        return False, [f"Error reading SESSION_LOG: {e}"]


def check_doc_links() -> tuple[bool, str]:
    try:
        result = _run_script("check_links.py", timeout=60)
        if result.returncode == 0:
            return True, "All doc links valid"
        broken = [line.strip() for line in result.stdout.split("\n") if "BROKEN" in line or "❌" in line]
        return False, f"{len(broken)} broken link(s) found"
    except Exception as e:
        return True, f"Link check skipped: {e}"


def get_changed_doc_folders() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        changed_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        result2 = subprocess.run(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True,
        )
        for line in result2.stdout.strip().split("\n"):
            if line.strip():
                parts = line.strip().split(maxsplit=1)
                if len(parts) > 1:
                    changed_files.append(parts[1])
        doc_folders = set()
        for f in changed_files:
            if f.startswith("docs/") and f.endswith(".md"):
                folder = Path(f).parent
                if len(folder.parts) >= 2:
                    doc_folders.add(REPO_ROOT / folder)
        return list(doc_folders)
    except Exception:
        return []


def update_folder_readmes(folders: list[Path], fix: bool = False) -> int:
    if not fix:
        return 0
    gen_script = REPO_ROOT / "scripts" / "generate_folder_index.py"
    if not gen_script.exists():
        return 0
    updated = 0
    for folder in folders:
        if not folder.exists():
            continue
        try:
            md_files = list(folder.glob("*.md"))
            if len(md_files) < 3:
                continue
            result = subprocess.run(
                [_python_exe(), str(gen_script), str(folder)],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                updated += 1
        except Exception:
            pass
    return updated


def get_today_prs() -> list[str]:
    try:
        today_str = date.today().strftime("%Y-%m-%d")
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={today_str}", "--merges", "-n", "10"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        if not result.stdout.strip():
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={today_str}", "-n", "10"],
                cwd=REPO_ROOT, capture_output=True, text=True,
            )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return [line for line in lines if line][:5]
    except Exception:
        return []


def cmd_end(args: argparse.Namespace) -> int:
    print()
    print("=" * 60)
    print("🏁 SESSION END CHECK")
    print("=" * 60)
    print()

    all_passed = True

    # 1. Uncommitted changes
    print("📁 Uncommitted Changes:")
    uncommitted = get_uncommitted_changes()
    if uncommitted:
        print(f"  ⚠️  {len(uncommitted)} uncommitted file(s):")
        for f in uncommitted[:5]:
            print(f"     {f}")
        if len(uncommitted) > 5:
            print(f"     ... and {len(uncommitted) - 5} more")
        all_passed = False
    else:
        print("  ✅ Working tree clean")
    print()

    # 2. Handoff brief update (if --fix)
    if args.fix:
        print("🧭 Handoff Brief:")
        ok, msg = _do_handoff()
        if ok:
            print(f"  ✅ {msg}")
        else:
            print(f"  ⚠️  {msg}")
            all_passed = False
        print()

    # 3. Handoff checks
    print("🔍 Handoff Checks:")
    passed, msg = run_handoff_check(skip_tests=args.quick)
    if "All checks passed" in msg or "passed" in msg.lower():
        print(f"  ✅ {msg}")
    else:
        print("  ⚠️  Issues found:")
        for line in msg.split("\n"):
            if line.strip():
                print(f"     {line}")
        all_passed = False
    print()

    # 4. Session log completeness
    print("📝 Session Log:")
    complete, issues = check_session_log_complete()
    if complete:
        print("  ✅ Today's entry looks complete")
    else:
        for issue in issues:
            print(f"  ⚠️  {issue}")
        all_passed = False
    print()

    # 5. Link check
    print("🔗 Doc Links:")
    passed, msg = check_doc_links()
    if passed:
        print(f"  ✅ {msg}")
    else:
        print(f"  ⚠️  {msg}")
    print()

    # 6. README updates
    print("📚 README Index Updates:")
    changed_folders = get_changed_doc_folders()
    if changed_folders:
        print(f"  📂 {len(changed_folders)} folder(s) with changes detected")
        updated = update_folder_readmes(changed_folders, fix=args.fix)
        if args.fix and updated:
            print(f"  ✅ Updated {updated} README file(s)")
        elif not args.fix:
            print("  ℹ️  Run with --fix to auto-update READMEs")
    else:
        print("  ✅ No doc folder changes detected")
    print()

    # 7. Governance compliance
    print("📋 Governance Compliance:")
    gov_script = REPO_ROOT / "scripts" / "check_governance.py"
    if gov_script.exists():
        try:
            result = subprocess.run(
                [_python_exe(), str(gov_script)],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                print("  ✅ All governance checks passed")
            else:
                critical = result.stdout.count("CRITICAL")
                high = result.stdout.count("HIGH")
                if critical > 0:
                    print(f"  🔴 {critical} CRITICAL issue(s) found")
                    all_passed = False
                if high > 0:
                    print(f"  🟠 {high} HIGH severity issue(s)")
                if critical == 0 and high == 0:
                    print("  ✅ Only minor issues (MEDIUM/LOW)")
        except Exception as e:
            print(f"  ⚠️  Could not run governance check: {e}")
    else:
        print("  ⏭️  Governance checker not found (skipping)")
    print()

    # 8. Today's activity
    print("📊 Today's Activity:")
    prs = get_today_prs()
    if prs:
        for pr in prs:
            print(f"  • {pr}")
    else:
        print("  (No commits today)")
    print()

    print("=" * 60)
    if all_passed:
        print("✅ All checks passed! Safe to end session.")
    else:
        print("⚠️  Some issues found. Consider fixing before handoff.")
        if not args.fix:
            print("   Run with --fix to auto-fix what's possible.")
        print()
        print("💡 Tip: Collect diagnostics for troubleshooting:")
        print("   .venv/bin/python scripts/collect_diagnostics.py > diagnostics.txt")
    print("=" * 60)
    print()

    return 0 if all_passed else 1


# ─── Handoff ─────────────────────────────────────────────────────────────────


def _latest_session_block(lines: list[str]) -> tuple[str, list[str]]:
    start_idx = -1
    date_str = ""
    for idx, line in enumerate(lines):
        match = DATE_RE.match(line.strip())
        if match:
            start_idx = idx
            date_str = match.group(1)
            break
    if start_idx == -1:
        raise ValueError("No session header found in SESSION_LOG.md")
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            end_idx = idx
            break
    return date_str, lines[start_idx:end_idx]


def _parse_focus(block: list[str]) -> str:
    for line in block:
        if line.startswith("**Focus:**"):
            return line.split("**Focus:**", 1)[1].strip()
    return ""


def _parse_completed(block: list[str]) -> list[str]:
    completed: list[str] = []
    in_completed = False
    for line in block:
        if line.startswith("**Completed:**"):
            in_completed = True
            continue
        if in_completed:
            if line.startswith("### ") or line.startswith("## "):
                break
            if line.strip().startswith("-"):
                item = line.strip().lstrip("-").strip()
                if item:
                    completed.append(item)
            elif line.strip() == "" and completed:
                break
    return completed


def _parse_prs(block: list[str]) -> list[str]:
    prs: list[str] = []
    for line in block:
        match = re.search(r"\|\s*#(\d+)", line)
        if match:
            prs.append(f"#{match.group(1)}")
    return prs


def _build_handoff_lines(date_str: str, block: list[str]) -> list[str]:
    focus = _parse_focus(block)
    completed = _parse_completed(block)[:3]
    prs = _parse_prs(block)[:6]
    lines = [f"- Date: {date_str}"]
    if focus:
        lines.append(f"- Focus: {focus}")
    if completed:
        lines.append(f"- Completed: {'; '.join(completed)}")
    if prs:
        lines.append(f"- PRs: {', '.join(prs)}")
    return lines


def _update_next_brief(handoff_lines: list[str]) -> None:
    text = NEXT_BRIEF.read_text(encoding="utf-8")
    block = "\n".join([
        "## Latest Handoff (auto)",
        "",
        HANDOFF_START,
        *handoff_lines,
        HANDOFF_END,
        "",
    ])
    if HANDOFF_START in text and HANDOFF_END in text:
        pattern = re.compile(
            r"## Latest Handoff \(auto\)\n\n"
            + re.escape(HANDOFF_START) + r"[\s\S]*?" + re.escape(HANDOFF_END)
        )
        new_text = pattern.sub(block.rstrip(), text)
    else:
        lines = text.splitlines()
        insert_idx = None
        for idx, line in enumerate(lines):
            if line.strip() == "---":
                insert_idx = idx + 1
                break
        if insert_idx is None:
            insert_idx = 2
        new_lines = lines[:insert_idx] + ["", block, ""] + lines[insert_idx:]
        new_text = "\n".join(new_lines)
    NEXT_BRIEF.write_text(new_text.strip() + "\n", encoding="utf-8")


def _do_handoff() -> tuple[bool, str]:
    if not SESSION_LOG.exists():
        return False, "docs/SESSION_LOG.md not found"
    if not NEXT_BRIEF.exists():
        return False, "docs/planning/next-session-brief.md not found"
    try:
        lines = SESSION_LOG.read_text(encoding="utf-8").splitlines()
        date_str, block = _latest_session_block(lines)
        handoff_lines = _build_handoff_lines(date_str, block)
        if not handoff_lines:
            return False, "Could not build handoff lines from SESSION_LOG.md"
        _update_next_brief(handoff_lines)
        return True, "Updated next-session-brief.md handoff block"
    except Exception as e:
        return False, f"Handoff update failed: {e}"


def cmd_handoff(args: argparse.Namespace) -> int:
    ok, msg = _do_handoff()
    print(msg)
    return 0 if ok else 1


# ─── Check Session Docs ─────────────────────────────────────────────────────


def _find_heading(lines: list[str], heading: str) -> int:
    for idx, line in enumerate(lines):
        if line.strip() == heading:
            return idx
    return -1


def _section_lines(lines: list[str], start_idx: int) -> list[str]:
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            end_idx = idx
            break
    return lines[start_idx + 1 : end_idx]


def _handoff_date(lines: list[str]) -> str | None:
    start_idx = -1
    end_idx = -1
    for idx, line in enumerate(lines):
        if HANDOFF_START in line:
            start_idx = idx
        if HANDOFF_END in line and start_idx != -1:
            end_idx = idx
            break
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return None
    for line in lines[start_idx:end_idx]:
        if line.strip().startswith("- Date:"):
            match = HANDOFF_DATE_RE.search(line)
            if match:
                return match.group(1)
    return None


def _validate_commit_hashes(lines: list[str], filename: str) -> list[str]:
    errors: list[str] = []
    skip_patterns = [
        re.compile(r"^\d{4}-\d{2}-\d{2}"),
        re.compile(r"^\d+\.\d+\.\d+"),
        re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}"),
    ]
    for line_num, line in enumerate(lines, 1):
        if not any(kw in line.lower() for kw in ["commit", "hash", "sha", "merged", "squash"]):
            continue
        for match in COMMIT_HASH_RE.finditer(line):
            candidate = match.group(1)
            if any(p.match(candidate) for p in skip_patterns):
                continue
            if len(set(candidate)) == 1:
                errors.append(f"{filename}:{line_num}: Suspicious hash '{candidate}' (all same character)")
            # Skip pure digit candidates (likely numbers, not hashes)
    return errors


def cmd_check(args: argparse.Namespace) -> int:
    next_path = NEXT_BRIEF
    session_path = SESSION_LOG

    if not next_path.exists():
        print("ERROR: docs/planning/next-session-brief.md not found")
        return 1
    if not session_path.exists():
        print("ERROR: docs/SESSION_LOG.md not found")
        return 1

    next_lines = next_path.read_text(encoding="utf-8").splitlines()
    session_lines = session_path.read_text(encoding="utf-8").splitlines()

    if _find_heading(next_lines, "# Next Session Briefing") == -1:
        print("ERROR: next-session-brief.md missing '# Next Session Briefing'")
        return 1

    if not any("Required Reading" in line for line in next_lines):
        print("ERROR: next-session-brief.md missing 'Required Reading' section")
        return 1

    if not any("| **Current** |" in line for line in next_lines):
        print("ERROR: next-session-brief.md missing Current release row")
        return 1
    if not any("| **Next** |" in line for line in next_lines):
        print("ERROR: next-session-brief.md missing Next release row")
        return 1

    date_re = re.compile(r"Date:\*?\*?\s*(\d{4}-\d{2}-\d{2})")
    date_match = None
    for line in next_lines:
        m = date_re.search(line)
        if m:
            date_match = m
            break

    if not date_match:
        print("ERROR: next-session-brief.md missing Date field")
        return 1

    date_str = date_match.group(1)
    handoff_date = _handoff_date(next_lines)
    if not handoff_date:
        print("ERROR: next-session-brief.md missing Latest Handoff block")
        print("Run: python scripts/session.py handoff")
        return 1
    if handoff_date != date_str:
        print("ERROR: Latest Handoff date does not match next-session-brief Date field")
        print(f"Expected {date_str}, found {handoff_date}")
        return 1

    session_heading = f"## {date_str}"
    first_session_line = None
    session_idx = -1
    for idx, line in enumerate(session_lines):
        if line.startswith("## ") and first_session_line is None:
            first_session_line = line
        if line.startswith(session_heading) and "Session" in line:
            session_idx = idx
            break

    if session_idx == -1:
        print(f"ERROR: SESSION_LOG.md missing session entry for {date_str}")
        return 1

    if first_session_line is not None and not first_session_line.startswith(session_heading):
        print("ERROR: SESSION_LOG.md newest session must be at the top (append-only).")
        print(f"Expected first session header to start with {session_heading}.")
        return 1

    window = session_lines[session_idx : session_idx + 25]
    if not any("Focus:" in line for line in window):
        print(f"ERROR: SESSION_LOG.md entry for {date_str} missing 'Focus:' line")
        return 1

    hash_errors = _validate_commit_hashes(session_lines, "SESSION_LOG.md")
    hash_errors.extend(_validate_commit_hashes(next_lines, "next-session-brief.md"))
    if hash_errors:
        for err in hash_errors:
            print(f"WARNING: {err}")

    return 0


# ─── CLI ─────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="session.py",
        description="Unified session management (start, end, handoff, check)",
    )
    sub = parser.add_subparsers(dest="command", help="Session command")

    # start
    p_start = sub.add_parser("start", help="Start a coding session")
    p_start.add_argument("--quick", action="store_true", help="Skip test count verification")
    p_start.add_argument("--no-add", action="store_true", help="Don't add SESSION_LOG entry")

    # end
    p_end = sub.add_parser("end", help="End-of-session checks")
    p_end.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    p_end.add_argument("--quick", action="store_true", help="Skip test count verification")

    # handoff
    sub.add_parser("handoff", help="Update next-session-brief.md from SESSION_LOG")

    # check
    sub.add_parser("check", help="Validate session docs consistency")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    handlers = {
        "start": cmd_start,
        "end": cmd_end,
        "handoff": cmd_handoff,
        "check": cmd_check,
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
