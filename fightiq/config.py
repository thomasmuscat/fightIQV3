from __future__ import annotations
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT_DIR / "exports"
CACHE_DIR = ROOT_DIR / "cache"
LOG_DIR = ROOT_DIR / "logs"

UFCSTATS_BASE = "http://ufcstats.com"
FIGHTERS_URL = "http://ufcstats.com/statistics/fighters?char={char}&page=all"
EVENTS_URL = "http://ufcstats.com/statistics/events/completed?page=all"

LETTERS = list("abcdefghijklmnopqrstuvwxyz")

SLEEP_SECONDS = float(os.getenv("FIGHTIQ_SLEEP_SECONDS", "0.6") or "0.6")
USE_CACHE = (os.getenv("FIGHTIQ_USE_CACHE", "true").lower() == "true")

MAX_EVENTS = os.getenv("FIGHTIQ_MAX_EVENTS") or None
MAX_FIGHTERS = os.getenv("FIGHTIQ_MAX_FIGHTERS") or None
MAX_FIGHTS = os.getenv("FIGHTIQ_MAX_FIGHTS") or None

UPLOAD_TO_SUPABASE = (os.getenv("FIGHTIQ_UPLOAD_TO_SUPABASE", "false").lower() == "true")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
