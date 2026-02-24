import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from src.constants import TZ


def setup_env() -> None:
    load_dotenv()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def today_str() -> str:
    tz = ZoneInfo(TZ)
    return datetime.now(tz).strftime("%Y-%m-%d")


def yesterday_str() -> str:
    tz = ZoneInfo(TZ)
    return (datetime.now(tz) - timedelta(days=1)).strftime("%Y-%m-%d")
