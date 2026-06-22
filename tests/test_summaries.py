from datetime import date

from study_tracker.models import StudySession
from study_tracker.summaries import monthly_summary, total_minutes, weekly_summary


def test_weekly_summary_groups_sessions_by_subject():
    sessions = [
        StudySession("Math", 30, date(2026, 6, 22)),
        StudySession("Math", 45, date(2026, 6, 23)),
        StudySession("History", 60, date(2026, 6, 24)),
        StudySession("Math", 90, date(2026, 6, 29)),
    ]

    summary = weekly_summary(sessions, date(2026, 6, 23))

    assert summary == {"History": 60, "Math": 75}
    assert total_minutes(summary) == 135


def test_monthly_summary_groups_sessions_by_subject():
    sessions = [
        StudySession("Math", 30, date(2026, 6, 1)),
        StudySession("Science", 20, date(2026, 6, 30)),
        StudySession("Math", 40, date(2026, 7, 1)),
    ]

    assert monthly_summary(sessions, 2026, 6) == {"Math": 30, "Science": 20}
