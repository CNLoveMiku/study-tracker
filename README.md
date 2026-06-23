# Study Tracker

**Study Tracker** is a Flask + SQLite web application that helps students record
daily study time, understand their study habits, and turn raw revision logs into
clear statistics and charts.

I built this project because many students know they are "studying a lot" but do
not have evidence of where their time goes. Study Tracker solves that by making
study behavior visible: it records each session, calculates consistency metrics,
and shows which subjects are receiving the most attention.

![Study Tracker records page](docs/screenshots/records.png)

## Demo

| Statistics dashboard | Chart dashboard |
| --- | --- |
| ![Statistics dashboard](docs/screenshots/statistics.png) | ![Chart dashboard](docs/screenshots/charts.png) |

## What It Does

- Records study sessions with date, subject, and minutes studied
- Stores records locally in SQLite with a clear schema
- Shows recent records in a clean table
- Calculates daily, weekly, and monthly totals
- Identifies the most studied subject
- Calculates average daily study time and current study streak
- Generates interpretation-style insights, not only raw numbers
- Creates matplotlib PNG charts for trends and subject distribution

## Why It Matters

This project is designed as a portfolio-level student productivity tool. It
demonstrates:

- backend development with Flask
- database design with SQLite
- safe parameterized SQL queries
- data analysis with Python
- chart generation with matplotlib
- responsive frontend design with HTML and CSS

For an IB CAS or Computer Science portfolio, the app shows a complete cycle:
identify a real student problem, collect data, analyze patterns, and present
useful feedback through a web interface.

## Data Insights

The statistics page does more than list totals. It explains:

- which subject is receiving the most attention
- how much time is studied on an average active day
- whether the student is building a consistent study streak
- which week had the strongest study performance

These insights make the project more useful than a simple time log.

## Tech Stack

- Python
- Flask
- SQLite
- matplotlib
- HTML/CSS

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`sqlite3` is included with Python, so it does not need a separate pip install.

## Run

Initialize the database:

```bash
python -m study_tracker.init_db
```

Start the web app:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
study-tracker/
├── app.py
├── requirements.txt
├── data/
│   └── .gitkeep
├── docs/
│   └── screenshots/
├── src/
│   └── study_tracker/
│       ├── app.py          # Flask routes and app factory
│       ├── models.py       # SQLite schema and database functions
│       ├── analytics.py    # Statistics and insight logic
│       ├── charts.py       # matplotlib chart generation
│       ├── init_db.py      # Database initialization command
│       ├── static/
│       │   ├── charts/
│       │   └── styles.css
│       └── templates/
│           ├── base.html
│           ├── index.html
│           ├── statistics.html
│           └── charts.html
└── tests/
```

## Database Schema

```sql
CREATE TABLE study_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    subject TEXT NOT NULL,
    minutes INTEGER NOT NULL CHECK (minutes > 0)
);
```

## Routes

- `/` - add records and view recent study sessions
- `/statistics` - view totals, streaks, averages, and insights
- `/charts` - view generated matplotlib charts

## Future Improvements

- Add user accounts for multiple students
- Export records to CSV
- Add goal tracking by subject
- Add filters by date range
