import json
import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from utils.logger import get_logger

logger = get_logger()

class State(TypedDict):
    # This keeps a list of all responses from parallel nodes
    input: str
    results: Annotated[list, operator.add]
    final_choice: str

def filter_node(state: State):
    # Logic to clean or validate input
    logger.info(json.dumps(state['input']['combined_pool']))
    return {"input": state}

# --- Parallel Nodes ---
def node_a(state: State): return {"results": ["Option A"]}
def node_b(state: State): return {"results": ["Option B"]}
def node_c(state: State): return {"results": ["Option C"]}

# --- The Orchestrator / Selector ---
def selector_node(state: State):
    # state["results"] will now contain ["Option A", "Option B", "Option C"]
    all_results = state["results"]
    
    # Logic to pick the best one
    best = f"Selected the best: {all_results[0]}" 
    return {"final_choice": best}

builder = StateGraph(State)

# ... (add your filter and parallel nodes as before) ...
builder.add_node("filter", filter_node)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)
builder.add_node("selector", selector_node)

# Orchestration logic
builder.add_edge(START, "filter")
# 1. Fan-out from filter
builder.add_edge("filter", "node_a")
builder.add_edge("filter", "node_b")
builder.add_edge("filter", "node_c")

# 2. Fan-in (Wait for all 3 to reach the selector)
builder.add_edge("node_a", "selector")
builder.add_edge("node_b", "selector")
builder.add_edge("node_c", "selector")

# 3. Final exit
builder.add_edge("selector", END)

graph = builder.compile()