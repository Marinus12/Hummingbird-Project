from tools.backtest_runner import run_backtest
from tools.sample_strategy import simple_momentum

res = run_backtest(simple_momentum, "data/sample_1m.csv", latency_ms=3.0)
print("RESULTS:", res)