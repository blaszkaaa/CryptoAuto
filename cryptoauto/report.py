"""Reporting helpers: create simple daily percent change report."""
from typing import Optional

import pandas as pd



def percent_change_report(df: pd.DataFrame, group_col: str = "symbol") -> pd.DataFrame:
    """Return percent change since first record of the day for each symbol."""
    if df.empty:
        return pd.DataFrame()
    df = df.sort_values([group_col, "datetime"]).copy()
    first = df.groupby(group_col).first().reset_index()[[group_col, "price"]]
    first = first.rename(columns={"price": "start_price"})
    merged = df.merge(first, on=group_col)
    merged["pct_change"] = (merged["price"] - merged["start_price"]) / merged["start_price"] * 100
    latest = merged.groupby(group_col).last().reset_index()
    return latest[[group_col, "price", "start_price", "pct_change"]]
