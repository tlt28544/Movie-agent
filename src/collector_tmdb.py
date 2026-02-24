from datetime import datetime
from zoneinfo import ZoneInfo
import os

import requests

from src.constants import TZ


def get_trending_movies(limit: int = 30) -> list[dict]:
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
        directors: list[str] = []
        cast: list[str] = []
        if tmdb_id:
            try:
                credits_resp = requests.get(
                    f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits",
                    params={"api_key": api_key, "language": "en-US"},
                    timeout=20,
                )
                credits_resp.raise_for_status()
                credits = credits_resp.json()
                directors = [
                    c.get("name", "")
                    for c in credits.get("crew", [])
                    if c.get("job") == "Director" and c.get("name")
                ][:2]
                cast = [c.get("name", "") for c in credits.get("cast", []) if c.get("name")][:5]
            except requests.RequestException:
                directors = []
                cast = []

        movies.append(
            {
                "title": item.get("title") or item.get("name") or "Unknown",
                "year": year,
                "tmdb_id": tmdb_id,
                "overview": item.get("overview") or "",
                "vote_average": item.get("vote_average"),
                "vote_count": item.get("vote_count"),
                "popularity": item.get("popularity"),
                "url": f"https://www.themoviedb.org/movie/{tmdb_id}" if tmdb_id else "",
                "rank": idx,
                "snapshot_date": snapshot_date,
                "source": "tmdb_trending",
                "directors": directors,
                "cast": cast,
            }
        )
    return movies
