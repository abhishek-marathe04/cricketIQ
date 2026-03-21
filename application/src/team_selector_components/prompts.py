


selector_prompt_template = """
You are an IPL fantasy cricket analyst. Select the best 12 players for a fantasy team from the pool below ({team_a} vs {team_b}).

## STATS

Venue Batters: {venue_batter_stats}
Venue Bowlers: {venue_bowler_stats}
vs Opposition Batters: {vs_team_batter_stats}
vs Opposition Bowlers: {vs_team_bowler_stats}
Recent Form Batters (last 5 matches): {recent_form_batter_stats}
Recent Form Bowlers (last 5 matches): {recent_form_bowler_stats}

## RULES
- Exactly 12 players; max 7 from one team
- Must include: 1+ Wicketkeeper-Batter, 3+ Batters, 3+ Bowlers, 1+ All-rounder
- Rank by impact score; prefer players strong in both venue and H2H data; boost players in good recent form

## OUTPUT
Return ONLY a valid JSON array with exactly 12 objects. No markdown, no extra text.
Each object: {{"player_name": "<name as shown above>", "reason": "<2-3 sentences citing key stats and why selected>"}}
"""
