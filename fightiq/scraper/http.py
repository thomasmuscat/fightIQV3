from __future__ import annotations
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from fightiq.config import CACHE_DIR, SLEEP_SECONDS, USE_CACHE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FightIQDataEngine/3.0; +https://github.com/thomasmuscat/fightIQ)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def cache_path_for_url(url: str) -> Path:
    safe = url.replace("://", "_").replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_").replace(":", "_")
    return CACHE_DIR / f"{safe}.html"

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=30))
def fetch_html(url: str) -> str:
    CACHE_DIR.mkdir(exist_ok=True)
    path = cache_path_for_url(url)
    if USE_CACHE and path.exists() and path.stat().st_size > 0:
        return path.read_text(encoding="utf-8", errors="ignore")

    time.sleep(SLEEP_SECONDS)
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    html = response.text
    path.write_text(html, encoding="utf-8")
    return html

def soup_from_url(url: str) -> BeautifulSoup:
    return BeautifulSoup(fetch_html(url), "lxml")
