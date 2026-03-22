
from team_selector_components.tools import get_batter_at_venue_stats, get_bowler_at_venue_stats, get_batter_vs_team_stats, get_bowler_vs_team_stats, get_batter_recent_form_stats, get_bowler_recent_form_stats
from team_selector_components.prompts import selector_prompt_template
from utils.llm import call_llm_with_fallback
import operator
import json
from json_repair import repair_json
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, TypedDict, List, Any
from utils.logger import get_logger
from config import ENV, MOCK_LLM
logger = get_logger()

def orchastrator(state):
    pass


# 1. Define the internal structure of your session state data
class SessionData(BaseModel):
    combined_pool: List[Any] = Field(default_factory=list)
    team_a: str
    team_b: str
    match_city: str
    
    # Ignore extra Streamlit internal keys (like widget IDs)
    model_config = ConfigDict(extra="ignore")

class Team(BaseModel):
    batters: list[dict]
    bowlers: list[dict]

class PlayerPools(BaseModel):
    team_a: Team    
    team_b: Team    

class State(TypedDict):
    # This keeps a list of all responses from parallel nodes
    input: SessionData
    venue_scores: list[dict]
    vs_team_scores: list[dict]
    recent_form_scores: dict
    results: Annotated[list, operator.add]
    player_pools : PlayerPools
    final_choice: list[dict]

def prepare_player_pools(state: State):
    # Logic to clean or validate input
    combined_pool = state['input']['combined_pool']
    team_a = state['input']['team_a']
    team_b = state['input']['team_b']
    # Define the roles you want to keep
    batter_roles = {"Batter", "All-rounder", "Wicketkeeper-Batter"}
    bowler_roles = {"Bowler", "All-rounder"}

    batter_list = [player for player in combined_pool if player["specialisation"] in batter_roles]
    team_a_batters = [player for player in batter_list if player["_team"] == team_a]
    team_b_batters = [player for player in batter_list if player["_team"] == team_b]

    bowler_list = [player for player in combined_pool if player["specialisation"] in bowler_roles]
    team_a_bowlers = [player for player in bowler_list if player["_team"] == team_a]
    team_b_bowlers = [player for player in bowler_list if player["_team"] == team_b]

    team_a = {
        "batters": team_a_batters,
        "bowlers": team_a_bowlers,
    }
    team_b = {
        "batters": team_b_batters,
        "bowlers": team_b_bowlers,
    }

    return {
        "player_pools": {
            "team_a": team_a,
            "team_b": team_b
        }
}


def vs_team_agent(state: State):
    player_pool = state['player_pools']
    team_a = state['input']['team_a']
    team_b = state['input']['team_b']

    # team_a batters face team_b bowlers, so their opposition is team_b (and vice versa)
    raw_batter_stats = []
    for batter in player_pool['team_a']['batters']:
        bv_stats = get_batter_vs_team_stats.invoke({"batter": batter['dbName'], "team": team_b})
        if bv_stats['stats'] is not None:
            bv_stats['player_name'] = batter['name']
            bv_stats['specialisation'] = batter['specialisation']
            raw_batter_stats.append(bv_stats)
    for batter in player_pool['team_b']['batters']:
        bv_stats = get_batter_vs_team_stats.invoke({"batter": batter['dbName'], "team": team_a})
        if bv_stats['stats'] is not None:
            bv_stats['player_name'] = batter['name']
            bv_stats['specialisation'] = batter['specialisation']
            raw_batter_stats.append(bv_stats)

    top_batters = sorted(raw_batter_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:7]
    batter_vs_team_stats = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) vs {s['opposition_team']} | avg:{s['stats']['average']} | sr:{s['stats']['strike_rate']} | impact:{s['stats']['impact_score']}"
        for s in top_batters
    )

    # team_a bowlers face team_b batters, so their opposition is team_b (and vice versa)
    raw_bowler_stats = []
    for bowler in player_pool['team_a']['bowlers']:
        bw_stats = get_bowler_vs_team_stats.invoke({"bowler": bowler['dbName'], "team": team_b})
        if bw_stats['stats'] is not None:
            bw_stats['player_name'] = bowler['name']
            bw_stats['specialisation'] = bowler['specialisation']
            raw_bowler_stats.append(bw_stats)
    for bowler in player_pool['team_b']['bowlers']:
        bw_stats = get_bowler_vs_team_stats.invoke({"bowler": bowler['dbName'], "team": team_a})
        if bw_stats['stats'] is not None:
            bw_stats['player_name'] = bowler['name']
            bw_stats['specialisation'] = bowler['specialisation']
            raw_bowler_stats.append(bw_stats)

    top_bowlers = sorted(raw_bowler_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:7]
    bowler_vs_team_stats = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) vs {s['opposition_team']} | economy:{s['stats']['economy']} | avg:{s['stats']['average']} | impact:{s['stats']['impact_score']}"
        for s in top_bowlers
    )

    return {"vs_team_scores": {
        "batters": batter_vs_team_stats,
        "bowlers": bowler_vs_team_stats,
    }}


def recent_form_agent(state: State):
    player_pool = state['player_pools']
    all_batters = player_pool['team_a']['batters'] + player_pool['team_b']['batters']
    all_bowlers = player_pool['team_a']['bowlers'] + player_pool['team_b']['bowlers']

    raw_batter_stats = []
    for batter in all_batters:
        result = get_batter_recent_form_stats.invoke({"batter": batter['dbName']})
        if result.get('stats') is not None:
            result['player_name'] = batter['name']
            result['specialisation'] = batter['specialisation']
            raw_batter_stats.append(result)

    top_batters = sorted(raw_batter_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:7]
    batter_form_str = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) | last_{s['matches_considered']}_avg:{s['stats']['average']} | last_{s['matches_considered']}_sr:{s['stats']['strike_rate']} | impact:{s['stats']['impact_score']}"
        for s in top_batters
    )

    raw_bowler_stats = []
    for bowler in all_bowlers:
        result = get_bowler_recent_form_stats.invoke({"bowler": bowler['dbName']})
        if result.get('stats') is not None:
            result['player_name'] = bowler['name']
            result['specialisation'] = bowler['specialisation']
            raw_bowler_stats.append(result)

    top_bowlers = sorted(raw_bowler_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:7]
    bowler_form_str = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) | last_{s['matches_considered']}_economy:{s['stats']['economy']} | last_{s['matches_considered']}_avg:{s['stats']['average']} | impact:{s['stats']['impact_score']}"
        for s in top_bowlers
    )

    return {"recent_form_scores": {"batters": batter_form_str, "bowlers": bowler_form_str}}


# --- Parallel Nodes ---
def venue_agent(state: State):
    player_pool = state['player_pools']
    city = state['input']['match_city']

    all_batters = player_pool['team_a']['batters'] + player_pool['team_b']['batters']
    all_bowlers = player_pool['team_a']['bowlers'] + player_pool['team_b']['bowlers']

    # Collect batter stats, skip players with no historical data
    raw_batter_stats = []
    for batter in all_batters:
        bv_stats = get_batter_at_venue_stats.invoke({"batter": batter['dbName'], "city": city})
        if bv_stats['stats'] is not None:
            bv_stats['player_name'] = batter['name']
            bv_stats['specialisation'] = batter['specialisation']
            raw_batter_stats.append(bv_stats)

    # Sort by impact_score descending, keep top 6
    top_batters = sorted(raw_batter_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:7]
    batter_venue_stats = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) | venue_avg:{s['stats']['average']} | venue_sr:{s['stats']['strike_rate']} | impact:{s['stats']['impact_score']}"
        for s in top_batters
    )

    # Collect bowler stats, skip players with no historical data
    raw_bowler_stats = []
    for bowler in all_bowlers:
        bw_stats = get_bowler_at_venue_stats.invoke({"bowler": bowler['dbName'], "city": city})
        if bw_stats['stats'] is not None:
            bw_stats['player_name'] = bowler['name']
            bw_stats['specialisation'] = bowler['specialisation']
            raw_bowler_stats.append(bw_stats)

    # Sort by impact_score descending, keep top 6
    top_bowlers = sorted(raw_bowler_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:7]
    bowler_venue_stats = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) | venue_economy:{s['stats']['economy']} | venue_avg:{s['stats']['average']} | impact:{s['stats']['impact_score']}"
        for s in top_bowlers
    )

    return {"venue_scores": {
        "batters": batter_venue_stats,
        "bowlers": bowler_venue_stats,
    }}

MOCK_LLM_RESPONSE = [
  {"player_name": "Suryakumar Yadav", "reason": "Highest impact score among batters, with a venue average of 41.26 and SR of 161.88, indicating his consistency at the venue."},
  {"player_name": "Ruturaj Gaikwad", "reason": "High impact score against Mumbai Indians, averaging 41.57 with an SR of 146.97, making him a strong pick for this match."},
  {"player_name": "Jasprit Bumrah", "reason": "Highest impact score among bowlers at the venue, with an economy rate of 7.36 and average of 21.25, showcasing his effectiveness in containing opposition batsmen."},
  {"player_name": "Tilak Varma", "reason": "High impact score against Chennai Super Kings, averaging 56.33 with an SR of 117.36, indicating his potential to perform well in this match."},
  {"player_name": "Shivam Dube", "reason": "Good all-round performance, with a venue average of 34.21 and impact score of 49.9, making him a valuable asset for the team."},
  {"player_name": "Rohit Sharma", "reason": "Consistent performer at the venue, averaging 31.22 with an SR of 131.65, providing stability to the batting lineup."},
  {"player_name": "MS Dhoni", "reason": "High impact score against Mumbai Indians, averaging 32.17 with an SR of 124.52, making him a strong pick for this match as wicketkeeper-batter."},
  {"player_name": "Hardik Pandya", "reason": "Good all-round performance, with a venue average of 29.39 and impact score of 42.85, providing balance to the team."},
  {"player_name": "Khaleel Ahmed", "reason": "Economical bowler against Mumbai Indians, with an economy rate of 8.71 and average of 21.17, making him a good pick for this match."},
  {"player_name": "Trent Boult", "reason": "Good impact score against Chennai Super Kings, with an economy rate of 8.72 and average of 30.6, providing depth to the bowling lineup."},
  {"player_name": "Mayank Markande", "reason": "Economical bowler at the venue, with an economy rate of 7.69 and average of 24.6, making him a good pick for this match."},
  {"player_name": "Ayush Mhatre", "reason": "High impact score against Mumbai Indians, averaging 32.0 with an SR of 188.24, providing depth to the batting lineup."},
]

# --- The Orchestrator / Selector ---
def selector_node(state: State):
    if MOCK_LLM:
        logger.info("MOCK_LLM is enabled, returning mock response")
        return {"final_choice": MOCK_LLM_RESPONSE}

    venue_scores = state["venue_scores"]
    vs_team_scores = state["vs_team_scores"]
    recent_form_scores = state.get("recent_form_scores", {})

    team_a = state["input"]["team_a"]
    team_b = state["input"]["team_b"]

    formatted_prompt = selector_prompt_template.format(
        team_a=team_a,
        team_b=team_b,
        venue_batter_stats=venue_scores["batters"] or "No data available",
        venue_bowler_stats=venue_scores["bowlers"] or "No data available",
        vs_team_batter_stats=vs_team_scores["batters"] or "No data available",
        vs_team_bowler_stats=vs_team_scores["bowlers"] or "No data available",
        recent_form_batter_stats=recent_form_scores.get("batters") or "No data available",
        recent_form_bowler_stats=recent_form_scores.get("bowlers") or "No data available",
    )

    try:
        logger.info(f'env : {ENV}')
        response = call_llm_with_fallback(
            env=ENV,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.2,
            max_tokens=8192,
        )
        logger.info(f"Response from llm: {response}")
        message_from_llm = response.choices[0].message.content
        logger.info(f'selector_node LLM response: {message_from_llm}')

        try:
            final_choice = json.loads(message_from_llm)
        except json.JSONDecodeError:
            logger.warning("JSON parse failed, attempting repair")
            final_choice = json.loads(repair_json(message_from_llm))
        return {"final_choice": final_choice}
    except Exception as e:
        logger.error(f"Error in selector_node: {e}")
        return {"final_choice": [], "error": str(e)}
