# NVIDIA Tesla T4: LLM Inference Performance Benchmark

An experimental investigation of large language model (LLM) inference performance on an NVIDIA Tesla T4 GPU, using [vLLM](https://github.com/vllm-project/vllm).

## Research question

**How does concurrency affect LLM inference performance on an NVIDIA Tesla T4, and at what point do additional concurrent requests produce diminishing throughput returns?**

The experiment deployed an open-source instruction-tuned model behind a vLLM API, then measured response latency and token throughput as the number of simultaneous requests increased.

## Preliminary findings

The initial experiment used Qwen2.5-0.5B-Instruct with vLLM on a Tesla T4.

| Concurrent requests | Aggregate throughput (tokens/sec) | Average request latency |
|---:|---:|---:|
| 1 | 160.38 | 1.60 s |
| 2 | 333.44 | 1.53 s |
| 4 | 663.20 | 1.54 s |
| 8 | 1,147.22 | 1.77 s |
| 16 | 1,960.64 | 2.07 s |
| 32 | 3,007.24 | 2.68 s |
| 64 | 4,296.89 | 3.70 s |
| 96 | 5,593.91 | 4.24 s |
| 128 | 6,063.05 | 5.05 s |

Throughput increased with concurrency, while the incremental gains diminished at higher request counts:

- 32 to 64 concurrent requests: approximately 43% more aggregate throughput.
- 64 to 96: approximately 30% more.
- 96 to 128: approximately 8.4% more, despite a 33% increase in concurrency.

This suggests diminishing throughput returns for this specific model, GPU and test configuration. It does **not** establish the Tesla T4's maximum capacity or prove that the GPU was fully saturated at 128 requests.

### Other captured observations

- Streaming time to first non-empty content chunk: 25 ms average across three runs.
- Streaming generation throughput: approximately 175 tokens/sec across three runs.
- During a separate 64-request monitoring run, GPU utilisation averaged 89% and peaked at 100%; reported VRAM use averaged and peaked at 12,699 MiB.
- During a separate 128-request monitoring run, the peak number of running requests was 128, with no waiting requests observed in the monitoring samples.

These were separate test runs and should not be treated as simultaneous measurements from one identical workload.

## Test environment

| Component | Configuration |
|---|---|
| Cloud environment | Google Colab |
| GPU | NVIDIA Tesla T4 |
| GPU memory | 16 GB nominal |
| Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Model parameters | 0.5 billion |
| Inference engine | vLLM 0.32.0 |
| Precision | FP16 |
| Maximum model length | 2,048 tokens |
| GPU memory utilisation setting | 0.85 |
| Python | 3.13.16 |
| PyTorch | 2.13.0+cu132 |

## Methodology

The recorded experiment included:

1. API smoke test to confirm successful model responses through the OpenAI-compatible vLLM endpoint.
2. Single-request generation test.
3. Streaming test measuring time to first non-empty content chunk and generation throughput.
4. Burst concurrency tests at 1, 2, 4, 8, 16, 32, 64, 96 and 128 simultaneous requests.
5. Separate GPU monitoring and vLLM metrics collection.

The concurrency tests used a common prompt and requested up to 256 output tokens per request.

## Repository contents

- `benchmarks/`: reconstructed Python tools for API checks, single-request, streaming, concurrency and metrics monitoring.
- `results/`: captured aggregate results and notes about data provenance.
- `docs/`: explanations of inference performance concepts and measurement interpretation.

## Reproducing the experiment

The original Google Colab notebook and raw per-request records were not retained. The scripts in this repository are reconstructed utilities based on the recorded setup and methodology; they have not been verified as byte-for-byte reproductions of the original notebook.

See [Benchmark usage](benchmarks/README.md) for setup and commands. Use a running vLLM server and ensure the model, GPU, software versions and workload settings match before comparing results.

## Limitations

- The model is small (0.5B parameters); larger models can behave very differently.
- The GPU was provided through a shared cloud environment, not dedicated production hardware.
- The concurrency workload is a burst test, not a comprehensive production load test.
- Raw per-request records were not retained; only aggregate observations were captured.
- GPU utilisation measurements were collected in a separate run from the 128-request throughput test.
- A throughput plateau alone does not identify the bottleneck. GPU compute, memory bandwidth, KV-cache capacity, scheduler behaviour and client-side overhead would require further controlled experiments.

## Next steps

- Validate the reconstructed scripts in a fresh Colab T4 runtime.
- Preserve raw per-request output and machine-readable results for future runs.
- Compare different model sizes and output lengths.
- Investigate KV-cache usage and continuous batching behaviour.
- Compare configurations and, where available, GPU types.

## Technologies

NVIDIA Tesla T4 · CUDA · Python · PyTorch · vLLM · Hugging Face · OpenAI-compatible API · Prometheus metrics · Git
