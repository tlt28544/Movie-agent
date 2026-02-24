import os
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.constants import TZ

DB_PATH = os.path.join("data", "app.db")


def _connect() -> sqlite3.Connection:
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_snapshot (
          snapshot_date TEXT,
          source TEXT,
          tmdb_id TEXT,
          rank INTEGER,
          title TEXT,
          year INTEGER,
          url TEXT,
          PRIMARY KEY (snapshot_date, source, tmdb_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sent_log (
          sent_date TEXT,
          tmdb_id TEXT,
          title TEXT,
          year INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def upsert_daily_snapshot(snapshot_date: str, source: str, movies: list[dict]) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT OR REPLACE INTO daily_snapshot
        (snapshot_date, source, tmdb_id, rank, title, year, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                snapshot_date,
                source,
                m["tmdb_id"],
                m["rank"],
                m["title"],
                m.get("year"),
                m.get("url", ""),
            )
            for m in movies
        ],
    )
    conn.commit()
    conn.close()


def get_yesterday_ranks(source: str, yesterday_date: str) -> dict[str, int]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT tmdb_id, rank
        FROM daily_snapshot
        WHERE source = ? AND snapshot_date = ?
        """,
        (source, yesterday_date),
    )
    rows = cur.fetchall()
    conn.close()
    return {str(tmdb_id): int(rank) for tmdb_id, rank in rows}


def was_sent_recently(tmdb_id: str, days: int = 7) -> bool:
    cutoff = (datetime.now(ZoneInfo(TZ)) - timedelta(days=days)).strftime("%Y-%m-%d")

    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT 1 FROM sent_log
        WHERE tmdb_id = ? AND sent_date >= ?
        LIMIT 1
        """,
        (tmdb_id, cutoff),
    )
    found = cur.fetchone() is not None
    conn.close()
    return found


def log_sent(tmdb_id: str, title: str, year: int | None, sent_date: str) -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sent_log (sent_date, tmdb_id, title, year)
        VALUES (?, ?, ?, ?)
        """,
        (sent_date, tmdb_id, title, year),
    )
    conn.commit()
    conn.close()
