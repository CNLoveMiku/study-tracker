from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_DATABASE_FILE = Path("data/study_tracker.db")


@dataclass(frozen=True)
class StudySession:
    subject: str
    duration_minutes: int
    study_date: date
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject is required")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS study_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    subject TEXT NOT NULL,
    minutes INTEGER NOT NULL CHECK (minutes > 0)
);

CREATE INDEX IF NOT EXISTS idx_study_records_date
ON study_records(date);
"""


def init_db(database_file: Path = DEFAULT_DATABASE_FILE) -> None:
    """Create the SQLite database and study_records table if needed."""
    database_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_file) as connection:
        connection.executescript(SCHEMA_SQL)


def _row_to_session(row: sqlite3.Row) -> StudySession:
    return StudySession(
        id=row["id"],
        study_date=date.fromisoformat(row["date"]),
        subject=row["subject"],
        duration_minutes=row["minutes"],
    )


def get_connection(database_file: Path = DEFAULT_DATABASE_FILE) -> sqlite3.Connection:
    """Open a SQLite connection configured for dictionary-like rows."""
    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row
    return connection


def add_study_record(
    database_file: Path,
    study_date: date,
    subject: str,
    minutes: int,
) -> StudySession:
    """Validate and safely insert one study record."""
    session = StudySession(
        study_date=study_date,
        subject=subject.strip(),
        duration_minutes=minutes,
    )
    init_db(database_file)
    with get_connection(database_file) as connection:
        cursor = connection.execute(
            """
            INSERT INTO study_records (date, subject, minutes)
            VALUES (?, ?, ?)
            """,
            (
                session.study_date.isoformat(),
                session.subject,
                session.duration_minutes,
            ),
        )
        return StudySession(
            id=cursor.lastrowid,
            study_date=session.study_date,
            subject=session.subject,
            duration_minutes=session.duration_minutes,
        )


def get_all_records(database_file: Path) -> list[StudySession]:
    """Return all study records sorted newest first."""
    init_db(database_file)
    with get_connection(database_file) as connection:
        rows = connection.execute(
            """
            SELECT id, date, subject, minutes
            FROM study_records
            ORDER BY date DESC, id DESC
            """
        ).fetchall()
    return [_row_to_session(row) for row in rows]


def get_records_by_date_range(
    database_file: Path,
    start_date: date,
    end_date: date,
) -> list[StudySession]:
    """Return records inside an inclusive date range."""
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    init_db(database_file)
    with get_connection(database_file) as connection:
        rows = connection.execute(
            """
            SELECT id, date, subject, minutes
            FROM study_records
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC, id ASC
            """,
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
    return [_row_to_session(row) for row in rows]
