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
你是电影推荐编辑。请基于以下电影信息输出严格 JSON（不要 markdown，不要额外文字）。
字段必须包含：
one_liner (str)
why_now (list[str])
who_should_watch (list[str])
who_should_avoid (list[str])
similar_titles (list[str], 恰好3个)
best_viewing_mode (str)
risk_flags (list[str])
tags (list[str])

电影信息：
- title: {movie.get('title')}
- year: {movie.get('year')}
- overview: {movie.get('overview')}
- rank: {movie.get('rank')}
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
                "why_now": _normalize_list(parsed.get("why_now")),
                "who_should_watch": _normalize_list(parsed.get("who_should_watch")),
                "who_should_avoid": _normalize_list(parsed.get("who_should_avoid")),
                "similar_titles": _normalize_list(parsed.get("similar_titles"))[:3],
                "best_viewing_mode": str(parsed.get("best_viewing_mode", "")).strip(),
                "risk_flags": _normalize_list(parsed.get("risk_flags")),
                "tags": _normalize_list(parsed.get("tags")),
            }
            while len(normalized["similar_titles"]) < 3:
                normalized["similar_titles"].append("N/A")
            return normalized
        except Exception as e:  # noqa: BLE001
            last_error = e
    raise RuntimeError(f"DeepSeek analyze failed after retries: {last_error}")
