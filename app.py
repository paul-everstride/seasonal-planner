from __future__ import annotations

import io
import os

from flask import Flask, jsonify, request, send_file
from supabase import create_client

from generate_plan import create_season_plan
from planner import build_plan_context


app = Flask(__name__)

# ── Supabase client ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as html_file:
        return html_file.read()


@app.route("/dashboard")
def dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as html_file:
        return html_file.read()


# ── Planner API ──────────────────────────────────────────────────────────────

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


# ── Everstride integration API ──────────────────────────────────────────────

@app.route("/api/athletes", methods=["GET"])
def get_athletes():
    """Return athletes belonging to a coach (by Supabase auth user ID)."""
    coach_id = request.args.get("coach_id")
    if not coach_id:
        return jsonify([])

    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500

    # Get teams for this coach
    teams_resp = sb.table("teams").select("id").eq("coach_id", coach_id).execute()
    team_ids = [t["id"] for t in (teams_resp.data or [])]
    if not team_ids:
        return jsonify([])

    # Get athletes from those teams
    athletes_resp = (
        sb.table("team_athletes")
        .select("ow_user_id, athlete_name, athlete_email")
        .in_("team_id", team_ids)
        .execute()
    )

    # Deduplicate by ow_user_id (athlete could be in multiple teams)
    seen = set()
    athletes = []
    for a in athletes_resp.data or []:
        if a["ow_user_id"] not in seen:
            seen.add(a["ow_user_id"])
            athletes.append({
                "id": a["ow_user_id"],
                "name": a.get("athlete_name") or "Unnamed Athlete",
                "email": a.get("athlete_email") or "",
            })

    return jsonify(athletes)


@app.route("/api/save-plan", methods=["POST"])
def save_plan():
    """Save or update a season plan in Supabase."""
    data = request.get_json()
    required = ["coach_id", "athlete_ow_id", "athlete_name", "season_year",
                "season_start", "season_end", "plan_data", "form_payload"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500

    row = {
        "coach_id": data["coach_id"],
        "athlete_ow_id": data["athlete_ow_id"],
        "athlete_name": data["athlete_name"],
        "season_year": data["season_year"],
        "season_start": data["season_start"],
        "season_end": data["season_end"],
        "plan_data": data["plan_data"],
        "form_payload": data["form_payload"],
        "updated_at": "now()",
    }

    resp = (
        sb.table("season_plans")
        .upsert(row, on_conflict="coach_id,athlete_ow_id,season_year")
        .execute()
    )

    if resp.data:
        return jsonify({"success": True, "id": resp.data[0].get("id")})
    return jsonify({"error": "Failed to save"}), 500


@app.route("/api/load-plan", methods=["GET"])
def load_plan():
    """Load an existing season plan."""
    coach_id = request.args.get("coach_id")
    athlete_id = request.args.get("athlete_id")
    year = request.args.get("year")

    if not coach_id or not athlete_id:
        return jsonify({"error": "Missing coach_id or athlete_id"}), 400

    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500

    query = (
        sb.table("season_plans")
        .select("*")
        .eq("coach_id", coach_id)
        .eq("athlete_ow_id", athlete_id)
    )
    if year:
        query = query.eq("season_year", int(year))
    else:
        query = query.order("season_year", desc=True).limit(1)

    resp = query.execute()

    if resp.data:
        return jsonify(resp.data[0])
    return jsonify(None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=int(os.environ.get("PORT", "5002")))
