import pandas as pd
from cryptoauto.report import percent_change_report


def test_percent_change_report():
    df = pd.DataFrame([
        {"symbol": "BTC-USD", "datetime": pd.Timestamp("2025-01-01T09:00"), "price": 100},
        {"symbol": "BTC-USD", "datetime": pd.Timestamp("2025-01-01T15:00"), "price": 110},
        {"symbol": "AAPL", "datetime": pd.Timestamp("2025-01-01T10:00"), "price": 200},
        {"symbol": "AAPL", "datetime": pd.Timestamp("2025-01-01T16:00"), "price": 190},
    ])
    rpt = percent_change_report(df)
    assert not rpt.empty
    btc = rpt[rpt['symbol'] == 'BTC-USD'].iloc[0]
    assert round(btc['pct_change'], 6) == 10.0
    aapl = rpt[rpt['symbol'] == 'AAPL'].iloc[0]
    assert round(aapl['pct_change'], 6) == -5.0
