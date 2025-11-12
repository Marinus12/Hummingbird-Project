"""
agents/hummingbird_agent.py
--------------------------------
Main orchestration logic for the Hummingbird AI Agent.
Integrates latency estimator and backtest runner to form an
end-to-end analysis workflow.
"""

import os
from datetime import datetime
from tools.latency_estimator import compare_locations
from tools.backtest_runner import run_backtest
from tools.sample_strategy import simple_momentum


def run_latency_adjusted_backtest(
    data_csv: str,
    origin: str,
    destination: str,
    distance_km: float,
    strategy_fn=simple_momentum,
    slippage_bps: float = 1.0,
    starting_cash: float = 100000.0,
    save_log: bool = True
):
    """
    Complete workflow:
    1. Estimate latency between origin & destination.
    2. Pass that latency to the backtest runner.
    3. Return combined performance + latency results.
    """

    print(f"\n[1/3] Estimating latency between {origin} → {destination} ({distance_km} km)...")
    latency_stats = compare_locations(origin, destination, distance_km)
    latency_ms = latency_stats["round_trip_latency_ms"] / 2  # one-way latency

    print(f"    ↳ Route: {latency_stats['route']}")
    print(f"    ↳ One-way latency: {latency_ms:.2f} ms")

    print(f"\n[2/3] Running backtest with simulated latency {latency_ms:.2f} ms...")
    backtest_results = run_backtest(
        strategy_fn=strategy_fn,
        data_csv=data_csv,
        latency_ms=latency_ms,
        slippage_bps=slippage_bps,
        starting_cash=starting_cash
    )

    print("[3/3] Combining performance and latency results...")
    combined_results = {
        "origin": origin,
        "destination": destination,
        "latency_ms": round(latency_ms, 2),
        **latency_stats,
        **backtest_results
    }

    # Optional logging to file
    if save_log:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"logs/run_{timestamp}.txt"
        with open(log_path, "w") as f:
            f.write("=== Hummingbird Backtest Report ===\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Origin: {origin}\nDestination: {destination}\n")
            f.write(f"Latency (ms): {latency_ms:.2f}\n\n")
            f.write("Results:\n")
            for k, v in combined_results.items():
                f.write(f"  {k}: {v}\n")
        print(f"\n🗂️  Results saved to: {log_path}")

    return combined_results


if __name__ == "__main__":
    print("\n🚀 Running integrated latency-adjusted backtest demo...\n")

    try:
        result = run_latency_adjusted_backtest(
            data_csv="data/sample_1m.csv",
            origin="Kansas City",
            destination="New York",
            distance_km=1800
        )

        print("\n✅ Combined Results:\n")
        for k, v in result.items():
            print(f"{k}: {v}")
        print("\n🎉 Run complete.\n")

    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user. Exiting gracefully...")
    except FileNotFoundError as e:
        print(f"\n❌ Data file not found: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")