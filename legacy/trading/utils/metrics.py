from __future__ import annotations

import pandas as pd


def calculate_equity_curve(trades: pd.DataFrame, initial_balance: float = 10000) -> pd.DataFrame:
    out = trades.copy()
    out["equity"] = initial_balance + out["pnl"].cumsum()
    return out


def max_drawdown(equity_series: pd.Series) -> float:
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    return float(drawdown.min()) if not drawdown.empty else 0.0


def summarize_trades(trades: pd.DataFrame, initial_balance: float = 10000) -> dict:
    if trades.empty:
        return {
            "trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "net_profit": 0.0,
            "avg_trade": 0.0,
            "max_drawdown": 0.0,
        }

    wins = trades[trades["pnl"] > 0]
    losses = trades[trades["pnl"] < 0]

    gross_profit = wins["pnl"].sum()
    gross_loss = abs(losses["pnl"].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

    win_rate = len(wins) / len(trades) * 100
    net_profit = trades["pnl"].sum()
    avg_trade = trades["pnl"].mean()

    equity = calculate_equity_curve(trades, initial_balance)
    mdd = max_drawdown(equity["equity"])

    return {
        "trades": int(len(trades)),
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "net_profit": float(net_profit),
        "avg_trade": float(avg_trade),
        "max_drawdown": float(mdd),
    }