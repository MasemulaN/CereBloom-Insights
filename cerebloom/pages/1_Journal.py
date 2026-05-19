import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.db import save_journal_entry, get_journal_entries, delete_journal_entry
from utils.sentiment import analyze_sentiment, sentiment_color

st.set_page_config(page_title="Journal · CereBloom", page_icon="📓", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #EDE8DC; }
    .entry-card { background:#EDE8DC; border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.8rem; }
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

st.title("📓 Journal")
st.markdown("Write your thoughts. CereBloom will analyze the sentiment of your entries automatically.")
st.markdown("---")

tab_write, tab_history = st.tabs(["✍️ New Entry", "📚 Past Entries"])

with tab_write:
    with st.form("journal_form", clear_on_submit=True):
        title = st.text_input("Entry Title", placeholder="Give this entry a title…")
        content = st.text_area(
            "Your Thoughts",
            placeholder="Write freely — how are you feeling today? What's on your mind?",
            height=250
        )
        submitted = st.form_submit_button("Save Entry", use_container_width=True)

    if submitted:
        if not title.strip() or not content.strip():
            st.warning("Please provide both a title and some content before saving.")
        else:
            result = analyze_sentiment(content)
            save_journal_entry(title.strip(), content.strip(), result["label"], result["score"])
            color = sentiment_color(result["label"])
            st.success("Entry saved!")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sentiment", result["label"])
            with col2:
                st.metric("Polarity Score", f"{result['score']:+.3f}")
            with col3:
                st.metric("Subjectivity", f"{result['subjectivity']:.2f}")
            st.info(
                f"**Sentiment Analysis:** Your entry reads as **{result['label']}** with a polarity of {result['score']:+.3f}. "
                f"A score near +1 is very positive, near -1 is very negative, and near 0 is neutral."
            )

with tab_history:
    entries = get_journal_entries()
    if not entries:
        st.info("No journal entries yet. Write your first entry above!")
    else:
        st.markdown(f"**{len(entries)} entries** in your journal.")
        search = st.text_input("Search entries…", placeholder="Search by title or content")
        if search:
            entries = [e for e in entries if search.lower() in e["title"].lower() or search.lower() in e["content"].lower()]
            st.markdown(f"Showing {len(entries)} matching results.")

        for entry in entries:
            sentiment = entry.get("sentiment", "Neutral") or "Neutral"
            score = entry.get("sentiment_score", 0.0) or 0.0
            color = sentiment_color(sentiment)
            date_str = entry["created_at"][:16].replace("T", " ")

            with st.expander(f"**{entry['title']}** — {date_str}"):
                col_badge, col_score = st.columns([2, 1])
                with col_badge:
                    st.markdown(f"<span style='background:{color}; color:white; border-radius:12px; padding:3px 12px; font-size:0.8rem; font-weight:600;'>{sentiment}</span>", unsafe_allow_html=True)
                with col_score:
                    st.markdown(f"<span style='color:#8D8072; font-size:0.85rem;'>Polarity: {score:+.3f}</span>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(entry["content"])
                st.markdown("---")
                if st.button(f"🗑 Delete this entry", key=f"del_{entry['id']}"):
                    delete_journal_entry(entry["id"])
                    st.success("Entry deleted.")
                    st.rerun()
