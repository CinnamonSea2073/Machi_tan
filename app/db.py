import sqlite3
from pathlib import Path
from typing import Generator
from datetime import datetime
import sys

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    # comments table (ensure schema exists). Do NOT drop existing comments
    # on startup - dropping here caused persisted comments to be erased when
    # the app restarted. Use IF NOT EXISTS to keep data safe.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            comment_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            reply_to TEXT,
            genre TEXT,
            student_id TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    # Ensure lat/lon columns exist for comments (store location of comment)
    cur.execute("PRAGMA table_info(comments)")
    cols = [r[1] for r in cur.fetchall()]
    print(f"[init_db] comments columns before migration: {cols}")
    if 'lat' not in cols:
        try:
            cur.execute("ALTER TABLE comments ADD COLUMN lat REAL")
            print("[init_db] added column: lat")
        except Exception:
            e = sys.exc_info()[1]
            print(f"[init_db] failed to add column lat: {e}")
    if 'lon' not in cols:
        try:
            cur.execute("ALTER TABLE comments ADD COLUMN lon REAL")
            print("[init_db] added column: lon")
        except Exception:
            e = sys.exc_info()[1]
            print(f"[init_db] failed to add column lon: {e}")

    # users table for mapping name to uuid
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # students table for student registration
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # courses table to store GPX content
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            gpx_content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # class_course pointer table (single row stored by key)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS class_course (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            course_id TEXT,
            set_at TEXT
        )
        """
    )

    # statuses log
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # ensure there is at least one initial status (デバッグ) to avoid client-side overwrite logic
    cur.execute("SELECT COUNT(1) as cnt FROM statuses")
    row = cur.fetchone()
    if row and row[0] == 0:
        now = datetime.utcnow().isoformat() + "Z"
        cur.execute("INSERT INTO statuses (status, created_at) VALUES (?, ?)", ("デバッグ", now))

    # groq logs (text/audio)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS groq_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            input TEXT,
            output TEXT,
            user_id TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def iter_conn() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# Ensure DB is initialized when module is imported (useful for tests/import-time)
try:
    init_db()
except Exception:
    e = sys.exc_info()[1]
    # do not raise here, but print the error so migration issues are visible during import
    print(f"[init_db] import-time init_db() raised exception: {e}")
