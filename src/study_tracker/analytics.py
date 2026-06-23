from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import mean
from typing import Any

from study_tracker.models import StudySession


AnalyticsResult = dict[str, Any]


def total_study_time_per_day(records: list[StudySession]) -> dict[str, int]:
    """Return total minutes studied for each date."""
    totals: defaultdict[date, int] = defaultdict(int)
    for record in records:
        totals[record.study_date] += record.duration_minutes

    return {
        study_date.isoformat(): minutes
        for study_date, minutes in sorted(totals.items())
    }


def weekly_total_study_time(records: list[StudySession]) -> dict[str, int]:
    """Return total minutes studied for each ISO week."""
    totals: defaultdict[tuple[int, int], int] = defaultdict(int)
    for record in records:
        iso_year, iso_week, _ = record.study_date.isocalendar()
        totals[(iso_year, iso_week)] += record.duration_minutes

    return {
        f"{iso_year}-W{iso_week:02d}": minutes
        for (iso_year, iso_week), minutes in sorted(totals.items())
    }


def monthly_total_study_time(records: list[StudySession]) -> dict[str, int]:
    """Return total minutes studied for each calendar month."""
    totals: defaultdict[tuple[int, int], int] = defaultdict(int)
    for record in records:
        totals[(record.study_date.year, record.study_date.month)] += (
            record.duration_minutes
        )

    return {
        f"{year}-{month:02d}": minutes
        for (year, month), minutes in sorted(totals.items())
    }


def most_studied_subject(records: list[StudySession]) -> dict[str, int | str | None]:
    """Return the subject with the highest total study time."""
    totals: defaultdict[str, int] = defaultdict(int)
    for record in records:
        totals[record.subject] += record.duration_minutes

    if not totals:
        return {"subject": None, "minutes": 0}

    subject, minutes = max(totals.items(), key=lambda item: (item[1], item[0]))
    return {"subject": subject, "minutes": minutes}


def average_daily_study_time(records: list[StudySession]) -> float:
    """Return average minutes per active study day."""
    daily_totals = total_study_time_per_day(records)
    if not daily_totals:
        return 0
    return round(mean(daily_totals.values()), 2)


def current_streak_days(records: list[StudySession]) -> int:
    """Return the consecutive-day study streak ending on the latest study date."""
    study_dates = {record.study_date for record in records}
    if not study_dates:
        return 0

    cursor = max(study_dates)
    streak = 0
    while cursor in study_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def study_insights(records: list[StudySession]) -> list[str]:
    """Convert raw study metrics into short, student-friendly interpretations."""
    if not records:
        return [
            "Add your first study record to unlock personalized study insights.",
        ]

    stats = {
        "daily_totals": total_study_time_per_day(records),
        "weekly_totals": weekly_total_study_time(records),
        "monthly_totals": monthly_total_study_time(records),
        "most_studied_subject": most_studied_subject(records),
        "average_daily_minutes": average_daily_study_time(records),
        "current_streak_days": current_streak_days(records),
    }
    insights: list[str] = []

    strongest_subject = stats["most_studied_subject"]
    if strongest_subject["subject"]:
        insights.append(
            f"You spend the most time on {strongest_subject['subject']} "
            f"({strongest_subject['minutes']} minutes), which shows your main "
            "academic focus."
        )

    insights.append(
        f"On active study days, you average {stats['average_daily_minutes']} "
        "minutes of study time."
    )

    streak = stats["current_streak_days"]
    if streak > 1:
        insights.append(
            f"Your current streak is {streak} days, showing consistent daily effort."
        )
    else:
        insights.append(
            "Your streak is currently one day or less; studying on consecutive days "
            "would improve consistency."
        )

    weekly_totals = stats["weekly_totals"]
    if weekly_totals:
        best_week, best_minutes = max(weekly_totals.items(), key=lambda item: item[1])
        insights.append(
            f"Your strongest week was {best_week} with {best_minutes} minutes studied."
        )

    return insights


def summary_statistics(records: list[StudySession]) -> AnalyticsResult:
    """Return structured statistics for templates or JSON APIs."""
    total_minutes = sum(record.duration_minutes for record in records)
    session_count = len(records)
    unique_subjects = sorted({record.subject for record in records})
    studied_dates = sorted({record.study_date for record in records})

    return {
        "total_minutes": total_minutes,
        "session_count": session_count,
        "average_minutes_per_session": mean(
            record.duration_minutes for record in records
        )
        if records
        else 0,
        "average_daily_minutes": average_daily_study_time(records),
        "current_streak_days": current_streak_days(records),
        "unique_subject_count": len(unique_subjects),
        "subjects": unique_subjects,
        "first_study_date": studied_dates[0].isoformat() if studied_dates else None,
        "last_study_date": studied_dates[-1].isoformat() if studied_dates else None,
        "daily_totals": total_study_time_per_day(records),
        "weekly_totals": weekly_total_study_time(records),
        "monthly_totals": monthly_total_study_time(records),
        "most_studied_subject": most_studied_subject(records),
        "insights": study_insights(records),
    }
