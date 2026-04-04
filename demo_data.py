"""
Demo data for the Everstride Season Planner.
Provides mock athletes and pre-built season plan payloads
that match the demo Everstride frontend (6 athletes).
"""

from __future__ import annotations

from datetime import date, timedelta

# ── Helpers ─────────────────────────────────────────────────────────────────

def _monday_of(d: date) -> date:
    """Return the Monday of the week containing *d*."""
    return d - timedelta(days=d.weekday())


def _season_dates() -> tuple[str, str]:
    """Return season start/end anchored ~10 weeks before today,
    matching the Everstride frontend's buildDemoSeasonPlan logic."""
    today = date.today()
    start = _monday_of(today - timedelta(weeks=10))
    # 22-week season (same as frontend DEMO_PHASES total)
    end = start + timedelta(weeks=22) - timedelta(days=1)
    return start.isoformat(), end.isoformat()


def _race_date(weeks_from_start: int, start_str: str) -> str:
    """Compute a race date as a Sunday offset from season start."""
    start = date.fromisoformat(start_str)
    return (start + timedelta(weeks=weeks_from_start) - timedelta(days=1)).isoformat()


# ── Demo athletes ───────────────────────────────────────────────────────────

DEMO_COACH = {
    "id": "local-demo-user",
    "name": "Local Coach",
    "first": "Coach",
    "last": "Everstride",
}

DEMO_ATHLETES: list[dict] = []

def _build_athletes():
    """Build athlete list with season dates anchored to today."""
    season_start, season_end = _season_dates()
    year = date.today().year

    return [
        {
            "id": "demo-1",
            "name": "Lena Berger",
            "email": "lena.berger@mail.com",
            "team": "Endurance Squad",
            "payload": {
                "riderFirst": "Lena",
                "riderLast": "Berger",
                "coachFirst": DEMO_COACH["first"],
                "coachLast": DEMO_COACH["last"],
                "year": year,
                "seasonStartDate": season_start,
                "seasonEndDate": season_end,
                "mainRaces": [
                    {"name": "Ironman 70.3 Mallorca", "date": _race_date(19, season_start)},
                ],
                "secondaryRaces": [
                    {"name": "Sprint Tri — Zurich", "date": _race_date(10, season_start)},
                    {"name": "Olympic Tri — Lucerne", "date": _race_date(15, season_start)},
                ],
                "trainingCamps": [
                    {"name": "Altitude Camp — Livigno",
                     "date": _race_date(6, season_start),
                     "endDate": (date.fromisoformat(_race_date(6, season_start)) + timedelta(days=10)).isoformat()},
                ],
            },
        },
        {
            "id": "demo-2",
            "name": "Marco Silva",
            "email": "marco.silva@mail.com",
            "team": "Endurance Squad",
            "payload": {
                "riderFirst": "Marco",
                "riderLast": "Silva",
                "coachFirst": DEMO_COACH["first"],
                "coachLast": DEMO_COACH["last"],
                "year": year,
                "seasonStartDate": season_start,
                "seasonEndDate": season_end,
                "mainRaces": [
                    {"name": "Tour des Flandres GF", "date": _race_date(19, season_start)},
                ],
                "secondaryRaces": [
                    {"name": "Strade Bianche GF", "date": _race_date(11, season_start)},
                    {"name": "Amstel Gold GF", "date": _race_date(16, season_start)},
                ],
                "trainingCamps": [
                    {"name": "Spring Camp — Girona",
                     "date": _race_date(5, season_start),
                     "endDate": (date.fromisoformat(_race_date(5, season_start)) + timedelta(days=7)).isoformat()},
                ],
            },
        },
        {
            "id": "demo-3",
            "name": "Sophie Chen",
            "email": "sophie.chen@mail.com",
            "team": "Sprint Group",
            "payload": {
                "riderFirst": "Sophie",
                "riderLast": "Chen",
                "coachFirst": DEMO_COACH["first"],
                "coachLast": DEMO_COACH["last"],
                "year": year,
                "seasonStartDate": season_start,
                "seasonEndDate": season_end,
                "mainRaces": [
                    {"name": "Berlin Marathon", "date": _race_date(19, season_start)},
                ],
                "secondaryRaces": [
                    {"name": "Hamburg Half", "date": _race_date(10, season_start)},
                    {"name": "Copenhagen 10K", "date": _race_date(14, season_start)},
                ],
                "trainingCamps": [
                    {"name": "Altitude Camp — St. Moritz",
                     "date": _race_date(7, season_start),
                     "endDate": (date.fromisoformat(_race_date(7, season_start)) + timedelta(days=14)).isoformat()},
                ],
            },
        },
        {
            "id": "demo-4",
            "name": "Jonas Keller",
            "email": "jonas.keller@mail.com",
            "team": "Endurance Squad",
            "payload": {
                "riderFirst": "Jonas",
                "riderLast": "Keller",
                "coachFirst": DEMO_COACH["first"],
                "coachLast": DEMO_COACH["last"],
                "year": year,
                "seasonStartDate": season_start,
                "seasonEndDate": season_end,
                "mainRaces": [
                    {"name": "Maratona dles Dolomites", "date": _race_date(19, season_start)},
                ],
                "secondaryRaces": [
                    {"name": "Ötztaler Radmarathon Quali", "date": _race_date(12, season_start)},
                ],
                "trainingCamps": [
                    {"name": "Training Camp — Tenerife",
                     "date": _race_date(4, season_start),
                     "endDate": (date.fromisoformat(_race_date(4, season_start)) + timedelta(days=10)).isoformat()},
                ],
            },
        },
        {
            "id": "demo-5",
            "name": "Emma Larsson",
            "email": "emma.larsson@mail.com",
            "team": "Sprint Group",
            "payload": {
                "riderFirst": "Emma",
                "riderLast": "Larsson",
                "coachFirst": DEMO_COACH["first"],
                "coachLast": DEMO_COACH["last"],
                "year": year,
                "seasonStartDate": season_start,
                "seasonEndDate": season_end,
                "mainRaces": [
                    {"name": "European Track Championships", "date": _race_date(19, season_start)},
                ],
                "secondaryRaces": [
                    {"name": "Swedish Nationals 800m", "date": _race_date(11, season_start)},
                    {"name": "Diamond League — Stockholm", "date": _race_date(16, season_start)},
                ],
                "trainingCamps": [
                    {"name": "Speed Camp — Chula Vista",
                     "date": _race_date(8, season_start),
                     "endDate": (date.fromisoformat(_race_date(8, season_start)) + timedelta(days=12)).isoformat()},
                ],
            },
        },
        {
            "id": "demo-6",
            "name": "Tom Hartmann",
            "email": "tom.hartmann@mail.com",
            "team": "Sprint Group",
            "payload": {
                "riderFirst": "Tom",
                "riderLast": "Hartmann",
                "coachFirst": DEMO_COACH["first"],
                "coachLast": DEMO_COACH["last"],
                "year": year,
                "seasonStartDate": season_start,
                "seasonEndDate": season_end,
                "mainRaces": [
                    {"name": "Cyclassics Hamburg", "date": _race_date(19, season_start)},
                ],
                "secondaryRaces": [
                    {"name": "Eschborn-Frankfurt GF", "date": _race_date(9, season_start)},
                    {"name": "Vätternrundan", "date": _race_date(15, season_start)},
                ],
                "trainingCamps": [
                    {"name": "Training Camp — Calpe",
                     "date": _race_date(5, season_start),
                     "endDate": (date.fromisoformat(_race_date(5, season_start)) + timedelta(days=7)).isoformat()},
                ],
            },
        },
    ]


def get_demo_athletes() -> list[dict]:
    """Return the list of demo athletes (simplified for /api/athletes)."""
    athletes = _build_athletes()
    return [{"id": a["id"], "name": a["name"], "email": a["email"]} for a in athletes]


def get_demo_athlete_payload(athlete_id: str) -> dict | None:
    """Return the full form payload for a demo athlete, or None if not found."""
    athletes = _build_athletes()
    for a in athletes:
        if a["id"] == athlete_id:
            return a["payload"]
    return None


def get_demo_athlete(athlete_id: str) -> dict | None:
    """Return full demo athlete record, or None."""
    athletes = _build_athletes()
    for a in athletes:
        if a["id"] == athlete_id:
            return a
    return None
