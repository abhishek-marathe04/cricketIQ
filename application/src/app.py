
import uuid
from stats.common_functions.custom_exceptions import AmbiguousPlayerNameError, NoPlayerFoundError
from utils.logger import get_logger
import streamlit as st
from langgraph_components.main import graph  # your LangGraph runnable
from analytics import inject_analytics_script, track_event

logger = get_logger()
st.set_page_config(page_title="CricketIQ LLM", layout="wide")



inject_analytics_script()
st.title("🏏 CricketIQ Chat")

st.markdown("""
Welcome to **CricketIQ Chat** – your AI-powered cricket companion!  
Ask natural questions and get **instant insights** from IPL data – whether it's player performance, team matchups, or head-to-head stats.  
No filters, no dropdowns – just ask like you would to a cricket expert!

_Currently supports IPL data only. More formats coming soon!_  
""")

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
user_id = st.session_state.user_id


# Define sample prompts
sample_prompts = {
    'Fetch Player stats in season': '"How did Virat Kohli perform in season 2024?"',
    'Fetch Player stats vs bowler type': '"How does Rohit Sharma fare against pacers?"',
    'Fetch Batter stats vs bowler': '"How has Virat Kohli played against Bumrah?"',
    'Fetch Batter stats vs Team': '"Shubman Gill’s record vs MI, especially in Mumbai?"',
    'Fetch Team vs Team Stats': '"MI vs Csk stats"',
    "Particular Ipl Season Overview": "Ipl 2024 Overview"
}

with st.expander("📋 Show Sample Prompts"):
    st.write("Click the copy icon to use any of these prompts:")
    for name, text in sample_prompts.items():
        st.markdown(f"**{name}**")
        st.code(text, language="plaintext")
# Input field
user_input = st.text_input("Ask a question:")

# Track event when user types input
if user_input:
    track_event(user_id, "User Input Typed", {"input_text": user_input})

# Run on button click
if st.button("Ask") and user_input:
    # LangGraph invocation
    track_event(user_id, "User Submitted Query", {"query": user_input})
    try:
        result = graph.invoke({"input": user_input})
        inner_result = result.get("result", {})

        st.markdown(f"### 🧠 Query")
        st.markdown(f"`{user_input}`")
        # track_user_event(user_input, "Sucess")
        track_event(user_id, "Sucess", {"query": user_input})
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
            # track_error_event(error_msg, context="Rendering Graph/Table")
            track_event(user_id, "Error Occurred", {"error": str(error_msg)})
            st.error(error_msg)
    except NoPlayerFoundError as e:
        error_msg = str(e)
        st.warning(error_msg)  # Show a yellow warning box
        logger.error(error_msg)
        # track_error_event(error_msg, context="Bad User Query")
        track_event(user_id, "Error Occurred", {"error": str(e)})
    except AmbiguousPlayerNameError as e:
        error_msg = str(e)
        st.warning(error_msg)  # Show a yellow warning box
        logger.error(error_msg)
        # track_error_event(error_msg, context="Bad User Query")
        track_event(user_id, "Error Occurred", {"error": str(e)})
    except Exception as e:
        st.error("Oops! Something went wrong.")
        error_msg = str(e)
        logger.error(error_msg, exc_info=True)
        # track_error_event(error_msg, context="Generating LLM response")
        track_event(user_id, "Error Occurred", {"error": str(e)})