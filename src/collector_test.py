import argparse

from src.collector_tmdb import get_trending_movies
from src.utils import setup_env


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart", default="classic", choices=["trending", "top_rated", "popular", "classic", "upcoming"])
    args = parser.parse_args()

    setup_env()
    movies = get_trending_movies(limit=10, chart=args.chart)
    for m in movies:
        print(f"#{m['rank']:02d} {m['title']} ({m.get('year')})")
