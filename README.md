# Study Tracker V3: AI Study Analytics System

Study Tracker V3 is a Flask + SQLite web application that helps students
understand and improve study behavior through computational analytics. The
project has evolved from a study logging tool into an AI-style decision-support
system that converts daily study records into scores, trends, behavioral
patterns, and practical recommendations.

![AI Study Analytics Dashboard](docs/screenshots/dashboard.png)

## Problem Statement

Students often know how long they studied, but they do not always know whether
their study behavior is healthy, balanced, or improving. A raw list of study
sessions does not clearly answer questions such as:

- Is my weekly study consistency improving or declining?
- Am I over-focusing on one subject while ignoring another?
- Which subject appears weakest based on logged engagement?
- Is my study distribution balanced across subjects?
- What should I adjust next week?

Study Tracker V3 addresses this problem by transforming study logs into
interpretable analytics and recommendation messages.

## Why This Project Exists

This project demonstrates how a small, well-scoped software system can support
student decision-making. Instead of adding many unrelated features, it focuses
on a clear academic productivity problem: helping a student reflect on study
behavior using structured data, algorithms, visualizations, and a clean web
interface.

The result is suitable for an IB CAS portfolio, a Computer Science project, or
a university application portfolio because it shows database design, backend
engineering, data analysis, visualization, testing, and user-centered product
thinking in one coherent system.

## System Architecture

```text
Flask web application
    |
    |-- app.py              Routes, form handling, flash messages, redirects
    |-- models.py           SQLite schema, validation, safe parameterized queries
    |-- analytics.py        Basic statistics and backward-compatible summaries
    |-- study_insights.py   V3 insight engine and recommendation logic
    |-- analytics_v2.py     Compatibility facade for older V2 imports
    |-- charts.py           Matplotlib chart generation saved to static/charts/
    |
HTML templates + CSS
    |
SQLite local database
```

## Key Features

- Add study records with subject, duration, and date
- Store records locally in SQLite with a defined schema
- Validate form input before database insertion
- View recent records in a responsive table
- Calculate daily, weekly, and monthly study totals
- Calculate average daily study time and current streak
- Generate charts for daily trends, weekly totals, and subject distribution
- Display a dashboard with productivity score, trends, balance, weak areas, and recommendations

## Insight Engine

The V3 insight engine lives in `src/study_tracker/study_insights.py`. It is
rule-based and explainable, which makes the output easy to understand and
debug.

The engine calculates:

- **Productivity Score**: a 0-100 score based on weekly consistency, total study
  time, and subject distribution balance.
- **Trend Analysis**: compares the latest 7 days with the previous 7 days and
  classifies behavior as improving, stable, or declining.
- **Weak Area Detection**: identifies the least productive subject based on
  logged engagement and average session length.
- **Behavioral Pattern Analysis**: detects imbalanced study distribution and
  over-focus on one subject.
- **Weekly Insight Report**: returns a structured dictionary used by the
  dashboard to display metrics and recommendation messages.

Example recommendation messages:

- "Your study pattern is imbalanced."
- "You are improving consistently; keep the current rhythm."
- "Consider redistributing study time across subjects."

## Demo Screens

| Records | Statistics | Charts |
| --- | --- | --- |
| ![Records page](docs/screenshots/records.png) | ![Statistics dashboard](docs/screenshots/statistics.png) | ![Chart dashboard](docs/screenshots/charts.png) |

## Tech Stack

- Python
- Flask
- SQLite
- matplotlib
- HTML/CSS
- pytest

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

SQLite is included with Python, so it does not need to be installed with pip.

## Main Routes

- `/` - AI study analytics dashboard
- `/dashboard` - same decision-support dashboard
- `/records` - add and view study records
- `/statistics` - detailed statistical summaries
- `/charts` - generated matplotlib charts

## Project Structure

```text
study-tracker/
├── app.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── docs/
│   └── screenshots/
├── src/
│   └── study_tracker/
│       ├── app.py
│       ├── models.py
│       ├── analytics.py
│       ├── study_insights.py
│       ├── analytics_v2.py
│       ├── charts.py
│       ├── init_db.py
│       ├── static/
│       └── templates/
└── tests/
```

## Learning Outcomes

This project demonstrates:

- Modular Flask application design
- SQLite schema design and safe SQL queries
- Input validation and error handling
- Separation of persistence, analytics, visualization, and presentation layers
- Algorithmic thinking through scoring, trend classification, and balance analysis
- Matplotlib chart generation for web applications
- Automated testing with pytest
- Documentation and release management for a portfolio-ready project
