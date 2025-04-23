from langgraph_components.pydantic_models import AppState
from langgraph_components.nodes import parse_query_node, run_batter_stats_vs_bowler, run_player_stats_per_season, run_player_stats_vs_bowler_type
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
    return END



builder = StateGraph(state_schema=AppState)
builder.add_node("llm_parser", RunnableLambda(parse_query_node))
builder.add_node("player_stats_per_season", RunnableLambda(run_player_stats_per_season))
builder.add_node("player_stats_vs_bowler_type", RunnableLambda(run_player_stats_vs_bowler_type))
builder.add_node("batter_stats_vs_bowler", RunnableLambda(run_batter_stats_vs_bowler))

builder.set_entry_point("llm_parser")
builder.add_conditional_edges(
    "llm_parser",  # from node
    router,   # router function returning name of next node
    {
        "player_stats_per_season": "player_stats_per_season",
        "player_stats_vs_bowler_type": "player_stats_vs_bowler_type",
        "batter_stats_vs_bowler": "batter_stats_vs_bowler",
        "__end__": END
    }
)


graph = builder.compile()
