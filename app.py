from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
import time
import urllib.parse

from flask import Flask, jsonify, request, send_file
from supabase import create_client

from generate_plan import create_season_plan
from planner import build_plan_context


app = Flask(__name__)

# Reject oversized request bodies (denial-of-wallet / OOM protection).
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB

# ── Supabase client ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Shared secret used to verify signed access tokens minted by the Everstride app.
# When set, the data endpoints REQUIRE a valid token and derive the coach id from
# it (so a caller can only ever touch their own data). When unset, the endpoints
# fall back to the legacy query-param behaviour so nothing breaks before the
# secret is configured in Railway — set the SAME value on the Everstride service
# and here to turn authentication on.
PLANNER_SHARED_SECRET = os.environ.get("PLANNER_SHARED_SECRET", "")


def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Auth ─────────────────────────────────────────────────────────────────────

def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def verify_token(token: str) -> str | None:
    """Verify an Everstride-issued token and return the coach_id, or None.

    Token format: base64url(json_payload) + "." + base64url(hmac_sha256).
    Payload: {"coach_id": "...", "exp": <unix_seconds>}.
    """
    if not PLANNER_SHARED_SECRET or not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    expected = hmac.new(PLANNER_SHARED_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    try:
        provided = _b64url_decode(sig)
    except Exception:
        return None
    if not hmac.compare_digest(expected, provided):
        return None
    try:
        payload = json.loads(_b64url_decode(body))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if float(payload.get("exp", 0)) < time.time():
        return None
    coach_id = payload.get("coach_id")
    return coach_id if isinstance(coach_id, str) and coach_id else None


def _extract_token() -> str:
    return (
        request.args.get("token")
        or request.headers.get("X-Everstride-Token", "")
        or (request.get_json(silent=True) or {}).get("token", "")
    )


def authenticated_coach_id() -> tuple[str | None, tuple | None]:
    """Return (coach_id, error_response). coach_id derives from a verified token
    when a shared secret is configured; otherwise falls back to the query param."""
    if PLANNER_SHARED_SECRET:
        coach_id = verify_token(_extract_token())
        if not coach_id:
            return None, (jsonify({"error": "Unauthorized"}), 401)
        return coach_id, None
    # Legacy fallback (no secret configured yet) — trust the query param.
    return request.args.get("coach_id"), None


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as html_file:
        return html_file.read()


@app.route("/dashboard")
def dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as html_file:
        return html_file.read()


# ── Planner API (no stored data — operates only on the caller's own payload) ──

@app.route("/preview", methods=["POST"])
def preview():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400
    try:
        context = build_plan_context(data)
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid plan data: {e}"}), 400
    return jsonify(context)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400
    if "riderLast" not in data or "year" not in data:
        return jsonify({"error": "Missing riderLast or year"}), 400
    try:
        excel_bytes = create_season_plan(data)
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid plan data: {e}"}), 400
    # Sanitize the filename so user input can't inject response headers.
    safe_last = urllib.parse.quote(str(data["riderLast"]), safe="")[:64] or "athlete"
    safe_year = urllib.parse.quote(str(data["year"]), safe="")[:8]
    return send_file(
        io.BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"SeasonPlan_{safe_last}_{safe_year}.xlsx",
    )


# ── Everstride integration API (authenticated, coach-scoped) ─────────────────

@app.route("/api/athletes", methods=["GET"])
def get_athletes():
    """Return athletes belonging to the authenticated coach."""
    coach_id, err = authenticated_coach_id()
    if err:
        return err
    if not coach_id:
        return jsonify([])

    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500

    teams_resp = sb.table("teams").select("id").eq("coach_id", coach_id).execute()
    team_ids = [t["id"] for t in (teams_resp.data or [])]
    if not team_ids:
        return jsonify([])

    athletes_resp = (
        sb.table("team_athletes")
        .select("ow_user_id, athlete_name, athlete_email")
        .in_("team_id", team_ids)
        .execute()
    )

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
    """Save or update a season plan for the authenticated coach."""
    coach_id, err = authenticated_coach_id()
    if err:
        return err

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400

    # coach_id always comes from the verified token when auth is on; the body
    # value (legacy) is only used as a fallback when no secret is configured.
    coach_id = coach_id or data.get("coach_id")
    if not coach_id:
        return jsonify({"error": "Unauthorized"}), 401

    required = ["athlete_ow_id", "athlete_name", "season_year",
                "season_start", "season_end", "plan_data", "form_payload"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500

    row = {
        "coach_id": coach_id,
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
    """Load an existing season plan for the authenticated coach."""
    coach_id, err = authenticated_coach_id()
    if err:
        return err

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
        try:
            query = query.eq("season_year", int(year))
        except ValueError:
            return jsonify({"error": "Invalid year"}), 400
    else:
        query = query.order("season_year", desc=True).limit(1)

    resp = query.execute()

    if resp.data:
        return jsonify(resp.data[0])
    return jsonify(None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=int(os.environ.get("PORT", "5002")))
