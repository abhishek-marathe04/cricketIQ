import os
from pydantic import ValidationError
from langgraph_components.tools import call_batter_stats_vs_bowler, call_player_stats_per_season, call_player_stats_vs_bowler_type
from langgraph_components.pydantic_models import ParseIntentAndArguments
from utils.utilities import extract_json_from_response
from utils.llm import get_llm_client, get_model_name
from langgraph_components.prompts import prompt_template
from utils.logger import get_logger
from langchain_core.prompts import PromptTemplate
from config import ENV
function_call_counts = {}
logger = get_logger()


def parse_query_node(state):
    logger.info(f'Inside parse_query_node  : {state}')
    user_input = state["input"]
    
    name = 'parse_query_node'
    function_call_counts[name] = function_call_counts.get(name, 0) + 1
    
    logger.info(f"Function '{name}' has been called {function_call_counts[name]} times")
    prompt = PromptTemplate.from_template(prompt_template)

    try:
        formatted_prompt = prompt.format(query=user_input)

        # LLM
        logger.info(f'env : {ENV}')
        llm = get_llm_client(env=ENV)

        model = get_model_name(env=ENV)


        response = llm.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.2,
        )

        message_from_llm = response.choices[0].message.content
        logger.info(f'message_from_llm: {message_from_llm}')
        parsed_json = extract_json_from_response(message_from_llm)
        parsed_json_model = ParseIntentAndArguments(**parsed_json)
        logger.info(f'parsed_json_model: {parsed_json_model}')
        response_to_return = {
            "intent": parsed_json_model.intent,
            "args": parsed_json_model.arguments.model_dump()  # 👈 convert to plain dict
        }
        return {**state, **response_to_return}
        # return response_to_return
    except ValidationError as e:
        logger.error(f"Pydantic validation failed: {e}")
        return {"error": "Validation failed", "details": str(e)}
    except Exception as e:
        logger.error(f"Other error in parsing: {e}")
        return {"error": "Other parsing failure", "details": str(e)}


def run_player_stats_per_season(state):
    logger.info(f'run_player_stats: {state}')
    tool_args = state["args"]
    name = 'run_player_stats_per_season'
    function_call_counts[name] = function_call_counts.get(name, 0) + 1
    
    logger.info(f"Function '{name}' has been called {function_call_counts[name]} times")
    # result = call_player_stats.run(state["args"])  # try `.run()` instead of `.invoke()`
    table, graph = call_player_stats_per_season.invoke(tool_args)
    # result = 'Sample stats'
    return {**state, "result": {'table': table, 'graph': graph}}


def run_player_stats_vs_bowler_type(state):
    logger.info(f'run_player_stats_vs_bowler_type: {state}')
    name = 'run_player_stats_vs_bowler_type'
    function_call_counts[name] = function_call_counts.get(name, 0) + 1
    
    logger.info(f"Function '{name}' has been called {function_call_counts[name]} times")
    tool_args = state["args"]
    table, graph = call_player_stats_vs_bowler_type.invoke(tool_args)
    return {**state, "result": {'table': table, 'graph': graph}}


def run_batter_stats_vs_bowler(state):
    logger.info(f'run_batter_stats_vs_bowler: {state}')
    name = 'run_batter_stats_vs_bowler'
    function_call_counts[name] = function_call_counts.get(name, 0) + 1
    
    logger.info(f"Function '{name}' has been called {function_call_counts[name]} times")
    tool_args = state["args"]
    table, graph = call_batter_stats_vs_bowler.invoke(tool_args)
    return {**state, "result": {'table': table, 'graph': graph}}