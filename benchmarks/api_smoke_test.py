#!/usr/bin/env python3
"""Send a small completion request to a running vLLM OpenAI-compatible API."""

import argparse
import json
import sys

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--prompt", default="Explain machine learning in three sentences.")
    parser.add_argument("--max-tokens", type=int, default=100)
    args = parser.parse_args()

    url = args.base_url.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
        "max_tokens": args.max_tokens,
        "temperature": 0,
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"API request failed: {exc}", file=sys.stderr)
        return 1

    data = response.json()
    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    usage = data.get("usage", {})

    print("API request successful (HTTP 200)")
    print("\nAssistant response:\n")
    print(message.get("content", ""))
    print("\nUsage:")
    print(json.dumps(usage, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
