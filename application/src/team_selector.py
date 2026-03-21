import csv
import json
import os
import re
import streamlit as st
from team_selector_components.main import graph  # your LangGraph runnable
from stats.common_functions.custom_exceptions import AllModelsRateLimitedError

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
    width='stretch',
)

if pick_clicked:
    combined = [
        {**p, "_team": team_a} for p in selected_a
    ] + [
        {**p, "_team": team_b} for p in selected_b
    ]

    # Build a lookup for quick access to player metadata from the pool
    player_meta = {p["name"]: p for p in combined}

    st.session_state["combined_pool"] = combined
    st.session_state["team_a"] = team_a
    st.session_state["team_b"] = team_b
    st.session_state["match_city"] = match_city

    with st.spinner("🤖 AI agent is analysing stats and picking the best XI + 1…"):
        try:
            result = graph.invoke({"input": dict(st.session_state)})
        except AllModelsRateLimitedError:
            st.warning("⚠️ Unfortunately, the daily token limit has been reached. Please try again tomorrow!")
            st.stop()

    # ── Parse final_choice ────────────────────────────────────────────────────
    raw = result.get("final_choice", "[]")
    try:
        picks = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError):
        picks = []

    # ── Show stats used by AI ─────────────────────────────────────────────────
    def parse_stat_lines(text: str) -> list[dict]:
        """Parse pipe-delimited stat lines into a list of dicts for table display."""
        rows = []
        for line in text.strip().splitlines():
            parts = [p.strip() for p in line.split("|")]
            if not parts:
                continue
            row = {"Player": parts[0]}
            for part in parts[1:]:
                m = re.match(r"([^:]+):(.*)", part)
                if m:
                    row[m.group(1).strip()] = m.group(2).strip()
            rows.append(row)
        return rows

    venue_scores = result.get("venue_scores", {})
    vs_team_scores = result.get("vs_team_scores", {})
    recent_form_scores = result.get("recent_form_scores", "")

    with st.expander("📊 Stats used by AI  *(from IPL dataset — no internet)*", expanded=False):
        st.caption(
            "These are the only numbers the AI saw. All data is sourced from your local IPL dataset "
            f"(2008–2025), filtered for **{match_city}** venue and **{team_a} vs {team_b}** matchups."
        )
        tab_venue, tab_opp, tab_form = st.tabs(["🏟️ Venue Stats", "⚔️ vs Opposition Stats", "🔥 Recent Form"])

        with tab_venue:
            col_vb, col_vbw = st.columns(2)
            with col_vb:
                st.markdown("**Batters at venue**")
                vb_rows = parse_stat_lines(venue_scores.get("batters", ""))
                if vb_rows:
                    st.dataframe(vb_rows, width='stretch', hide_index=True)
                else:
                    st.caption("No data")
            with col_vbw:
                st.markdown("**Bowlers at venue**")
                vbw_rows = parse_stat_lines(venue_scores.get("bowlers", ""))
                if vbw_rows:
                    st.dataframe(vbw_rows, width='stretch', hide_index=True)
                else:
                    st.caption("No data")

        with tab_opp:
            col_ob, col_obw = st.columns(2)
            with col_ob:
                st.markdown("**Batters vs opposition**")
                ob_rows = parse_stat_lines(vs_team_scores.get("batters", ""))
                if ob_rows:
                    st.dataframe(ob_rows, width='stretch', hide_index=True)
                else:
                    st.caption("No data")
            with col_obw:
                st.markdown("**Bowlers vs opposition**")
                obw_rows = parse_stat_lines(vs_team_scores.get("bowlers", ""))
                if obw_rows:
                    st.dataframe(obw_rows, width='stretch', hide_index=True)
                else:
                    st.caption("No data")

        with tab_form:
            col_fb, col_fbw = st.columns(2)
            with col_fb:
                st.markdown("**Batters — last 5 matches**")
                fb_rows = parse_stat_lines(recent_form_scores.get("batters", ""))
                if fb_rows:
                    st.dataframe(fb_rows, width='stretch', hide_index=True)
                else:
                    st.caption("No data")
            with col_fbw:
                st.markdown("**Bowlers — last 5 matches**")
                fbw_rows = parse_stat_lines(recent_form_scores.get("bowlers", ""))
                if fbw_rows:
                    st.dataframe(fbw_rows, width='stretch', hide_index=True)
                else:
                    st.caption("No data")

    if picks:
        st.success(f"✅ AI has selected {len(picks)} players!")
        st.divider()
        st.markdown("## 🏆 AI Dream XI + 1")

        for i, pick in enumerate(picks, start=1):
            name = pick.get("player_name", "Unknown")
            reason = pick.get("reason", "")
            meta = player_meta.get(name, {})
            role = meta.get("specialisation", "")
            team = meta.get("_team", "")
            icon = ROLE_ICONS.get(role, "👤")
            team_color = "🔵" if team == team_a else "🔴"

            with st.container(border=True):
                col_num, col_info = st.columns([1, 11])
                col_num.markdown(f"### {i}")
                with col_info:
                    st.markdown(f"**{icon} {name}** &nbsp; {team_color} {team}")
                    st.caption(f"{role}")
                    st.write(reason)
    else:
        st.error("⚠️ Could not parse AI response. Raw output below:")
        st.text(raw)
