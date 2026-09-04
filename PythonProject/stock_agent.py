#!/usr/bin/env python3
"""Explainable, research-only Indian equity analysis agent."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf


@dataclass
class Analysis:
    symbol: str
    company: str | None
    sector: str | None
    as_of: str
    close: float
    ma20: float
    ma50: float
    rsi14: float
    annualised_volatility_pct: float
    drawdown_from_52_week_high_pct: float
    trailing_pe: float | None
    market_cap_inr: int | None
    score: int
    view: str
    reasons: list[str]
    risk_note: str


def normalise_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    return symbol if symbol.endswith((".NS", ".BO")) else f"{symbol}.NS"


def rsi(close: pd.Series, days: int = 14) -> float:
    changes = close.diff()
    gains = changes.clip(lower=0).rolling(days).mean()
    losses = -changes.clip(upper=0).rolling(days).mean()
    relative_strength = gains / losses.replace(0, np.nan)
    result = 100 - (100 / (1 + relative_strength))
    return float(result.iloc[-1])


def number(value: Any) -> float | None:
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def analyse(symbol: str, period: str) -> Analysis:
    ticker_symbol = normalise_symbol(symbol)
    ticker = yf.Ticker(ticker_symbol)
    history = ticker.history(period=period, auto_adjust=True)
    if history.empty or len(history) < 55:
        raise ValueError("Not enough price history returned (need at least 55 trading days).")

    close = history["Close"].dropna()
    latest = float(close.iloc[-1])
    ma20 = float(close.rolling(20).mean().iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1])
    rsi14 = rsi(close)
    returns = close.pct_change().dropna()
    volatility = float(returns.tail(20).std() * math.sqrt(252) * 100)
    high_252 = float(close.tail(min(252, len(close))).max())
    drawdown = (latest / high_252 - 1) * 100

    try:
        info = ticker.info
    except Exception:
        info = {}
    pe = number(info.get("trailingPE"))
    cap = info.get("marketCap") if isinstance(info.get("marketCap"), int) else None

    score, reasons = 0, []
    if latest > ma20 > ma50:
        score += 2
        reasons.append("Price is above both the 20-day and 50-day averages, with the short trend leading.")
    elif latest < ma20 < ma50:
        score -= 2
        reasons.append("Price is below both the 20-day and 50-day averages, with the short trend weaker.")
    else:
        reasons.append("Moving averages are mixed; the trend signal is not decisive.")

    if 50 <= rsi14 <= 70:
        score += 1
        reasons.append(f"RSI at {rsi14:.1f} shows positive momentum without an obvious overbought reading.")
    elif rsi14 > 70:
        score -= 1
        reasons.append(f"RSI at {rsi14:.1f} is elevated; momentum may be stretched.")
    elif rsi14 < 30:
        score += 1
        reasons.append(f"RSI at {rsi14:.1f} is oversold; this can signal a rebound opportunity but needs confirmation.")
    else:
        reasons.append(f"RSI at {rsi14:.1f} is neutral to weak.")

    if volatility > 45:
        score -= 1
        reasons.append(f"Recent annualised volatility is high ({volatility:.1f}%), increasing position risk.")

    view = "Bullish" if score >= 2 else "Bearish" if score <= -2 else "Neutral"
    risk_note = (
        "High recent volatility: use conservative position sizing and a predefined exit level."
        if volatility > 45
        else "Technical signals can fail around earnings, corporate actions, and macro events."
    )
    return Analysis(
        symbol=ticker_symbol,
        company=info.get("longName") or info.get("shortName"),
        sector=info.get("sector"),
        as_of=str(close.index[-1].date()),
        close=round(latest, 2), ma20=round(ma20, 2), ma50=round(ma50, 2), rsi14=round(rsi14, 1),
        annualised_volatility_pct=round(volatility, 1), drawdown_from_52_week_high_pct=round(drawdown, 1),
        trailing_pe=round(pe, 2) if pe is not None else None, market_cap_inr=cap,
        score=score, view=view, reasons=reasons, risk_note=risk_note,
    )


def print_report(item: Analysis) -> None:
    title = item.company or item.symbol
    print(f"\n{title} ({item.symbol}) — {item.view} research view | score {item.score:+d}")
    print(f"As of {item.as_of}: close ₹{item.close:,.2f} | MA20 ₹{item.ma20:,.2f} | MA50 ₹{item.ma50:,.2f} | RSI14 {item.rsi14:.1f}")
    print(f"Risk: volatility {item.annualised_volatility_pct:.1f}% | drawdown from 52-week high {item.drawdown_from_52_week_high_pct:.1f}%")
    if item.trailing_pe is not None:
        print(f"Trailing P/E: {item.trailing_pe:.2f}")
    for reason in item.reasons:
        print(f"- {reason}")
    print(f"Note: {item.risk_note}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Research-only Indian stock analysis agent")
    parser.add_argument("symbols", nargs="*", help="NSE/BSE symbols; NSE is assumed when no suffix is supplied")
    parser.add_argument("--watchlist", help="Text file containing symbols, one per line")
    parser.add_argument("--period", default="1y", help="Yahoo Finance history period (default: 1y)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()
    symbols = args.symbols[:]
    watchlist_path = args.watchlist

    if not symbols and not watchlist_path:
        requested_symbol = input(
            "Enter an NSE stock symbol (example: RELIANCE): "
        ).strip()

        if not requested_symbol:
            parser.error("Please enter a stock symbol.")

        symbols.append(requested_symbol)


        if watchlist_path and not symbols:
            with open(watchlist_path, encoding="utf-8") as file:
                symbols += [
                    line.strip()
                    for line in file
                    if line.strip() and not line.startswith("#")
                ]

    if not symbols:
        parser.error("No symbols found in the watchlist.")
        parser.error("Provide symbols or --watchlist.")
        parser.error("No symbols found in the watchlist.")

    reports, failures = [], []
    for symbol in dict.fromkeys(symbols):
        try:
            reports.append(analyse(symbol, args.period))
        except Exception as exc:
            failures.append({"symbol": symbol, "error": str(exc)})
    if args.json:
        print(json.dumps({"reports": [asdict(x) for x in reports], "failures": failures}, indent=2))
    else:
        for report in reports:
            print_report(report)
        for failure in failures:
            print(f"\n{failure['symbol']}: unable to analyse — {failure['error']}", file=sys.stderr)
    return 1 if failures and not reports else 0


if __name__ == "__main__":
    raise SystemExit(main())