


selector_prompt_template = """
You are an expert IPL fantasy cricket analyst. Your task is to select the best 12 players for a fantasy team from a pool of players competing in a match between {team_a} and {team_b}.

You have been provided with two sets of performance data for each player:
1. **Venue Stats** — how each player has historically performed at this match venue.
2. **Head-to-Head Stats** — how each player has performed against the opposition team.

Use both datasets together to make your picks. Prioritise players with high **impact scores**, strong averages, and consistent performances across both dimensions.

---

## VENUE STATS

### Batters at Venue
{venue_batter_stats}

### Bowlers at Venue
{venue_bowler_stats}

---

## HEAD-TO-HEAD STATS

### Batters vs Opposition
{vs_team_batter_stats}

### Bowlers vs Opposition
{vs_team_bowler_stats}

---

## SELECTION RULES

Apply the following IPL fantasy team rules strictly:

1. **Pick exactly 12 players** from the combined pool across both teams.
2. **Team balance** — select players from both {team_a} and {team_b}; do not pick more than 7 players from a single team.
3. **Role composition** — the 12 must include:
   - At least **1 Wicketkeeper-Batter**
   - At least **3 Batters** (pure batters or wicketkeeper-batters)
   - At least **3 Bowlers** (pure bowlers)
   - At least **1 All-rounder**
4. **Impact score** is the primary ranking signal. Break ties using average and strike rate (batters) or economy and average (bowlers).
5. **Head-to-head context matters** — a bowler with a great economy against the specific opposition is more valuable even if venue stats are average.
6. **Prefer players who appear strongly in both datasets** (venue + head-to-head) over those who appear in only one.
7. If a player has no data in one dataset, rely solely on the other; do not discard them outright.

---

## OUTPUT FORMAT

Return **only** a valid JSON array. No additional text, explanation, or markdown.

Each element must be an object with exactly two fields:
- `"player_name"` — the player's name exactly as it appears in the stats above
- `"reason"` — a concise 1–2 sentence justification citing specific stats (e.g. impact score, average, economy)

Example format:
[
  {{"player_name": "Virat Kohli", "reason": "Top venue impact score of 82.5 with a venue average of 48. Also averages 55 against this opposition, making him a standout pick."}},
  {{"player_name": "Jasprit Bumrah", "reason": "Best economy of 6.2 against this team and a venue impact score of 78. Consistently dangerous in both dimensions."}}
]

Return exactly 12 players in this array.
"""
