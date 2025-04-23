from stats.common_functions.custom_exceptions import AmbiguousPlayerNameError, NoPlayerFoundError
from utils.logger import get_logger
import streamlit as st
from langgraph_components.main import graph  # your LangGraph runnable
from analytics import inject_ga_script, track_user_event, track_error_event

logger = get_logger()

st.set_page_config(page_title="CricketIQ LLM", layout="wide")
st.title("🏏 CricketIQ Chat")

st.markdown("""
Welcome to **CricketIQ Chat** – your AI-powered cricket companion!  
Ask natural questions and get **instant insights** from IPL data – whether it's player performance, team matchups, or head-to-head stats.  
No filters, no dropdowns – just ask like you would to a cricket expert!

_Currently supports IPL data only. More formats coming soon!_  
""")

inject_ga_script()

# Define sample prompts
sample_prompts = {
    'Fetch Player stats in season': '"Show me stats of Virat Kohli in 2024"',
    'Fetch Player stats vs bowler type': '"Show me stats of Rohit Sharma vs fast bowlers"',
    'Fetch Batter stats vs bowler': '"Show me stats of Virat Kohli vs Jasprit Bumrah"',
}

with st.expander("📋 Show Sample Prompts"):
    st.write("Click the copy icon to use any of these prompts:")
    for name, text in sample_prompts.items():
        st.markdown(f"**{name}**")
        st.text_input(label="", value=text, key=name)
# Input field
user_input = st.text_input("Ask a question:")

# Run on button click
if st.button("Ask") and user_input:
    # LangGraph invocation
    try:
        result = graph.invoke({"input": user_input})
        inner_result = result.get("result", {})

        st.markdown(f"### 🧠 Query")
        st.markdown(f"`{user_input}`")
        track_user_event(user_input, "Sucess")
        if isinstance(inner_result, dict) and "table" in inner_result and "graph" in inner_result:
            st.markdown("### 📊 Summary Table")
            st.plotly_chart(inner_result["table"])

            # st.markdown("### 📈 Graph")
            # st.plotly_chart(inner_result["graph"])
            graphs = inner_result["graph"]

            if isinstance(graphs, list):
                st.markdown("### 📊 Visualizations")
                for i, fig in enumerate(graphs):
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Single graph fallback
                st.plotly_chart(graphs)
        else:
            error_msg = "⚠️ No valid 'table' or 'graph' returned from the model."
            track_error_event(error_msg, context="Rendering Graph/Table")
            st.error(error_msg)
    except NoPlayerFoundError as e:
        error_msg = str(e)
        st.warning(error_msg)  # Show a yellow warning box
        logger.error(error_msg)
        track_error_event(error_msg, context="Bad User Query")
    except AmbiguousPlayerNameError as e:
        error_msg = str(e)
        st.warning(error_msg)  # Show a yellow warning box
        logger.error(error_msg)
        track_error_event(error_msg, context="Bad User Query")
    except Exception as e:
        st.error("Oops! Something went wrong.")
        error_msg = str(e)
        logger.error(error_msg, exc_info=True)
        track_error_event(error_msg, context="Generating LLM response")