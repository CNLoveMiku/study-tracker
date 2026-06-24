from datetime import date

from study_tracker.models import StudySession
from study_tracker.study_insights import (
    behavioral_pattern_analysis,
    productivity_score,
    trend_analysis,
    weak_area_detection,
    weekly_insight_report,
)


def sample_records():
    return [
        StudySession("Math", 60, date(2026, 6, 10)),
        StudySession("Physics", 40, date(2026, 6, 11)),
        StudySession("Math", 55, date(2026, 6, 17)),
        StudySession("Computer Science", 70, date(2026, 6, 18)),
        StudySession("Math", 65, date(2026, 6, 19)),
        StudySession("English", 30, date(2026, 6, 20)),
        StudySession("Computer Science", 80, date(2026, 6, 21)),
        StudySession("Math", 75, date(2026, 6, 22)),
        StudySession("Physics", 45, date(2026, 6, 23)),
    ]


def test_productivity_score_is_normalized():
    result = productivity_score(sample_records())

    assert 0 <= result["score"] <= 100
    assert result["weekly_minutes"] == 420


def test_trend_analysis_compares_two_weeks():
    result = trend_analysis(sample_records())

    assert result["status"] == "improving"
    assert result["last_7_days_minutes"] == 420
    assert result["previous_7_days_minutes"] == 100


def test_weak_area_detection_finds_least_productive_subject():
    result = weak_area_detection(sample_records())

    assert result["subject"] == "English"
    assert result["average_minutes_per_session"] == 30


def test_behavioral_pattern_analysis_returns_flags():
    result = behavioral_pattern_analysis(sample_records())

    assert "is_imbalanced" in result
    assert "over_focus" in result
    assert isinstance(result["flags"], list)


def test_weekly_insight_report_contains_dashboard_fields():
    result = weekly_insight_report(sample_records())

    assert set(result) >= {
        "productivity",
        "trend",
        "best_subject",
        "worst_subject",
        "balance",
        "behavioral_patterns",
        "recommendation",
        "recommendations",
    }
