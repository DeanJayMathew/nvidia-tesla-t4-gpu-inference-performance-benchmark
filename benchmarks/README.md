# Benchmark scripts

This directory contains reconstructed Python utilities for testing a running vLLM OpenAI-compatible inference server.

> **Data provenance:** The original Colab notebook was not saved. These scripts are reconstructed tools based on the recorded experiment, not a verified reproduction of the original notebook.

## Scripts

| Script | Purpose |
|---|---|
| `api_smoke_test.py` | Check that the inference endpoint returns a successful completion. |
| `single_request.py` | Measure elapsed time and effective output tokens per second for one request. |
| `streaming_benchmark.py` | Measure time to first non-empty content chunk and streaming generation throughput. |
| `concurrency_benchmark.py` | Run a burst of simultaneous requests and calculate aggregate throughput and average latency. |
| `live_monitor.py` | Sample selected vLLM Prometheus metrics while a workload runs. |

## Requirements

- Python 3.10+
- A reachable vLLM server exposing the OpenAI-compatible `/v1/chat/completions` endpoint.
- The Python packages in the repository's `requirements.txt`.

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

## Start a vLLM server

For a Tesla T4 setup similar to the initial experiment:

```bash
vllm serve Qwen/Qwen2.5-0.5B-Instruct \
  --dtype half \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.85
```

By default, scripts target `http://localhost:8000` and the model `Qwen/Qwen2.5-0.5B-Instruct`. Override these with command-line arguments when required.

## Example commands

Run from the repository root:

```bash
python benchmarks/api_smoke_test.py
python benchmarks/single_request.py --max-tokens 256
python benchmarks/streaming_benchmark.py --runs 3 --max-tokens 256
python benchmarks/concurrency_benchmark.py --levels 1 2 4 8 16 32 64 96 128 --max-tokens 256
python benchmarks/live_monitor.py --duration 30 --interval 0.5
```

The concurrency benchmark submits one burst per concurrency level. It is a simple exploratory test, not a production-grade load generator. Results depend on model, prompt, output length, hardware, server configuration and client environment.

## Important measurement details

- **Elapsed time** is measured client-side and includes request/response overhead.
- **Effective tokens/sec** is output tokens divided by elapsed time; it is not a pure model-kernel decode measurement.
- **TTFT** here is the time until the first non-empty content chunk is received, not a hardware-level measurement of the first generated token.
- **Aggregate throughput** combines output tokens from all requests in a concurrency test divided by the overall wall-clock duration.
- vLLM's `/metrics` counters and histograms are cumulative since server startup. Compare deltas over a defined interval rather than interpreting lifetime counters as a single test.

For the captured experiment and caveats, see the [main README](../README.md) and [results notes](../results/README.md).
