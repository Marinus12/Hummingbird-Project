"""
tools/backtest_runner.py
Expanded backtest runner with:
- Latency simulation
- Slippage (basis points)
- Position sizing and cash tracking
- PnL and win-rate metrics
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, Generator, Any

def compute_metrics(equity_curve: pd.Series) -> Dict[str, float]:
    """Compute Sharpe ratio and maximum drawdown."""
    returns = equity_curve.pct_change().dropna()
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if not returns.empty else 0.0

    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_drawdown = drawdown.min() if not drawdown.empty else 0.0

    return {
        "sharpe_ratio": round(float(sharpe), 3),
        "max_drawdown": round(float(max_drawdown * 100), 2)
    }

def run_backtest(
    strategy_fn: Callable[[pd.DataFrame], Generator[Dict[str, Any], None, None]],
    data_csv: str,
    latency_ms: float = 0.0,
    starting_cash: float = 100000.0,
    slippage_bps: float = 1.0
) -> Dict[str, Any]:
    """
    Runs a more realistic backtest simulation.

    Args:
        strategy_fn: function yielding trade dicts {'time','side','price','size'}.
        data_csv: path to CSV containing OHLCV data (must include 'timestamp' and 'close').
        latency_ms: artificial execution delay in milliseconds.
        starting_cash: initial portfolio value.
        slippage_bps: slippage in basis points (0.01%).

    Returns:
        dict: backtest summary containing PnL, equity, trades, etc.
    """
    df = pd.read_csv(data_csv, parse_dates=['timestamp']).sort_values('timestamp')

    cash = starting_cash
    position = 0.0
    trades = []

    for trade in strategy_fn(df):
        side = trade.get('side')
        price = float(trade.get('price', 0))
        size = float(trade.get('size', 1))
        exec_time = trade['time'] + pd.Timedelta(milliseconds=latency_ms)

        # Apply slippage
        slip = price * (slippage_bps / 10000.0)
        exec_price = price + slip if side == 'buy' else price - slip

        if side == 'buy':
            cost = exec_price * size
            if cash >= cost:
                cash -= cost
                position += size
                trades.append({
                    **trade,
                    'exec_time': exec_time,
                    'exec_price': exec_price
                })
        elif side == 'sell':
            if position >= size:
                cash += exec_price * size
                position -= size
                trades.append({
                    **trade,
                    'exec_time': exec_time,
                    'exec_price': exec_price
                })

    last_price = df['close'].iloc[-1]
    equity = cash + position * last_price
    pnl = equity - starting_cash
    total_trades = len(trades)

    win_trades = [
        t for t in trades
        if t['side'] == 'sell' and t['exec_price'] > t['price']
    ]
    win_rate = (len(win_trades) / (total_trades / 2)) * 100 if total_trades >= 2 else 0.0

    return {
        'pnl': round(pnl, 2),
        'final_equity': round(equity, 2),
        'cash': round(cash, 2),
        'position': round(position, 4),
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'trades': trades
    }


if __name__ == '__main__':
    from tools.sample_strategy import simple_momentum
    result = run_backtest(simple_momentum, 'data/sample_1m.csv', latency_ms=3.0)
    print(result)