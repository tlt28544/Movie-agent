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


def _build_prompt(movie: dict) -> str:
    # Keep prompt content unchanged by requirement.
    return f"""
你是一位资深中文电影编辑。请基于下面的电影信息，仅输出严格 JSON（不要 markdown，不要额外说明文字）。
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
- 所有文本字段必须使用自然、地道的中文。
- 推荐理由需结合评分、投票数、热度、剧情简介、导演与演员信息。
- 导演背景应基于提供信息，禁止编造具体奖项。
- 不要包含“避雷”或“不推荐人群”等负面劝退段落。

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


def _build_payload(prompt: str) -> dict:
    return {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
    }


def _extract_json_text(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
    return text


def _normalize_analysis(parsed: dict[str, Any]) -> dict:
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


def _call_deepseek(api_key: str, payload: dict) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=45,
    )
    response.raise_for_status()
    response_data = response.json()
    content = response_data["choices"][0]["message"]["content"]
    json_text = _extract_json_text(str(content))
    return json.loads(json_text)


def analyze_movie(movie: dict) -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is missing")

    prompt = _build_prompt(movie)
    payload = _build_payload(prompt)

    last_error = None
    for _ in range(2):
        try:
            parsed = _call_deepseek(api_key=api_key, payload=payload)
            return _normalize_analysis(parsed)
        except Exception as e:  # noqa: BLE001
            last_error = e

    raise RuntimeError(f"DeepSeek analyze failed after retries: {last_error}")
