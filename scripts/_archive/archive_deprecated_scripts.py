#!/usr/bin/env python3
"""Archive deprecated/superseded/one-off scripts to scripts/_archive/.

This is Phase 1 of the scripts consolidation plan.
See docs/_active/scripts-consolidation-plan.md for full details.
"""
from __future__ import annotations

import shutil
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = SCRIPTS_DIR / "_archive"

# Scripts to archive — all verified as deprecated, superseded, or one-off
TO_ARCHIVE = [
    # Deprecated/superseded
    "quick_push.sh",              # Already deprecated, prints error
    "install_enforcement_hook.sh", # Self-labeled DEPRECATED
    "install_hooks.sh",           # Superseded by install_git_hooks.sh
    "migrate_module.py",          # Superseded by migrate_python_module.py
    "generate_folder_index.py",   # Superseded by generate_enhanced_index.py
    "cleanup_stale_branches.sh",  # Duplicate of .py version
    "pre-push-hook.sh",          # Superseded by scripts/git-hooks/

    # Migration one-offs (Phase 1/2 complete)
    "create_reexport_stub.py",
    "fix_services_relative_imports.py",
    "pre_migration_check.py",
    "update_is456_init.py",
    "update_redirect_refs.py",
    "validate_migration.py",

    # Research/analysis one-offs
    "analyze_doc_redundancy.py",
    "analyze_navigation_data.py",
    "analyze_release_cadence.py",
    "predict_velocity.py",
    "measure_agent_navigation.sh",

    # Agent-specific tooling (agent-8/agent-9)
    "git_ops.sh",
    "git_automation_health.sh",
    "ci_monitor_daemon.sh",
    "worktree_manager.sh",
    "pr_async_merge.sh",
    "governance_session.sh",
    "weekly_governance_check.sh",
    "generate_dashboard.sh",
    "test_agent_automation.sh",
    "test_branch_operations.sh",
    "test_git_workflow.sh",
    "test_merge_conflicts.sh",
    "test_should_use_pr.sh",
    "verify_git_fix.sh",

    # Streamlit-era one-offs
    "auto_fix_page.py",
    "autonomous_fixer.py",
    "pylint_streamlit.sh",
    "streamlit_preflight.sh",
    "test_page.sh",

    # Doc one-offs
    "consolidate_docs.py",
    "enhance_readme.py",
    "find_orphan_files.py",
    "archive_deprecated_docs.py",
    "archive_old_sessions.sh",
    "batch_archive.py",

    # Code one-offs
    "add_license_headers.py",
    "add_future_annotations.py",
    "rename_folder_safe.py",
    "risk_cache.sh",
    "quick_check.sh",
    "lint_docs_git_examples.sh",
    "check_redirect_stubs.py",
    "validate_trial_data.py",
]


def main() -> None:
    """Archive scripts."""
    ARCHIVE_DIR.mkdir(exist_ok=True)

    moved = 0
    skipped = 0
    not_found = 0

    for script_name in TO_ARCHIVE:
        src = SCRIPTS_DIR / script_name
        dst = ARCHIVE_DIR / script_name

        if not src.exists():
            print(f"  Skip (not found): {script_name}")
            not_found += 1
            continue

        if dst.exists():
            print(f"  Skip (already archived): {script_name}")
            skipped += 1
            continue

        shutil.move(str(src), str(dst))
        print(f"  Archived: {script_name}")
        moved += 1

    print(f"\nArchived: {moved}, Skipped: {skipped}, Not found: {not_found}")
    print(f"Total in _archive/: {len(list(ARCHIVE_DIR.glob('*')))}")


if __name__ == "__main__":
    main()
