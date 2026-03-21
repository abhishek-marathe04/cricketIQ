
from team_selector_components.tools import get_batter_at_venue_stats, get_bowler_at_venue_stats, get_batter_vs_team_stats, get_bowler_vs_team_stats
from team_selector_components.prompts import selector_prompt_template
from utils.llm import get_llm_client, get_model_name
import operator
import json
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, TypedDict, List, Any
from utils.logger import get_logger
from config import ENV
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

    batter_list = [player for player in combined_pool if player["specialisation"] in batter_roles]
    team_a_batters = [player for player in batter_list if player["_team"] == team_a]
    team_b_batters = [player for player in batter_list if player["_team"] == team_b]

    bowler_list = [player for player in combined_pool if player["specialisation"] not in batter_roles]
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

    top_batters = sorted(raw_batter_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:6]
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

    top_bowlers = sorted(raw_bowler_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:6]
    bowler_vs_team_stats = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) vs {s['opposition_team']} | economy:{s['stats']['economy']} | avg:{s['stats']['average']} | impact:{s['stats']['impact_score']}"
        for s in top_bowlers
    )

    return {"vs_team_scores": {
        "batters": batter_vs_team_stats,
        "bowlers": bowler_vs_team_stats,
    }}


def node_c(state: State): return {"results": ["Option C"]}


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
    top_batters = sorted(raw_batter_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:6]
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
    top_bowlers = sorted(raw_bowler_stats, key=lambda x: x['stats']['impact_score'] or 0, reverse=True)[:6]
    bowler_venue_stats = "\n".join(
        f"{s['player_name']} ({s['specialisation']}) | venue_economy:{s['stats']['economy']} | venue_avg:{s['stats']['average']} | impact:{s['stats']['impact_score']}"
        for s in top_bowlers
    )

    return {"venue_scores": {
        "batters": batter_venue_stats,
        "bowlers": bowler_venue_stats,
    }}

# --- The Orchestrator / Selector ---
def selector_node(state: State):
    logger.info(f'Inside selector_node')
    venue_scores = state["venue_scores"]
    vs_team_scores = state["vs_team_scores"]
    team_a = state["input"]["team_a"]
    team_b = state["input"]["team_b"]

    formatted_prompt = selector_prompt_template.format(
        team_a=team_a,
        team_b=team_b,
        venue_batter_stats=venue_scores["batters"] or "No data available",
        venue_bowler_stats=venue_scores["bowlers"] or "No data available",
        vs_team_batter_stats=vs_team_scores["batters"] or "No data available",
        vs_team_bowler_stats=vs_team_scores["bowlers"] or "No data available",
    )

    try:
        logger.info(f'env : {ENV}')
        llm = get_llm_client(env=ENV)
        model = get_model_name(env=ENV)

        response = llm.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.2,
            max_tokens=8192,
        )
        logger.info(f"Response from llm: {response}")
        message_from_llm = response.choices[0].message.content
        logger.info(f'selector_node LLM response: {message_from_llm}')

        final_choice = json.loads(message_from_llm)
        return {"final_choice": final_choice}
    except Exception as e:
        logger.error(f"Error in selector_node: {e}")
        return {"final_choice": [], "error": str(e)}
