#!/usr/bin/env python3
"""Run burst concurrency tests against a vLLM chat-completions endpoint."""

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def send_request(url: str, model: str, prompt: str, max_tokens: int) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    start = time.perf_counter()
    response = requests.post(url, json=payload, timeout=600)
    elapsed = time.perf_counter() - start
    response.raise_for_status()
    data = response.json()
    tokens = data.get("usage", {}).get("completion_tokens")
    if tokens is None:
        raise RuntimeError("Response did not include usage.completion_tokens.")
    return {"latency_seconds": elapsed, "completion_tokens": tokens}


def run_level(url: str, model: str, prompt: str, max_tokens: int, concurrency: int) -> dict:
    start = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(send_request, url, model, prompt, max_tokens)
            for _ in range(concurrency)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    wall_time = time.perf_counter() - start

    total_tokens = sum(item["completion_tokens"] for item in results)
    return {
        "concurrency": concurrency,
        "requests_completed": len(results),
        "wall_time_seconds": wall_time,
        "average_latency_seconds": statistics.mean(item["latency_seconds"] for item in results),
        "max_latency_seconds": max(item["latency_seconds"] for item in results),
        "total_output_tokens": total_tokens,
        "aggregate_tokens_per_second": total_tokens / wall_time if wall_time else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--prompt", default="Explain machine learning in three sentences.")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--levels", nargs="+", type=int, default=[1, 2, 4, 8, 16, 32, 64, 96, 128])
    parser.add_argument("--output", help="Optional CSV output path.")
    args = parser.parse_args()

    url = args.base_url.rstrip("/") + "/v1/chat/completions"
    results = []
    for level in args.levels:
        print(f"Running {level} concurrent requests...")
        result = run_level(url, args.model, args.prompt, args.max_tokens, level)
        results.append(result)
        print(
            f"{level:>3} requests | wall={result['wall_time_seconds']:.2f}s | "
            f"avg latency={result['average_latency_seconds']:.2f}s | "
            f"aggregate={result['aggregate_tokens_per_second']:.2f} tokens/s"
        )

    if args.output:
        import csv

        with open(args.output, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"Saved results to {args.output}")


if __name__ == "__main__":
    main()
