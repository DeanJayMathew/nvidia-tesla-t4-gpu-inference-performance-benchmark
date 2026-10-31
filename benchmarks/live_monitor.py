#!/usr/bin/env python3
"""Sample selected vLLM Prometheus metrics from /metrics."""

import argparse
import re
import time

import requests


METRICS = {
    "num_requests_running": "vllm:num_requests_running",
    "num_requests_waiting": "vllm:num_requests_waiting",
}


def read_metric(text: str, metric_name: str) -> float:
    values = []
    pattern = re.compile(r"^" + re.escape(metric_name) + r"(?:\{[^}]*\})?\s+([-+0-9.eE]+)\s*$")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match:
            values.append(float(match.group(1)))
    return sum(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--duration", type=float, default=30)
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()

    metrics_url = args.base_url.rstrip("/") + "/metrics"
    samples = {name: [] for name in METRICS}

    end_time = time.monotonic() + args.duration
    while time.monotonic() < end_time:
        response = requests.get(metrics_url, timeout=10)
        response.raise_for_status()
        body = response.text
        row = {}
        for label, metric in METRICS.items():
            row[label] = read_metric(body, metric)
            samples[label].append(row[label])
        print(
            f"running={row['num_requests_running']:.0f} "
            f"waiting={row['num_requests_waiting']:.0f}"
        )
        time.sleep(args.interval)

    print("\nSummary:")
    for label, values in samples.items():
        print(f"{label}: peak={max(values, default=0):.1f}, average={sum(values) / len(values) if values else 0:.1f}")


if __name__ == "__main__":
    main()
