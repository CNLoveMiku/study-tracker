from datetime import date

from study_tracker.analytics import (
    average_daily_study_time,
    current_streak_days,
    monthly_total_study_time,
    most_studied_subject,
    summary_statistics,
    total_study_time_per_day,
    weekly_total_study_time,
    study_insights,
)
from study_tracker.models import StudySession


def sample_records():
    return [
        StudySession("Math", 30, date(2026, 6, 22)),
        StudySession("Math", 45, date(2026, 6, 22)),
        StudySession("History", 60, date(2026, 6, 24)),
        StudySession("Science", 90, date(2026, 7, 1)),
    ]


def test_total_study_time_per_day():
    assert total_study_time_per_day(sample_records()) == {
        "2026-06-22": 75,
        "2026-06-24": 60,
        "2026-07-01": 90,
    }


def test_weekly_total_study_time():
    assert weekly_total_study_time(sample_records()) == {
        "2026-W26": 135,
        "2026-W27": 90,
    }


def test_monthly_total_study_time():
    assert monthly_total_study_time(sample_records()) == {
        "2026-06": 135,
        "2026-07": 90,
    }


def test_most_studied_subject():
    assert most_studied_subject(sample_records()) == {
        "subject": "Science",
        "minutes": 90,
    }


def test_average_daily_study_time():
    assert average_daily_study_time(sample_records()) == 75


def test_current_streak_days_ends_on_latest_study_date():
    records = [
        StudySession("Math", 30, date(2026, 6, 20)),
        StudySession("Math", 30, date(2026, 6, 22)),
        StudySession("Math", 30, date(2026, 6, 23)),
        StudySession("Math", 30, date(2026, 6, 24)),
    ]

    assert current_streak_days(records) == 3


def test_study_insights_returns_interpretation_text():
    insights = study_insights(sample_records())

    assert any("Science" in insight for insight in insights)
    assert any("average" in insight for insight in insights)


def test_summary_statistics():
    stats = summary_statistics(sample_records())
    advanced = stats.pop("advanced")

    assert advanced["productivity"]["score"] > 0
    assert advanced["trend"]["status"] in {"improving", "stable", "declining"}
    assert stats == {
        "total_minutes": 225,
        "session_count": 4,
        "average_minutes_per_session": 56.25,
        "average_daily_minutes": 75,
        "current_streak_days": 1,
        "unique_subject_count": 3,
        "subjects": ["History", "Math", "Science"],
        "first_study_date": "2026-06-22",
        "last_study_date": "2026-07-01",
        "daily_totals": {
            "2026-06-22": 75,
            "2026-06-24": 60,
            "2026-07-01": 90,
        },
        "weekly_totals": {
            "2026-W26": 135,
            "2026-W27": 90,
        },
        "monthly_totals": {
            "2026-06": 135,
            "2026-07": 90,
        },
        "most_studied_subject": {
            "subject": "Science",
            "minutes": 90,
        },
        "insights": [
            "You spend the most time on Science (90 minutes), which shows your main "
            "academic focus.",
            "On active study days, you average 75 minutes of study time.",
            "Your streak is currently one day or less; studying on consecutive days "
            "would improve consistency.",
            "Your strongest week was 2026-W26 with 135 minutes studied.",
        ],
    }


def test_summary_statistics_for_empty_records():
    stats = summary_statistics([])
    advanced = stats.pop("advanced")

    assert advanced["productivity"]["score"] == 0
    assert advanced["recommendations"] == [
        "Start by logging one week of study sessions to unlock guidance."
    ]
    assert stats == {
        "total_minutes": 0,
        "session_count": 0,
        "average_minutes_per_session": 0,
        "average_daily_minutes": 0,
        "current_streak_days": 0,
        "unique_subject_count": 0,
        "subjects": [],
        "first_study_date": None,
        "last_study_date": None,
        "daily_totals": {},
        "weekly_totals": {},
        "monthly_totals": {},
        "most_studied_subject": {
            "subject": None,
            "minutes": 0,
        },
        "insights": [
            "Add your first study record to unlock personalized study insights.",
        ],
    }
