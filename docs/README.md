# Technical Documentation

This directory contains explanations of the inference concepts, measurements and system behaviour investigated by this project.

## Topics

- **Inference latency:** request latency, time to first token (TTFT), and inter-token latency.
- **Throughput:** per-request generation speed versus aggregate tokens per second across concurrent requests.
- **GPU memory:** model weights, runtime allocations and the key-value (KV) cache.
- **Continuous batching:** how vLLM schedules active requests together as sequences arrive and finish.
- **Monitoring:** GPU utilisation, memory use and vLLM's Prometheus-compatible metrics.

## Measurement notes

The initial experiment used Qwen/Qwen2.5-0.5B-Instruct with vLLM 0.32.0 on a Google Colab NVIDIA Tesla T4. The main project README records the captured aggregate results and their limitations.

The original Colab notebook and raw per-request records were not retained. Any reconstructed scripts must be validated before being described as an exact reproduction of the original experiment.

## Further reading

- [vLLM documentation](https://docs.vllm.ai/)
- [vLLM GitHub repository](https://github.com/vllm-project/vllm)
- [NVIDIA Tesla T4 specifications](https://www.nvidia.com/en-us/data-center/tesla-t4/)
- [Prometheus documentation](https://prometheus.io/docs/introduction/overview/)
