from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

check_links = importlib.import_module("check_links")
safe_file_move = importlib.import_module("safe_file_move")
safe_ops = importlib.import_module("_lib.safe_file_ops")


def _write_checker(root: Path, *, fail_when_source_missing: bool = False) -> None:
    checker = root / "scripts" / "check_links.py"
    checker.parent.mkdir(parents=True, exist_ok=True)
    condition = (
        "not (Path(__file__).resolve().parents[1] / 'docs/source.md').exists()"
        if fail_when_source_missing
        else "False"
    )
    checker.write_text(
        "from pathlib import Path\n"
        "import json\n"
        f"broken = [{{'file': 'docs/ref.md', 'target': 'source.md'}}] if {condition} else []\n"
        "print(json.dumps({'tool': 'check_links', 'broken_links': broken}))\n"
        "raise SystemExit(1 if broken else 0)\n",
        encoding="utf-8",
    )


def _move_args(source: str, destination: str) -> argparse.Namespace:
    return argparse.Namespace(
        source=source,
        destination=destination,
        stub=False,
        dry_run=False,
        json=True,
    )


def test_path_contract_rejects_directory_outside_symlink_and_destination(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    source = root / "source.md"
    source.write_text("source\n", encoding="utf-8")
    directory = root / "folder"
    directory.mkdir()
    destination = root / "existing.md"
    destination.write_text("existing\n", encoding="utf-8")

    with pytest.raises(safe_ops.SafeFileError, match="regular file"):
        safe_ops.resolve_regular_source(directory, root)
    with pytest.raises(safe_ops.SafeFileError, match="inside repository"):
        safe_ops.resolve_new_destination(tmp_path / "outside.md", root, source)
    with pytest.raises(safe_ops.SafeFileError, match="already exists"):
        safe_ops.resolve_new_destination(destination, root, source)

    symlink = root / "source-link.md"
    symlink.symlink_to(source)
    with pytest.raises(safe_ops.SafeFileError, match="Symlink"):
        safe_ops.resolve_regular_source(symlink, root)


def test_reference_classification_blocks_basename_only_mentions(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "source.md"
    destination = root / "docs" / "moved" / "source.md"
    note = root / "scripts" / "note.py"
    source.parent.mkdir(parents=True)
    note.parent.mkdir(parents=True)
    source.write_text("source\n", encoding="utf-8")
    note.write_text(
        "MESSAGE = 'source.md requires manual handling'\n", encoding="utf-8"
    )

    references = safe_ops.classify_references(source, destination, root)
    assert [(ref.file, ref.classification) for ref in references] == [
        (note, "unresolved")
    ]


def test_move_refuses_missing_validator_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "source.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"original bytes\n")
    monkeypatch.setattr(safe_file_move, "REPO_ROOT", root)

    exit_code, payload = safe_file_move.run_move(
        _move_args("docs/source.md", "docs/moved/source.md")
    )

    assert exit_code == 1
    assert "Link baseline unavailable" in str(payload["error"])
    assert source.read_bytes() == b"original bytes\n"
    assert not (root / "docs" / "moved" / "source.md").exists()


def test_move_restores_exact_bytes_after_post_validation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    source = root / "docs" / "source.md"
    reference = root / "docs" / "ref.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"original bytes\n")
    reference.write_bytes(b"[source](source.md)\n")
    _write_checker(root, fail_when_source_missing=True)
    monkeypatch.setattr(safe_file_move, "REPO_ROOT", root)

    exit_code, payload = safe_file_move.run_move(
        _move_args("docs/source.md", "docs/moved/source.md")
    )

    assert exit_code == 1
    assert payload["rolled_back"] is True
    assert source.read_bytes() == b"original bytes\n"
    assert reference.read_bytes() == b"[source](source.md)\n"
    assert not (root / "docs" / "moved" / "source.md").exists()


def test_content_hashed_backups_do_not_collide_for_same_basename(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    first = root / "a" / "same.md"
    second = root / "b" / "same.md"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_bytes(b"identical\n")
    second.write_bytes(b"identical\n")

    first_backup, first_manifest = safe_ops.create_content_hashed_backup(first, root)
    second_backup, second_manifest = safe_ops.create_content_hashed_backup(second, root)

    assert first_backup != second_backup
    assert first_manifest != second_manifest
    assert first_backup.read_bytes() == second_backup.read_bytes() == b"identical\n"


def test_link_checker_covers_images_and_ignores_code_examples(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "readme.md").write_text(
        "![missing](missing.png)\n" "```markdown\n![example](example.png)\n```\n",
        encoding="utf-8",
    )

    payload = check_links.scan_links(root=root)

    assert payload["images_checked"] == 1
    assert payload["broken_count"] == 1
    assert payload["broken_links"][0]["kind"] == "image"


def test_link_checker_does_not_choose_between_ambiguous_matches(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "readme.md").write_text("[guide](missing/guide.md)\n", encoding="utf-8")
    for folder in ("a", "b"):
        candidate = root / folder / "guide.md"
        candidate.parent.mkdir()
        candidate.write_text("guide\n", encoding="utf-8")

    payload = check_links.scan_links(root=root, suggest=True)

    assert payload["broken_count"] == 1
    assert payload["broken_links"][0]["suggestion"] is None
