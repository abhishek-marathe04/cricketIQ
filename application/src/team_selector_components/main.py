import json
import operator
from langgraph.graph import StateGraph, START, END
from team_selector_components.nodes import State, prepare_player_pools, venue_agent, node_b, node_c, selector_node
from utils.logger import get_logger


logger = get_logger()

builder = StateGraph(State)

# ... (add your filter and parallel nodes as before) ...
builder.add_node("prepare_player_pools", prepare_player_pools)
builder.add_node("venue_agent", venue_agent)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)
builder.add_node("selector", selector_node)

# Orchestration logic
builder.add_edge(START, "prepare_player_pools")
# 1. Fan-out from filter
builder.add_edge("prepare_player_pools", "venue_agent")
builder.add_edge("prepare_player_pools", "node_b")
builder.add_edge("prepare_player_pools", "node_c")

# 2. Fan-in (Wait for all 3 to reach the selector)
builder.add_edge("venue_agent", "selector")
builder.add_edge("node_b", "selector")
builder.add_edge("node_c", "selector")

# 3. Final exit
builder.add_edge("selector", END)

graph = builder.compile()