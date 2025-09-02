"""Main runnable script: load config, schedule fetches, save and report.

Provides a small CLI to run once or as a long-running scheduler. Config is
loaded from `config.yaml` by default.
"""
import argparse
import logging
import os
import smtplib
import signal
import sys
import time
from email.message import EmailMessage
from typing import List

import pandas as pd
import yaml
from dotenv import load_dotenv

from cryptoauto.fetcher import fetch_tickers
from cryptoauto.storage import save, ensure_path
from cryptoauto.report import percent_change_report
from cryptoauto.utils import normalize_symbols


logger = logging.getLogger("cryptoauto")
# When True, print fetched raw data and reports to console each cycle
CONSOLE_VIEW = True


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def send_email(report_text: str, cfg: dict):
    try:
        msg = EmailMessage()
        msg["Subject"] = "CryptoAuto daily report"
        msg["From"] = cfg["email"]["username"]
        msg["To"] = cfg["email"]["username"]
        msg.set_content(report_text)
        server = smtplib.SMTP(cfg["email"]["smtp_server"], cfg["email"]["smtp_port"])
        server.starttls()
        server.login(cfg["email"]["username"], os.environ.get("SMTP_PASSWORD", ""))
        server.send_message(msg)
        server.quit()
    except Exception:
        logger.exception("Failed to send email report")


def run_cycle(cfg: dict):
    symbols = normalize_symbols(cfg["symbols"].get("crypto", []), cfg["symbols"].get("stocks", []))
    df = fetch_tickers(symbols)
    if df.empty:
        logger.warning("No data fetched this cycle")
        return
    if CONSOLE_VIEW:
        try:
            print("\n=== Raw fetched data ===")
            print(df.to_string(index=False))
            print("========================\n")
        except Exception:
            logger.exception("Failed to print fetched data to console")
    path = cfg["storage"].get("path", "data")
    fmt = cfg["storage"].get("format", "csv")
    ensure_path(path)
    try:
        saved = save(df, fmt, path)
        logger.info("Saved data to %s", saved)
    except Exception:
        logger.exception("Failed to save data")
    if cfg.get("report", {}).get("enabled", False):
        rpt = percent_change_report(df)
        txt = rpt.to_string(index=False)
        if cfg.get("report", {}).get("method") == "email":
            send_email(txt, cfg)
        else:
            print("--- Report ---")
            print(txt)
            print("--------------")


def configure_logging(log_path: str = "cryptoauto.log"):
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)
    try:
        from logging.handlers import RotatingFileHandler

        fh = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except Exception:
        logger.debug("RotatingFileHandler not available; continuing without file logging")


def main(argv: List[str] = None):
    parser = argparse.ArgumentParser(description="CryptoAuto price fetcher and reporter")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to config file")
    parser.add_argument("--once", action="store_true", help="Run one fetch cycle and exit")
    parser.add_argument("--no-console", action="store_true", help="Disable console output of fetched data and reports")
    parser.add_argument("--dashboard", action="store_true", help="Run terminal dashboard UI (Rich)")
    parser.add_argument("--log", default="cryptoauto.log", help="Log file path")
    args = parser.parse_args(argv)

    configure_logging(args.log)
    logger.info("Starting CryptoAuto")
    load_dotenv()
    cfg = load_config(args.config)
    global CONSOLE_VIEW
    if getattr(args, "no_console", False):
        CONSOLE_VIEW = False
    if getattr(args, "dashboard", False):
        # Launch the simple dashboard and exit
        from cryptoauto.dashboard import run_dashboard
        symbols = normalize_symbols(cfg["symbols"].get("crypto", []), cfg["symbols"].get("stocks", []))
        refresh = cfg.get("schedule", {}).get("interval_minutes", 10)
        run_dashboard(symbols, refresh_seconds=refresh * 60)
        return

    # graceful shutdown support
    stop = False

    def _signal_handler(sig, frame):
        nonlocal stop
        logger.info("Received signal %s, stopping...", sig)
        stop = True

    signal.signal(signal.SIGINT, _signal_handler)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
    except Exception:
        # SIGTERM may not be available on Windows
        pass

    # initial run
    run_cycle(cfg)

    if args.once:
        logger.info("Run-once complete, exiting")
        return

    import schedule

    interval = cfg.get("schedule", {}).get("interval_minutes", 10)
    schedule.every(interval).minutes.do(run_cycle, cfg)

    logger.info("Entering scheduler loop (interval=%d minutes)", interval)
    while not stop:
        try:
            schedule.run_pending()
        except Exception:
            logger.exception("Error during scheduled run")
        time.sleep(1)


if __name__ == "__main__":
    main()
