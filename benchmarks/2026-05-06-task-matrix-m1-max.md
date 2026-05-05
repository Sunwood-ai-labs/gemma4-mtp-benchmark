# Task Matrix: MacBook Pro M1 Max 64 GB

This is an exploratory local run from 2026-05-06 in Japan time. It is meant to show task fit, not to be an official benchmark.

## Environment

- Machine: MacBook Pro
- Chip: Apple M1 Max
- Memory: 64 GB
- Architecture: arm64
- OS reported by Python: macOS-26.4.1-arm64-arm-64bit
- LiteRT-LM Python package: litert-lm-api-nightly 0.11.0.dev20260422
- Rounds: 1
- Warmups: 1
- Token/sec: estimated from generated text length

## E2B GPU

| task | MTP off sec | MTP on sec | off est tok/s | on est tok/s | ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| quick | 2.69 | 3.43 | 55.7 | 45.6 | 0.82x |
| summarize | 8.90 | 8.85 | 42.8 | 35.2 | 0.82x |
| rewrite | 5.83 | 6.12 | 35.8 | 36.5 | 1.02x |
| extract | 4.30 | 3.54 | 29.2 | 35.4 | 1.21x |
| json | 2.37 | 1.55 | 22.8 | 34.8 | 1.53x |
| translation | 8.54 | 7.30 | 42.3 | 49.7 | 1.18x |
| creative | 7.88 | 7.95 | 42.0 | 35.7 | 0.85x |

## E4B GPU

| task | MTP off sec | MTP on sec | off est tok/s | on est tok/s | ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| coding | 76.28 | 40.79 | 17.8 | 33.2 | 1.87x |
| summarize | 8.74 | 7.60 | 30.2 | 34.8 | 1.15x |
| rewrite | 5.46 | 4.86 | 27.0 | 30.3 | 1.12x |
| extract | 4.25 | 2.82 | 22.4 | 33.9 | 1.51x |
| json | 2.91 | 1.77 | 17.0 | 28.1 | 1.65x |
| translation | 3.52 | 3.38 | 32.7 | 34.0 | 1.04x |
| creative | 11.15 | 12.30 | 26.8 | 24.3 | 0.91x |

## E2B CPU Spot Check

| task | MTP off sec | MTP on sec | off est tok/s | on est tok/s | ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| json | 4.65 | 2.57 | 11.6 | 20.9 | 1.81x |

## Takeaways

- The strongest wins in this run were structured or predictable tasks: `coding`, `json`, and `extract`.
- Short freeform or more open-ended creative prompts did not improve and sometimes slowed down.
- E4B showed clearer wins than E2B on GPU for the tasks that naturally suit MTP.
- E2B CPU can still show a visible gain on a very structured task, but GPU remains the recommended first path for this benchmark.
- Because this was a one-round local run, repeat with `--rounds 3` or higher before treating a ratio as stable.
