# 🏏 CricketIQ App

This is an interactive application that visualizes IPL player and team performance using natural language queries. Built with **Streamlit**, **LangGraph**, and **Pandas**, the app helps uncover deep cricket insights using AI-powered querying and beautiful visualizations.

## 🚀 Features

- Query player stats across seasons or against teams/bowler types
- Team vs team performance comparisons
- Natural language input using LLM with LangGraph
- Graphs powered by Plotly, displayed in Streamlit
- Weekly refreshed IPL data for fast analysis

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend Logic**: LangGraph + LangChain
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy

## 📁 Project Structure

```plaintext
application/
├── src/
│   ├── langgraph_components/    # LangGraph nodes, tools, prompts, and pydantic models for routing user queries
│   ├── stats/                   # Main statistics processing
│   │   ├── common_functions/     # Common reusable functions for player and team stats
│   │   ├── player/               # Functions related to player statistics (vs bowler, vs team, in season, etc.)
│   │   ├── team/                 # Functions related to team-level analytics (team vs team, season overview)
│   │   └── utils/                # Utility scripts for app configuration and analytics
│   └── app.py                   # Entry point for Streamlit app
│   └── config.py                # App configuration settings
data_ingestion/
├── dataset/                     # Finalized CSV datasets (ball-by-ball, matches, players, teams)
├── *.js                          # Scripts to insert and prepare IPL data into SQL database
├── cricketiq_db_schema.sql       # SQL schema for database design
├── data_analytics_script.py      # Scripts to analyze and clean the dataset
ipl-dataset-2008-to-2025/
├── ball_by_ball_data.csv         # Main ball-by-ball data
├── ipl_matches_data.csv          # Match-level data
├── players-data-updated.csv      # Player metadata
├── team_aliases.csv              # Mapping of team aliases to proper team names
├── teams_data.csv                # Team metadata
README.md                         # Project overview and instructions
requirements.txt                  # Python package dependencies
startup.sh                        # Startup script
```

## 📥 Data Ingestion Process

- Sourced IPL ball-by-ball JSON data from [Cricsheet.com](https://cricsheet.org/). Huge thanks to them!
- Created a relational SQL database to structure the data for more effective querying.
- Exported the required tables into CSV format to make them easier to load and use in the project.
- Fine-tuned data queries extensively using Kaggle notebooks before final integration.
- Developed common reusable Python functions to generate different types of stats (player, team, head-to-head, etc.).
- These reusable functions are used throughout the app to ensure consistency and reduce duplication.

## 🛠️ Pre-Work for the Project

- Cleaned and transformed the raw JSON data into structured formats.
- Verified data consistency, created required joins, and formatted it season-wise.
- Optimized and tested queries on Kaggle to ensure fast performance.
- Finalized a set of utility functions for stats extraction, graph generation, and table creation.
- Ensured reusability of components for faster extension of app features.

## ⚙️ How It Works

- The app uses **LangGraph**, where LLMs (Large Language Models) are responsible for understanding user queries in plain English.
- The LLMs return the **function name** and the **arguments** that the app needs to execute.
- A **Router** is implemented in the LangGraph app that directs the flow based on the function name.
- Specific nodes are triggered to run the appropriate logic (like fetching player stats, team stats, head-to-head stats, etc.).
- These nodes filter and process the dataframes, and generate visualizations using Plotly.
- The final graphs and tables are passed back to the Streamlit frontend, where they are beautifully rendered for the user.
