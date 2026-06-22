from study_tracker.charts import (
    save_daily_trend_line_chart,
    save_subject_distribution_pie_chart,
    save_weekly_bar_chart,
)


def assert_png_created(path):
    assert path.exists()
    assert path.read_bytes().startswith(b"\x89PNG")


def test_save_weekly_bar_chart(tmp_path):
    output_file = tmp_path / "weekly.png"

    save_weekly_bar_chart({"2026-W26": 135, "2026-W27": 90}, output_file)

    assert_png_created(output_file)


def test_save_daily_trend_line_chart(tmp_path):
    output_file = tmp_path / "daily.png"

    save_daily_trend_line_chart(
        {"2026-06-22": 75, "2026-06-24": 60, "2026-07-01": 90},
        output_file,
    )

    assert_png_created(output_file)


def test_save_subject_distribution_pie_chart(tmp_path):
    output_file = tmp_path / "subjects.png"

    save_subject_distribution_pie_chart(
        {"Math": 75, "History": 60, "Science": 90},
        output_file,
    )

    assert_png_created(output_file)


def test_chart_functions_handle_empty_data(tmp_path):
    output_file = tmp_path / "empty.png"

    save_weekly_bar_chart({}, output_file)

    assert_png_created(output_file)
