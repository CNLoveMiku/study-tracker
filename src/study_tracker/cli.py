from __future__ import annotations

import argparse
import calendar
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

from study_tracker.analytics import (
    monthly_total_study_time,
    summary_statistics,
    total_study_time_per_day,
    weekly_total_study_time,
)
from study_tracker.storage import (
    DEFAULT_DATA_FILE,
    add_record,
    filter_records_by_date_range,
    read_all_records,
)
from study_tracker.summaries import summarize_by_subject


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track study sessions locally.")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="CSV file used to store study sessions.",
    )
    return parser


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Date must use YYYY-MM-DD format.") from exc


def prompt_date(
    input_func: InputFunc,
    output_func: OutputFunc,
    prompt: str,
    default: date | None = None,
) -> date:
    while True:
        suffix = f" [{default.isoformat()}]" if default else ""
        raw_value = input_func(f"{prompt}{suffix}: ").strip()
        if not raw_value and default:
            return default
        try:
            return parse_date(raw_value)
        except ValueError as error:
            output_func(str(error))


def prompt_positive_int(
    input_func: InputFunc,
    output_func: OutputFunc,
    prompt: str,
) -> int:
    while True:
        raw_value = input_func(f"{prompt}: ").strip()
        try:
            value = int(raw_value)
        except ValueError:
            output_func("Please enter a whole number.")
            continue
        if value > 0:
            return value
        output_func("Please enter a number greater than zero.")


def prompt_month(
    input_func: InputFunc,
    output_func: OutputFunc,
) -> tuple[int, int]:
    today = date.today()
    while True:
        raw_value = input_func(
            f"Month to summarize as YYYY-MM [{today.year}-{today.month:02d}]: "
        ).strip()
        if not raw_value:
            return today.year, today.month
        try:
            year_text, month_text = raw_value.split("-", maxsplit=1)
            year = int(year_text)
            month = int(month_text)
        except ValueError:
            output_func("Month must use YYYY-MM format.")
            continue
        if 1 <= month <= 12:
            return year, month
        output_func("Month must be between 1 and 12.")


def month_range(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def week_range(reference_date: date) -> tuple[date, date]:
    start = reference_date - timedelta(days=reference_date.weekday())
    return start, start + timedelta(days=6)


def print_totals(title: str, totals: dict[str, int], output_func: OutputFunc) -> None:
    output_func("")
    output_func(title)
    output_func("-" * len(title))
    if not totals:
        output_func("No study records found.")
        return
    for label, minutes in totals.items():
        output_func(f"{label}: {minutes} minutes")


def print_stats(records_title: str, records, output_func: OutputFunc) -> None:
    stats = summary_statistics(records)
    output_func("")
    output_func(records_title)
    output_func("-" * len(records_title))
    output_func(f"Total: {stats['total_minutes']} minutes")
    output_func(f"Sessions: {stats['session_count']}")
    output_func(f"Average/session: {stats['average_minutes_per_session']} minutes")
    most_studied = stats["most_studied_subject"]
    if most_studied["subject"]:
        output_func(
            f"Most studied: {most_studied['subject']} "
            f"({most_studied['minutes']} minutes)"
        )
    else:
        output_func("Most studied: none")


def add_study_record(
    data_file: Path,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> None:
    output_func("")
    output_func("Add Study Record")
    subject = input_func("Subject: ").strip()
    minutes = prompt_positive_int(input_func, output_func, "Minutes studied")
    study_date = prompt_date(input_func, output_func, "Study date", date.today())

    try:
        session = add_record(data_file, study_date, subject, minutes)
    except ValueError as error:
        output_func(f"Could not save record: {error}")
        return

    output_func(
        f"Saved {session.duration_minutes} minutes of {session.subject} "
        f"on {session.study_date.isoformat()}."
    )


def view_weekly_summary(
    data_file: Path,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> None:
    reference_date = prompt_date(
        input_func,
        output_func,
        "Reference date for week",
        date.today(),
    )
    start_date, end_date = week_range(reference_date)
    records = filter_records_by_date_range(data_file, start_date, end_date)

    print_stats(
        f"Weekly Summary ({start_date.isoformat()} to {end_date.isoformat()})",
        records,
        output_func,
    )
    print_totals("Daily totals", total_study_time_per_day(records), output_func)


def view_monthly_summary(
    data_file: Path,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> None:
    year, month = prompt_month(input_func, output_func)
    start_date, end_date = month_range(year, month)
    records = filter_records_by_date_range(data_file, start_date, end_date)

    print_stats(f"Monthly Summary ({year}-{month:02d})", records, output_func)
    print_totals("Weekly totals", weekly_total_study_time(records), output_func)


def generate_charts(
    data_file: Path,
    input_func: InputFunc,
    output_func: OutputFunc,
) -> None:
    try:
        from study_tracker.charts import (
            save_daily_trend_line_chart,
            save_subject_distribution_pie_chart,
            save_weekly_bar_chart,
        )
    except ModuleNotFoundError:
        output_func("matplotlib is required for charts. Install with: pip install -e .")
        return

    records = read_all_records(data_file)
    if not records:
        output_func("No study records found. Add records before generating charts.")
        return

    output_dir_raw = input_func("Output folder [charts]: ").strip()
    output_dir = Path(output_dir_raw) if output_dir_raw else Path("charts")

    weekly_path = output_dir / "weekly_study_time.png"
    daily_path = output_dir / "daily_study_trend.png"
    subjects_path = output_dir / "subject_distribution.png"

    save_weekly_bar_chart(weekly_total_study_time(records), weekly_path)
    save_daily_trend_line_chart(total_study_time_per_day(records), daily_path)
    save_subject_distribution_pie_chart(summarize_by_subject(records), subjects_path)

    output_func(f"Saved weekly bar chart to {weekly_path}")
    output_func(f"Saved daily trend line chart to {daily_path}")
    output_func(f"Saved subject distribution pie chart to {subjects_path}")


def print_menu(output_func: OutputFunc) -> None:
    output_func("")
    output_func("Study Tracker")
    output_func("1. Add study record")
    output_func("2. View weekly summary")
    output_func("3. View monthly summary")
    output_func("4. Generate charts")
    output_func("5. Exit")


def run_menu(
    data_file: Path,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> int:
    actions = {
        "1": add_study_record,
        "2": view_weekly_summary,
        "3": view_monthly_summary,
        "4": generate_charts,
    }

    while True:
        print_menu(output_func)
        choice = input_func("Choose an option: ").strip()
        if choice == "5":
            output_func("Goodbye.")
            return 0

        action = actions.get(choice)
        if not action:
            output_func("Please choose a valid option from 1 to 5.")
            continue
        action(data_file, input_func, output_func)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_menu(args.data_file)
