from __future__ import annotations
import pandas as pd

def add_basic_fighter_metrics(fighters: pd.DataFrame) -> pd.DataFrame:
    if fighters.empty:
        return fighters

    fighters = fighters.copy()
    for col in ["wins", "losses", "draws", "wins_ko", "wins_sub", "wins_decision"]:
        if col not in fighters.columns:
            fighters[col] = 0

    total = (fighters["wins"].fillna(0) + fighters["losses"].fillna(0) + fighters["draws"].fillna(0)).replace(0, pd.NA)
    fighters["win_rate"] = (fighters["wins"].fillna(0) / total * 100).round(2)
    fighters["elo_rating"] = fighters.get("elo_rating", 1500)
    fighters["elo_rating"] = fighters["elo_rating"].fillna(1500)
    return fighters
