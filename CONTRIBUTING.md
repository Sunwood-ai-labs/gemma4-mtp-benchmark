# Contributing

Thanks for helping make local Gemma 4 MTP benchmarking easier to reproduce.

Useful contributions include:

- benchmark results from different Apple Silicon Macs
- bug reports for LiteRT-LM install or backend issues
- clearer prompts that make the MTP difference easier to feel
- small portability fixes for Linux or CPU-only runs

Before opening a pull request:

```bash
python3 -m compileall src
PYTHONPATH=src python3 -m gemma4_mtp_benchmark run --model e2b --backend gpu --dry-run
```

Do not commit model files, Hugging Face caches, or generated result files unless they are intentionally small examples.
