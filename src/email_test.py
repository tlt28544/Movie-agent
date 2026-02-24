import argparse

from src.email_template import render_email
from src.emailer_smtp import send_email
from src.utils import setup_env, today_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    setup_env()
    html = render_email(
        today_str(),
        [
            {
                "movie": {"title": "Demo Movie", "year": 2024, "url": "https://www.themoviedb.org"},
                "analysis": {
                    "one_liner": "一部节奏紧凑、话题度高的院线片。",
                    "why_now": ["热度攀升", "社交平台讨论多", "适合周末观影"],
                    "who_should_watch": ["喜欢悬疑", "想看话题片"],
                    "who_should_avoid": ["不喜欢高压节奏"],
                    "similar_titles": ["Movie A", "Movie B", "Movie C"],
                },
            }
        ],
    )

    if args.preview:
        print(html)
    else:
        import os

        to_email = os.getenv("TO_EMAIL", "").strip()
        send_email("[TEST] movie-agent", html, to_email)
        print("test email sent")
