from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from study_tracker.analytics import summary_statistics
from study_tracker.models import (
    DEFAULT_DATABASE_FILE,
    add_study_record,
    get_all_records,
    init_db,
)


def try_generate_charts(records, output_dir: Path) -> list[dict[str, str]]:
    """Generate charts if matplotlib is installed."""
    try:
        from study_tracker.charts import generate_all_charts
    except ModuleNotFoundError:
        return []
    return generate_all_charts(records, output_dir)


def create_app(database_file: Path | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = os.environ.get("STUDY_TRACKER_SECRET_KEY", "study-tracker-dev")
    app.config["DATABASE_FILE"] = database_file or Path(
        os.environ.get("STUDY_TRACKER_DATABASE_FILE", DEFAULT_DATABASE_FILE)
    )
    app.config["CHART_OUTPUT_DIR"] = Path(app.static_folder or "static") / "charts"
    init_db(app.config["DATABASE_FILE"])

    @app.get("/")
    def index():
        records = get_all_records(app.config["DATABASE_FILE"])
        return render_template(
            "index.html",
            records=records,
            today=date.today().isoformat(),
        )

    @app.post("/add", endpoint="add")
    def add_record_route():
        subject = request.form.get("subject", "").strip()
        minutes_text = request.form.get("minutes", "").strip()
        date_text = request.form.get("study_date", "").strip()

        try:
            minutes = int(minutes_text)
            study_date = date.fromisoformat(date_text)
            add_study_record(
                app.config["DATABASE_FILE"],
                study_date,
                subject,
                minutes,
            )
        except ValueError as error:
            flash(f"Could not add record: {error}", "error")
            return redirect(url_for("index"))

        try_generate_charts(
            get_all_records(app.config["DATABASE_FILE"]),
            app.config["CHART_OUTPUT_DIR"],
        )
        flash("Study record added successfully.", "success")
        return redirect(url_for("index"))

    @app.get("/statistics")
    def statistics():
        records = get_all_records(app.config["DATABASE_FILE"])
        return render_template("statistics.html", stats=summary_statistics(records))

    @app.get("/charts")
    def charts():
        records = get_all_records(app.config["DATABASE_FILE"])
        chart_files = try_generate_charts(records, app.config["CHART_OUTPUT_DIR"])
        if not chart_files:
            flash("Install matplotlib to generate charts.", "error")
        return render_template("charts.html", charts=chart_files)

    return app


def main() -> int:
    app = create_app()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
