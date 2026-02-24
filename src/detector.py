def pick_trending_candidates(today_movies: list[dict], yesterday_rank_map: dict[str, int], limit: int = 3) -> list[dict]:
    if not today_movies:
        return []

    enriched = []
    for m in today_movies:
        tmdb_id = str(m.get("tmdb_id", ""))
        today_rank = int(m.get("rank", 9999))
        y_rank = yesterday_rank_map.get(tmdb_id)
        is_new = y_rank is None
        jump = (y_rank - today_rank) if y_rank is not None else -999
        candidate = {**m, "new_entry": is_new, "rank_jump": jump}
        enriched.append(candidate)

    high_jumpers = [m for m in enriched if not m["new_entry"] and m["rank_jump"] >= 5]
    new_entries = [m for m in enriched if m["new_entry"]]
    low_jumpers = [m for m in enriched if not m["new_entry"] and 0 < m["rank_jump"] < 5]

    high_jumpers.sort(key=lambda x: x["rank_jump"], reverse=True)
    new_entries.sort(key=lambda x: x["rank"])
    low_jumpers.sort(key=lambda x: x["rank_jump"], reverse=True)

    prioritized = high_jumpers + new_entries + low_jumpers
    seen_ids = {m["tmdb_id"] for m in prioritized}

    # 候选不足时补齐榜单
    for m in sorted(enriched, key=lambda x: x["rank"]):
        if m["tmdb_id"] not in seen_ids:
            prioritized.append(m)
            seen_ids.add(m["tmdb_id"])

    return prioritized[:limit]
