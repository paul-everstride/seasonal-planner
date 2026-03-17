from __future__ import annotations

import io
import os

from flask import Flask, jsonify, request, send_file

from generate_plan import create_season_plan
from planner import build_plan_context


app = Flask(__name__)


@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as html_file:
        return html_file.read()


@app.route("/dashboard")
def dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as html_file:
        return html_file.read()


@app.route("/preview", methods=["POST"])
def preview():
    data = request.get_json()
    context = build_plan_context(data)
    return jsonify(context)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    excel_bytes = create_season_plan(data)
    return send_file(
        io.BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"SeasonPlan_{data['riderLast']}_{data['year']}.xlsx",
    )


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", "5002")))
