#!/usr/bin/env python3
"""Measure client-observed latency and effective output throughput for one request."""

import argparse
import time

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--prompt", default="Explain machine learning in three sentences.")
    parser.add_argument("--max-tokens", type=int, default=256)
    args = parser.parse_args()

    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
        "max_tokens": args.max_tokens,
        "temperature": 0,
    }
    url = args.base_url.rstrip("/") + "/v1/chat/completions"

    start = time.perf_counter()
    response = requests.post(url, json=payload, timeout=300)
    elapsed = time.perf_counter() - start
    response.raise_for_status()

    data = response.json()
    usage = data.get("usage", {})
    output_tokens = usage.get("completion_tokens")

    print(f"HTTP status: {response.status_code}")
    print(f"Client-observed elapsed time: {elapsed:.3f} s")
    print(f"Output tokens: {output_tokens if output_tokens is not None else 'not reported'}")
    if output_tokens is not None and elapsed > 0:
        print(f"Effective output throughput: {output_tokens / elapsed:.2f} tokens/s")
    print("\nNote: elapsed time includes client, network and server overhead; it is not pure GPU decode speed.")


if __name__ == "__main__":
    main()
