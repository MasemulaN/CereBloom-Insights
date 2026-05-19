import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.db import get_journal_entries, get_mood_entries
from utils.sentiment import MOOD_COLORS, mood_to_valence

st.set_page_config(page_title="Insights · CereBloom", page_icon="💡", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #EDE8DC; }
    .insight-box {
        background: #EDE8DC;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #6B8F71;
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
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Journal.py", label="📓 Journal")
    st.page_link("pages/2_Mood_Tracker.py", label="🎯 Mood Tracker")
    st.page_link("pages/3_Insights.py", label="💡 Insights")
    st.page_link("pages/4_Wellness_Data.py", label="📁 Wellness Data")
    st.page_link("pages/5_Reports.py", label="📊 Reports")

st.title("💡 Insights")
st.markdown("Understand your emotional patterns at a glance.")
st.markdown("---")

journal_entries = get_journal_entries()
mood_entries = get_mood_entries()

if not journal_entries and not mood_entries:
    st.info("No data yet. Write some journal entries and log moods to see your insights here.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Mood Trends")
    if mood_entries:
        df_mood = pd.DataFrame(mood_entries)
        df_mood["created_at"] = pd.to_datetime(df_mood["created_at"])
        df_mood = df_mood.sort_values("created_at")
        df_mood["valence"] = df_mood["mood"].apply(mood_to_valence)

        window = st.selectbox("Time window", ["Last 7 days", "Last 30 days", "All time"], key="mood_window")
        if window == "Last 7 days":
            cutoff = datetime.now() - timedelta(days=7)
        elif window == "Last 30 days":
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = df_mood["created_at"].min()
        df_mood_f = df_mood[df_mood["created_at"] >= cutoff]

        if not df_mood_f.empty:
            daily_avg = df_mood_f.groupby(df_mood_f["created_at"].dt.date).agg(
                avg_intensity=("intensity", "mean"),
                avg_valence=("valence", "mean"),
                count=("mood", "count")
            ).reset_index()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_avg["created_at"],
                y=daily_avg["avg_intensity"],
                name="Avg Intensity",
                mode="lines+markers",
                line=dict(color="#6B8F71", width=2),
                marker=dict(size=8)
            ))
            fig.update_layout(
                paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
                xaxis=dict(showgrid=False, color="#8D8072"),
                yaxis=dict(showgrid=True, gridcolor="#D5CCBA", range=[0, 11], color="#8D8072"),
                margin=dict(l=10, r=10, t=10, b=10), height=260,
                legend=dict(bgcolor="#F5F0E8")
            )
            st.plotly_chart(fig, use_container_width=True)

            top_mood = df_mood_f["mood"].value_counts().idxmax()
            avg_intensity = df_mood_f["intensity"].mean()
            avg_valence = df_mood_f["valence"].mean()
            st.markdown(f"""
            <div class="insight-box">
                <strong>Summary</strong><br>
                Most frequent mood: <strong>{top_mood}</strong><br>
                Average intensity: <strong>{avg_intensity:.1f}/10</strong><br>
                Average emotional valence: <strong>{avg_valence:+.2f}</strong> ({'positive' if avg_valence > 0 else 'negative' if avg_valence < 0 else 'neutral'})
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No mood data in the selected window.")
    else:
        st.info("No mood data yet.")

with col2:
    st.subheader("Sentiment Distribution")
    if journal_entries:
        df_journal = pd.DataFrame(journal_entries)
        df_journal["sentiment"] = df_journal["sentiment"].fillna("Neutral")
        sentiment_counts = df_journal["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]

        sentiment_palette = {"Positive": "#6B8F71", "Negative": "#C0392B", "Neutral": "#8D8072"}
        colors = [sentiment_palette.get(s, "#8D8072") for s in sentiment_counts["Sentiment"]]

        fig2 = go.Figure(go.Pie(
            labels=sentiment_counts["Sentiment"],
            values=sentiment_counts["Count"],
            marker=dict(colors=colors, line=dict(color="#F5F0E8", width=2)),
            hole=0.4,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} entries<extra></extra>"
        ))
        fig2.update_layout(
            paper_bgcolor="#F5F0E8",
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            legend=dict(bgcolor="#F5F0E8")
        )
        st.plotly_chart(fig2, use_container_width=True)

        pos = len(df_journal[df_journal["sentiment"] == "Positive"])
        neg = len(df_journal[df_journal["sentiment"] == "Negative"])
        neu = len(df_journal[df_journal["sentiment"] == "Neutral"])
        total = len(df_journal)
        avg_score = df_journal["sentiment_score"].mean()

        st.markdown(f"""
        <div class="insight-box">
            <strong>Summary</strong><br>
            Positive entries: <strong>{pos}</strong> ({pos/total*100:.0f}%)<br>
            Neutral entries: <strong>{neu}</strong> ({neu/total*100:.0f}%)<br>
            Negative entries: <strong>{neg}</strong> ({neg/total*100:.0f}%)<br>
            Average polarity: <strong>{avg_score:+.3f}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No journal data yet.")

st.markdown("---")
st.subheader("Emotional Pattern Summary")

insights = []

if mood_entries:
    df_mood = pd.DataFrame(mood_entries)
    df_mood["created_at"] = pd.to_datetime(df_mood["created_at"])
    df_mood["valence"] = df_mood["mood"].apply(mood_to_valence)
    top_mood = df_mood["mood"].value_counts().idxmax()
    avg_val = df_mood["valence"].mean()
    avg_int = df_mood["intensity"].mean()

    insights.append(f"Your most frequently logged mood is **{top_mood}**, suggesting this emotional state is particularly common for you.")

    if avg_val > 0.2:
        insights.append(f"Overall, your emotional tone skews **positive** (valence: {avg_val:+.2f}). You appear to spend more time in uplifting emotional states.")
    elif avg_val < -0.2:
        insights.append(f"Your emotional tone tends to be **negative** (valence: {avg_val:+.2f}). Consider mindfulness, journaling, or speaking to a trusted person when you feel this way.")
    else:
        insights.append(f"Your emotional tone is broadly **neutral** (valence: {avg_val:+.2f}), indicating a balanced emotional landscape with variation.")

    if avg_int > 7:
        insights.append(f"Your moods tend to be **high-intensity** (avg: {avg_int:.1f}/10). Whether positive or negative, you experience emotions quite strongly.")
    elif avg_int < 4:
        insights.append(f"Your moods tend to be **low-intensity** (avg: {avg_int:.1f}/10), suggesting a generally mild and stable emotional experience.")

    stressed_pct = (df_mood["mood"] == "Stressed").sum() / len(df_mood)
    if stressed_pct > 0.3:
        insights.append(f"You've logged **Stressed** {stressed_pct*100:.0f}% of the time. Consider exploring what situations or times of day trigger this, and try relaxation techniques.")

if journal_entries:
    df_j = pd.DataFrame(journal_entries)
    df_j["sentiment"] = df_j["sentiment"].fillna("Neutral")
    pos_pct = (df_j["sentiment"] == "Positive").mean()
    neg_pct = (df_j["sentiment"] == "Negative").mean()

    if pos_pct > 0.6:
        insights.append(f"Your journal writing is predominantly **positive** ({pos_pct*100:.0f}%). This suggests a generally optimistic thinking style.")
    elif neg_pct > 0.5:
        insights.append(f"A significant portion of your journal entries ({neg_pct*100:.0f}%) express **negative sentiment**. Writing is a healthy outlet — keep it up, and seek support if needed.")

    insights.append(f"You have written **{len(journal_entries)} journal entries** so far. Consistent journaling is associated with improved emotional awareness.")

if not insights:
    st.info("Log more moods and write more journal entries to unlock personalized insights.")
else:
    for i, insight in enumerate(insights):
        icon = "🌱" if i % 3 == 0 else ("💬" if i % 3 == 1 else "📌")
        st.markdown(f"""
        <div class="insight-box">
            {icon} {insight}
        </div>
        """, unsafe_allow_html=True)
