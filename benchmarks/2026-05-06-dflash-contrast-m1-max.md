# DFlash contrast experiment on M1 Max

Date: 2026-05-06  
Machine: Apple M1 Max, 64 GiB memory, macOS 26.4.1, arm64  
Target: `Qwen/Qwen3.5-4B`  
Draft: `z-lab/Qwen3.5-4B-DFlash`  
Max tokens: `256`  
Block size: `16`  
Temperature: `0.0`

## Goal

This experiment is designed to make the difference visible. It runs the same target and draft model across three prompt styles:

| Case | Expected behavior |
| --- | --- |
| `math_step` | Predictable reasoning text, likely better acceptance |
| `json_structured` | Structured output, often draft-friendly |
| `creative_open` | Open-ended wording, likely lower acceptance |

The key DFlash metric is `accepted`: how many proposed tokens from the 16-token draft block are accepted before the target model disagrees. Higher acceptance means the extra draft work is more likely to pay off.

## Command

```bash
scripts/run-dflash-contrast.sh
```

## Result

| case | baseline tok/s | DFlash tok/s | speedup | mean accepted | accepted histogram |
| --- | ---: | ---: | ---: | ---: | --- |
| `math_step` | 30.61 | 56.80 | 1.86x | 6.59 | 1:3, 2:5, 3:2, 4:5, 5:5, 6:1, 7:1, 8:3, 9:4, 10:2, 11:4, 12:2, 16:2 |
| `json_structured` | 30.46 | 43.74 | 1.44x | 5.14 | 1:7, 2:8, 3:7, 4:5, 5:4, 6:3, 7:3, 8:2, 9:3, 10:5, 12:1, 13:1, 16:1 |
| `creative_open` | 30.03 | 27.85 | 0.93x | 3.62 | 1:20, 2:17, 3:8, 4:9, 5:4, 6:2, 7:2, 8:3, 9:1, 10:1, 11:1, 12:1, 15:1, 16:1 |

## Reading it

The baseline target model stayed around `30 tok/s` across all three prompts. DFlash changed dramatically depending on acceptance:

- `math_step`: mean accepted `6.59`, speedup `1.86x`
- `json_structured`: mean accepted `5.14`, speedup `1.44x`
- `creative_open`: mean accepted `3.62`, speedup `0.93x`

That makes the mechanism visible: DFlash is useful when the draft model can get enough of the next block right. When acceptance falls, the draft and rollback overhead eats the gain.
