from langgraph_components.pydantic_models import AppState
from langgraph_components.nodes import parse_query_node, run_batter_stats_vs_bowler, run_batter_stats, run_player_stats_per_season, run_player_stats_vs_bowler_type, run_season_overview, run_team_vs_team_stats
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from utils.logger import get_logger

logger = get_logger()

def router(state):
    print(state)
    logger.info(f'Inside router  : {state}')
    if state["intent"] == "player_stats_in_season":
        return "player_stats_per_season"
    if state["intent"] == "player_stats_vs_bowler_type":
        return "player_stats_vs_bowler_type"
    if state["intent"] == "batter_stats_vs_bowler":
        return "batter_stats_vs_bowler"
    if state["intent"] == "batter_stats":
        return "batter_stats"
    if state["intent"] == "team_vs_team_stats":
        return "team_vs_team_stats"
    if state["intent"] == "season_overview":
        return "season_overview"
    return END



builder = StateGraph(state_schema=AppState)
builder.add_node("llm_parser", RunnableLambda(parse_query_node))
builder.add_node("player_stats_per_season", RunnableLambda(run_player_stats_per_season))
builder.add_node("player_stats_vs_bowler_type", RunnableLambda(run_player_stats_vs_bowler_type))
builder.add_node("batter_stats_vs_bowler", RunnableLambda(run_batter_stats_vs_bowler))
builder.add_node("batter_stats", RunnableLambda(run_batter_stats))
builder.add_node("team_vs_team_stats", RunnableLambda(run_team_vs_team_stats))
builder.add_node("season_overview", RunnableLambda(run_season_overview))

builder.set_entry_point("llm_parser")
builder.add_conditional_edges(
    "llm_parser",  # from node
    router,   # router function returning name of next node
    {
        "player_stats_per_season": "player_stats_per_season",
        "player_stats_vs_bowler_type": "player_stats_vs_bowler_type",
        "batter_stats_vs_bowler": "batter_stats_vs_bowler",
        "batter_stats": "batter_stats",
        "team_vs_team_stats": "team_vs_team_stats",
        "season_overview": "season_overview",
        "__end__": END
    }
)


graph = builder.compile()
