"""CLI compatibility facade for the source-free exact-wheel UAT."""

from structural_lib.services.release_uat import main, run

__all__ = ["main", "run"]


if __name__ == "__main__":
    raise SystemExit(main())
