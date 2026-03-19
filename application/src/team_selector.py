import csv
import json
import os
import streamlit as st

st.set_page_config(page_title="CricketIQ – Dream XI Picker", layout="wide")

# ── Load squads ──────────────────────────────────────────────────────────────
SQUADS_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../ipl-dataset-2008-to-2025/ipl_2026_squads_mapped.json",
)
CITIES_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../ipl-dataset-2008-to-2025/ipl_venue_cities.csv",
)

@st.cache_data
def load_squads():
    with open(SQUADS_PATH) as f:
        return json.load(f)

@st.cache_data
def load_cities():
    with open(CITIES_PATH) as f:
        reader = csv.DictReader(f)
        return sorted({row["city"].strip() for row in reader if row["city"].strip()})

squads = load_squads()
team_names = sorted(squads.keys())
cities = load_cities()

# ── Helpers ───────────────────────────────────────────────────────────────────
ROLE_ICONS = {
    "Batter": "🏏",
    "Wicketkeeper-Batter": "🧤",
    "All-rounder": "⚡",
    "Bowler": "🎯",
}

ROLE_ORDER = ["Batter", "Wicketkeeper-Batter", "All-rounder", "Bowler"]


def player_card(player: dict, key: str, default_selected: bool) -> bool:
    """Render a single player row with a checkbox. Returns selection state."""
    icon = ROLE_ICONS.get(player["specialisation"], "👤")
    flag = "🇮🇳" if player["nationality"] == "India" else "🌍"
    label = f"{icon} {player['name']}  {flag}"
    return st.checkbox(label, value=default_selected, key=key)


def render_team_panel(team_key: str, squad_key: str):
    """Render the full team selection panel. Returns list of selected player dicts."""
    team_data = squads[squad_key]
    players = team_data["players"]

    # Group by role
    by_role = {role: [] for role in ROLE_ORDER}
    for p in players:
        role = p["specialisation"]
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(p)

    selected = []
    for role in ROLE_ORDER:
        role_players = by_role.get(role, [])
        if not role_players:
            continue
        st.markdown(f"**{ROLE_ICONS[role]} {role}s**")
        for p in role_players:
            cb_key = f"{team_key}__{p['name']}"
            is_probable = p.get("probableXi", False)
            chosen = player_card(p, cb_key, is_probable)
            if chosen:
                selected.append(p)
        st.divider()

    return selected


# ── Page header ───────────────────────────────────────────────────────────────
st.title("🏏 CricketIQ – Dream XI Picker")
st.markdown(
    "Select **Team A** and **Team B**, customise the probable XI for each, "
    "then let the AI agent choose the best **11 + 1 (Impact Player)** from the combined pool."
)

st.divider()

# ── Team selectors ────────────────────────────────────────────────────────────
col_a_sel, col_b_sel = st.columns(2)

with col_a_sel:
    default_a = team_names.index("Mumbai Indians") if "Mumbai Indians" in team_names else 0
    team_a = st.selectbox("🔵 Team A", team_names, index=default_a, key="team_a_select")

with col_b_sel:
    default_b = team_names.index("Chennai Super Kings") if "Chennai Super Kings" in team_names else 1
    team_b = st.selectbox("🔴 Team B", team_names, index=default_b, key="team_b_select")

if team_a == team_b:
    st.warning("⚠️ Please select two different teams.")
    st.stop()

default_city_idx = cities.index("Mumbai") if "Mumbai" in cities else 0
match_city = st.selectbox("📍 Match City", cities, index=default_city_idx, key="match_city_select")

st.divider()

# ── Player selection panels ───────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader(f"🔵 {team_a}")
    captain_a = squads[team_a].get("captain", "")
    st.caption(f"Captain: {captain_a}  |  Ground: {squads[team_a].get('home_ground', '')}")
    selected_a = render_team_panel("team_a", team_a)
    st.info(f"✅ {len(selected_a)} players selected")

with col_b:
    st.subheader(f"🔴 {team_b}")
    captain_b = squads[team_b].get("captain", "")
    st.caption(f"Captain: {captain_b}  |  Ground: {squads[team_b].get('home_ground', '')}")
    selected_b = render_team_panel("team_b", team_b)
    st.info(f"✅ {len(selected_b)} players selected")

st.divider()

# ── Summary banner ────────────────────────────────────────────────────────────
total = len(selected_a) + len(selected_b)
col_sum1, col_sum2, col_sum3 = st.columns(3)
col_sum1.metric("Team A selected", len(selected_a))
col_sum2.metric("Team B selected", len(selected_b))
col_sum3.metric("Combined pool", total)

if total < 11:
    st.warning(f"⚠️ You need at least 11 players in total. Currently {total} selected.")

# ── Pick Best XI button ───────────────────────────────────────────────────────
st.divider()

pick_clicked = st.button(
    "🤖 Let AI Pick the Best 11 + 1",
    type="primary",
    disabled=(total < 11),
    use_container_width=True,
)

if pick_clicked:
    combined = [
        {**p, "_team": team_a} for p in selected_a
    ] + [
        {**p, "_team": team_b} for p in selected_b
    ]

    # Store in session state for the AI agent to consume later
    st.session_state["combined_pool"] = combined
    st.session_state["team_a"] = team_a
    st.session_state["team_b"] = team_b
    st.session_state["match_city"] = match_city

    st.success("✅ Player pool locked in! AI agent thinking will appear here soon.")

    # ── Placeholder: show the pool as a preview ───────────────────────────────
    st.markdown("### 📋 Selected Player Pool")

    def pool_table(players, team_label):
        rows = []
        for p in players:
            rows.append({
                "Player": p["name"],
                "Role": p["specialisation"],
                "Nationality": p["nationality"],
            })
        if rows:
            st.markdown(f"**{team_label}**")
            st.table(rows)

    pool_table(selected_a, f"🔵 {team_a}")
    pool_table(selected_b, f"🔴 {team_b}")

    st.info(
        "🧠 **AI Agent thinking** will be displayed here in the next version. "
        "The agent will analyse historical IPL stats and pick the optimal XI + Impact Player."
    )
