"""Simple terminal dashboard using Rich to display live prices."""
from typing import List
import time

from rich.table import Table
from rich.live import Live
from rich.console import Console

from cryptoauto.fetcher import fetch_tickers


console = Console()
# store last prices to compute change
_last_prices = {}


def _build_table(df) -> Table:
    table = Table(title="Live Prices")
    table.add_column("Symbol")
    table.add_column("Datetime")
    table.add_column("Price", justify="right")
    table.add_column("Δ%", justify="right")
    rows = []
    for _, row in df.iterrows():
        sym = str(row["symbol"])
        price = float(row["price"])
        prev = _last_prices.get(sym)
        pct = None
        if prev is not None and prev > 0:
            pct = (price - prev) / prev * 100
        rows.append((sym, str(row["datetime"]), price, pct))
        _last_prices[sym] = price
    # sort by pct change desc (None -> 0)
    rows.sort(key=lambda r: (r[3] is None, -(r[3] or 0)))
    for sym, dt, price, pct in rows:
        price_s = f"{price:.6f}"
        if pct is None:
            pct_s = "-"
            pct_text = pct_s
        else:
            pct_s = f"{pct:+.2f}%"
            pct_text = pct_s
            if pct > 0:
                pct_text = f"[green]{pct_s}[/green]"
            elif pct < 0:
                pct_text = f"[red]{pct_s}[/red]"
        table.add_row(sym, dt, price_s, pct_text)
    return table


def run_dashboard(symbols: List[str], refresh_seconds: int = 10):
    """Run a simple live dashboard that refreshes every `refresh_seconds` seconds."""
    with Live(console=console, refresh_per_second=4) as live:
        while True:
            df = fetch_tickers(symbols)
            table = _build_table(df)
            live.update(table)
            try:
                time.sleep(refresh_seconds)
            except KeyboardInterrupt:
                break
"""Simple terminal dashboard using Rich to display live prices."""
from typing import List
import time

from rich.table import Table
from rich.live import Live
from rich.console import Console

from cryptoauto.fetcher import fetch_tickers


console = Console()


def _build_table(df) -> Table:
    table = Table(title="Live Prices")
    table.add_column("Symbol")
    table.add_column("Datetime")
    table.add_column("Price", justify="right")
    for _, row in df.iterrows():
        table.add_row(str(row["symbol"]), str(row["datetime"]), f"{row['price']:.6f}")
    return table


def run_dashboard(symbols: List[str], refresh_seconds: int = 10):
    """Run a simple live dashboard that refreshes every `refresh_seconds` seconds."""
    with Live(console=console, refresh_per_second=4) as live:
        while True:
            df = fetch_tickers(symbols)
            table = _build_table(df)
            live.update(table)
            try:
                time.sleep(refresh_seconds)
            except KeyboardInterrupt:
                break
