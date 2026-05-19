import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from utils.db import save_wellness_file, get_wellness_files
from utils.sentiment import analyze_sentiment, sentiment_color

st.set_page_config(page_title="Wellness Data · CereBloom", page_icon="📁", layout="wide")

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

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text_from_pdf(file_bytes):
    try:
        import pdfplumber
        import io
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_image(file_bytes):
    try:
        import pytesseract
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "[No text detected in image]"
    except Exception as e:
        return f"[Image OCR error: {e}]"


def extract_text_from_csv(file_bytes):
    try:
        import io
        df = pd.read_csv(io.BytesIO(file_bytes))
        text_cols = df.select_dtypes(include="object").columns.tolist()
        if text_cols:
            combined = " ".join(df[text_cols].fillna("").astype(str).values.flatten())
            return combined[:3000]
        else:
            return "[CSV has no text columns]"
    except Exception as e:
        return f"[CSV extraction error: {e}]"


st.title("📁 Wellness Data")
st.markdown("Upload files — PDFs, images, CSVs, or audio — and CereBloom will extract text and analyze their sentiment.")
st.markdown("---")

tab_upload, tab_files = st.tabs(["⬆️ Upload File", "📋 Uploaded Files"])

with tab_upload:
    st.subheader("Upload a Wellness File")
    st.markdown("Supported: **PDF**, **Images (JPG, PNG)**, **CSV**, **Audio (MP3, WAV)** *(text extraction not available for audio)*")

    uploaded = st.file_uploader(
        "Choose a file",
        type=["pdf", "jpg", "jpeg", "png", "csv", "mp3", "wav", "txt"],
        label_visibility="collapsed"
    )

    if uploaded:
        file_bytes = uploaded.read()
        filename = uploaded.name
        file_ext = filename.rsplit(".", 1)[-1].lower()
        file_size = len(file_bytes) / 1024

        st.markdown(f"**File:** {filename} · {file_size:.1f} KB")

        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        with st.spinner("Extracting text…"):
            if file_ext == "pdf":
                extracted_text = extract_text_from_pdf(file_bytes)
                file_type = "PDF"
            elif file_ext in ("jpg", "jpeg", "png"):
                extracted_text = extract_text_from_image(file_bytes)
                file_type = "Image"
                st.image(file_bytes, caption=filename, width=300)
            elif file_ext == "csv":
                extracted_text = extract_text_from_csv(file_bytes)
                file_type = "CSV"
            elif file_ext == "txt":
                extracted_text = file_bytes.decode("utf-8", errors="replace")
                file_type = "Text"
            elif file_ext in ("mp3", "wav"):
                extracted_text = ""
                file_type = "Audio"
                st.info("Audio files cannot be transcribed in this version. The file has been saved.")
            else:
                extracted_text = ""
                file_type = "Unknown"

        if extracted_text and not extracted_text.startswith("["):
            st.success("Text extracted successfully.")
            with st.expander("Preview extracted text"):
                st.text(extracted_text[:1500] + ("…" if len(extracted_text) > 1500 else ""))

            sentiment_result = analyze_sentiment(extracted_text)
            color = sentiment_color(sentiment_result["label"])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sentiment", sentiment_result["label"])
            with col2:
                st.metric("Polarity", f"{sentiment_result['score']:+.3f}")
            with col3:
                st.metric("Subjectivity", f"{sentiment_result['subjectivity']:.2f}")

            save_wellness_file(
                filename, file_type, extracted_text[:5000],
                sentiment_result["label"], sentiment_result["score"]
            )
            st.success(f"'{filename}' saved to your Wellness Data.")
        elif extracted_text.startswith("["):
            st.warning(extracted_text)
            save_wellness_file(filename, file_type, "", None, None)
        else:
            save_wellness_file(filename, file_type, "", None, None)

with tab_files:
    files = get_wellness_files()
    if not files:
        st.info("No files uploaded yet.")
    else:
        st.markdown(f"**{len(files)} files** in your Wellness Data.")
        for f in files:
            sentiment = f.get("sentiment") or "—"
            score = f.get("sentiment_score")
            score_str = f"{score:+.3f}" if score is not None else "—"
            color = sentiment_color(sentiment) if sentiment != "—" else "#8D8072"
            date_str = f["uploaded_at"][:16].replace("T", " ")
            badge = f"<span style='background:{color}; color:white; border-radius:12px; padding:2px 10px; font-size:0.75rem;'>{sentiment}</span>" if sentiment != "—" else ""

            with st.expander(f"**{f['filename']}** · {f['file_type']} · {date_str}"):
                st.markdown(f"Sentiment: {badge} &nbsp; Polarity: **{score_str}**", unsafe_allow_html=True)
                if f.get("extracted_text"):
                    st.markdown("**Extracted Text Preview:**")
                    st.text(f["extracted_text"][:600] + ("…" if len(f["extracted_text"]) > 600 else ""))
                else:
                    st.markdown("*No text extracted from this file.*")
