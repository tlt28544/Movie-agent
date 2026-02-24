import argparse
import logging
import os
import sys

from src.analyzer_deepseek import analyze_movie
from src.collector_tmdb import get_trending_movies
from src.detector import pick_trending_candidates
from src.email_template import render_email
from src.emailer_smtp import send_email
from src.report_excel import build_excel_report
from src.store_sqlite import (
    get_yesterday_ranks,
    init_db,
    log_sent,
    upsert_daily_snapshot,
    cleanup_old_data,
    was_sent_recently,
)
from src.utils import setup_env, setup_logging, today_str, yesterday_str


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    setup_env()
    setup_logging()
    logger = logging.getLogger("movie-agent")

    to_email = os.getenv("TO_EMAIL", "").strip()
    if not to_email and not args.dry_run:
        logger.error("TO_EMAIL is missing")
        return 1

    init_db()
    cleanup_old_data(retention_days=365)
    today = today_str()
    yday = yesterday_str()

    try:
        today_movies = get_trending_movies(limit=30)
    except Exception as e:  # noqa: BLE001
        logger.exception("failed to fetch TMDB trending: %s", e)
        return 1

    if not today_movies:
        logger.error("TMDB returned empty list")
        return 1

    upsert_daily_snapshot(today, "tmdb_trending", today_movies)
    yesterday_map = get_yesterday_ranks("tmdb_trending", yday)

    raw_candidates = pick_trending_candidates(today_movies, yesterday_map, limit=30)
    candidates = [m for m in raw_candidates if not was_sent_recently(str(m.get("tmdb_id")), days=7)]
    candidates = candidates[: args.limit]

    if not candidates:
        logger.info("no candidates")
        return 0

    movies_with_cards = []
    for m in candidates:
        try:
            card = analyze_movie(m)
            movies_with_cards.append({"movie": m, "analysis": card})
        except Exception as e:  # noqa: BLE001
            logger.error("failed to analyze %s: %s", m.get("title"), e)

    if not movies_with_cards:
        logger.error("all DeepSeek analyses failed")
        return 1

    subject = f"🎬 今日电影推荐 {today}"
    html = render_email(today, movies_with_cards, today_movies[:20])

    attachment_path = build_excel_report(today)

    if args.dry_run:
        logger.info("dry-run subject: %s", subject)
        logger.info("dry-run candidates: %s", [x['movie']['title'] for x in movies_with_cards])
        logger.info("dry-run attachment: %s", attachment_path)
        return 0

    try:
        send_email(subject, html, to_email, attachments=[attachment_path])
        for item in movies_with_cards:
            m = item["movie"]
            log_sent(str(m.get("tmdb_id")), m.get("title", ""), m.get("year"), today)
        logger.info("email sent successfully to %s", to_email)
        return 0
    except Exception as e:  # noqa: BLE001
        logger.exception("failed to send email: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
