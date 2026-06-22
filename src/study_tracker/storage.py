from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from study_tracker.models import StudySession


CSV_FIELDS = ["date", "subject", "duration_minutes"]
# CSV is intentionally used instead of SQLite for the first version: study
# records are small, append-friendly, human-readable, and easy to open in
# spreadsheet tools. SQLite can replace this module later if querying,
# migrations, or concurrent writes become important.
DEFAULT_DATA_FILE = Path("data/study_sessions.csv")


def ensure_data_file(data_file: Path) -> None:
    """Create the CSV file and header if they do not already exist."""
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if not data_file.exists():
        with data_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()


def add_record(
    data_file: Path,
    study_date: date,
    subject: str,
    minutes_studied: int,
) -> StudySession:
    """Persist one study record and return the validated session."""
    session = StudySession(
        subject=subject,
        duration_minutes=minutes_studied,
        study_date=study_date,
    )
    add_session(data_file, session)
    return session


def add_session(data_file: Path, session: StudySession) -> None:
    """Append a study session to disk so it persists between app runs."""
    ensure_data_file(data_file)
    with data_file.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writerow(
            {
                "date": session.study_date.isoformat(),
                "subject": session.subject.strip(),
                "duration_minutes": session.duration_minutes,
            }
        )


def read_all_records(data_file: Path) -> list[StudySession]:
    """Read every saved study record from the CSV file."""
    if not data_file.exists():
        return []

    sessions: list[StudySession] = []
    with data_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            sessions.append(
                StudySession(
                    subject=row["subject"],
                    duration_minutes=int(row["duration_minutes"]),
                    study_date=date.fromisoformat(row["date"]),
                )
            )
    return sessions


def load_sessions(data_file: Path) -> list[StudySession]:
    """Compatibility wrapper used by the CLI and analytics modules."""
    return read_all_records(data_file)


def filter_records_by_date_range(
    data_file: Path,
    start_date: date,
    end_date: date,
) -> list[StudySession]:
    """Return records with dates between start_date and end_date, inclusive."""
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    return [
        session
        for session in read_all_records(data_file)
        if start_date <= session.study_date <= end_date
    ]
