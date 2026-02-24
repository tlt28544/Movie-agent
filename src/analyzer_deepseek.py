import json
import os
from typing import Any

import requests

from src.constants import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


def _normalize_list(v: Any, fallback: list[str] | None = None) -> list[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return fallback or []


def analyze_movie(movie: dict) -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is missing")

    prompt = f"""
You are a senior English-language movie editor. Based on the movie details below, output strict JSON only (no markdown, no extra text).
The JSON must include:
one_liner (str)
recommendation (str)
why_now (list[str])
who_should_watch (list[str])
director_background (str)
starring_cast (list[str], up to 5 items)
movie_profile (str)
similar_titles (list[str], exactly 3 items)
best_viewing_mode (str)
tags (list[str])

Writing requirements:
- Write all text fields in natural English.
- Use rating, vote count, popularity, overview, director, and cast details to make the recommendation.
- Keep director background grounded in provided info; do not fabricate specific awards.
- Do not include warning/avoidance sections.

Movie details:
- title: {movie.get('title')}
- year: {movie.get('year')}
- overview: {movie.get('overview')}
- rank: {movie.get('rank')}
- vote_average: {movie.get('vote_average')}
- vote_count: {movie.get('vote_count')}
- popularity: {movie.get('popularity')}
- directors: {movie.get('directors')}
- cast: {movie.get('cast')}
""".strip()

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
    }

    last_error = None
    for _ in range(2):
        try:
            resp = requests.post(f"{DEEPSEEK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=45)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            parsed = json.loads(content)

            normalized = {
                "one_liner": str(parsed.get("one_liner", "")).strip(),
                "recommendation": str(parsed.get("recommendation", "")).strip(),
                "why_now": _normalize_list(parsed.get("why_now")),
                "who_should_watch": _normalize_list(parsed.get("who_should_watch")),
                "director_background": str(parsed.get("director_background", "")).strip(),
                "starring_cast": _normalize_list(parsed.get("starring_cast"))[:5],
                "movie_profile": str(parsed.get("movie_profile", "")).strip(),
                "similar_titles": _normalize_list(parsed.get("similar_titles"))[:3],
                "best_viewing_mode": str(parsed.get("best_viewing_mode", "")).strip(),
                "tags": _normalize_list(parsed.get("tags")),
            }
            while len(normalized["similar_titles"]) < 3:
                normalized["similar_titles"].append("N/A")
            return normalized
        except Exception as e:  # noqa: BLE001
            last_error = e
    raise RuntimeError(f"DeepSeek analyze failed after retries: {last_error}")
