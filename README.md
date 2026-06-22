# Study Tracker

A polished Flask web application for tracking study time. It stores study records
locally in SQLite, calculates useful statistics, and generates matplotlib charts.

## Features

- Add study records with subject, minutes, and date
- Store data in a local SQLite database
- View recent records in a table
- View statistics in dashboard cards
- Generate PNG charts with matplotlib
- Mobile-friendly Flask web UI

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

`sqlite3` is included with Python, so it does not need to be installed with pip.
If installing packages manually, use:

```bash
pip install flask matplotlib
```

## Run

Initialize the database:

```bash
study-tracker-init-db
```

Start the web app:

```bash
study-tracker-web
```

Then open `http://127.0.0.1:5000`.

By default, the database is stored at `data/study_tracker.db`. To use another
database file:

```bash
STUDY_TRACKER_DATABASE_FILE=/path/to/study_tracker.db study-tracker-web
```

## Pages

- Records: Add a study record and view recent records
- Statistics: Total time, average study time, streak, weekly totals, monthly totals
- Charts: Daily trend, weekly totals, and subject distribution charts

## Project Layout

```text
study-tracker/
├── data/
│   └── .gitkeep
├── src/
│   └── study_tracker/
│       ├── app.py
│       ├── analytics.py
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
│           ├── index.html
│           └── statistics.html
├── tests/
├── ARCHITECTURE.md
├── pyproject.toml
└── README.md
```
