from study_tracker.cli import run_menu
from study_tracker.storage import read_all_records


def make_input(values):
    iterator = iter(values)
    return lambda prompt="": next(iterator)


def test_menu_adds_study_record(tmp_path):
    data_file = tmp_path / "study.csv"
    output = []

    result = run_menu(
        data_file,
        input_func=make_input(["1", "Math", "45", "2026-06-23", "5"]),
        output_func=output.append,
    )

    records = read_all_records(data_file)
    assert result == 0
    assert len(records) == 1
    assert records[0].subject == "Math"
    assert records[0].duration_minutes == 45
    assert records[0].study_date.isoformat() == "2026-06-23"


def test_menu_rejects_unknown_choice(tmp_path):
    output = []

    result = run_menu(
        tmp_path / "study.csv",
        input_func=make_input(["9", "5"]),
        output_func=output.append,
    )

    assert result == 0
    assert "Please choose a valid option from 1 to 5." in output
