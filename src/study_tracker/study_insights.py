from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean
from typing import Any

from study_tracker.analytics import (
    total_study_time_by_subject,
    total_study_time_per_day,
)
from study_tracker.models import StudySession


InsightResult = dict[str, Any]


def _reference_date(records: list[StudySession]) -> date:
    """Use the latest logged date so historical test data stays meaningful."""
    return max((record.study_date for record in records), default=date.today())


def _records_between(
    records: list[StudySession],
    start_date: date,
    end_date: date,
) -> list[StudySession]:
    return [
        record
        for record in records
        if start_date <= record.study_date <= end_date
    ]


def _total_minutes(records: list[StudySession]) -> int:
    return sum(record.duration_minutes for record in records)


def study_balance_score(records: list[StudySession]) -> InsightResult:
    """Score how evenly study time is distributed across subjects."""
    subject_totals = total_study_time_by_subject(records)
    if not subject_totals:
        return {
            "score": 0,
            "status": "no_data",
            "subject_distribution": {},
            "dominant_subject": None,
            "dominant_share": 0,
            "message": "Add study records to measure subject balance.",
        }

    total = sum(subject_totals.values())
    dominant_subject, dominant_minutes = max(
        subject_totals.items(),
        key=lambda item: item[1],
    )
    dominant_share = round((dominant_minutes / total) * 100, 2)

    if len(subject_totals) == 1:
        return {
            "score": 40,
            "status": "unbalanced",
            "subject_distribution": subject_totals,
            "dominant_subject": dominant_subject,
            "dominant_share": dominant_share,
            "message": "All recorded study time is focused on one subject.",
        }

    entropy = -sum(
        (minutes / total) * math.log(minutes / total)
        for minutes in subject_totals.values()
    )
    max_entropy = math.log(len(subject_totals))
    score = round((entropy / max_entropy) * 100)
    status = "balanced" if score >= 75 else "uneven" if score >= 50 else "unbalanced"

    return {
        "score": score,
        "status": status,
        "subject_distribution": subject_totals,
        "dominant_subject": dominant_subject,
        "dominant_share": dominant_share,
        "message": "Study time is spread across subjects."
        if score >= 75
        else "Study time is concentrated in a small number of subjects.",
    }


def productivity_score(records: list[StudySession]) -> InsightResult:
    """Calculate a 0-100 score from consistency, weekly volume, and balance."""
    if not records:
        return {
            "score": 0,
            "consistency_score": 0,
            "total_time_score": 0,
            "balance_score": 0,
            "weekly_minutes": 0,
            "active_days": 0,
            "message": "Add records to calculate a productivity score.",
        }

    end_date = _reference_date(records)
    start_date = end_date - timedelta(days=6)
    week_records = _records_between(records, start_date, end_date)
    active_days = len({record.study_date for record in week_records})
    weekly_minutes = _total_minutes(week_records)

    consistency_score = round((active_days / 7) * 100)
    total_time_score = min(round((weekly_minutes / 420) * 100), 100)
    balance_value = study_balance_score(week_records)["score"]
    score = round(
        (consistency_score * 0.4)
        + (total_time_score * 0.4)
        + (balance_value * 0.2)
    )

    return {
        "score": max(0, min(score, 100)),
        "consistency_score": consistency_score,
        "total_time_score": total_time_score,
        "balance_score": balance_value,
        "weekly_minutes": weekly_minutes,
        "active_days": active_days,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "message": "Strong weekly productivity."
        if score >= 75
        else "Moderate productivity with room to improve."
        if score >= 50
        else "Low productivity this week; consistency should be the first focus.",
    }


def trend_analysis(records: list[StudySession]) -> InsightResult:
    """Compare the latest 7 days with the previous 7 days."""
    if not records:
        return {
            "status": "stable",
            "last_7_days_minutes": 0,
            "previous_7_days_minutes": 0,
            "change_percent": 0,
            "message": "Add records to detect study trends.",
        }

    end_date = _reference_date(records)
    last_start = end_date - timedelta(days=6)
    previous_end = last_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=6)

    last_minutes = _total_minutes(_records_between(records, last_start, end_date))
    previous_minutes = _total_minutes(
        _records_between(records, previous_start, previous_end)
    )

    if previous_minutes == 0:
        change_percent = 100 if last_minutes > 0 else 0
    else:
        change_percent = round(
            ((last_minutes - previous_minutes) / previous_minutes) * 100,
            2,
        )

    if change_percent > 10:
        status = "improving"
    elif change_percent < -10:
        status = "declining"
    else:
        status = "stable"

    return {
        "status": status,
        "last_7_days_minutes": last_minutes,
        "previous_7_days_minutes": previous_minutes,
        "change_percent": change_percent,
        "date_ranges": {
            "last_7_days": {
                "start": last_start.isoformat(),
                "end": end_date.isoformat(),
            },
            "previous_7_days": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
            },
        },
        "message": f"Study time is {status} compared with the previous week.",
    }


def subject_performance(records: list[StudySession]) -> list[InsightResult]:
    """Return subject-level engagement metrics used by the insight engine."""
    grouped: defaultdict[str, list[StudySession]] = defaultdict(list)
    for record in records:
        grouped[record.subject].append(record)

    metrics: list[InsightResult] = []
    for subject, subject_records in grouped.items():
        total = _total_minutes(subject_records)
        average_minutes = round(mean(r.duration_minutes for r in subject_records), 2)
        session_count = len(subject_records)
        metrics.append(
            {
                "subject": subject,
                "average_minutes_per_session": average_minutes,
                "total_minutes": total,
                "session_count": session_count,
                "engagement_score": round(total * 0.7 + average_minutes * 0.3, 2),
            }
        )
    return sorted(metrics, key=lambda metric: metric["subject"])


def weak_area_detection(records: list[StudySession]) -> InsightResult:
    """Identify the subject with the weakest logged engagement pattern."""
    if not records:
        return {
            "subject": None,
            "average_minutes_per_session": 0,
            "total_minutes": 0,
            "session_count": 0,
            "engagement_score": 0,
            "message": "Add subject records to identify weak areas.",
        }

    weakest = min(
        subject_performance(records),
        key=lambda metric: (
            metric["average_minutes_per_session"],
            metric["total_minutes"],
        ),
    )
    return {
        **weakest,
        "message": (
            f"{weakest['subject']} has the lowest average minutes per session. "
            "This may indicate shallow engagement or under-supported study time."
        ),
    }


def strongest_subject_analysis(records: list[StudySession]) -> InsightResult:
    """Identify the subject with the strongest logged engagement pattern."""
    if not records:
        return {
            "subject": None,
            "average_minutes_per_session": 0,
            "total_minutes": 0,
            "session_count": 0,
            "engagement_score": 0,
            "message": "Add subject records to identify strong areas.",
        }

    strongest = max(
        subject_performance(records),
        key=lambda metric: (metric["total_minutes"], metric["average_minutes_per_session"]),
    )
    return {
        **strongest,
        "message": f"{strongest['subject']} is currently your strongest study area.",
    }


def best_day_analysis(records: list[StudySession]) -> InsightResult:
    """Find the weekday with the highest total logged study time."""
    if not records:
        return {
            "weekday": None,
            "minutes": 0,
            "weekday_totals": {},
            "message": "Add records to identify your most productive weekday.",
        }

    weekday_totals: defaultdict[str, int] = defaultdict(int)
    for record in records:
        weekday_totals[record.study_date.strftime("%A")] += record.duration_minutes

    weekday, minutes = max(weekday_totals.items(), key=lambda item: item[1])
    return {
        "weekday": weekday,
        "minutes": minutes,
        "weekday_totals": dict(sorted(weekday_totals.items())),
        "message": f"{weekday} is your strongest study day.",
    }


def behavioral_pattern_analysis(records: list[StudySession]) -> InsightResult:
    """Detect imbalance and over-focus patterns in study behavior."""
    balance = study_balance_score(records)
    over_focus = (
        bool(balance["dominant_subject"])
        and balance["dominant_share"] >= 60
        and len(balance["subject_distribution"]) > 1
    )
    imbalanced = balance["score"] < 60

    flags: list[str] = []
    if imbalanced:
        flags.append("imbalanced_distribution")
    if over_focus:
        flags.append("over_focus")

    return {
        "is_imbalanced": imbalanced,
        "over_focus": over_focus,
        "dominant_subject": balance["dominant_subject"],
        "dominant_share": balance["dominant_share"],
        "flags": flags,
        "message": "Your study pattern is imbalanced."
        if imbalanced
        else "Your subject distribution is reasonably balanced.",
    }


def generate_recommendations(records: list[StudySession]) -> list[str]:
    """Generate explainable AI-style recommendations from rule-based insights."""
    if not records:
        return ["Start by logging one week of study sessions to unlock guidance."]

    recommendations: list[str] = []
    productivity = productivity_score(records)
    trend = trend_analysis(records)
    balance = study_balance_score(records)
    weak_area = weak_area_detection(records)
    behavior = behavioral_pattern_analysis(records)

    if behavior["over_focus"]:
        recommendations.append(
            f"You are over-focused on {behavior['dominant_subject']}; "
            "consider redistributing study time across subjects."
        )
    elif balance["score"] < 60:
        recommendations.append("Your study pattern is imbalanced.")

    if trend["status"] == "improving":
        recommendations.append("You are improving consistently; keep the current rhythm.")
    elif trend["status"] == "declining":
        recommendations.append("Your study time is declining; schedule a recovery week.")

    if productivity["active_days"] < 4:
        recommendations.append("Aim for at least four active study days this week.")
    if weak_area["subject"]:
        recommendations.append(
            f"Give {weak_area['subject']} a longer focused session next."
        )

    if not recommendations:
        recommendations.append("Your study behavior looks balanced; maintain the pattern.")
    return recommendations


def weekly_insight_report(records: list[StudySession]) -> InsightResult:
    """Return the structured V3 insight object consumed by the dashboard."""
    recommendations = generate_recommendations(records)
    return {
        "productivity": productivity_score(records),
        "trend": trend_analysis(records),
        "best_subject": strongest_subject_analysis(records),
        "worst_subject": weak_area_detection(records),
        "weak_subject": weak_area_detection(records),
        "best_day": best_day_analysis(records),
        "balance": study_balance_score(records),
        "behavioral_patterns": behavioral_pattern_analysis(records),
        "recommendation": recommendations[0],
        "recommendations": recommendations,
        "daily_totals": total_study_time_per_day(records),
        "subject_totals": total_study_time_by_subject(records),
    }


def intelligent_dashboard(records: list[StudySession]) -> InsightResult:
    """Backward-compatible name for the V3 weekly insight report."""
    return weekly_insight_report(records)


# Compatibility aliases for the V2 public API.
trend_detection = trend_analysis
weak_subject_analysis = weak_area_detection
