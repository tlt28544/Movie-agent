import json

from src.analyzer_deepseek import analyze_movie
from src.collector_tmdb import get_trending_movies
from src.utils import setup_env


if __name__ == "__main__":
    setup_env()
    movie = get_trending_movies(limit=1)[0]
    res = analyze_movie(movie)
    print(json.dumps(res, ensure_ascii=False, indent=2))
