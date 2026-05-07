# DFlash success-case rerun on M1 Max

Date: 2026-05-07  
Machine: Apple M1 Max, 64 GiB memory, macOS 26.4.1, arm64  
Target: `Qwen/Qwen3.5-4B`  
Draft: `z-lab/Qwen3.5-4B-DFlash`  
Max tokens: `256`  
Block size: `16`  
Temperature: `0.0`

## Goal

Rerun the contrast experiment and confirm a positive case, not only slowdown or flat cases.

## Command

```bash
scripts/run-dflash-contrast.sh
```

## Result

| case | baseline tok/s | DFlash tok/s | speedup | mean accepted |
| --- | ---: | ---: | ---: | ---: |
| `math_step` | 19.15 | 26.45 | 1.38x | 6.59 |
| `json_structured` | 17.24 | 17.88 | 1.04x | 5.14 |
| `creative_open` | 15.36 | 13.73 | 0.89x | 3.62 |

## Reading it

`math_step` is the clean success case in this rerun. The same accepted length as the earlier run (`6.59`) still translated into a positive speedup, although the absolute tokens/sec were lower under this run's machine load. This reinforces the main finding: DFlash works best when the draft can propose a predictable block and the runtime can keep draft/verify overhead below the target work saved.
