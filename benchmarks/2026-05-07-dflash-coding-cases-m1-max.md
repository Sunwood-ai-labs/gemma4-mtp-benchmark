# DFlash coding cases on M1 Max

Date: 2026-05-07  
Machine: Apple M1 Max, 64 GiB memory, macOS 26.4.1, arm64  
Target: `Qwen/Qwen3.5-4B`  
Draft: `z-lab/Qwen3.5-4B-DFlash`  
Max tokens: `320`  
Block size: `16`  
Temperature: `0.0`

## Goal

Check whether "coding prompts are good for DFlash" is actually true, or whether
the result depends on the shape of the coding task.

## Command

```bash
scripts/run-dflash-coding-cases.sh
```

## Result

| case | baseline tok/s | DFlash tok/s | speedup | mean accepted |
| --- | ---: | ---: | ---: | ---: |
| `cli_argparse` | 26.44 | 33.50 | 1.27x | 5.10 |
| `pytest_tests` | 28.76 | 35.63 | 1.24x | 4.57 |
| `unified_diff_fix` | 28.53 | 34.51 | 1.21x | 5.18 |
| `open_architecture` | 24.27 | 19.82 | 0.82x | 3.82 |

## Reading it

Coding is not automatically a win. DFlash helped on constrained coding formats:
argparse CLI scaffolding, pytest test generation, and a unified diff fix. Those
tasks have repeated syntax and a predictable output format, so the draft can
propose blocks that the target accepts.

The open architecture task slowed down. It is still a coding-related prompt, but
the answer has more freedom in structure, ordering, wording, and tradeoff
selection. The mean accepted length dropped to `3.82`, and the extra draft and
verify work cost more than it saved.
