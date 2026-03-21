# CricketIQ — Multi-Agent Best XI System Plan

## What You Already Have (Strong Foundation)

Your existing infra covers most of the data layer you need:

| Existing Function | Reusable For |
|---|---|
| `call_batter_stats(player, opponent_team, city)` | Batter vs team, batter at ground |
| `call_batter_stats_vs_bowler(batter, bowler)` | Direct H2H matchup analysis |
| `player_stats_in_season.py` | Recent form (filter last 1-2 seasons) |
| `player_stats_vs_bowler_type.py` | Batter weakness profiling |
| LM Studio integration in `utils/llm.py` | Local LLM already wired |

You're not building from scratch — you're building a **scoring + selection layer** on top of existing stat functions.

---

## Proposed Multi-Agent Architecture

```
Input: 24 players (from team_selector.py) + Venue + Match Date
                          │
                ┌─────────▼──────────┐
                │  Orchestrator      │  ← LangGraph entry
                │  pure Python/code  │  ← NO LLM — fixed, deterministic flow
                └──────────┬─────────┘
                           │ Send API parallel fan-out
          ┌────────────────┼────────────────────┐
          ▼                ▼                    ▼
  ┌──────────────┐  ┌─────────────┐   ┌──────────────────┐
  │  Form Agent  │  │ Venue Agent │   │ Vs-Team Agent    │
  │  last 5 mats │  │ city stats  │   │ vs opponent team │
  │  pure math   │  │ pure math   │   │ pure math        │
  └──────┬───────┘  └──────┬──────┘   └────────┬─────────┘
         └──────────────────┴──────────────────┘
                        ▼
               ┌────────────────────┐
               │  Score Aggregator  │
               │  normalize scores  │  ← pure math, no LLM
               │  per dimension     │
               └────────┬───────────┘
                        ▼
               ┌────────────────────┐
               │  XI Selector Agent │  ← LLM here ONLY
               │  role constraints  │  (min 5 batters, 4+ bowlers)
               │  + justification   │
               └────────────────────┘
```

---

## 4 Specialized Agents Breakdown

**1. Form Agent** — for each of 22 players
- Filters ball-by-ball data to the last 5 matches per player
- Computes runs, SR, avg (batters) and economy, wickets (bowlers) over that window
- Score: weighted recent SR + avg; flags hot/cold form trend

**2. Venue Agent** — for each of 22 players
- Calls `call_batter_stats(player, city=venue)` (already exists)
- For bowlers: filter where they are bowling at that city
- Score: SR/avg/economy at that ground relative to career average

**3. Vs-Team Agent** — for each of 22 players
- Calls `call_batter_stats(player, opponent_team_name=opponent)`
- Captures how a player historically performs vs this specific opposition
- Score: SR/avg vs that team

**4. XI Selector Agent** — final LLM-powered selection
- Receives all scores (form + venue + vs-team) as a structured JSON
- Applies role constraints (need valid batting order + bowling attack)
- Produces ranked shortlist + explanation per player selected/rejected

---

## LLM Strategy (Local/Open Source)

Since you already have LM Studio wired:

| Task | Model Recommendation | Why |
|---|---|---|
| Orchestration | No LLM — pure Python/LangGraph | Flow is fixed and deterministic; no routing decisions to make |
| Individual stat scoring | No LLM — pure math | Deterministic, faster, cheaper |
| Final XI selection + justification | Llama 3.3 70B or Qwen2.5-72B | Needs constrained reasoning + natural language output |

The orchestrator's job is fixed: always fan out to the same agents, always aggregate, always call XI selector. There is no ambiguity to resolve, so an LLM adds cost with zero benefit. Only the **XI selector** needs LLM reasoning — one LLM call per run total. This keeps local inference load minimal.

---

## LangGraph Pattern to Use

Your current graph is a simple linear state machine. For this, use **Map-Reduce with the `Send` API**:

```python
# Fan out: one Send per player per analysis dimension
from langgraph.types import Send

def fan_out_players(state):
    return [
        Send("form_agent", {"player": p, "role": r})
        for p, r in state["players"].items()
    ]

builder.add_conditional_edges("orchestrator", fan_out_players, ["form_agent"])
# Reduce: aggregate_scores collects all results
builder.add_edge("form_agent", "aggregate_scores")
```

This runs all 22 player analyses in parallel within the graph — no sequential bottleneck.

---

## What You Need to Build (New)

| New Component | Effort | Description |
|---|---|---|
| `PlayerProfile` Pydantic model | Low | Holds role tag, team, scores per dimension |
| Scoring functions | Medium | Normalize stats → 0-100 score per dimension |
| `form_agent` node | Medium | Filters last 5 matches from ball-by-ball data, computes form score |
| `venue_agent` node | Low | Wraps existing `call_batter_stats` with city filter |
| `vs_team_agent` node | Low | Wraps existing `call_batter_stats` with team filter |
| `xi_selector_agent` node | Medium-High | LLM prompt with role constraints |
| New Streamlit UI tab | Medium | Input 22 players + roles + venue |

---

## Recommendation Summary

1. **Keep LangGraph** — don't switch frameworks, you're already invested and it handles this well with the `Send` API for parallel execution
2. **Don't use an LLM for scoring** — pure pandas math is faster, cheaper, and deterministic; LLM only for final synthesis
3. **Reuse your stat functions as-is** — they return DataFrames, just wrap them with a score normalizer
4. **Local LLM is fine** — only 1 node (XI selector) needs LLM; Llama 3.3 70B via LM Studio handles it with minimal inference load
5. **Build Form + Venue + VsTeam agents** — matchup agent skipped for now due to sparse H2H data at player level
