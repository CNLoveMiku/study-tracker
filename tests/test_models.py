from datetime import date

from study_tracker.models import (
    add_study_record,
    get_all_records,
    get_records_by_date_range,
    init_db,
)


def test_init_db_creates_database_file(tmp_path):
    database_file = tmp_path / "study_tracker.db"

    init_db(database_file)

    assert database_file.exists()


def test_add_and_query_study_record(tmp_path):
    database_file = tmp_path / "study_tracker.db"

    record = add_study_record(database_file, date(2026, 6, 23), "Math", 45)

    records = get_all_records(database_file)
    assert record.id is not None
    assert len(records) == 1
    assert records[0].subject == "Math"
    assert records[0].duration_minutes == 45
    assert records[0].study_date == date(2026, 6, 23)


def test_get_records_by_date_range_is_inclusive(tmp_path):
    database_file = tmp_path / "study_tracker.db"
    add_study_record(database_file, date(2026, 6, 1), "Math", 20)
    add_study_record(database_file, date(2026, 6, 15), "Science", 30)
    add_study_record(database_file, date(2026, 7, 1), "History", 40)

    records = get_records_by_date_range(
        database_file,
        date(2026, 6, 1),
        date(2026, 6, 30),
    )

    assert [record.subject for record in records] == ["Math", "Science"]
