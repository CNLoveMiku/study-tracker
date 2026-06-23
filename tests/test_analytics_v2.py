from datetime import date

from study_tracker.analytics_v2 import (
    best_day_analysis,
    intelligent_dashboard,
    productivity_score,
    study_balance_score,
    trend_detection,
    weak_subject_analysis,
)
from study_tracker.models import StudySession


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


def test_productivity_score_returns_component_scores():
    result = productivity_score(sample_records())

    assert result["score"] > 0
    assert result["weekly_minutes"] == 420
    assert result["active_days"] == 7
    assert set(result) >= {
        "consistency_score",
        "total_time_score",
        "balance_score",
    }


def test_trend_detection_classifies_recent_change():
    result = trend_detection(sample_records())

    assert result["status"] == "improving"
    assert result["last_7_days_minutes"] == 420
    assert result["previous_7_days_minutes"] == 100


def test_weak_subject_analysis_identifies_lowest_average_session():
    result = weak_subject_analysis(sample_records())

    assert result["subject"] == "English"
    assert result["average_minutes_per_session"] == 30


def test_best_day_analysis_returns_weekday_totals():
    result = best_day_analysis(sample_records())

    assert result["weekday"] == "Wednesday"
    assert result["minutes"] == 115


def test_study_balance_score_is_structured():
    result = study_balance_score(sample_records())

    assert 0 <= result["score"] <= 100
    assert result["status"] in {"balanced", "uneven", "unbalanced"}
    assert result["subject_distribution"]["Math"] == 255


def test_intelligent_dashboard_combines_all_sections():
    result = intelligent_dashboard(sample_records())

    assert set(result) >= {
        "productivity",
        "trend",
        "weak_subject",
        "best_day",
        "balance",
        "recommendations",
    }
    assert result["recommendations"]
