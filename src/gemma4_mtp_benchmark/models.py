from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    repo_id: str
    filename: str
    disk_size_gb: float
    recommended_memory_gb: int


MODELS = {
    "e2b": ModelSpec(
        key="e2b",
        label="Gemma 4 E2B IT LiteRT-LM",
        repo_id="litert-community/gemma-4-E2B-it-litert-lm",
        filename="gemma-4-E2B-it.litertlm",
        disk_size_gb=2.58,
        recommended_memory_gb=8,
    ),
    "e4b": ModelSpec(
        key="e4b",
        label="Gemma 4 E4B IT LiteRT-LM",
        repo_id="litert-community/gemma-4-E4B-it-litert-lm",
        filename="gemma-4-E4B-it.litertlm",
        disk_size_gb=3.66,
        recommended_memory_gb=16,
    ),
}


def get_model_spec(key: str) -> ModelSpec:
    try:
        return MODELS[key.lower()]
    except KeyError as exc:
        known = ", ".join(sorted(MODELS))
        raise ValueError(f"Unknown model '{key}'. Choose one of: {known}") from exc
