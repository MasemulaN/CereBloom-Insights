# CereBloom

A personal wellness dashboard that turns emotions into insights — track moods, analyze journal sentiment, and discover emotional patterns.

## Run & Operate

- Workflow: `artifacts/api-server: CereBloom` runs the app on port 5000
- Command: `cd /home/runner/workspace/cerebloom && streamlit run app.py --server.port 5000 --server.address 0.0.0.0`
- Required Python packages: streamlit, pandas, plotly, textblob, pdfplumber, pytesseract, Pillow, nltk, openpyxl

## Stack

- Python 3.11, Streamlit
- Storage: SQLite (via `data/cerebloom.db`)
- Sentiment: TextBlob (polarity + subjectivity)
- Charts: Plotly
- File parsing: pdfplumber (PDF), pytesseract + Pillow (images/OCR), pandas (CSV)

## Where things live

- `cerebloom/app.py` — main home page entry point
- `cerebloom/pages/` — multi-page Streamlit pages (Journal, Mood Tracker, Insights, Wellness Data, Reports)
- `cerebloom/utils/db.py` — SQLite helpers (journals, moods, wellness files)
- `cerebloom/utils/sentiment.py` — TextBlob sentiment + mood utilities
- `cerebloom/data/cerebloom.db` — local SQLite database (auto-created)
- `cerebloom/uploads/` — uploaded wellness files stored here
- `cerebloom/.streamlit/config.toml` — theme (earthy tones) and server config

## Deployment

- CereBloom is registered as a service in `artifacts/api-server/.replit-artifact/artifact.toml`
- It serves at the root `/` path on port 5000
- Deployment type: VM (always-on, preserves SQLite data)
- Production run: `sh -c "cd /home/runner/workspace/cerebloom && streamlit run app.py --server.port 5000 --server.address 0.0.0.0"`

## Architecture decisions

- SQLite chosen for local-first storage — no external DB required, all data stays on device
- TextBlob used for sentiment (polarity-based, not keyword-only) — supports nuanced text scoring
- Streamlit multi-page app pattern using `pages/` directory for clean navigation
- pytesseract + pdfplumber handle file text extraction; audio files saved but not transcribed (placeholder)
- Mood valence mapping converts categorical moods to numeric scores for trend charts

## Product

- **Journal**: Write entries, auto-analyze sentiment, browse/search history
- **Mood Tracker**: Log mood + intensity, view charts over time
- **Insights**: Mood trend chart, sentiment distribution pie, personalized pattern summary
- **Wellness Data**: Upload PDF/images/CSV/audio, extract text, run sentiment analysis
- **Reports**: Detailed journal analytics, polarity trends, writing stats, mood charts, recommendations

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- NLTK corpora (TextBlob) downloaded on first run — takes ~30 seconds on cold start
- pytesseract requires tesseract system binary; OCR may fail if not installed in Nix env
- `cerebloom/data/` and `cerebloom/uploads/` are auto-created if missing
- CereBloom workflow runs from the workspace root via absolute path (not from artifacts/api-server/)
