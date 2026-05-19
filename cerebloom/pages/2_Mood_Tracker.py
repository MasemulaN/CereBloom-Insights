import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.db import save_mood_entry, get_mood_entries
from utils.sentiment import mood_emoji, MOOD_COLORS, mood_to_valence

st.set_page_config(page_title="Mood Tracker · CereBloom", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #EDE8DC; }
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
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Journal.py", label="📓 Journal")
    st.page_link("pages/2_Mood_Tracker.py", label="🎯 Mood Tracker")
    st.page_link("pages/3_Insights.py", label="💡 Insights")
    st.page_link("pages/4_Wellness_Data.py", label="📁 Wellness Data")
    st.page_link("pages/5_Reports.py", label="📊 Reports")

MOODS = ["Happy", "Calm", "Neutral", "Stressed", "Sad", "Angry", "Anxious"]

st.title("🎯 Mood Tracker")
st.markdown("Log how you feel right now. Track patterns over time.")
st.markdown("---")

tab_log, tab_history = st.tabs(["➕ Log Mood", "📈 Mood History"])

with tab_log:
    st.subheader("How are you feeling?")
    cols = st.columns(len(MOODS))
    selected_mood = st.session_state.get("selected_mood", None)

    for i, mood in enumerate(MOODS):
        with cols[i]:
            emoji = mood_emoji(mood)
            color = MOOD_COLORS[mood]
            border = f"3px solid {color}" if selected_mood == mood else "2px solid #D5CCBA"
            if st.button(f"{emoji}\n{mood}", key=f"mood_{mood}", use_container_width=True):
                st.session_state["selected_mood"] = mood
                st.rerun()
            st.markdown(f"<div style='height:4px; background:{color}; border-radius:2px; margin-top:-8px;'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    selected_mood = st.session_state.get("selected_mood", None)
    if selected_mood:
        st.markdown(f"**Selected:** {mood_emoji(selected_mood)} {selected_mood}")
        emoji = mood_emoji(selected_mood)
        color = MOOD_COLORS[selected_mood]
        st.markdown(f"<div style='background:{color}20; border-left:4px solid {color}; padding:0.8rem 1rem; border-radius:8px; margin-bottom:1rem;'><strong>{emoji} {selected_mood}</strong> selected</div>", unsafe_allow_html=True)

    intensity = st.slider(
        "Intensity (1 = very mild · 10 = very intense)",
        min_value=1, max_value=10, value=5
    )
    note = st.text_input("Optional note", placeholder="What triggered this feeling? (optional)")

    if st.button("💾 Save Mood Log", use_container_width=True, disabled=(not selected_mood)):
        if selected_mood:
            save_mood_entry(selected_mood, intensity, note)
            st.success(f"Mood logged: {mood_emoji(selected_mood)} **{selected_mood}** at intensity {intensity}.")
            del st.session_state["selected_mood"]
            st.rerun()

with tab_history:
    entries = get_mood_entries()
    if not entries:
        st.info("No mood entries yet. Log your first mood above!")
    else:
        df = pd.DataFrame(entries)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df = df.sort_values("created_at")
        df["valence"] = df["mood"].apply(mood_to_valence)
        df["date"] = df["created_at"].dt.date

        period = st.selectbox("Time range", ["Last 7 days", "Last 30 days", "All time"], index=0)
        if period == "Last 7 days":
            cutoff = datetime.now() - timedelta(days=7)
        elif period == "Last 30 days":
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = df["created_at"].min()

        df_filtered = df[df["created_at"] >= cutoff]

        if df_filtered.empty:
            st.info(f"No entries in the selected period.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Mood Intensity Over Time**")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_filtered["created_at"],
                    y=df_filtered["intensity"],
                    mode="lines+markers",
                    line=dict(color="#6B8F71", width=2),
                    marker=dict(
                        size=12,
                        color=[MOOD_COLORS.get(m, "#8D8072") for m in df_filtered["mood"]],
                        line=dict(color="white", width=1.5)
                    ),
                    text=df_filtered["mood"],
                    hovertemplate="<b>%{text}</b><br>Intensity: %{y}<br>%{x|%b %d %H:%M}<extra></extra>"
                ))
                fig.update_layout(
                    paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
                    xaxis=dict(showgrid=False, color="#8D8072"),
                    yaxis=dict(showgrid=True, gridcolor="#D5CCBA", range=[0, 11], color="#8D8072", title="Intensity"),
                    margin=dict(l=10, r=10, t=10, b=10), height=300
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**Mood Distribution**")
                mood_counts = df_filtered["mood"].value_counts().reset_index()
                mood_counts.columns = ["mood", "count"]
                mood_counts["color"] = mood_counts["mood"].map(MOOD_COLORS)
                fig2 = go.Figure(go.Bar(
                    x=mood_counts["mood"],
                    y=mood_counts["count"],
                    marker_color=mood_counts["color"],
                    text=mood_counts["count"],
                    textposition="outside",
                ))
                fig2.update_layout(
                    paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
                    xaxis=dict(showgrid=False, color="#8D8072"),
                    yaxis=dict(showgrid=True, gridcolor="#D5CCBA", color="#8D8072"),
                    margin=dict(l=10, r=10, t=10, b=10), height=300,
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("**Valence Trend** *(positive → negative emotional tone)*")
            fig3 = go.Figure()
            fig3.add_hrect(y0=0, y1=1.1, fillcolor="#6B8F7130", line_width=0, annotation_text="Positive zone", annotation_position="top left")
            fig3.add_hrect(y0=-1.1, y1=0, fillcolor="#C0392B20", line_width=0, annotation_text="Negative zone", annotation_position="bottom left")
            fig3.add_trace(go.Scatter(
                x=df_filtered["created_at"],
                y=df_filtered["valence"],
                mode="lines+markers",
                line=dict(color="#6B8F71", width=2),
                marker=dict(size=8, color=[MOOD_COLORS.get(m, "#8D8072") for m in df_filtered["mood"]]),
                text=df_filtered["mood"],
                hovertemplate="<b>%{text}</b><br>Valence: %{y:.2f}<extra></extra>"
            ))
            fig3.add_hline(y=0, line_dash="dash", line_color="#8D8072", opacity=0.5)
            fig3.update_layout(
                paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
                xaxis=dict(showgrid=False, color="#8D8072"),
                yaxis=dict(showgrid=False, range=[-1.2, 1.2], color="#8D8072", title="Emotional Valence"),
                margin=dict(l=10, r=10, t=20, b=10), height=280
            )
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown("**Recent Log**")
            display_df = df_filtered[["created_at", "mood", "intensity", "note"]].copy()
            display_df = display_df.sort_values("created_at", ascending=False)
            display_df["created_at"] = display_df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
            display_df.columns = ["Date", "Mood", "Intensity", "Note"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
