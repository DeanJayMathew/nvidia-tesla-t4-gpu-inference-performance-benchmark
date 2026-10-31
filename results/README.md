# Benchmark results

This directory documents the aggregate measurements captured during the initial exploratory experiment.

## Concurrency results

| Concurrent requests | Total elapsed (s) | Average request latency (s) | Aggregate throughput (tokens/s) |
|---:|---:|---:|---:|
| 1 | 1.60 | 1.60 | 160.38 |
| 2 | 1.54 | 1.53 | 333.44 |
| 4 | 1.54 | 1.54 | 663.20 |
| 8 | 1.79 | 1.77 | 1,147.22 |
| 16 | 2.09 | 2.07 | 1,960.64 |
| 32 | 2.72 | 2.68 | 3,007.24 |
| 64 | 3.81 | 3.70 | 4,296.89 |
| 96 | 4.39 | 4.24 | 5,593.91 |
| 128 | 5.40 | 5.05 | 6,063.05 |

The recorded average latency is the mean elapsed time per request. Total elapsed is the wall-clock duration for the batch. Aggregate throughput is the total output tokens across requests divided by the batch wall-clock duration.

## Streaming measurements

Three runs, each generating 256 output tokens:

| Run | TTFT (s) | Total time (s) | Generation throughput (tokens/s) |
|---:|---:|---:|---:|
| 1 | 0.024 | 1.482 | 174.89 |
| 2 | 0.023 | 1.475 | 175.57 |
| 3 | 0.027 | 1.489 | 174.53 |
| **Average** | **0.025** | **1.482** | **175.00** |

TTFT is measured to the first non-empty streamed content chunk. Generation throughput was calculated as (completion tokens - 1) divided by (total time - TTFT).

## GPU and live metrics observations

- Separate 64-request monitoring run: average GPU utilisation 89%; peak 100%; average and peak reported VRAM use 12,699 MiB.
- Separate 128-request monitoring run: peak running requests 128; peak waiting requests 0; average running requests 119.5 across 45 samples over 5.24 seconds.
- vLLM metrics were also scraped after the benchmark workload. Those counters and histograms were cumulative since server startup, not isolated to the 128-request test.

## Data provenance and limitations

The original notebook was not saved, and raw per-request records were not retained. The tables above transcribe the aggregate values recorded during the experiment. No raw CSV dataset is claimed to exist in this repository.

The measurements were collected on Google Colab with a Tesla T4, Qwen/Qwen2.5-0.5B-Instruct, vLLM 0.32.0, FP16, a 2,048-token maximum model length and 256-token requested outputs for the concurrency tests.

These results are exploratory and specific to this setup. They should not be presented as a production capacity guarantee or as proof of the exact point of GPU saturation.
