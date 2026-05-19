import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cerebloom.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            sentiment TEXT,
            sentiment_score REAL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            intensity INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS wellness_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            extracted_text TEXT,
            sentiment TEXT,
            sentiment_score REAL,
            uploaded_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_journal_entry(title, content, sentiment, sentiment_score):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO journal_entries (title, content, sentiment, sentiment_score, created_at) VALUES (?, ?, ?, ?, ?)",
        (title, content, sentiment, sentiment_score, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_journal_entries():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM journal_entries ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_journal_entry(entry_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def save_mood_entry(mood, intensity, note=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO mood_entries (mood, intensity, note, created_at) VALUES (?, ?, ?, ?)",
        (mood, intensity, note, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_mood_entries():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM mood_entries ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_wellness_file(filename, file_type, extracted_text, sentiment, sentiment_score):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO wellness_files (filename, file_type, extracted_text, sentiment, sentiment_score, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
        (filename, file_type, extracted_text, sentiment, sentiment_score, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_wellness_files():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM wellness_files ORDER BY uploaded_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
