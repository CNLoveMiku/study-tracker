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


AnalyticsV2Result = dict[str, Any]


def _reference_date(records: list[StudySession]) -> date:
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


def study_balance_score(records: list[StudySession]) -> AnalyticsV2Result:
    """Measure how evenly study time is distributed across subjects."""
    subject_totals = total_study_time_by_subject(records)
    if not subject_totals:
        return {
            "score": 0,
            "status": "no_data",
            "subject_distribution": {},
            "message": "Add study records to measure subject balance.",
        }
    if len(subject_totals) == 1:
        return {
            "score": 40,
            "status": "unbalanced",
            "subject_distribution": subject_totals,
            "message": "All recorded study time is focused on one subject.",
        }

    total = sum(subject_totals.values())
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
        "message": "Study time is spread across subjects."
        if score >= 75
        else "Study time is concentrated in a small number of subjects.",
    }


def productivity_score(records: list[StudySession]) -> AnalyticsV2Result:
    """Score weekly productivity using consistency, volume, and balance."""
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
    balance = study_balance_score(week_records)
    balance_value = balance["score"]
    score = round(
        (consistency_score * 0.4)
        + (total_time_score * 0.4)
        + (balance_value * 0.2)
    )

    return {
        "score": score,
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


def trend_detection(records: list[StudySession]) -> AnalyticsV2Result:
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


def weak_subject_analysis(records: list[StudySession]) -> AnalyticsV2Result:
    """Identify the subject with the weakest logged engagement pattern."""
    if not records:
        return {
            "subject": None,
            "average_minutes_per_session": 0,
            "total_minutes": 0,
            "session_count": 0,
            "message": "Add subject records to identify weak areas.",
        }

    grouped: defaultdict[str, list[StudySession]] = defaultdict(list)
    for record in records:
        grouped[record.subject].append(record)

    subject_metrics = []
    for subject, subject_records in grouped.items():
        total = _total_minutes(subject_records)
        average_minutes = round(mean(r.duration_minutes for r in subject_records), 2)
        subject_metrics.append(
            {
                "subject": subject,
                "average_minutes_per_session": average_minutes,
                "total_minutes": total,
                "session_count": len(subject_records),
            }
        )

    weakest = min(
        subject_metrics,
        key=lambda metric: (
            metric["average_minutes_per_session"],
            metric["total_minutes"],
        ),
    )
    weakest["message"] = (
        f"{weakest['subject']} has the lowest average minutes per session. "
        "This may indicate shallow engagement or under-supported study time."
    )
    return weakest


def best_day_analysis(records: list[StudySession]) -> AnalyticsV2Result:
    """Find the weekday with the highest total logged study time."""
    if not records:
        return {
            "weekday": None,
            "minutes": 0,
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


def generate_recommendations(records: list[StudySession]) -> list[str]:
    """Generate decision-support recommendations from analytics rules."""
    if not records:
        return ["Start by logging one week of study sessions to unlock guidance."]

    recommendations: list[str] = []
    productivity = productivity_score(records)
    trend = trend_detection(records)
    balance = study_balance_score(records)
    weak_subject = weak_subject_analysis(records)

    if balance["score"] < 60:
        recommendations.append("Try distributing study more evenly across subjects.")
    if trend["status"] == "improving":
        recommendations.append("Your consistency is improving; keep the current rhythm.")
    elif trend["status"] == "declining":
        recommendations.append("Your study time is declining; schedule a recovery week.")
    if productivity["active_days"] < 4:
        recommendations.append("Aim for at least four active study days this week.")
    if weak_subject["subject"]:
        recommendations.append(
            f"Give {weak_subject['subject']} a longer focused session next."
        )
    if not recommendations:
        recommendations.append("Your study behavior looks balanced; maintain the pattern.")

    return recommendations


def intelligent_dashboard(records: list[StudySession]) -> AnalyticsV2Result:
    """Return the full decision-support payload for the dashboard."""
    return {
        "productivity": productivity_score(records),
        "trend": trend_detection(records),
        "weak_subject": weak_subject_analysis(records),
        "best_day": best_day_analysis(records),
        "balance": study_balance_score(records),
        "recommendations": generate_recommendations(records),
        "daily_totals": total_study_time_per_day(records),
        "subject_totals": total_study_time_by_subject(records),
    }
