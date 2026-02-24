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
                    "recommendation": "口碑和热度都不错，适合本周观看。",
                    "why_now": ["热度攀升", "社交平台讨论多", "适合周末观影"],
                    "who_should_watch": ["喜欢悬疑", "想看话题片"],
                    "director_background": "导演以类型片见长，叙事节奏稳健。",
                    "starring_cast": ["演员A", "演员B"],
                    "movie_profile": "一部围绕家庭与真相展开的悬疑电影。",
                    "similar_titles": ["Movie A", "Movie B", "Movie C"],
                },
            }
        ],
        [
            {"rank": 1, "title": "Top Movie", "year": 2024, "vote_average": 7.8},
            {"rank": 2, "title": "Top Movie 2", "year": 2023, "vote_average": 7.5},
        ],
    )

    if args.preview:
        print(html)
    else:
        import os

        to_email = os.getenv("TO_EMAIL", "").strip()
        send_email("[TEST] movie-agent", html, to_email)
        print("test email sent")
