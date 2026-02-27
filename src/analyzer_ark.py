import json
import os
from typing import Any

import requests

from src.constants import ARK_BASE_URL, ARK_MODEL_WEBSEARCH


def _normalize_list(v: Any, fallback: list[str] | None = None) -> list[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return fallback or []


def _extract_json_text(content: Any) -> str:
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict):
                t = str(item.get("text", "")).strip()
                if t:
                    chunks.append(t)
        text = "\n".join(chunks).strip()
    else:
        text = ""

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def analyze_movie(movie: dict) -> dict:
    api_key = os.getenv("ARK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ARK_API_KEY is missing")
    if not ARK_MODEL_WEBSEARCH:
        raise ValueError("ARK model is missing: set ARK_ENDPOINT_ID or ARK_MODEL_WEBSEARCH")

    prompt = f"""
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
- 可结合实时 web_search 信息补充口碑/话题热度，但禁止编造来源或不确定结论。

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
    base_payload = {
        "model": ARK_MODEL_WEBSEARCH,
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
    }

    # 部分模型/接入点不支持 web_search tools，失败时自动降级重试。
    payload_candidates = [
        {**base_payload, "tools": [{"type": "web_search"}]},
        base_payload,
    ]

    last_error = None
    for payload in payload_candidates:
        for _ in range(2):
            try:
                resp = requests.post(f"{ARK_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"].get("content")
                parsed = json.loads(_extract_json_text(content))

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
    raise RuntimeError(f"Ark analyze failed after retries: {last_error}")
