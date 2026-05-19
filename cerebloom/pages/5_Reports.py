import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db import get_journal_entries, get_mood_entries, get_wellness_files
from utils.sentiment import MOOD_COLORS, mood_to_valence, mood_emoji

st.set_page_config(page_title="Reports · CereBloom", page_icon="📊", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #EDE8DC; }
    .report-section {
        background: #EDE8DC;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .rec-card {
        background: white;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        border-left: 3px solid #6B8F71;
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

st.title("📊 Reports")
st.markdown("A consolidated view of your emotional wellness — journals, moods, and uploaded data.")
st.markdown("---")

journal_entries = get_journal_entries()
mood_entries = get_mood_entries()
wellness_files = get_wellness_files()

if not journal_entries and not mood_entries:
    st.info("No data available yet. Journal and log moods to generate your first report.")
    st.stop()

period = st.selectbox("Report period", ["Last 7 days", "Last 30 days", "All time"])

now = datetime.now()
if period == "Last 7 days":
    cutoff = now - timedelta(days=7)
elif period == "Last 30 days":
    cutoff = now - timedelta(days=30)
else:
    cutoff = datetime(2000, 1, 1)

st.markdown(f"**Generated:** {now.strftime('%B %d, %Y at %H:%M')} · Period: **{period}**")
st.markdown("---")

df_journal = pd.DataFrame(journal_entries) if journal_entries else pd.DataFrame()
df_mood = pd.DataFrame(mood_entries) if mood_entries else pd.DataFrame()
df_files = pd.DataFrame(wellness_files) if wellness_files else pd.DataFrame()

if not df_journal.empty:
    df_journal["created_at"] = pd.to_datetime(df_journal["created_at"])
    df_journal_f = df_journal[df_journal["created_at"] >= cutoff]
    df_journal_f["sentiment"] = df_journal_f["sentiment"].fillna("Neutral")
else:
    df_journal_f = pd.DataFrame()

if not df_mood.empty:
    df_mood["created_at"] = pd.to_datetime(df_mood["created_at"])
    df_mood_f = df_mood[df_mood["created_at"] >= cutoff]
    df_mood_f = df_mood_f.copy()
    df_mood_f["valence"] = df_mood_f["mood"].apply(mood_to_valence)
else:
    df_mood_f = pd.DataFrame()

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric("Journal Entries", len(df_journal_f))
with col_b:
    st.metric("Mood Logs", len(df_mood_f))
with col_c:
    if not df_mood_f.empty:
        st.metric("Avg Intensity", f"{df_mood_f['intensity'].mean():.1f}/10")
    else:
        st.metric("Avg Intensity", "—")
with col_d:
    if not df_journal_f.empty and "sentiment_score" in df_journal_f.columns:
        st.metric("Avg Polarity", f"{df_journal_f['sentiment_score'].mean():+.3f}")
    else:
        st.metric("Avg Polarity", "—")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Mood Over Time")
    if not df_mood_f.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_mood_f["created_at"],
            y=df_mood_f["intensity"],
            mode="lines+markers",
            line=dict(color="#6B8F71", width=2),
            marker=dict(
                size=10,
                color=[MOOD_COLORS.get(m, "#8D8072") for m in df_mood_f["mood"]],
                line=dict(color="white", width=1)
            ),
            text=df_mood_f["mood"],
            hovertemplate="<b>%{text}</b><br>Intensity: %{y}<br>%{x|%b %d}<extra></extra>"
        ))
        fig.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", range=[0, 11], color="#8D8072"),
            margin=dict(l=10, r=10, t=10, b=10), height=240
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mood data for this period.")

with col2:
    st.subheader("Sentiment Breakdown")
    if not df_journal_f.empty:
        counts = df_journal_f["sentiment"].value_counts()
        sentiment_palette = {"Positive": "#6B8F71", "Negative": "#C0392B", "Neutral": "#8D8072"}
        fig2 = go.Figure(go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=[sentiment_palette.get(s, "#8D8072") for s in counts.index],
            text=counts.values,
            textposition="outside"
        ))
        fig2.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", color="#8D8072"),
            margin=dict(l=10, r=10, t=10, b=10), height=240, showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No journal data for this period.")

st.markdown("---")
st.subheader("Sentiment Summary")
if not df_journal_f.empty:
    pos = (df_journal_f["sentiment"] == "Positive").sum()
    neg = (df_journal_f["sentiment"] == "Negative").sum()
    neu = (df_journal_f["sentiment"] == "Neutral").sum()
    total = len(df_journal_f)
    avg_score = df_journal_f["sentiment_score"].mean() if "sentiment_score" in df_journal_f.columns else 0

    dominant = df_journal_f["sentiment"].value_counts().idxmax()
    dominant_pct = df_journal_f["sentiment"].value_counts(normalize=True).max() * 100

    st.markdown(f"""
    <div class="report-section">
        <strong>Journal Sentiment Analysis</strong><br><br>
        Of your <strong>{total}</strong> journal entries in this period:<br>
        &nbsp;&nbsp;✅ Positive: <strong>{pos}</strong> ({pos/total*100:.0f}%)<br>
        &nbsp;&nbsp;⚪ Neutral: <strong>{neu}</strong> ({neu/total*100:.0f}%)<br>
        &nbsp;&nbsp;❌ Negative: <strong>{neg}</strong> ({neg/total*100:.0f}%)<br><br>
        Your dominant sentiment is <strong>{dominant}</strong> ({dominant_pct:.0f}% of entries) with an average polarity of <strong>{avg_score:+.3f}</strong>.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No journal data for this period.")

if not df_mood_f.empty:
    top_mood = df_mood_f["mood"].value_counts().idxmax()
    top_mood_pct = df_mood_f["mood"].value_counts(normalize=True).max() * 100
    avg_int = df_mood_f["intensity"].mean()
    avg_val = df_mood_f["valence"].mean()
    mood_counts_str = ", ".join([f"{mood_emoji(m)} {m} ({c})" for m, c in df_mood_f["mood"].value_counts().items()])

    st.markdown(f"""
    <div class="report-section">
        <strong>Mood Tracking Summary</strong><br><br>
        You logged <strong>{len(df_mood_f)}</strong> mood entries: {mood_counts_str}<br><br>
        Most frequent: <strong>{mood_emoji(top_mood)} {top_mood}</strong> ({top_mood_pct:.0f}%)<br>
        Average intensity: <strong>{avg_int:.1f}/10</strong><br>
        Average emotional valence: <strong>{avg_val:+.2f}</strong> ({'leaning positive' if avg_val > 0.1 else 'leaning negative' if avg_val < -0.1 else 'broadly neutral'})
    </div>
    """, unsafe_allow_html=True)

if not df_files.empty:
    files_in_period = df_files.copy()
    files_in_period["uploaded_at"] = pd.to_datetime(files_in_period["uploaded_at"])
    files_in_period = files_in_period[files_in_period["uploaded_at"] >= cutoff]
    if not files_in_period.empty:
        sentiments = files_in_period["sentiment"].dropna().value_counts()
        st.markdown(f"""
        <div class="report-section">
            <strong>Wellness Files</strong><br><br>
            {len(files_in_period)} files uploaded in this period. Sentiments from file content: {", ".join([f"{s}: {c}" for s, c in sentiments.items()]) or "—"}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Recommendations")

recommendations = []

if not df_mood_f.empty:
    avg_val = df_mood_f["valence"].mean()
    avg_int = df_mood_f["intensity"].mean()
    stressed_pct = (df_mood_f["mood"] == "Stressed").mean()
    anxious_pct = (df_mood_f["mood"] == "Anxious").mean()

    if avg_val < -0.2:
        recommendations.append(("🌿", "Grounding Exercises", "Your emotional tone has been on the lower side. Try 5 minutes of box breathing or a short walk in nature each day."))
    if stressed_pct > 0.25:
        recommendations.append(("🧘", "Stress Management", f"You've logged Stressed {stressed_pct*100:.0f}% of the time. Consider identifying your top stressors and breaking tasks into smaller steps."))
    if anxious_pct > 0.2:
        recommendations.append(("📵", "Digital Detox", "Anxiety shows up frequently in your logs. Try a 30-minute phone-free window each evening to help your nervous system settle."))
    if avg_int > 7.5:
        recommendations.append(("✍️", "Expressive Journaling", "Your moods tend to be intense. Daily journaling can help you process and release strong emotions constructively."))
    if avg_val >= 0.3:
        recommendations.append(("🌟", "Maintain Your Momentum", "Your emotional tone is positive! Keep nurturing the habits and connections that are supporting your wellbeing."))

if not df_journal_f.empty:
    neg_pct = (df_journal_f["sentiment"] == "Negative").mean()
    if neg_pct > 0.4:
        recommendations.append(("💬", "Seek Connection", "Many of your journal entries carry a negative tone. Sharing how you feel with someone you trust can make a real difference."))
    if len(df_journal_f) < 3:
        recommendations.append(("📓", "Write More Often", "Journaling even 5 minutes a day can measurably improve emotional clarity and resilience. Try to make it a daily habit."))

if not recommendations:
    recommendations.append(("📈", "Keep Going", "You're building a valuable picture of your emotional health. The more data you log, the richer your insights will become."))

for icon, title, text in recommendations:
    st.markdown(f"""
    <div class="rec-card">
        <strong>{icon} {title}</strong><br>
        <span style="color:#5C5140; font-size:0.9rem;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("CereBloom is a personal wellness tool. It is not a substitute for professional mental health support. If you are struggling, please reach out to a qualified healthcare provider.")
