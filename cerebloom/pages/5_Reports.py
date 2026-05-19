import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.db import get_journal_entries, get_mood_entries, get_wellness_files
from utils.sentiment import MOOD_COLORS, mood_to_valence, mood_emoji, sentiment_color

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
    .highlight-card {
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }
    .section-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8D8072;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }
    .stat-row {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }
    .stat-chip {
        background: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: #3D3522;
        border: 1px solid #D5CCBA;
    }
    .entry-row {
        background: white;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.4rem;
        border-left: 4px solid #D5CCBA;
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
st.markdown("A detailed view of your emotional wellness — journals, moods, and patterns over time.")
st.markdown("---")

journal_entries = get_journal_entries()
mood_entries = get_mood_entries()
wellness_files = get_wellness_files()

if not journal_entries and not mood_entries:
    st.info("No data available yet. Write journal entries and log moods to generate your first report.")
    st.stop()

col_period, col_gen = st.columns([2, 3])
with col_period:
    period = st.selectbox("Report period", ["Last 7 days", "Last 30 days", "All time"])
with col_gen:
    st.markdown(f"<div style='padding-top:2rem; color:#8D8072; font-size:0.85rem;'>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</div>", unsafe_allow_html=True)

now = datetime.now()
if period == "Last 7 days":
    cutoff = now - timedelta(days=7)
elif period == "Last 30 days":
    cutoff = now - timedelta(days=30)
else:
    cutoff = datetime(2000, 1, 1)

# ── Prepare DataFrames ──────────────────────────────────────────────────────
df_journal = pd.DataFrame(journal_entries) if journal_entries else pd.DataFrame()
df_mood    = pd.DataFrame(mood_entries)    if mood_entries    else pd.DataFrame()
df_files   = pd.DataFrame(wellness_files)  if wellness_files  else pd.DataFrame()

if not df_journal.empty:
    df_journal["created_at"] = pd.to_datetime(df_journal["created_at"])
    df_journal_f = df_journal[df_journal["created_at"] >= cutoff].copy()
    df_journal_f["sentiment"] = df_journal_f["sentiment"].fillna("Neutral")
    df_journal_f["sentiment_score"] = df_journal_f["sentiment_score"].fillna(0.0)
    df_journal_f["word_count"] = df_journal_f["content"].apply(lambda x: len(str(x).split()))
    df_journal_f["char_count"] = df_journal_f["content"].apply(lambda x: len(str(x)))
    df_journal_f["date"] = df_journal_f["created_at"].dt.date
    df_journal_f["day_of_week"] = df_journal_f["created_at"].dt.day_name()
    df_journal_f = df_journal_f.sort_values("created_at")
else:
    df_journal_f = pd.DataFrame()

if not df_mood.empty:
    df_mood["created_at"] = pd.to_datetime(df_mood["created_at"])
    df_mood_f = df_mood[df_mood["created_at"] >= cutoff].copy()
    df_mood_f["valence"] = df_mood_f["mood"].apply(mood_to_valence)
    df_mood_f["date"] = df_mood_f["created_at"].dt.date
    df_mood_f["day_of_week"] = df_mood_f["created_at"].dt.day_name()
    df_mood_f = df_mood_f.sort_values("created_at")
else:
    df_mood_f = pd.DataFrame()

# ── Top-level KPI row ────────────────────────────────────────────────────────
st.markdown("---")
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.metric("Journal Entries", len(df_journal_f))
with kpi2:
    st.metric("Mood Logs", len(df_mood_f))
with kpi3:
    if not df_journal_f.empty:
        st.metric("Avg Words/Entry", f"{df_journal_f['word_count'].mean():.0f}")
    else:
        st.metric("Avg Words/Entry", "—")
with kpi4:
    if not df_journal_f.empty:
        st.metric("Avg Polarity", f"{df_journal_f['sentiment_score'].mean():+.3f}")
    else:
        st.metric("Avg Polarity", "—")
with kpi5:
    if not df_mood_f.empty:
        st.metric("Avg Intensity", f"{df_mood_f['intensity'].mean():.1f}/10")
    else:
        st.metric("Avg Intensity", "—")
with kpi6:
    if not df_mood_f.empty:
        avg_val = df_mood_f["valence"].mean()
        tone = "Positive" if avg_val > 0.1 else ("Negative" if avg_val < -0.1 else "Neutral")
        st.metric("Emotional Tone", tone, delta=f"{avg_val:+.2f}")
    else:
        st.metric("Emotional Tone", "—")

st.markdown("---")

# ════════════════════════════════════════════════════════════
#  SECTION 1 — JOURNAL DEEP-DIVE
# ════════════════════════════════════════════════════════════
st.header("📓 Journal Report")

if df_journal_f.empty:
    st.info("No journal entries for this period.")
else:
    # 1a. Sentiment polarity over time
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Sentiment Polarity Over Time")
        fig_pol = go.Figure()
        fig_pol.add_hrect(y0=0.1, y1=1.05, fillcolor="#6B8F7118", line_width=0)
        fig_pol.add_hrect(y0=-1.05, y1=-0.1, fillcolor="#C0392B18", line_width=0)
        fig_pol.add_hline(y=0, line_dash="dash", line_color="#8D8072", opacity=0.5)
        colors_pol = [sentiment_color(s) for s in df_journal_f["sentiment"]]
        fig_pol.add_trace(go.Scatter(
            x=df_journal_f["created_at"],
            y=df_journal_f["sentiment_score"],
            mode="lines+markers",
            line=dict(color="#6B8F71", width=2),
            marker=dict(size=10, color=colors_pol, line=dict(color="white", width=1.5)),
            text=df_journal_f["title"],
            customdata=df_journal_f["sentiment"],
            hovertemplate="<b>%{text}</b><br>Sentiment: %{customdata}<br>Polarity: %{y:+.3f}<br>%{x|%b %d}<extra></extra>"
        ))
        # Rolling average if enough points
        if len(df_journal_f) >= 3:
            rolling = df_journal_f.set_index("created_at")["sentiment_score"].rolling("3D", min_periods=1).mean().reset_index()
            fig_pol.add_trace(go.Scatter(
                x=rolling["created_at"],
                y=rolling["sentiment_score"],
                mode="lines",
                line=dict(color="#3D3522", width=1.5, dash="dot"),
                name="3-day avg",
                hoverinfo="skip"
            ))
        fig_pol.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", range=[-1.1, 1.1], color="#8D8072", title="Polarity"),
            margin=dict(l=10, r=10, t=10, b=10), height=280,
            legend=dict(bgcolor="#F5F0E8", font=dict(size=11)),
            showlegend=len(df_journal_f) >= 3
        )
        st.plotly_chart(fig_pol, use_container_width=True)

    with col_chart2:
        st.subheader("Sentiment Distribution")
        sentiment_palette = {"Positive": "#6B8F71", "Negative": "#C0392B", "Neutral": "#8D8072"}
        counts = df_journal_f["sentiment"].value_counts()
        fig_dist = go.Figure(go.Pie(
            labels=counts.index,
            values=counts.values,
            marker=dict(colors=[sentiment_palette.get(s, "#8D8072") for s in counts.index],
                        line=dict(color="#F5F0E8", width=2)),
            hole=0.45,
            textinfo="label+percent+value",
            hovertemplate="%{label}: %{value} entries (%{percent})<extra></extra>"
        ))
        fig_dist.update_layout(
            paper_bgcolor="#F5F0E8",
            margin=dict(l=10, r=10, t=10, b=10), height=280,
            legend=dict(bgcolor="#F5F0E8")
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    # 1b. Writing activity & word count
    col_act, col_wc = st.columns(2)

    with col_act:
        st.subheader("Writing Activity by Day of Week")
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_counts = df_journal_f["day_of_week"].value_counts().reindex(day_order, fill_value=0)
        day_avg_pol = df_journal_f.groupby("day_of_week")["sentiment_score"].mean().reindex(day_order, fill_value=0)
        fig_dow = go.Figure()
        fig_dow.add_trace(go.Bar(
            x=day_order,
            y=day_counts.values,
            name="Entries",
            marker_color="#6B8F71",
            text=day_counts.values,
            textposition="outside",
        ))
        fig_dow.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", color="#8D8072", title="Entries"),
            margin=dict(l=10, r=10, t=10, b=10), height=250, showlegend=False
        )
        st.plotly_chart(fig_dow, use_container_width=True)

    with col_wc:
        st.subheader("Word Count per Entry")
        fig_wc = go.Figure()
        fig_wc.add_trace(go.Bar(
            x=df_journal_f["created_at"].dt.strftime("%b %d"),
            y=df_journal_f["word_count"],
            marker_color=[sentiment_color(s) for s in df_journal_f["sentiment"]],
            text=df_journal_f["word_count"],
            textposition="outside",
            hovertext=df_journal_f["title"],
            hovertemplate="<b>%{hovertext}</b><br>Words: %{y}<extra></extra>"
        ))
        fig_wc.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", color="#8D8072", title="Words"),
            margin=dict(l=10, r=10, t=10, b=10), height=250, showlegend=False
        )
        st.plotly_chart(fig_wc, use_container_width=True)

    # 1c. Journal writing statistics
    st.subheader("Writing Statistics")
    total_words = df_journal_f["word_count"].sum()
    avg_words   = df_journal_f["word_count"].mean()
    max_words   = df_journal_f["word_count"].max()
    min_words   = df_journal_f["word_count"].min()
    avg_score   = df_journal_f["sentiment_score"].mean()
    max_score   = df_journal_f["sentiment_score"].max()
    min_score   = df_journal_f["sentiment_score"].min()
    pos_streak  = 0
    cur_streak  = 0
    for s in df_journal_f["sentiment"]:
        if s == "Positive":
            cur_streak += 1
            pos_streak = max(pos_streak, cur_streak)
        else:
            cur_streak = 0

    stat_cols = st.columns(4)
    stat_cols[0].metric("Total Words Written", f"{total_words:,}")
    stat_cols[1].metric("Average Words / Entry", f"{avg_words:.0f}")
    stat_cols[2].metric("Longest Entry", f"{max_words} words")
    stat_cols[3].metric("Shortest Entry", f"{min_words} words")

    stat_cols2 = st.columns(4)
    stat_cols2[0].metric("Highest Polarity Entry", f"{max_score:+.3f}")
    stat_cols2[1].metric("Lowest Polarity Entry",  f"{min_score:+.3f}")
    stat_cols2[2].metric("Avg Polarity",            f"{avg_score:+.3f}")
    stat_cols2[3].metric("Longest Positive Streak", f"{pos_streak} entries")

    # 1d. Most positive and most negative entries
    st.subheader("Entry Highlights")
    hi_col, lo_col = st.columns(2)

    most_pos = df_journal_f.loc[df_journal_f["sentiment_score"].idxmax()]
    most_neg = df_journal_f.loc[df_journal_f["sentiment_score"].idxmin()]

    with hi_col:
        st.markdown("<div class='section-label'>Most Positive Entry</div>", unsafe_allow_html=True)
        excerpt = str(most_pos["content"])[:200] + ("…" if len(str(most_pos["content"])) > 200 else "")
        st.markdown(f"""
        <div class="highlight-card" style="background:#6B8F7115; border-left:4px solid #6B8F71;">
            <strong style="color:#3D3522;">{most_pos['title']}</strong>
            <span style="float:right; background:#6B8F71; color:white; border-radius:10px; padding:1px 9px; font-size:0.8rem;">{most_pos['sentiment_score']:+.3f}</span><br>
            <span style="color:#8D8072; font-size:0.78rem;">{str(most_pos['created_at'])[:16]}</span><br><br>
            <span style="color:#5C5140; font-size:0.88rem;">{excerpt}</span>
        </div>
        """, unsafe_allow_html=True)

    with lo_col:
        st.markdown("<div class='section-label'>Most Challenging Entry</div>", unsafe_allow_html=True)
        excerpt2 = str(most_neg["content"])[:200] + ("…" if len(str(most_neg["content"])) > 200 else "")
        st.markdown(f"""
        <div class="highlight-card" style="background:#C0392B15; border-left:4px solid #C0392B;">
            <strong style="color:#3D3522;">{most_neg['title']}</strong>
            <span style="float:right; background:#C0392B; color:white; border-radius:10px; padding:1px 9px; font-size:0.8rem;">{most_neg['sentiment_score']:+.3f}</span><br>
            <span style="color:#8D8072; font-size:0.78rem;">{str(most_neg['created_at'])[:16]}</span><br><br>
            <span style="color:#5C5140; font-size:0.88rem;">{excerpt2}</span>
        </div>
        """, unsafe_allow_html=True)

    # 1e. Full entry-by-entry breakdown
    st.subheader("Entry-by-Entry Breakdown")
    df_display = df_journal_f[["created_at", "title", "sentiment", "sentiment_score", "word_count"]].copy()
    df_display = df_display.sort_values("created_at", ascending=False)
    df_display["created_at"] = df_display["created_at"].dt.strftime("%Y-%m-%d %H:%M")
    df_display.columns = ["Date", "Title", "Sentiment", "Polarity", "Words"]

    sentiment_palette = {"Positive": "#6B8F71", "Negative": "#C0392B", "Neutral": "#8D8072"}

    for _, row in df_display.iterrows():
        color = sentiment_palette.get(row["Sentiment"], "#8D8072")
        st.markdown(f"""
        <div class="entry-row" style="border-left-color: {color};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; color:#3D3522;">{row['Title']}</span>
                <span style="background:{color}; color:white; border-radius:10px; padding:1px 10px; font-size:0.78rem; font-weight:600;">{row['Sentiment']}</span>
            </div>
            <div style="display:flex; gap:1.5rem; margin-top:4px;">
                <span style="color:#8D8072; font-size:0.78rem;">📅 {row['Date']}</span>
                <span style="color:#8D8072; font-size:0.78rem;">📊 Polarity: <strong style="color:#3D3522;">{row['Polarity']:+.3f}</strong></span>
                <span style="color:#8D8072; font-size:0.78rem;">✍️ {row['Words']} words</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 1f. Sentiment narrative summary
    st.markdown("---")
    st.subheader("Journal Sentiment Summary")
    pos_n = (df_journal_f["sentiment"] == "Positive").sum()
    neg_n = (df_journal_f["sentiment"] == "Negative").sum()
    neu_n = (df_journal_f["sentiment"] == "Neutral").sum()
    total_n = len(df_journal_f)
    dominant = df_journal_f["sentiment"].value_counts().idxmax()
    dominant_pct = df_journal_f["sentiment"].value_counts(normalize=True).max() * 100
    most_active_day = df_journal_f["day_of_week"].value_counts().idxmax() if not df_journal_f.empty else "—"
    avg_pol = df_journal_f["sentiment_score"].mean()

    if avg_pol > 0.2:
        tone_narrative = "Your writing reflects a generally optimistic and constructive mindset during this period."
    elif avg_pol < -0.2:
        tone_narrative = "Your writing carries some emotional weight during this period — a sign you're processing real challenges."
    else:
        tone_narrative = "Your writing reflects a balanced emotional state, touching on both positive and difficult themes."

    st.markdown(f"""
    <div class="report-section">
        <strong>📓 Journal Analysis — {period}</strong><br><br>
        You wrote <strong>{total_n}</strong> entries totalling <strong>{total_words:,} words</strong>.
        Your most active writing day is <strong>{most_active_day}</strong>.<br><br>
        <strong>Sentiment breakdown:</strong><br>
        &nbsp;&nbsp;✅ Positive: <strong>{pos_n}</strong> ({pos_n/total_n*100:.0f}%) &nbsp;
        ⚪ Neutral: <strong>{neu_n}</strong> ({neu_n/total_n*100:.0f}%) &nbsp;
        ❌ Negative: <strong>{neg_n}</strong> ({neg_n/total_n*100:.0f}%)<br><br>
        Your dominant sentiment is <strong>{dominant}</strong> ({dominant_pct:.0f}% of entries).
        Average polarity score: <strong>{avg_pol:+.3f}</strong>
        (range: {df_journal_f['sentiment_score'].min():+.3f} to {df_journal_f['sentiment_score'].max():+.3f}).<br><br>
        <em>{tone_narrative}</em>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════
#  SECTION 2 — MOOD REPORT
# ════════════════════════════════════════════════════════════
st.header("🎯 Mood Report")

if df_mood_f.empty:
    st.info("No mood data for this period.")
else:
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.subheader("Mood Intensity Over Time")
        fig_mi = go.Figure()
        fig_mi.add_trace(go.Scatter(
            x=df_mood_f["created_at"], y=df_mood_f["intensity"],
            mode="lines+markers",
            line=dict(color="#6B8F71", width=2),
            marker=dict(size=10, color=[MOOD_COLORS.get(m, "#8D8072") for m in df_mood_f["mood"]],
                        line=dict(color="white", width=1.5)),
            text=df_mood_f["mood"],
            hovertemplate="<b>%{text}</b><br>Intensity: %{y}<br>%{x|%b %d %H:%M}<extra></extra>"
        ))
        fig_mi.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", range=[0, 11], color="#8D8072"),
            margin=dict(l=10, r=10, t=10, b=10), height=260
        )
        st.plotly_chart(fig_mi, use_container_width=True)

    with col_m2:
        st.subheader("Mood Breakdown")
        mood_counts = df_mood_f["mood"].value_counts().reset_index()
        mood_counts.columns = ["mood", "count"]
        fig_mb = go.Figure(go.Bar(
            x=mood_counts["mood"],
            y=mood_counts["count"],
            marker_color=[MOOD_COLORS.get(m, "#8D8072") for m in mood_counts["mood"]],
            text=mood_counts["count"], textposition="outside"
        ))
        fig_mb.update_layout(
            paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
            xaxis=dict(showgrid=False, color="#8D8072"),
            yaxis=dict(showgrid=True, gridcolor="#D5CCBA", color="#8D8072"),
            margin=dict(l=10, r=10, t=10, b=10), height=260, showlegend=False
        )
        st.plotly_chart(fig_mb, use_container_width=True)

    # Mood by day of week
    st.subheader("Emotional Valence by Day of Week")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_val = df_mood_f.groupby("day_of_week")["valence"].mean().reindex(day_order, fill_value=None)
    day_int = df_mood_f.groupby("day_of_week")["intensity"].mean().reindex(day_order, fill_value=None)
    fig_dv = go.Figure()
    fig_dv.add_trace(go.Bar(
        x=day_order, y=day_val.values, name="Avg Valence",
        marker_color=["#6B8F71" if (v is not None and v >= 0) else "#C0392B" for v in day_val.values],
        text=[f"{v:+.2f}" if v is not None else "" for v in day_val.values],
        textposition="outside"
    ))
    fig_dv.add_hline(y=0, line_dash="dash", line_color="#8D8072", opacity=0.5)
    fig_dv.update_layout(
        paper_bgcolor="#F5F0E8", plot_bgcolor="#F5F0E8",
        xaxis=dict(showgrid=False, color="#8D8072"),
        yaxis=dict(showgrid=True, gridcolor="#D5CCBA", color="#8D8072", title="Avg Emotional Valence"),
        margin=dict(l=10, r=10, t=10, b=10), height=240, showlegend=False
    )
    st.plotly_chart(fig_dv, use_container_width=True)

    top_mood = df_mood_f["mood"].value_counts().idxmax()
    top_mood_pct = df_mood_f["mood"].value_counts(normalize=True).max() * 100
    avg_int = df_mood_f["intensity"].mean()
    avg_val = df_mood_f["valence"].mean()
    mood_counts_str = " · ".join([f"{mood_emoji(m)} {m} ({c})" for m, c in df_mood_f["mood"].value_counts().items()])
    best_day = day_val.idxmax() if day_val.notna().any() else "—"
    hard_day = day_val.idxmin() if day_val.notna().any() else "—"

    st.markdown(f"""
    <div class="report-section">
        <strong>🎯 Mood Summary — {period}</strong><br><br>
        {mood_counts_str}<br><br>
        Most frequent mood: <strong>{mood_emoji(top_mood)} {top_mood}</strong> ({top_mood_pct:.0f}%)<br>
        Average intensity: <strong>{avg_int:.1f}/10</strong> · Average valence: <strong>{avg_val:+.2f}</strong>
        ({'leaning positive' if avg_val > 0.1 else 'leaning negative' if avg_val < -0.1 else 'broadly neutral'})<br>
        Best emotional day of week: <strong>{best_day}</strong> · Most challenging: <strong>{hard_day}</strong>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  SECTION 3 — WELLNESS FILES
# ════════════════════════════════════════════════════════════
if not df_files.empty:
    df_files_c = df_files.copy()
    df_files_c["uploaded_at"] = pd.to_datetime(df_files_c["uploaded_at"])
    files_in_period = df_files_c[df_files_c["uploaded_at"] >= cutoff]
    if not files_in_period.empty:
        st.markdown("---")
        st.header("📁 Wellness Files")
        sentiments = files_in_period["sentiment"].dropna().value_counts()
        avg_file_pol = files_in_period["sentiment_score"].dropna().mean()
        st.markdown(f"""
        <div class="report-section">
            <strong>📁 Uploaded Files Summary</strong><br><br>
            {len(files_in_period)} files uploaded · Types: {", ".join(files_in_period["file_type"].value_counts().index.tolist())}<br>
            Sentiments found: {", ".join([f"{s}: {c}" for s, c in sentiments.items()]) or "—"}<br>
            {"Average polarity of file content: <strong>" + f"{avg_file_pol:+.3f}</strong>" if not pd.isna(avg_file_pol) else ""}
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  SECTION 4 — RECOMMENDATIONS
# ════════════════════════════════════════════════════════════
st.markdown("---")
st.header("💡 Recommendations")

recommendations = []

if not df_mood_f.empty:
    avg_val = df_mood_f["valence"].mean()
    avg_int = df_mood_f["intensity"].mean()
    stressed_pct = (df_mood_f["mood"] == "Stressed").mean()
    anxious_pct  = (df_mood_f["mood"] == "Anxious").mean()
    sad_pct      = (df_mood_f["mood"] == "Sad").mean()

    if avg_val < -0.2:
        recommendations.append(("🌿", "Grounding Exercises", "Your emotional tone has been on the lower side. Try 5 minutes of box breathing or a short walk in nature each day to reconnect with the present moment."))
    if stressed_pct > 0.25:
        recommendations.append(("🧘", "Stress Management", f"You logged Stressed in {stressed_pct*100:.0f}% of entries. Try identifying your top two stressors and breaking related tasks into smaller, manageable steps. A brief mindfulness practice before bed can help reset."))
    if anxious_pct > 0.2:
        recommendations.append(("📵", "Digital Detox", f"Anxiety appears in {anxious_pct*100:.0f}% of your mood logs. A 30-minute phone-free window each evening can help your nervous system settle and reduce background worry."))
    if sad_pct > 0.2:
        recommendations.append(("☀️", "Mood-Boosting Activity", "Sadness features regularly in your logs. Consider adding one small pleasurable activity per day — a favourite song, a short walk, or time with someone you enjoy."))
    if avg_int > 7.5:
        recommendations.append(("✍️", "Expressive Journaling", f"Your average mood intensity is {avg_int:.1f}/10 — you feel things strongly. Daily expressive writing helps channel intense emotions constructively and can reduce their hold over time."))
    if avg_val >= 0.3:
        recommendations.append(("🌟", "Maintain Your Momentum", "Your emotional tone is broadly positive. Keep nurturing the habits, routines, and relationships that are supporting your wellbeing — and note what's working."))

if not df_journal_f.empty:
    neg_pct = (df_journal_f["sentiment"] == "Negative").mean()
    avg_words = df_journal_f["word_count"].mean()
    if neg_pct > 0.4:
        recommendations.append(("💬", "Seek Connection", f"{neg_pct*100:.0f}% of your journal entries carry a negative tone. Sharing how you feel with someone you trust — a friend, family member, or counsellor — can make a real difference."))
    if len(df_journal_f) < 3:
        recommendations.append(("📓", "Write More Often", "Journaling just 5 minutes a day has measurable benefits for emotional clarity and resilience. Try setting a consistent time — morning coffee or before bed works well for many people."))
    if avg_words < 50:
        recommendations.append(("🖊️", "Write in More Depth", f"Your entries average {avg_words:.0f} words. Longer, more exploratory writing tends to produce greater emotional insight. Try prompts like 'What am I really feeling underneath this?' to go deeper."))

if not recommendations:
    recommendations.append(("📈", "Keep Going", "You're building a valuable picture of your emotional health. The more you log, the richer your insights and recommendations will become over time."))

for icon, title, text in recommendations:
    st.markdown(f"""
    <div class="rec-card">
        <strong style="color:#3D3522;">{icon} {title}</strong><br>
        <span style="color:#5C5140; font-size:0.9rem;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("CereBloom is a personal wellness tool. It is not a substitute for professional mental health support. If you are struggling, please reach out to a qualified healthcare provider.")
