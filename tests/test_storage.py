from datetime import date

from study_tracker.models import StudySession
from study_tracker.storage import (
    add_record,
    add_session,
    filter_records_by_date_range,
    load_sessions,
    read_all_records,
)


def test_add_and_load_session(tmp_path):
    data_file = tmp_path / "study.csv"
    session = StudySession("Math", 45, date(2026, 6, 23))

    add_session(data_file, session)

    assert load_sessions(data_file) == [session]


def test_add_record_persists_to_csv(tmp_path):
    data_file = tmp_path / "study.csv"

    saved_session = add_record(data_file, date(2026, 6, 23), "History", 30)

    assert saved_session == StudySession("History", 30, date(2026, 6, 23))
    assert read_all_records(data_file) == [saved_session]


def test_load_missing_file_returns_empty_list(tmp_path):
    assert load_sessions(tmp_path / "missing.csv") == []


def test_filter_records_by_date_range_is_inclusive(tmp_path):
    data_file = tmp_path / "study.csv"
    sessions = [
        StudySession("Math", 20, date(2026, 6, 1)),
        StudySession("Science", 30, date(2026, 6, 15)),
        StudySession("History", 40, date(2026, 6, 30)),
        StudySession("Art", 50, date(2026, 7, 1)),
    ]
    for session in sessions:
        add_session(data_file, session)

    assert filter_records_by_date_range(
        data_file,
        date(2026, 6, 15),
        date(2026, 6, 30),
    ) == sessions[1:3]


def test_filter_records_rejects_invalid_range(tmp_path):
    data_file = tmp_path / "study.csv"

    try:
        filter_records_by_date_range(data_file, date(2026, 7, 1), date(2026, 6, 1))
    except ValueError as error:
        assert str(error) == "start_date must be on or before end_date"
    else:
        raise AssertionError("Expected invalid date range to raise ValueError")
