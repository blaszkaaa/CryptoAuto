"""Utility helpers."""
from typing import List


def normalize_symbols(crypto: List[str], stocks: List[str]) -> List[str]:
    return list(dict.fromkeys([*crypto, *stocks]))
