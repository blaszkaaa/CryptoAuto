"""Fetch current prices for crypto and stocks.

Primary source: yfinance. For crypto symbols (e.g. BTC-USD) a CoinGecko
fallback is available if yfinance returns no data.

This module implements simple retries with exponential backoff to
handle transient network/API issues.
"""
import logging
import time
from typing import List, Optional

import pandas as pd
import requests
import yfinance as yf

logger = logging.getLogger(__name__)

# Minimal mapping for common coin symbols to CoinGecko ids. This can be
# extended or replaced with a search call if needed.
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
}


def _search_coingecko(symbol: str) -> Optional[str]:
    """Search CoinGecko for a coin id matching the given symbol.

    Returns coin id or None.
    """
    try:
        s = symbol.lower()
        url = "https://api.coingecko.com/api/v3/search"
        resp = requests.get(url, params={"query": s}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        coins = data.get("coins", [])
        # prefer exact symbol match
        for c in coins:
            if c.get("symbol", "").lower() == s:
                return c.get("id")
        # fallback to first result
        if coins:
            return coins[0].get("id")
    except Exception:
        logger.exception("CoinGecko search failed for %s", symbol)
    return None


def _fetch_coingecko_price(coin_id: str) -> Optional[float]:
    """Fetch USD price from CoinGecko for given coin id.

    Returns price as float or None on failure.
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        resp = requests.get(url, params={"ids": coin_id, "vs_currencies": "usd"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        price = data.get(coin_id, {}).get("usd")
        if price is None:
            logger.debug("CoinGecko returned no price for %s", coin_id)
            return None
        return float(price)
    except Exception:
        logger.exception("CoinGecko fetch failed for %s", coin_id)
        return None


def fetch_tickers(symbols: List[str], retries: int = 3, backoff: float = 1.0) -> pd.DataFrame:
    """Fetch latest market data for a list of symbols using yfinance.

    For each symbol we attempt up to `retries` times with exponential
    backoff. If yfinance provides no minute-level data for a crypto
    symbol ending with `-USD`, we will try CoinGecko for a best-effort
    USD price.

    Returns a DataFrame with columns: symbol, datetime, price
    """
    rows = []
    for sym in symbols:
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt < retries:
            try:
                ticker = yf.Ticker(sym)
                data = ticker.history(period="1d", interval="1m")
                if data is None or data.empty:
                    logger.debug("yfinance returned no data for %s (attempt %d)", sym, attempt + 1)
                    raise ValueError("no data")
                last = data.iloc[-1]
                price = last["Close"]
                rows.append({"symbol": sym, "datetime": last.name.to_pydatetime(), "price": float(price)})
                break
            except Exception as e:
                last_exc = e
                attempt += 1
                wait = backoff * (2 ** (attempt - 1))
                logger.debug("Fetch %s failed (attempt %d/%d): %s — retrying in %.1fs", sym, attempt, retries, e, wait)
                time.sleep(wait)

        else:
            # All retries exhausted. Try CoinGecko fallback for common crypto symbols
            logger.info("All yfinance attempts failed for %s: %s", sym, last_exc)
            if sym.upper().endswith("-USD"):
                short = sym.split("-")[0].upper()
                cg_id = COINGECKO_MAP.get(short)
                if cg_id is None:
                    # try searching CoinGecko
                    found = _search_coingecko(short)
                    if found:
                        cg_id = found
                        COINGECKO_MAP[short] = found
                if cg_id:
                    price = _fetch_coingecko_price(cg_id)
                    if price is not None:
                        rows.append({"symbol": sym, "datetime": pd.Timestamp.utcnow().to_pydatetime(), "price": float(price)})
                        continue
            logger.warning("No data available for %s after retries and fallbacks", sym)

    df = pd.DataFrame(rows)
    return df
