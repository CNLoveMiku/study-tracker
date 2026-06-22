from study_tracker.app import create_app
from study_tracker.models import get_all_records


def test_home_page_loads(tmp_path):
    app = create_app(tmp_path / "study_tracker.db")
    app.config.update(TESTING=True)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Add Study Record" in response.data


def test_add_record_redirects_and_persists(tmp_path):
    database_file = tmp_path / "study_tracker.db"
    app = create_app(database_file)
    app.config.update(TESTING=True)

    response = app.test_client().post(
        "/add",
        data={
            "subject": "Mathematics",
            "minutes": "45",
            "study_date": "2026-06-23",
        },
    )

    records = get_all_records(database_file)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert len(records) == 1
    assert records[0].subject == "Mathematics"


def test_add_record_rejects_invalid_minutes(tmp_path):
    database_file = tmp_path / "study_tracker.db"
    app = create_app(database_file)
    app.config.update(TESTING=True)

    response = app.test_client().post(
        "/add",
        data={
            "subject": "Mathematics",
            "minutes": "0",
            "study_date": "2026-06-23",
        },
    )

    assert response.status_code == 302
    assert get_all_records(database_file) == []
