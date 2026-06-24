# Study Tracker Architecture

## Folder Structure

```text
study-tracker/
├── data/
│   └── .gitkeep
├── src/
│   └── study_tracker/
│       ├── app.py
│       ├── analytics.py
│       ├── analytics_v2.py
│       ├── study_insights.py
│       ├── charts.py
│       ├── init_db.py
│       ├── models.py
│       ├── static/
│       │   ├── charts/
│       │   │   └── .gitkeep
│       │   └── styles.css
│       └── templates/
│           ├── base.html
│           ├── charts.html
│           ├── dashboard.html
│           ├── index.html
│           └── statistics.html
├── tests/
├── ARCHITECTURE.md
├── pyproject.toml
└── README.md
```

## Main Files

- `src/study_tracker/app.py`: Flask entry point, routes, form handling, redirects, and flash messages.
- `src/study_tracker/models.py`: SQLite database schema, initialization, safe inserts, and safe queries.
- `src/study_tracker/analytics.py`: Basic statistics logic for daily totals, weekly totals, monthly totals, average daily study time, and streaks.
- `src/study_tracker/study_insights.py`: V3 insight engine for productivity scoring, trend analysis, weak area detection, behavioral pattern analysis, balance scoring, and recommendations.
- `src/study_tracker/analytics_v2.py`: Compatibility facade that preserves older V2 imports while delegating advanced analytics to `study_insights.py`.
- `src/study_tracker/charts.py`: Matplotlib chart generation for daily trend, weekly total, and subject distribution.
- `src/study_tracker/init_db.py`: Command-line database initialization script.
- `src/study_tracker/templates/`: HTML pages for records, statistics, and charts.
- `src/study_tracker/static/styles.css`: Responsive CSS for the web UI.
- `src/study_tracker/static/charts/`: Generated PNG chart output directory.

## Data Model

SQLite table: `study_records`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `INTEGER` | Primary key, auto-incrementing |
| `date` | `TEXT` | ISO date string, `YYYY-MM-DD` |
| `subject` | `TEXT` | Required subject name |
| `minutes` | `INTEGER` | Required positive study duration |

## Design Notes

The project uses a small modular Flask architecture:

- `app.py` owns web routing and user experience.
- `models.py` owns persistence and hides raw SQL behind functions.
- `analytics.py` keeps stable summary statistics for existing views and tests.
- `study_insights.py` turns raw study logs into decision-support signals.
- `charts.py` turns analytics dictionaries into PNG files.

The dashboard is intentionally rule-based rather than AI-generated. This keeps
the system explainable: every recommendation can be traced back to study
consistency, total time, subject balance, trend movement, or weekday behavior.

SQLite is used instead of CSV for the production version because it provides a
real schema, primary keys, safe parameterized queries, and better long-term
growth while remaining local and simple.
