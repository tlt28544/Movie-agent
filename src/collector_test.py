from src.collector_tmdb import get_trending_movies
from src.utils import setup_env


if __name__ == "__main__":
    setup_env()
    movies = get_trending_movies(limit=10)
    for m in movies:
        print(f"#{m['rank']:02d} {m['title']} ({m.get('year')})")
