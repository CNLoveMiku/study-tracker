from __future__ import annotations

import argparse
from pathlib import Path

from study_tracker.models import DEFAULT_DATABASE_FILE, init_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize the Study Tracker database.")
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_FILE,
        help="SQLite database file to create.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    init_db(args.database)
    print(f"Initialized database at {args.database}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
