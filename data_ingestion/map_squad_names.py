#!/usr/bin/env python3
"""
Maps IPL 2026 squad player full names to their abbreviated DB names.

Matching strategy (in order of preference):
  1. Exact match on player_name (handles already-abbreviated names like "KL Rahul")
  2. Exact match on player_full_name
  3. Substring match (e.g. "Sanju Samson" found inside "Sanju Viswanath Samson")
  4. Last-name filtered fuzzy match
  5. Global fuzzy match (fallback)

Adds `dbName` field to each player in the JSON.
Low-confidence and unmatched players are printed to stdout for manual review.
"""

import json
import csv
from difflib import SequenceMatcher
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
JSON_PATH   = Path("/Users/abhishekmarathe/Downloads/ipl_2026_squads.json")
CSV_PATH    = Path("/Users/abhishekmarathe/workspace/cricketIQ/ipl-dataset-2008-to-2025/players-data-updated.csv")
OUTPUT_PATH = Path("/Users/abhishekmarathe/Downloads/ipl_2026_squads_mapped.json")

# Matches below this score get dbName=None and are flagged as unmatched.
UNMATCHED_THRESHOLD   = 0.55
# Matches between this and UNMATCHED_THRESHOLD are included but flagged low-confidence.
LOW_CONF_THRESHOLD    = 0.75
# ─────────────────────────────────────────────────────────────────────────────


def load_db_players(csv_path: Path) -> list[dict]:
    players = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            players.append({
                "player_id":   row["player_id"],
                "player_name": row["player_name"].strip(),
                "full_name":   (row["player_full_name"] or "").strip(),
            })
    return players


def normalize(name: str) -> str:
    return " ".join(name.lower().strip().split())


def last_word(name: str) -> str:
    parts = name.strip().split()
    return parts[-1].lower() if parts else ""


def sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_best_match(json_name: str, db_players: list[dict]) -> tuple[str | None, float, str]:
    """
    Returns (db_player_name, confidence_score, match_method).
    db_player_name is None when no confident match is found.
    """
    jn = normalize(json_name)
    j_last = last_word(json_name)

    # 1. Exact match on abbreviated player_name (e.g. "KL Rahul", "MS Dhoni")
    for p in db_players:
        if normalize(p["player_name"]) == jn:
            return p["player_name"], 1.0, "exact_abbrev"

    # 2. Exact match on full name
    for p in db_players:
        if normalize(p["full_name"]) == jn:
            return p["player_name"], 1.0, "exact_full"

    # 3. Substring match — json_name appears inside full_name
    #    Handles: "Sanju Samson" ⊂ "Sanju Viswanath Samson"
    #             "Wanindu Hasaranga" ⊂ "Pinnaduwage Wanindu Hasaranga de Silva"
    #             "Eshan Malinga" ⊂ "...Eshan Malinga Dharmasena"
    for p in db_players:
        fn = normalize(p["full_name"])
        if jn in fn:
            return p["player_name"], 0.95, "substring"

    # 4. Last-name filtered fuzzy match
    last_name_candidates = [
        (p, sim(json_name, p["full_name"]))
        for p in db_players
        if last_word(p["full_name"]) == j_last
    ]
    if last_name_candidates:
        last_name_candidates.sort(key=lambda x: x[1], reverse=True)
        best_p, best_score = last_name_candidates[0]
        if best_score >= UNMATCHED_THRESHOLD:
            return best_p["player_name"], best_score, "fuzzy_last_name"

    # 5. Global fuzzy fallback (last resort)
    all_scores = [
        (p, sim(json_name, p["full_name"]))
        for p in db_players
    ]
    all_scores.sort(key=lambda x: x[1], reverse=True)
    best_p, best_score = all_scores[0]
    return best_p["player_name"], best_score, "fuzzy_global"


def main():
    db_players = load_db_players(CSV_PATH)

    with open(JSON_PATH, encoding="utf-8") as f:
        squads = json.load(f)

    low_confidence: list[dict] = []
    unmatched: list[dict]      = []

    for team, team_data in squads.items():
        for player in team_data["players"]:
            name = player["name"]
            db_name, score, method = find_best_match(name, db_players)

            if score >= LOW_CONF_THRESHOLD:
                player["dbName"] = db_name
            elif score >= UNMATCHED_THRESHOLD:
                player["dbName"] = db_name
                low_confidence.append({
                    "team":      team,
                    "json_name": name,
                    "db_name":   db_name,
                    "score":     round(score, 3),
                    "method":    method,
                })
            else:
                player["dbName"] = None
                unmatched.append({
                    "team":       team,
                    "json_name":  name,
                    "best_guess": db_name,
                    "score":      round(score, 3),
                })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(squads, f, indent=2, ensure_ascii=False)

    print(f"✅  Output written to: {OUTPUT_PATH}")

    if low_confidence:
        print(f"\n⚠️  Low-confidence matches ({len(low_confidence)}) — please verify:")
        for m in low_confidence:
            print(f"  [{m['team']}]  '{m['json_name']}'  →  '{m['db_name']}'  "
                  f"(score={m['score']}, method={m['method']})")

    if unmatched:
        print(f"\n❌  Unmatched players ({len(unmatched)}) — dbName set to null:")
        for m in unmatched:
            print(f"  [{m['team']}]  '{m['json_name']}'  "
                  f"(best guess: '{m['best_guess']}', score={m['score']})")

    total = sum(len(t["players"]) for t in squads.values())
    matched = total - len(unmatched)
    print(f"\n📊  {matched}/{total} players matched  "
          f"({len(low_confidence)} low-confidence, {len(unmatched)} unmatched)")


if __name__ == "__main__":
    main()
