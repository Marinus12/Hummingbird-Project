"""
tools/latency_estimator.py
---------------------------
Latency Estimator Module for Hummingbird AI Agent.

Simulates latency between trading locations, APIs, or servers.
It can:
- Estimate theoretical latency (speed of light in fiber)
- Add overhead for routers, APIs, and congestion
- Benchmark actual round-trip time via ping or API request
"""

import math
import random
import time
from typing import Dict, Optional

import requests  # make sure 'requests' is installed in your venv


# Constants
SPEED_OF_LIGHT_FIBER_KM_PER_MS = 200.0  # 200,000 km/s = 200 km/ms
AVERAGE_OVERHEAD_MS = 1.5  # router and switching delay (approx)


def estimate_fiber_latency(distance_km: float, overhead_ms: float = AVERAGE_OVERHEAD_MS) -> float:
    """
    Estimate one-way latency (ms) based on distance in kilometers.

    Args:
        distance_km: distance between locations in km
        overhead_ms: typical network overhead (ms)
    Returns:
        float: estimated one-way latency in milliseconds
    """
    return (distance_km / SPEED_OF_LIGHT_FIBER_KM_PER_MS) + overhead_ms


def round_trip_latency(distance_km: float, jitter: float = 0.2) -> float:
    """
    Simulate round-trip latency (ms) including random jitter.

    Args:
        distance_km: distance in km
        jitter: percentage of variation (0.2 = ±20%)
    Returns:
        float: simulated RTT latency in milliseconds
    """
    base = estimate_fiber_latency(distance_km) * 2
    variation = base * random.uniform(-jitter, jitter)
    return round(base + variation, 3)


def api_latency_test(url: str, timeout: float = 3.0) -> Optional[float]:
    """
    Measure API endpoint latency via HTTP GET.

    Args:
        url: URL to test
        timeout: request timeout (s)
    Returns:
        float | None: latency in ms if success, None if failed
    """
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = (time.time() - start) * 1000.0  # ms
        if response.status_code == 200:
            return round(elapsed, 2)
        return None
    except requests.RequestException:
        return None


def compare_locations(name_a: str, name_b: str, distance_km: float) -> Dict[str, float]:
    """
    Compare theoretical and simulated latency between two named locations.

    Args:
        name_a: first location
        name_b: second location
        distance_km: fiber distance between them
    Returns:
        dict: latency metrics
    """
    one_way = estimate_fiber_latency(distance_km)
    rtt = round_trip_latency(distance_km)
    return {
        "route": f"{name_a} ↔ {name_b}",
        "distance_km": distance_km,
        "one_way_latency_ms": round(one_way, 3),
        "round_trip_latency_ms": rtt,
    }


if __name__ == "__main__":
    print("Example theoretical latency calculations:\n")
    ny_to_chicago = compare_locations("New York", "Chicago", 1150)
    kc_to_ny = compare_locations("Kansas City", "New York", 1800)

    print(ny_to_chicago)
    print(kc_to_ny)

    # Optional API latency test
    print("\nTesting API latency...")
    result = api_latency_test("https://api.github.com")
    if result:
        print(f"GitHub API latency: {result} ms")
    else:
        print("API latency test failed or timed out.")
