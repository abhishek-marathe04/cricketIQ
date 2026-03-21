
from team_selector_components.tools import get_batter_at_venue_stats
from utils.llm import get_llm_client, get_model_name
from langgraph_components.prompts import prompt_template
import operator
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, TypedDict, List, Any
from utils.logger import get_logger
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


def node_b(state: State): return {"results": ["Option B"]}
def node_c(state: State): return {"results": ["Option C"]}


# --- Parallel Nodes ---
def venue_agent(state: State):
    # Create a new list where objects meet a specific condition
    venue_stats = []
    player_pool = state['player_pools']
    city = state['input']['match_city']

    all_batters = player_pool['team_a']['batters'] + player_pool['team_b']['batters']
    all_bowlers = player_pool['team_a']['bowlers'] + player_pool['team_b']['bowlers']
    
    for batter in all_batters:
        batter_name = batter['dbName']
        batter_vs_venue_stats = get_batter_at_venue_stats.invoke({"batter": batter_name, "city": city})
        venue_stats.append(batter_vs_venue_stats)

    return {"venue_scores": venue_stats}

# --- The Orchestrator / Selector ---
def selector_node(state: State):
    # state["results"] will now contain ["Option A", "Option B", "Option C"]
    venue_scores = state["venue_scores"]
    return {"final_choice": venue_scores}
