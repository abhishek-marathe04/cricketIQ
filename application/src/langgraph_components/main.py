from langgraph_components.pydantic_models import AppState
from langgraph_components.nodes import out_of_scope_query, parse_query_node, run_batter_stats, run_team_vs_team_stats
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from utils.logger import get_logger

logger = get_logger()

def router(state):
    print(state)
    logger.info(f'Inside router  : {state}')
    if state["intent"] == "batter_stats":
        return "batter_stats"
    if state["intent"] == "team_vs_team_stats":
        return "team_vs_team_stats"
    if state["intent"] == "out_of_scope_query":
        return "out_of_scope_query"
    return END


builder = StateGraph(state_schema=AppState)
builder.add_node("llm_parser", RunnableLambda(parse_query_node))
builder.add_node("batter_stats", RunnableLambda(run_batter_stats))
builder.add_node("team_vs_team_stats", RunnableLambda(run_team_vs_team_stats))
builder.add_node("out_of_scope_query", RunnableLambda(out_of_scope_query))

builder.set_entry_point("llm_parser")
builder.add_conditional_edges(
    "llm_parser",  # from node
    router,   # router function returning name of next node
    {
        "batter_stats": "batter_stats",
        "team_vs_team_stats": "team_vs_team_stats",
        "out_of_scope_query": "out_of_scope_query",
        "__end__": END
    }
)


graph = builder.compile()
