from __future__ import annotations

import os
import time
from collections import Counter
from dataclasses import dataclass

from dflash.model_mlx import load, load_draft, stream_generate
from mlx_lm import stream_generate as baseline_generate
from mlx_lm.sample_utils import make_sampler


@dataclass(frozen=True)
class Case:
    name: str
    prompt: str


CASES = [
    Case(
        "math_step",
        "How many positive whole-number divisors does 196 have? "
        "Please reason step by step, and put your final answer within \\boxed{}.",
    ),
    Case(
        "json_structured",
        "Return only valid JSON. Create 30 task objects with keys id, title, priority, "
        "and estimate_hours. Use predictable short values and no markdown.",
    ),
    Case(
        "creative_open",
        "Write a lyrical, surprising short essay about why local AI feels different "
        "from cloud AI. Avoid bullet points and make each paragraph distinct.",
    ),
]


def chat_prompt(tokenizer, prompt: str, enable_thinking: bool) -> str:
    messages = [{"role": "user", "content": prompt}]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=enable_thinking,
    )


def format_histogram(values: list[int]) -> str:
    counts = Counter(values)
    return ", ".join(f"{key}:{counts[key]}" for key in sorted(counts))


def main() -> int:
    model_id = os.environ.get("DFLASH_MODEL", "Qwen/Qwen3.5-4B")
    draft_id = os.environ.get("DFLASH_DRAFT_MODEL", "z-lab/Qwen3.5-4B-DFlash")
    max_tokens = int(os.environ.get("DFLASH_MAX_NEW_TOKENS", "256"))
    block_size = int(os.environ.get("DFLASH_BLOCK_SIZE", "16"))
    temperature = float(os.environ.get("DFLASH_TEMPERATURE", "0.0"))
    enable_thinking = os.environ.get("DFLASH_ENABLE_THINKING", "1").lower() in {
        "1",
        "true",
        "yes",
    }

    print(f"Target: {model_id}")
    print(f"Draft:  {draft_id}")
    print(f"Max tokens: {max_tokens}")
    print(f"Block size: {block_size}")
    print(f"Temperature: {temperature}")
    print(f"Thinking: {enable_thinking}")
    print()

    model, tokenizer = load(model_id)
    draft = load_draft(draft_id)
    sampler = make_sampler(temp=temperature)

    warmup_prompt = chat_prompt(tokenizer, "Say OK.", enable_thinking)
    list(baseline_generate(model, tokenizer, warmup_prompt, 8, sampler=sampler))
    list(
        stream_generate(
            model,
            draft,
            tokenizer,
            warmup_prompt,
            block_size=block_size,
            max_tokens=8,
            sampler=sampler,
        )
    )

    print(
        "| case | baseline tok/s | DFlash tok/s | speedup | mean accepted | accepted histogram |"
    )
    print("| --- | ---: | ---: | ---: | ---: | --- |")

    for case in CASES:
        prompt = chat_prompt(tokenizer, case.prompt, enable_thinking)

        baseline_tokens = []
        baseline_tps = 0.0
        start = time.perf_counter()
        for response in baseline_generate(model, tokenizer, prompt, max_tokens, sampler=sampler):
            baseline_tokens.append(response.token)
            baseline_tps = response.generation_tps
        baseline_elapsed = time.perf_counter() - start

        dflash_tokens = []
        accepted = []
        dflash_tps = 0.0
        start = time.perf_counter()
        for response in stream_generate(
            model,
            draft,
            tokenizer,
            prompt,
            block_size=block_size,
            max_tokens=max_tokens,
            sampler=sampler,
        ):
            dflash_tokens.extend(response.tokens)
            if response.accepted:
                accepted.append(response.accepted)
            dflash_tps = response.generation_tps
        dflash_elapsed = time.perf_counter() - start

        speedup = dflash_tps / baseline_tps if baseline_tps else 0.0
        mean_accepted = sum(accepted) / len(accepted) if accepted else 0.0
        print(
            f"| {case.name} | {baseline_tps:.2f} | {dflash_tps:.2f} | "
            f"{speedup:.2f}x | {mean_accepted:.2f} | {format_histogram(accepted)} |"
        )
        print(
            f"  tokens: baseline={len(baseline_tokens)} in {baseline_elapsed:.2f}s, "
            f"dflash={len(dflash_tokens)} in {dflash_elapsed:.2f}s"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
