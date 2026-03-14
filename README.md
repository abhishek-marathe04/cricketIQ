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

## 🗄️ Local Database Setup

### 1. Start PostgreSQL and pgAdmin via Docker

```bash
bash startup.sh
```

- PostgreSQL runs on `localhost:5432`
- pgAdmin runs on `http://localhost:5050` (login: `abc@gmail.com` / `postgres_cric`)

> When connecting pgAdmin to the database, use `host.docker.internal` as the host (not `localhost`), since pgAdmin runs inside Docker.

### 2. Create the Database and Schema

```bash
# Create the database
docker exec -it mypostgres psql -U postgres -c "CREATE DATABASE cricketiq;"

# Run the schema to create all tables
docker exec -i mypostgres psql -U postgres -d cricketiq < data_ingestion/cricketiq_db_schema.sql
```

### 3. Install Node Dependencies

```bash
cd data_ingestion
npm install
```

### 4. Insert Data (run in this order — foreign key dependencies)

```bash
# Step 1: Teams (referenced by almost everything else)
node insert_teams.js

# Step 2: Team aliases
node insertAliases.js

# Step 3: Players (bulk insert from match JSON files)
node load_players.js

# Step 4: Enrich player details (bat/bowl style, full name) from CSV
node get_player_detailed_data.js

# Step 5: Seasons (depends on teams)
node insertSeasonsData.js

# Step 6: Matches (depends on teams, seasons, players)
node insertMatchData.js

# Step 7: Ball-by-ball data (depends on matches, players, teams)
node insertBallByBallData.js

# Step 8: Player performance aggregates
node insertPlayerPerformanceData.js
```

### Adding New Players When Updating Match Data

When you download new match JSONs, first check if they contain any players not yet in the DB:

```bash
# Step 1: Extract all player names from new match JSONs
node -e "
const fs = require('fs'), path = require('path');
const folder = './dataset/matches_data';
const players = new Set();
fs.readdirSync(folder).filter(f => f.endsWith('.json')).forEach(f => {
  const data = JSON.parse(fs.readFileSync(path.join(folder, f)));
  Object.values(data.info.players || {}).flat().forEach(p => players.add(p));
});
console.log([...players].join('\n'));
" > /tmp/json_players.txt

# Step 2: Dump existing players from DB
docker exec -i mypostgres psql -U postgres -d cricketiq -t \
  -c "SELECT player_name FROM players" > /tmp/db_players.txt

# Step 3: Show players in JSONs but NOT in DB
comm -23 <(sort /tmp/json_players.txt) <(sort /tmp/db_players.txt)
```

Any names printed are new players. Then run `load_players.js` to insert them — it uses `ON CONFLICT DO NOTHING` so existing players are safely skipped:

```bash
node load_players.js
```

Watch the logs — `added successfully with id 1234` = new player inserted, `id null` = already existed.

### Adding New Players Manually

If a new player is **not present in any match JSON** (e.g. a new signing not yet in the dataset), insert them manually before running `get_player_detailed_data.js`, otherwise the detail enrichment step will skip them with a warning.

```sql
-- Run in pgAdmin Query Tool or psql
INSERT INTO players (player_name) VALUES ('New Player Name');
```

After inserting, add their details to `dataset/player_data/player_profile.csv` and re-run:

```bash
node get_player_detailed_data.js
```

Similarly, to add a new team manually:

```bash
# Edit insert_teams.js: change insertTeam("") to insertTeam("New Team Name")
node insert_teams.js
```

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
