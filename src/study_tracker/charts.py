from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from study_tracker.summaries import Summary
from study_tracker.analytics import (
    total_study_time_per_day,
    weekly_total_study_time,
)
from study_tracker.models import StudySession
from study_tracker.summaries import summarize_by_subject


def _prepare_output_file(output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)


def _save_empty_chart(title: str, output_file: Path) -> None:
    _prepare_output_file(output_file)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.text(0.5, 0.5, "No study sessions found", ha="center", va="center")
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(output_file, format="png")
    plt.close(fig)


def save_weekly_bar_chart(
    weekly_totals: dict[str, int],
    output_file: Path,
    title: str = "Weekly Study Time",
) -> None:
    """Save a PNG bar chart from weekly total minutes."""
    if not weekly_totals:
        _save_empty_chart(title, output_file)
        return

    _prepare_output_file(output_file)
    weeks = list(weekly_totals.keys())
    minutes = list(weekly_totals.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(weeks, minutes, color="#4c78a8")
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel("Week")
    ax.set_ylabel("Minutes")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(output_file, format="png")
    plt.close(fig)


def save_daily_trend_line_chart(
    daily_totals: dict[str, int],
    output_file: Path,
    title: str = "Daily Study Trend",
) -> None:
    """Save a PNG line chart from daily total minutes."""
    if not daily_totals:
        _save_empty_chart(title, output_file)
        return

    _prepare_output_file(output_file)
    days = list(daily_totals.keys())
    minutes = list(daily_totals.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(days, minutes, marker="o", color="#4c78a8")
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Minutes")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_file, format="png")
    plt.close(fig)


def save_subject_distribution_pie_chart(
    subject_totals: dict[str, int],
    output_file: Path,
    title: str = "Subject Distribution",
) -> None:
    """Save a PNG pie chart from total minutes by subject."""
    if not subject_totals:
        _save_empty_chart(title, output_file)
        return

    _prepare_output_file(output_file)
    subjects = list(subject_totals.keys())
    minutes = list(subject_totals.values())

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(minutes, labels=subjects, autopct="%1.1f%%", startangle=90)
    ax.set_title(title, fontsize=14, weight="bold")
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(output_file, format="png")
    plt.close(fig)


def generate_all_charts(
    records: list[StudySession],
    output_dir: Path,
) -> list[dict[str, str]]:
    """Generate all web charts and return template-friendly metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    charts = [
        {
            "title": "Daily Study Trend",
            "filename": "daily_study_trend.png",
            "description": "Line chart showing total minutes studied each day.",
        },
        {
            "title": "Weekly Total",
            "filename": "weekly_study_time.png",
            "description": "Bar chart showing total study time per ISO week.",
        },
        {
            "title": "Subject Distribution",
            "filename": "subject_distribution.png",
            "description": "Pie chart showing total study time by subject.",
        },
    ]

    save_daily_trend_line_chart(
        total_study_time_per_day(records),
        output_dir / "daily_study_trend.png",
    )
    save_weekly_bar_chart(
        weekly_total_study_time(records),
        output_dir / "weekly_study_time.png",
    )
    save_subject_distribution_pie_chart(
        summarize_by_subject(records),
        output_dir / "subject_distribution.png",
    )
    return charts


def save_summary_chart(summary: Summary, title: str, output_file: Path) -> None:
    """Backward-compatible subject bar chart used by the CLI."""
    _prepare_output_file(output_file)

    subjects = list(summary.keys())
    minutes = list(summary.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    if subjects:
        ax.bar(subjects, minutes, color="#4c78a8")
        ax.set_ylabel("Minutes")
        ax.set_xlabel("Subject")
    else:
        ax.text(0.5, 0.5, "No study sessions found", ha="center", va="center")
        ax.set_xticks([])
        ax.set_yticks([])

    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_file, format="png")
    plt.close(fig)
