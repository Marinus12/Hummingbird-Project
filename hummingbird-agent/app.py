"""
app.py — Flask bridge for Hummingbird AI Agent
-----------------------------------------------
Exposes endpoints for:
1. Running a latency-adjusted backtest
2. Estimating latency between locations
3. Generating a Base64-encoded chart of backtest results
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.hummingbird_agent import run_latency_adjusted_backtest
from tools.latency_estimator import compare_locations
import io
import os
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import random

# Initialize Flask
CORS(app, origins=[
    "https://chat.openai.com",
    "https://hummingbird-agent.onrender.com"
])

@app.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    allowed = ["https://chat.openai.com", "https://hummingbird-agent.onrender.com"]
    if origin in allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

# ✅ Utility: Create a chart and return Base64 string
def create_backtest_chart(equity_curve, title="Equity Curve"):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(equity_curve, linewidth=2, color="tab:blue")
    ax.set_title(title)
    ax.set_xlabel("Time (steps)")
    ax.set_ylabel("Equity ($)")
    ax.grid(True, linestyle="--", alpha=0.6)

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_base64


# ✅ Route 1: Run full latency-adjusted backtest
@app.route("/run_latency_adjusted_backtest", methods=["POST"])
def run_latency_adjusted_backtest_endpoint():
    """
    Expects JSON like:
    {
        "origin": "Kansas City",
        "destination": "New York",
        "distance_km": 1800,
        "data_csv": "data/sample_1m.csv"
    }
    """
    try:
        payload = request.get_json(force=True)
        origin = payload.get("origin")
        destination = payload.get("destination")
        distance_km = float(payload.get("distance_km", 0))
        data_csv = payload.get("data_csv", "data/sample_1m.csv")

        result = run_latency_adjusted_backtest(
            data_csv=data_csv,
            origin=origin,
            destination=destination,
            distance_km=distance_km
        )

        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Route 2: Just estimate latency between two points
@app.route("/estimate_latency", methods=["POST"])
def estimate_latency_endpoint():
    """
    Expects JSON like:
    {
        "origin": "New York",
        "destination": "Chicago",
        "distance_km": 1150
    }
    """
    try:
        payload = request.get_json(force=True)
        origin = payload.get("origin")
        destination = payload.get("destination")
        distance_km = float(payload.get("distance_km", 0))

        result = compare_locations(origin, destination, distance_km)
        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Route 3: Generate a backtest chart
@app.route("/generate_backtest_chart", methods=["POST"])
def generate_backtest_chart_endpoint():
    """
    Expects JSON like:
    {
        "equity_curve": [100000, 100050, 100100, ...],
        "title": "Sample Equity Curve"
    }
    Returns:
    {
        "status": "success",
        "image_base64": "<base64-encoded PNG>"
    }
    """
    try:
        payload = request.get_json(force=True)
        equity_curve = payload.get("equity_curve")

        # Fallback: simulate a random curve if none provided
        if not equity_curve:
            equity_curve = [
                100000 + random.gauss(0, 50) + i * random.uniform(-10, 15)
                for i in range(120)
            ]

        title = payload.get("title", "Simulated Equity Curve")
        image_b64 = create_backtest_chart(equity_curve, title)

        return jsonify({
            "status": "success",
            "image_base64": image_b64
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ Root health check route
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Hummingbird AI Agent Backend is running.",
        "endpoints": [
            "/run_latency_adjusted_backtest",
            "/estimate_latency",
            "/generate_backtest_chart"
        ]
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)