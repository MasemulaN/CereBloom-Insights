import streamlit as st
from utils.db import init_db

st.set_page_config(
    page_title="CereBloom",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #EDE8DC;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .brand-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #3D3522;
        letter-spacing: 1px;
    }
    .brand-subtitle {
        font-size: 1rem;
        color: #6B8F71;
        font-style: italic;
        margin-top: -0.4rem;
    }
    .stat-card {
        background: #EDE8DC;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #6B8F71;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #6B8F71;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #8D8072;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .sentiment-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .divider {
        border: none;
        border-top: 1px solid #D5CCBA;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size:3rem;">🧠🌿</div>
        <div style="font-size:1.4rem; font-weight:700; color:#3D3522;">CereBloom</div>
        <div style="font-size:0.8rem; color:#6B8F71; font-style:italic;">Turning Emotions Into Insights</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Navigate**")
    st.page_link("app.py", label="🏠 Home", icon=None)
    st.page_link("pages/1_Journal.py", label="📓 Journal", icon=None)
    st.page_link("pages/2_Mood_Tracker.py", label="🎯 Mood Tracker", icon=None)
    st.page_link("pages/3_Insights.py", label="💡 Insights", icon=None)
    st.page_link("pages/4_Wellness_Data.py", label="📁 Wellness Data", icon=None)
    st.page_link("pages/5_Reports.py", label="📊 Reports", icon=None)
    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem; color:#8D8072; text-align:center;'>Your data stays on your device.</div>", unsafe_allow_html=True)

from utils.db import get_journal_entries, get_mood_entries, get_wellness_files
from utils.sentiment import mood_emoji, MOOD_COLORS
import pandas as pd
from datetime import datetime, timedelta

journal_entries = get_journal_entries()
mood_entries = get_mood_entries()
wellness_files = get_wellness_files()

st.markdown("""
<div class="main-header">
    <div class="brand-title">🧠🌿 CereBloom</div>
    <div class="brand-subtitle">Turning Emotions Into Insights</div>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(journal_entries)}</div>
        <div class="stat-label">Journal Entries</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(mood_entries)}</div>
        <div class="stat-label">Mood Logs</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(wellness_files)}</div>
        <div class="stat-label">Files Uploaded</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if mood_entries:
        latest_mood = mood_entries[0]["mood"]
        emoji = mood_emoji(latest_mood)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{emoji}</div>
            <div class="stat-label">Latest Mood: {latest_mood}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">—</div>
            <div class="stat-label">No Mood Yet</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Recent Journal Entries")
    if journal_entries:
        for entry in journal_entries[:3]:
            created = entry["created_at"][:10]
            sentiment = entry.get("sentiment", "Neutral") or "Neutral"
            score = entry.get("sentiment_score", 0.0) or 0.0
            badge_color = "#6B8F71" if sentiment == "Positive" else ("#C0392B" if sentiment == "Negative" else "#8D8072")
            with st.container():
                st.markdown(f"""
                <div style="background:#EDE8DC; border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.6rem; border-left:3px solid {badge_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#3D3522;">{entry['title']}</strong>
                        <span style="background:{badge_color}; color:white; border-radius:12px; padding:2px 10px; font-size:0.75rem;">{sentiment}</span>
                    </div>
                    <div style="color:#8D8072; font-size:0.8rem; margin-top:4px;">{created}</div>
                    <div style="color:#5C5140; font-size:0.85rem; margin-top:6px;">{entry['content'][:100]}{"..." if len(entry['content']) > 100 else ""}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No journal entries yet. Head to Journal to write your first entry.")

with col_right:
    st.subheader("Mood History (Last 7 Days)")
    if mood_entries:
        import plotly.graph_objects as go
        df = pd.DataFrame(mood_entries)
        df["created_at"] = pd.to_datetime(df["created_at"])
        cutoff = datetime.now() - timedelta(days=7)
        df_week = df[df["created_at"] >= cutoff].sort_values("created_at")

        if not df_week.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_week["created_at"],
                y=df_week["intensity"],
                mode="lines+markers",
                line=dict(color="#6B8F71", width=2),
                marker=dict(
                    size=10,
                    color=[MOOD_COLORS.get(m, "#8D8072") for m in df_week["mood"]],
                    line=dict(color="#3D3522", width=1)
                ),
                text=df_week["mood"],
                hovertemplate="<b>%{text}</b><br>Intensity: %{y}<br>%{x}<extra></extra>"
            ))
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#F5F0E8",
                plot_bgcolor="#F5F0E8",
                xaxis=dict(showgrid=False, color="#8D8072"),
                yaxis=dict(showgrid=True, gridcolor="#D5CCBA", range=[0, 11], color="#8D8072"),
                height=260,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No mood entries in the last 7 days.")
    else:
        st.info("No mood data yet. Visit Mood Tracker to log your first mood.")

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Getting Started")
cols = st.columns(3)
tips = [
    ("📓", "Write in your Journal", "Capture your thoughts and feelings daily. CereBloom will automatically analyze the sentiment of your writing."),
    ("🎯", "Track your Mood", "Log your mood and its intensity throughout the day to build a picture of your emotional patterns over time."),
    ("💡", "Discover Insights", "Visit the Insights page to see trends, sentiment distributions, and personalized observations about your wellbeing."),
]
for col, (icon, title, desc) in zip(cols, tips):
    with col:
        st.markdown(f"""
        <div style="background:#EDE8DC; border-radius:12px; padding:1.2rem; text-align:center;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:600; color:#3D3522; margin:0.5rem 0;">{title}</div>
            <div style="font-size:0.85rem; color:#5C5140;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
