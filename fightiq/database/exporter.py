from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from fightiq.config import EXPORT_DIR

def write_csv(name: str, df: pd.DataFrame) -> Path:
    EXPORT_DIR.mkdir(exist_ok=True)
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"[export] {name}.csv rows={len(df)}")
    return path

def write_json(name: str, data: dict) -> Path:
    EXPORT_DIR.mkdir(exist_ok=True)
    path = EXPORT_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[export] {name}.json")
    return path
