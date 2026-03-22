# CricketIQ — Multi-Agent Best XI System Plan

## What You Already Have (Strong Foundation)

Your existing infra covers most of the data layer you need:

| Existing Function | Reusable For |
|---|---|
| `batter_at_venue_stats(batter, city)` in `stats/metrics/batter_metrics.py` | Batter at ground |
| `batter_vs_team_stats(batter, team)` in `stats/metrics/batter_metrics.py` | Batter vs team |
| `batter_recent_form_stats(batter, num_matches)` in `stats/metrics/batter_metrics.py` | Recent form (last N matches) |
| `bowler_at_venue_stats`, `bowler_vs_team_stats`, `bowler_recent_form_stats` in `stats/metrics/bowler_metrics.py` | Bowler equivalents for all dimensions |
| `batter_vs_bowler_stats(batter, bowler)` in `stats/metrics/batter_metrics.py` | Direct H2H matchup (tool exists, agent not yet built) |
| `player_stats_in_season.py` | Per-season stats |
| Groq integration (prod) + LM Studio (local) in `utils/llm.py` | LLM wired with fallback chain |

You're not building from scratch — you're building a **scoring + selection layer** on top of existing stat functions.

---

## Actual Architecture (Built)

```
Input: combined player pool (from team_selector.py UI) + Venue + Match Date
                          │
                ┌─────────▼──────────┐
                │  prepare_player_pools  │  ← LangGraph entry node
                │  pure Python/code  │  ← NO LLM — splits combined_pool
                │                    │     into team_a/team_b × batters/bowlers
                └──────────┬─────────┘
                           │ 3-way parallel fan-out (edges, not Send API)
          ┌────────────────┼────────────────────┐
          ▼                ▼                    ▼
  ┌──────────────┐  ┌─────────────┐   ┌──────────────────┐
  │ venue_agent  │  │vs_team_agent│   │recent_form_agent │
  │ city stats   │  │ vs opponent │   │ last 5 matches   │
  │ pure math    │  │ pure math   │   │ pure math        │
  └──────┬───────┘  └──────┬──────┘   └────────┬─────────┘
         └──────────────────┴──────────────────┘
                        ▼  (fan-in: all 3 feed selector)
               ┌────────────────────┐
               │   selector_node    │  ← LLM here ONLY
               │  role constraints  │  (1+ WK, 3+ Batters, 3+ Bowlers,
               │  + justification   │   1+ All-rounder, max 7 from one team)
               │  selects 12 players│
               └────────────────────┘
```

**Note:** The original plan proposed using LangGraph's `Send` API for per-player parallel fan-out. The actual implementation uses simpler parallel edges — each agent processes all players in its pool sequentially within the node.

---

## 4 Nodes Breakdown (as built)

**1. `prepare_player_pools`** — orchestration / pre-processing
- Splits `combined_pool` from Streamlit session state into `team_a` / `team_b` × `batters` / `bowlers`
- Uses role sets: `{Batter, All-rounder, Wicketkeeper-Batter}` for batters; `{Bowler, All-rounder}` for bowlers
- No LLM — pure Python

**2. `recent_form_agent`** — for all players in combined pool
- Calls `get_batter_recent_form_stats` / `get_bowler_recent_form_stats` (last 5 matches default)
- Computes runs, SR, avg (batters) and economy, wickets (bowlers) over that window
- Sorts by `impact_score` descending, keeps top 7 batters + top 7 bowlers
- Returns formatted pipe-delimited string for the LLM prompt

**3. `venue_agent`** — for all players in combined pool
- Calls `get_batter_at_venue_stats` / `get_bowler_at_venue_stats` with `match_city`
- Players with no historical data at the venue are silently skipped
- Sorts by `impact_score` descending, keeps top 7 batters + top 7 bowlers

**4. `vs_team_agent`** — for all players in combined pool
- Team A batters face Team B (their opposition), Team B batters face Team A
- Calls `get_batter_vs_team_stats` / `get_bowler_vs_team_stats`
- Sorts by `impact_score` descending, keeps top 7 batters + top 7 bowlers

**5. `selector_node`** — final LLM-powered selection
- Receives venue / vs-team / recent-form stats as formatted strings
- Applies role constraints (1+ WK, 3+ Batters, 3+ Bowlers, 1+ All-rounder, max 7 from one team)
- Produces **12 players** (11 + 1 Impact Player) with per-player justification citing key stats
- Falls back to `MOCK_LLM_RESPONSE` if `MOCK_LLM=true` env var is set

---

## Impact Score Formula

Computed inline in `stats/metrics/batter_metrics.py` and `bowler_metrics.py` — no 0-100 normalization layer:

```python
# Batter
impact_score = (avg + 1) * (strike_rate / 100)

# Bowler
impact_score = (wickets_per_match * 10) + (1 / economy)  # see bowler_metrics.py
```

Agents sort by `impact_score` and pass the top-N as raw text to the LLM. The LLM does the final synthesis — there is no aggregation/normalization node between agents and the selector.

---

## LLM Strategy (Actual)

| Task | Implementation | Why |
|---|---|---|
| Orchestration / pool prep | No LLM — pure Python | Flow is fixed and deterministic |
| Individual stat scoring | No LLM — `impact_score` formula | Deterministic, faster, cheaper |
| Final XII selection + justification | Groq (prod) / LM Studio (local) | Needs constrained reasoning + natural language |

**Prod:** Groq API with model fallback chain in order of preference:
1. `llama-3.3-70b-versatile`
2. `llama-3.1-8b-instant`
3. `llama3-8b-8192`

On `RateLimitError`, automatically tries next model. Raises `AllModelsRateLimitedError` if all are exhausted.

**Local:** LM Studio at `http://localhost:1234/v1`

**Testing:** `MOCK_LLM=true` env var skips the LLM entirely and returns a hardcoded 12-player response.

---

## Pydantic Models (as built in `nodes.py`)

| Model | Fields | Purpose |
|---|---|---|
| `SessionData` | `combined_pool`, `team_a`, `team_b`, `match_city` | Input validation from Streamlit session |
| `Team` | `batters: list[dict]`, `bowlers: list[dict]` | Per-team player pools |
| `PlayerPools` | `team_a: Team`, `team_b: Team` | Output of `prepare_player_pools` node |
| `State` (TypedDict) | `input`, `venue_scores`, `vs_team_scores`, `recent_form_scores`, `results`, `player_pools`, `final_choice` | LangGraph graph state |

**Note:** The originally planned `PlayerProfile` Pydantic model (with normalized 0-100 scores per dimension) was not built. Scores are passed as formatted strings, not structured score objects.

---

## Streamlit UI (as built in `team_selector.py`)

- User picks Team A + Team B from IPL 2026 squads JSON
- Players pre-selected based on `probableXi` flag in squad data
- City selector from `ipl_venue_cities.csv`
- "Let AI Pick the Best 11 + 1" button triggers the LangGraph graph
- Results shown with role icon + team color per player + AI reasoning
- Expandable "Stats used by AI" section with 3 tabs: Venue / vs Opposition / Recent Form
- Rate limit errors surfaced gracefully to the user

---

## What Was Built vs. Planned

| Component | Planned | Status |
|---|---|---|
| `PlayerProfile` Pydantic model | Normalized scores per dimension | ❌ Not built — replaced by string-formatted stats |
| 0-100 score normalization layer | Aggregator between agents and selector | ❌ Not built — `impact_score` formula used directly |
| `form_agent` node | Last 5 matches, per-player | ✅ Built as `recent_form_agent` |
| `venue_agent` node | Wraps city stats | ✅ Built |
| `vs_team_agent` node | Wraps team H2H stats | ✅ Built |
| `xi_selector_agent` node | LLM with role constraints | ✅ Built as `selector_node` (selects 12, not 11) |
| LangGraph `Send` API fan-out | Per-player parallel execution | ❌ Not used — simple parallel edges instead |
| Streamlit UI tab | Input 22 players + roles + venue | ✅ Built as full page (`team_selector.py`) |
| Matchup agent (H2H bowler vs batter) | Skipped due to sparse data | ⏸ Tool exists (`get_batter_vs_bowler_stats`), agent not built |
| Groq fallback chain | Not planned (LM Studio only) | ✅ Added — 3-model fallback + `MOCK_LLM` flag |

---

## Remaining Work / Known Gaps

1. **LangGraph `Send` API** — current per-node sequential loops could be replaced with per-player parallel `Send` fan-out for lower latency on large pools
2. **Matchup agent** — `batter_vs_bowler_stats` tool exists but no agent node uses it; useful for specific H2H matchup signals
3. **Normalized score aggregator** — a 0-100 normalization layer between agents and the selector would make the prompt more structured and reduce LLM guesswork
4. **Player count** — currently no enforced cap on combined pool size; very large pools may exceed the LLM context window
