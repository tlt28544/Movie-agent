from datetime import datetime
from zoneinfo import ZoneInfo
import os

import requests

from src.constants import TZ


def get_trending_movies(limit: int = 20) -> list[dict]:
    api_key = os.getenv("TMDB_API_KEY", "").strip()
    if not api_key:
        raise ValueError("TMDB_API_KEY is missing")

    snapshot_date = datetime.now(ZoneInfo(TZ)).strftime("%Y-%m-%d")

    url = "https://api.themoviedb.org/3/trending/movie/day"
    resp = requests.get(
        url,
        params={"api_key": api_key, "language": "en-US"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])[:limit]

    movies: list[dict] = []
    for idx, item in enumerate(results, start=1):
        release_date = item.get("release_date") or ""
        year = int(release_date[:4]) if len(release_date) >= 4 and release_date[:4].isdigit() else None
        tmdb_id = str(item.get("id", ""))
        movies.append(
            {
                "title": item.get("title") or item.get("name") or "Unknown",
                "year": year,
                "tmdb_id": tmdb_id,
                "overview": item.get("overview") or "",
                "url": f"https://www.themoviedb.org/movie/{tmdb_id}" if tmdb_id else "",
                "rank": idx,
                "snapshot_date": snapshot_date,
                "source": "tmdb_trending",
            }
        )
    return movies
