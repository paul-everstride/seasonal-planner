from __future__ import annotations

import math
from datetime import date, datetime, timedelta

from dateutil import parser


PHASE_COLORS = {
    "Prep": (146, 208, 80),
    "Base 1": (0, 176, 240),
    "Base 2": (0, 112, 192),
    "Base 3": (0, 70, 127),
    "Build 1": (255, 217, 102),
    "Build 2": (255, 192, 0),
    "Peak": (255, 0, 255),
    "Taper": (255, 102, 0),
    "Race": (255, 0, 0),
    "Recovery": (189, 189, 189),
}

PRE_RACE_TEMPLATE = [
    {"phase": "Prep", "micro": "G P1", "volume": 1, "intensity": 1},
    {"phase": "Prep", "micro": "G P2", "volume": 1, "intensity": 1},
    {"phase": "Prep", "micro": "G P3", "volume": 2, "intensity": 1},
    {"phase": "Prep", "micro": "G P4", "volume": 2, "intensity": 2},
    {"phase": "Base 1", "micro": "RE", "volume": 2, "intensity": 1},
    {"phase": "Base 1", "micro": "G P5", "volume": 3, "intensity": 2},
    {"phase": "Base 1", "micro": "G P6", "volume": 3, "intensity": 2},
    {"phase": "Base 1", "micro": "TC 1", "volume": 3, "intensity": 3},
    {"phase": "Base 2", "micro": "TC 2", "volume": 3, "intensity": 2},
    {"phase": "Base 2", "micro": "RE 2", "volume": 4, "intensity": 2},
    {"phase": "Base 2", "micro": "G P8", "volume": 4, "intensity": 3},
    {"phase": "Base 2", "micro": "G P9", "volume": 4, "intensity": 3},
    {"phase": "Base 3", "micro": "GP10", "volume": 4, "intensity": 3},
    {"phase": "Base 3", "micro": "RE 3", "volume": 5, "intensity": 3},
    {"phase": "Base 3", "micro": "RE 3", "volume": 5, "intensity": 3},
    {"phase": "Base 3", "micro": "RE 4", "volume": 5, "intensity": 4},
    {"phase": "Build 1", "micro": "B1", "volume": 4, "intensity": 4},
    {"phase": "Build 1", "micro": "B2", "volume": 4, "intensity": 4},
    {"phase": "Build 1", "micro": "B3", "volume": 3, "intensity": 4},
    {"phase": "Build 1", "micro": "RE 5", "volume": 3, "intensity": 4},
    {"phase": "Build 2", "micro": "B5", "volume": 3, "intensity": 4},
    {"phase": "Build 2", "micro": "B6", "volume": 2, "intensity": 5},
    {"phase": "Build 2", "micro": "B7", "volume": 2, "intensity": 5},
    {"phase": "Build 2", "micro": "B8", "volume": 2, "intensity": 5},
]

INTER_RACE_TEMPLATE = [
    {"phase": "Base 2", "micro": "TC 2", "volume": 3, "intensity": 2},
    {"phase": "Base 2", "micro": "RE 2", "volume": 4, "intensity": 2},
    {"phase": "Base 2", "micro": "G P8", "volume": 4, "intensity": 3},
    {"phase": "Base 2", "micro": "G P9", "volume": 4, "intensity": 3},
    {"phase": "Base 3", "micro": "GP10", "volume": 4, "intensity": 3},
    {"phase": "Base 3", "micro": "RE 3", "volume": 5, "intensity": 3},
    {"phase": "Base 3", "micro": "RE 3", "volume": 5, "intensity": 3},
    {"phase": "Base 3", "micro": "RE 4", "volume": 5, "intensity": 4},
    {"phase": "Build 1", "micro": "B1", "volume": 4, "intensity": 4},
    {"phase": "Build 1", "micro": "B2", "volume": 4, "intensity": 4},
    {"phase": "Build 1", "micro": "B3", "volume": 3, "intensity": 4},
    {"phase": "Build 1", "micro": "RE 5", "volume": 3, "intensity": 4},
    {"phase": "Build 2", "micro": "B5", "volume": 3, "intensity": 4},
    {"phase": "Build 2", "micro": "B6", "volume": 2, "intensity": 5},
    {"phase": "Build 2", "micro": "B7", "volume": 2, "intensity": 5},
    {"phase": "Build 2", "micro": "B8", "volume": 2, "intensity": 5},
]

COMPETITION_TEMPLATE = [
    {"phase": "Peak", "micro": "P1", "volume": 4, "intensity": 4},
    {"phase": "Peak", "micro": "P2", "volume": 4, "intensity": 5},
    {"phase": "Taper", "micro": "TA PE R", "volume": 2, "intensity": 5},
    {"phase": "Race", "micro": "RACE", "volume": 1, "intensity": 5},
]

FOCUS_TEXT = {
    "Prep": "Prepare to train. Weights. General Athleticism. Cross Training",
    "Base 1": "General Training. Muscular Endurance. Aerobic Endurance.\nGetting used to long hours in the saddle. Work",
    "Base 2": "General Training. Muscular force. Speed skills. Aerobic endurance",
    "Base 3": "General Training. Muscular force. Speed skills. Aerobic endurance",
    "Build 1": "Specific Training. Anaerobic endurance, sprint power, maintain\naerobic endurance, muscular force and speed skills. Use some\nB-Races and stage races to build up fitness",
    "Build 2": "Specific Training. Anaerobic endurance, sprint power, maintain\naerobic endurance, muscular force and speed skills. Use some\nB-Races and stage races to build up fitness",
    "Peak": "Short Intervals at race intensity recovery in between races\nor race blocks. Maintain Fitness",
    "Taper": "Reduce fatigue and stay sharp. Be race ready. Maintain Fitness",
    "Race": "Short Intervals at race intensity recovery in between races\nor race blocks. Maintain Fitness. Towards the end of the\ncompetition phase have some longer rides to prepare worlds\nand get used to long distance",
    "Recovery": "Rest and recovery",
}

GOAL_TEXT_BY_MACRO = {
    "General Preparation": "Improve overall fitness. Build up aerobic endurance, increase FTP,\nIncrease power. Create stable foundation to work from in order to\nprevent injuries. Create strong support system for prime movers\nwhile on the bike.",
    "Pre-Competition": "Increase cycling abilities to become more efficient to the demands\nof the events to come up. Shift the focus towards specific\nperformance goals. Improve anaerobic capacities to be able to\ncomplete repeated short high power spikes and sustained power\nintervals",
    "Competition": "Reduce fatigue and stay sharp. Be race ready. Maintain Fitness",
    "Transition": "Recover physically and mentally. Reload the batteries",
}


def rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "".join(f"{value:02X}" for value in rgb)


def parse_date(value: str | date | datetime) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return parser.parse(value).date()


def monday_of_week(value: date) -> date:
    return value - timedelta(days=value.weekday())


def week_index_for_date(target: date, week_starts: list[date]) -> int | None:
    if not week_starts:
        return None
    monday = monday_of_week(target)
    try:
        return week_starts.index(monday) + 1
    except ValueError:
        return None


def normalize_event_list(items: list[dict], limit: int) -> list[dict]:
    normalized = []
    for item in items[:limit]:
        name = str(item.get("name", "")).strip()
        raw_date = item.get("date")
        if not name or not raw_date:
            continue
        entry: dict = {"name": name, "date": parse_date(raw_date)}
        raw_end = item.get("endDate")
        if raw_end:
            try:
                entry["endDate"] = parse_date(raw_end).isoformat()
            except Exception:
                pass
        normalized.append(entry)
    return normalized


def sample_template(template: list[dict], length: int) -> list[dict]:
    if length <= 0:
        return []
    if not template:
        return [{"phase": "Recovery", "micro": f"R{i + 1}", "volume": 1, "intensity": 1} for i in range(length)]

    sampled = []
    template_length = len(template)
    for index in range(length):
        template_index = min(math.ceil((index + 1) * template_length / length) - 1, template_length - 1)
        sampled.append(template[template_index].copy())
    return sampled


def assign_template_segment(plan: list[dict], start_week: int, template_items: list[dict]) -> None:
    for offset, template_item in enumerate(template_items):
        week_number = start_week + offset
        plan[week_number - 1]["phase"] = template_item["phase"]
        plan[week_number - 1]["micro"] = template_item["micro"]
        plan[week_number - 1]["volume"] = template_item["volume"]
        plan[week_number - 1]["intensity"] = template_item["intensity"]


def cluster_race_weeks(race_weeks: list[int], gap: int = 2) -> list[tuple[int, int]]:
    """Group race weeks within `gap` weeks of each other; return (first, last) of each cluster."""
    if not race_weeks:
        return []
    sorted_weeks = sorted(set(race_weeks))
    clusters: list[list[int]] = []
    cluster = [sorted_weeks[0]]
    for week in sorted_weeks[1:]:
        if week - cluster[-1] <= gap:
            cluster.append(week)
        else:
            clusters.append(cluster)
            cluster = [week]
    clusters.append(cluster)
    return [(min(c), max(c)) for c in clusters]


def build_phase_week_data(total_weeks: int, race_spans: list[tuple[int, int]]) -> list[dict]:
    phase_week_data = [{"week": week, "phase": None, "micro": None, "volume": None, "intensity": None} for week in range(1, total_weeks + 1)]
    if total_weeks <= 0:
        return phase_week_data

    sorted_spans = sorted(
        [(f, l) for f, l in race_spans if 1 <= f <= total_weeks],
        key=lambda x: x[0],
    )
    if not sorted_spans:
        assign_template_segment(phase_week_data, 1, sample_template(PRE_RACE_TEMPLATE, total_weeks))
        return phase_week_data

    cursor = 1
    previous_last_week: int | None = None

    for first_week, last_week in sorted_spans:
        # Build the Peak/Taper/Race lead-in ending at first_week
        competition_start = max(cursor, first_week - 3)
        if cursor <= competition_start - 1:
            open_length = competition_start - cursor
            if previous_last_week is None:
                assign_template_segment(phase_week_data, cursor, sample_template(PRE_RACE_TEMPLATE, open_length))
            else:
                phase_week_data[cursor - 1]["phase"] = "Recovery"
                phase_week_data[cursor - 1]["micro"] = "R1"
                phase_week_data[cursor - 1]["volume"] = 1
                phase_week_data[cursor - 1]["intensity"] = 1
                remaining_length = open_length - 1
                if remaining_length > 0:
                    assign_template_segment(
                        phase_week_data,
                        cursor + 1,
                        sample_template(INTER_RACE_TEMPLATE, remaining_length),
                    )

        competition_block = COMPETITION_TEMPLATE[-(first_week - competition_start + 1):]
        assign_template_segment(phase_week_data, competition_start, competition_block)

        # Extend Race phase across all weeks of the span (first_week already set to Race above)
        for span_week in range(first_week + 1, min(last_week, total_weeks) + 1):
            phase_week_data[span_week - 1]["phase"] = "Race"
            phase_week_data[span_week - 1]["micro"] = "RACE"
            phase_week_data[span_week - 1]["volume"] = 1
            phase_week_data[span_week - 1]["intensity"] = 5

        previous_last_week = last_week
        cursor = last_week + 1

    if cursor <= total_weeks:
        recovery_index = 1
        for week_number in range(cursor, total_weeks + 1):
            phase_week_data[week_number - 1]["phase"] = "Recovery"
            phase_week_data[week_number - 1]["micro"] = f"R{recovery_index}"
            phase_week_data[week_number - 1]["volume"] = 1
            phase_week_data[week_number - 1]["intensity"] = 1
            recovery_index += 1

    for item in phase_week_data:
        if item["phase"] is None:
            item["phase"] = "Recovery"
        if item["micro"] is None:
            item["micro"] = "R1"
        if item["volume"] is None:
            item["volume"] = 1
        if item["intensity"] is None:
            item["intensity"] = 1

    return phase_week_data


def phase_ranges(phase_week_data: list[dict]) -> list[tuple[str, int, int]]:
    if not phase_week_data:
        return []

    ranges = []
    current_phase = phase_week_data[0]["phase"]
    start = 1

    for item in phase_week_data[1:]:
        if item["phase"] != current_phase:
            ranges.append((current_phase, start, item["week"] - 1))
            current_phase = item["phase"]
            start = item["week"]

    ranges.append((current_phase, start, phase_week_data[-1]["week"]))
    return ranges


def macro_name_for_phase(phase_name: str) -> str:
    if phase_name in {"Prep", "Base 1", "Base 2", "Base 3"}:
        return "General Preparation"
    if phase_name in {"Build 1", "Build 2"}:
        return "Pre-Competition"
    if phase_name in {"Peak", "Taper", "Race"}:
        return "Competition"
    return "Transition"


def macro_ranges(phase_week_data: list[dict]) -> list[tuple[str, int, int]]:
    if not phase_week_data:
        return []

    ranges = []
    current_macro = macro_name_for_phase(phase_week_data[0]["phase"])
    start = 1

    for item in phase_week_data[1:]:
        macro_name = macro_name_for_phase(item["phase"])
        if macro_name != current_macro:
            ranges.append((current_macro, start, item["week"] - 1))
            current_macro = macro_name
            start = item["week"]

    ranges.append((current_macro, start, phase_week_data[-1]["week"]))
    return ranges


def assign_micro_cycles(plan_weeks: list[dict], week_overrides: dict | None = None) -> None:
    overrides = week_overrides or {}
    gp_counter = 1
    build_counter = 1
    recovery_counter = 1
    peak_counter = 1
    training_since_recovery = 0
    previous_phase = None

    for week in plan_weeks:
        override = overrides.get(str(week["week"])) or overrides.get(week["week"]) or {}
        phase_name = week["phase"]

        if phase_name != previous_phase:
            peak_counter = 1
        previous_phase = phase_name

        micro_type = override.get("microType")
        if not micro_type:
            if phase_name in {"Prep", "Base 1", "Base 2", "Base 3"}:
                if training_since_recovery >= 4:
                    micro_type = "Recovery"
                else:
                    micro_type = "General"
            elif phase_name in {"Build 1", "Build 2"}:
                if training_since_recovery >= 4:
                    micro_type = "Recovery"
                else:
                    micro_type = "Build"
            elif phase_name == "Peak":
                micro_type = "Peak"
            elif phase_name == "Taper":
                micro_type = "Taper"
            elif phase_name == "Race":
                micro_type = "Race"
            else:
                micro_type = "Recovery"

        week["microType"] = micro_type

        if micro_type == "Recovery":
            week["micro"] = f"Re{recovery_counter}"
            recovery_counter += 1
            if phase_name in {"Prep", "Base 1", "Base 2", "Base 3", "Build 1", "Build 2"}:
                week["volume"] = max(1, min(week["volume"], 2))
                week["intensity"] = max(1, min(week["intensity"], 2))
            training_since_recovery = 0
        elif micro_type == "General":
            week["micro"] = f"GP{gp_counter}"
            gp_counter += 1
            training_since_recovery += 1
        elif micro_type == "Build":
            week["micro"] = f"B{build_counter}"
            build_counter += 1
            training_since_recovery += 1
        elif micro_type == "Peak":
            week["micro"] = f"P{peak_counter}"
            peak_counter += 1
        elif micro_type == "Taper":
            week["micro"] = "TAPER"
        elif micro_type == "Race":
            week["micro"] = "RACE"
        else:
            week["micro"] = str(micro_type)


def build_plan_context(data: dict) -> dict:
    rider_first = str(data["riderFirst"]).strip()
    rider_last = str(data["riderLast"]).strip()
    coach_first = str(data["coachFirst"]).strip()
    coach_last = str(data["coachLast"]).strip()
    year = int(data["year"])
    season_start = parse_date(data["seasonStartDate"])
    season_end = parse_date(data["seasonEndDate"])
    main_race_name = str(data.get("mainRaceName", "")).strip()
    main_race_date = data.get("mainRaceDate")
    main_races = normalize_event_list(data.get("mainRaces", []), 10)
    if not main_races and main_race_name and main_race_date:
        main_races = [{"name": main_race_name, "date": parse_date(main_race_date)}]

    secondary_races = normalize_event_list(data.get("secondaryRaces", data.get("additionalRaces", [])), 15)
    training_camps = normalize_event_list(data.get("trainingCamps", []), 15)
    week_overrides = data.get("weekOverrides", {})

    if season_end < season_start:
        raise ValueError("Season end date must be on or after the season start date.")

    week_1_monday = monday_of_week(season_start)
    season_end_monday = monday_of_week(season_end)
    week_starts = []
    current_monday = week_1_monday
    while current_monday <= season_end_monday:
        week_starts.append(current_monday)
        current_monday += timedelta(days=7)

    total_weeks = len(week_starts)
    main_race_entries = [{**{"name": race["name"], "date": race["date"], "type": "main_race"}, **({"endDate": race["endDate"]} if race.get("endDate") else {})} for race in main_races]
    secondary_race_entries = [{**{"name": race["name"], "date": race["date"], "type": "secondary_race"}, **({"endDate": race["endDate"]} if race.get("endDate") else {})} for race in secondary_races]
    training_camp_entries = [{**{"name": camp["name"], "date": camp["date"], "type": "training_camp"}, **({"endDate": camp["endDate"]} if camp.get("endDate") else {})} for camp in training_camps]
    all_events = main_race_entries + secondary_race_entries + training_camp_entries

    event_cells: dict[int, dict] = {}
    race_weeks = []
    for event in all_events:
        event_week = week_index_for_date(event["date"], week_starts)
        if event_week is None:
            continue
        # Determine the last week this event spans into (via endDate)
        end_week_idx = event_week
        if event.get("endDate"):
            try:
                end_date_obj = parse_date(event["endDate"])
                ew = week_index_for_date(end_date_obj, week_starts)
                if ew is not None and ew > event_week:
                    end_week_idx = ew
            except Exception:
                pass

        if event["type"] == "main_race":
            # All spanned weeks are race weeks so the schedule is built around the full span
            for w in range(event_week, end_week_idx + 1):
                race_weeks.append(w)

        evt_entry: dict = {
            "name": event["name"],
            "date": event["date"].isoformat(),
            "type": event["type"],
        }
        if event.get("endDate"):
            evt_entry["endDate"] = event["endDate"]

        for week_num in range(event_week, end_week_idx + 1):
            bucket = event_cells.setdefault(
                week_num,
                {
                    "events": [],
                    "names": [],
                    "has_main": False,
                    "has_secondary_race": False,
                    "has_training_camp": False,
                    "dates": [],
                },
            )
            bucket["events"].append(evt_entry)
            bucket["names"].append(event["name"])
            bucket["dates"].append(event["date"].isoformat())
            bucket["has_main"] = bucket["has_main"] or event["type"] == "main_race"
            bucket["has_secondary_race"] = bucket["has_secondary_race"] or event["type"] == "secondary_race"
            bucket["has_training_camp"] = bucket["has_training_camp"] or event["type"] == "training_camp"

    race_spans = cluster_race_weeks(race_weeks)
    plan_weeks = build_phase_week_data(total_weeks, race_spans)
    phase_blocks = phase_ranges(plan_weeks)
    macro_blocks = macro_ranges(plan_weeks)
    ftp_test_weeks = set()
    four_d_test_weeks = set()
    for phase_name, start_week, end_week in phase_blocks:
        if phase_name in {"Base 1", "Base 2"}:
            ftp_test_weeks.add(end_week)
        elif phase_name == "Peak":
            ftp_test_weeks.add(start_week)

        if phase_name in {"Build 1", "Build 2"}:
            four_d_test_weeks.add(end_week)

    for week in plan_weeks:
        monday = week_starts[week["week"] - 1]
        sunday = monday + timedelta(days=6)
        week["monday"] = monday.isoformat()
        week["sunday"] = sunday.isoformat()
        week["month"] = monday.strftime("%B")
        week["monthKey"] = monday.strftime("%Y-%m")
        week["day"] = monday.day
        week["weekRangeShort"] = f"{monday.strftime('%b')} {monday.day} - {sunday.strftime('%b')} {sunday.day}"
        week["weekRangeFull"] = f"{monday.strftime('%B')} {monday.day} to {sunday.strftime('%B')} {sunday.day}"
        event_bucket = event_cells.get(week["week"])
        week_events = event_bucket["events"] if event_bucket else []
        week["events"] = week_events
        week["races"] = [event["name"] for event in week_events if event["type"] in {"main_race", "secondary_race"}]
        week["trainingCamps"] = [event["name"] for event in week_events if event["type"] == "training_camp"]
        week["hasMainRace"] = event_bucket["has_main"] if event_bucket else False
        week["hasSecondaryRace"] = event_bucket["has_secondary_race"] if event_bucket else False
        week["hasTrainingCamp"] = event_bucket["has_training_camp"] if event_bucket else False
        week["mainRaceCount"] = sum(1 for e in week_events if e["type"] == "main_race")
        week["ftpTest"] = week["week"] in ftp_test_weeks
        week["fourDTest"] = week["week"] in four_d_test_weeks

    for week in plan_weeks:
        override = week_overrides.get(str(week["week"])) or week_overrides.get(week["week"])
        if override and "phase" in override and override["phase"] in PHASE_COLORS:
            week["phase"] = str(override["phase"])

    assign_micro_cycles(plan_weeks, week_overrides)

    for week in plan_weeks:
        override = week_overrides.get(str(week["week"])) or week_overrides.get(week["week"])
        week["macro"] = macro_name_for_phase(week["phase"])
        week["color"] = rgb_hex(PHASE_COLORS[week["phase"]])
        week["focusText"] = FOCUS_TEXT[week["phase"]]
        week["goalText"] = GOAL_TEXT_BY_MACRO[week["macro"]]

        if override:
            if "volume" in override:
                week["volume"] = max(1, min(5, int(override["volume"])))
            if "intensity" in override:
                week["intensity"] = max(1, min(5, int(override["intensity"])))
            if "ftpTest" in override:
                week["ftpTest"] = bool(override["ftpTest"])
            if "fourDTest" in override:
                week["fourDTest"] = bool(override["fourDTest"])
            if "focusText" in override and str(override["focusText"]).strip():
                week["focusText"] = str(override["focusText"]).strip()
            if "goalText" in override and str(override["goalText"]).strip():
                week["goalText"] = str(override["goalText"]).strip()

        week["tests"] = []
        if week["ftpTest"]:
            week["tests"].append("FTP")
        if week["fourDTest"]:
            week["tests"].append("4D")

    phase_blocks = phase_ranges(plan_weeks)
    macro_blocks = macro_ranges(plan_weeks)

    month_groups = []
    seen_months = set()
    for week in plan_weeks:
        if week["monthKey"] in seen_months:
            continue
        seen_months.add(week["monthKey"])
        month_groups.append(
            {
                "key": week["monthKey"],
                "label": f"{week['month']} {week['monday'][:4]}",
                "weeks": [item["week"] for item in plan_weeks if item["monthKey"] == week["monthKey"]],
            }
        )

    return {
        "athlete": {
            "riderFirst": rider_first,
            "riderLast": rider_last,
            "coachFirst": coach_first,
            "coachLast": coach_last,
            "year": year,
        },
        "weekStarts": [item.isoformat() for item in week_starts],
        "totalWeeks": total_weeks,
        "phaseBlocks": [{"phase": phase, "startWeek": start, "endWeek": end} for phase, start, end in phase_blocks],
        "macroBlocks": [{"macro": macro, "startWeek": start, "endWeek": end} for macro, start, end in macro_blocks],
        "monthGroups": month_groups,
        "raceCells": event_cells,
        "mainRaces": [{"name": r["name"], "date": r["date"].isoformat(), **({"endDate": r["endDate"]} if r.get("endDate") else {})} for r in main_races],
        "secondaryRaces": [{"name": r["name"], "date": r["date"].isoformat(), **({"endDate": r["endDate"]} if r.get("endDate") else {})} for r in secondary_races],
        "trainingCamps": [{"name": r["name"], "date": r["date"].isoformat(), **({"endDate": r["endDate"]} if r.get("endDate") else {})} for r in training_camps],
        "planWeeks": plan_weeks,
    }
