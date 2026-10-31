#!/usr/bin/env python3
"""Measure time to first non-empty streamed content chunk and generation throughput."""

import argparse
import json
import statistics
import time

import requests


def run_once(url: str, model: str, prompt: str, max_tokens: int) -> dict:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    start = time.perf_counter()
    first_content_at = None
    completion_tokens = 0

    with requests.post(url, json=payload, stream=True, timeout=300) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                continue

            usage = chunk.get("usage")
            if usage and usage.get("completion_tokens") is not None:
                completion_tokens = usage["completion_tokens"]

            choices = chunk.get("choices") or []
            if choices:
                content = (choices[0].get("delta") or {}).get("content")
                if content and first_content_at is None:
                    first_content_at = time.perf_counter()

    end = time.perf_counter()
    if first_content_at is None:
        raise RuntimeError("No non-empty content chunk received from the streaming API.")

    ttft = first_content_at - start
    total_time = end - start
    if completion_tokens == 0:
        raise RuntimeError("The server did not return completion-token usage. Check stream_options support.")

    generation_seconds = total_time - ttft
    throughput = (completion_tokens - 1) / generation_seconds if generation_seconds > 0 else 0.0
    return {
        "ttft_seconds": ttft,
        "total_seconds": total_time,
        "completion_tokens": completion_tokens,
        "generation_tokens_per_second": throughput,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--prompt", default="Explain machine learning in three sentences.")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    url = args.base_url.rstrip("/") + "/v1/chat/completions"
    results = []
    for index in range(args.runs):
        result = run_once(url, args.model, args.prompt, args.max_tokens)
        results.append(result)
        print(
            f"Run {index + 1}: TTFT={result['ttft_seconds']:.3f}s, "
            f"total={result['total_seconds']:.3f}s, "
            f"tokens={result['completion_tokens']}, "
            f"generation={result['generation_tokens_per_second']:.2f} tokens/s"
        )

    print("\nAverages:")
    for key in ("ttft_seconds", "total_seconds", "generation_tokens_per_second"):
        print(f"{key}: {statistics.mean(item[key] for item in results):.4f}")


if __name__ == "__main__":
    main()
