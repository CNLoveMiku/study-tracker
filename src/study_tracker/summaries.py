from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from study_tracker.models import StudySession


Summary = dict[str, int]


def weekly_range(reference_date: date) -> tuple[date, date]:
    start = reference_date - timedelta(days=reference_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def summarize_by_subject(sessions: list[StudySession]) -> Summary:
    totals: defaultdict[str, int] = defaultdict(int)
    for session in sessions:
        totals[session.subject] += session.duration_minutes
    return dict(sorted(totals.items()))


def weekly_summary(sessions: list[StudySession], reference_date: date) -> Summary:
    start, end = weekly_range(reference_date)
    return summarize_by_subject(
        [
            session
            for session in sessions
            if start <= session.study_date <= end
        ]
    )


def monthly_summary(sessions: list[StudySession], year: int, month: int) -> Summary:
    return summarize_by_subject(
        [
            session
            for session in sessions
            if session.study_date.year == year and session.study_date.month == month
        ]
    )


def total_minutes(summary: Summary) -> int:
    return sum(summary.values())
