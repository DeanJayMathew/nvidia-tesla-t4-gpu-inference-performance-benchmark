# LLM inference performance concepts

This document defines the measurements and system concepts used in this benchmark.

## Latency

Latency is the time a client waits for a request to complete. In these scripts, elapsed time is measured on the client and includes request transmission, server processing and response transfer. It is not a direct measurement of GPU kernel execution.

## Time to first token (TTFT)

TTFT is the time from sending a streaming request until the client receives its first non-empty generated content chunk. This is a useful user-experience measure: it approximates how long a user waits before text begins appearing.

The streaming script measures the first non-empty content chunk, so the value includes client, transport and server overhead. It should not be described as a hardware-level token timestamp.

## Inter-token latency

Inter-token latency describes the time between successive generated tokens. vLLM exposes histogram metrics for time per output token. When interpreting histograms, remember that counters are cumulative from server startup; calculate differences over a defined measurement window to estimate a test-specific rate or average.

## Throughput

Per-request generation throughput describes how quickly one request's output is produced. Aggregate throughput combines output tokens from all requests in a workload and divides by the total wall-clock time.

These values answer different questions. Under concurrent load, aggregate throughput can rise even while individual requests take longer to complete.

## KV cache and GPU memory

Autoregressive language models repeatedly attend to previous tokens. Inference engines store key and value tensors from attention layers in a key-value (KV) cache so they do not need to be recomputed for every generated token.

The KV cache consumes GPU memory. Available memory is shared among model weights, KV cache and other runtime allocations. More cache capacity can allow more active sequences or longer contexts, but actual capacity depends on model architecture, precision, sequence lengths and runtime implementation.

## Continuous batching

Continuous batching is a scheduling approach in which requests can enter and leave a batch as they arrive and finish. Unlike static batching, the engine does not need to wait for every sequence in a fixed batch to complete before admitting new work.

This can improve GPU utilisation and aggregate throughput for mixed request workloads. It does not mean every request has the same latency.

## GPU utilisation

GPU utilisation is a sampled indicator of how busy the GPU is. A high value suggests substantial activity, but does not by itself identify the limiting resource. Memory bandwidth, compute, CPU/client overhead, request scheduling and memory capacity can all influence end-to-end performance.

## Reading this project's results

The observed increase in aggregate throughput and diminishing incremental gains at higher concurrency is consistent with a system approaching a performance limit. The measurements alone do not prove which resource caused the diminishing returns or establish the hardware's maximum capacity. Controlled experiments with different model sizes, context lengths, output lengths and GPU configurations are needed to investigate the bottleneck.
