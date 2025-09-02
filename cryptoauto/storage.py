"""Storage helpers to save DataFrame into CSV, JSON or SQLite."""
import os
from pathlib import Path
from typing import Optional

import pandas as pd


def ensure_path(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save(df: pd.DataFrame, storage_format: str, path: str, filename: Optional[str] = None):
    p = ensure_path(path)
    if filename is None:
        filename = "prices"
    if storage_format == "csv":
        file = p / f"{filename}.csv"
        # Append without writing header if file exists
        if file.exists():
            df.to_csv(file, index=False, mode="a", header=False)
        else:
            df.to_csv(file, index=False)
        return str(file)
    if storage_format == "json":
        file = p / f"{filename}.json"
        df.to_json(file, orient="records", date_format="iso")
        return str(file)
    if storage_format == "sqlite":
        import sqlite3
        file = p / f"{filename}.db"
        conn = sqlite3.connect(str(file))
        # Use a sensible table name and append rows
        df.to_sql(filename, conn, if_exists="append", index=False)
        conn.close()
        return str(file)
    raise ValueError(f"Unknown storage format: {storage_format}")
