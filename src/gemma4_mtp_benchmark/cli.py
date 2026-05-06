from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from collections.abc import Iterable
from contextlib import ExitStack
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Optional, TextIO

from .models import MODELS, ModelSpec, get_model_spec
from .prompts import get_prompts, list_prompt_sets


@dataclass
class RunRecord:
    model: str
    backend: str
    mtp: bool
    prompt_index: int
    round_index: int
    load_seconds: float
    generation_seconds: float
    output_chars: int
    chars_per_second: float
    estimated_tokens: float
    estimated_tokens_per_second: float
    preview: str


@dataclass
class ChatTurnStats:
    seconds: float
    output_chars: int
    estimated_tokens: float


def _run_command(args: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        text = (completed.stdout + completed.stderr).strip()
        return completed.returncode, text
    except Exception as exc:  # pragma: no cover - defensive shell integration
        return 1, str(exc)


def _system_profiler_summary() -> dict[str, str]:
    if platform.system() != "Darwin":
        return {}
    code, output = _run_command(["system_profiler", "SPHardwareDataType"], timeout=30)
    if code != 0:
        return {"error": output}

    fields = {}
    for line in output.splitlines():
        stripped = line.strip()
        for key in ("Model Name", "Chip", "Memory"):
            if stripped.startswith(f"{key}:"):
                fields[key.lower().replace(" ", "_")] = stripped.split(":", 1)[1].strip()
    return fields


def collect_environment() -> dict[str, Any]:
    packages = {}
    for name in ("huggingface-hub", "litert-lm-api-nightly"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None

    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "system": platform.system(),
        "mac_hardware": _system_profiler_summary(),
        "packages": packages,
    }


def print_doctor() -> int:
    env = collect_environment()
    print(json.dumps(env, indent=2, ensure_ascii=False))

    if env["system"] == "Darwin" and env["machine"] == "arm64":
        memory = env["mac_hardware"].get("memory", "")
        print("\nApple Silicon Mac detected. GPU benchmarking is a good first target.")
        if memory:
            print(f"Detected memory: {memory}")
    else:
        print("\nThis benchmark is tuned for Apple Silicon Macs, but CPU dry runs still work.")

    missing = [name for name, version in env["packages"].items() if version is None]
    if missing:
        print("\nMissing optional runtime packages:")
        for name in missing:
            print(f"- {name}")
        print("\nInstall the full benchmark stack with:")
        print("  python3 -m pip install -e '.[bench]'")
    return 0


def resolve_model_path(
    model: ModelSpec,
    model_path: Optional[Path],
    cache_dir: Optional[Path],
) -> Path:
    if model_path is not None:
        return model_path.expanduser().resolve()

    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise RuntimeError(
            "huggingface_hub is required for automatic model download. "
            "Install with: python3 -m pip install -e ."
        ) from exc

    path = hf_hub_download(
        repo_id=model.repo_id,
        filename=model.filename,
        cache_dir=str(cache_dir.expanduser()) if cache_dir else None,
    )
    return Path(path)


def _backend_value(litert_lm: Any, backend: str) -> Any:
    normalized = backend.upper()
    try:
        return getattr(litert_lm.Backend, normalized)
    except AttributeError as exc:
        raise ValueError("backend must be cpu or gpu") from exc


def collect_text(stream: Iterable[dict[str, Any]]) -> str:
    parts = []
    for chunk in stream:
        for item in chunk.get("content", []):
            if item.get("type") == "text":
                parts.append(item.get("text", ""))
    return "".join(parts)


def stream_text(stream: Iterable[dict[str, Any]], out: TextIO) -> str:
    parts = []
    for chunk in stream:
        for item in chunk.get("content", []):
            if item.get("type") == "text":
                text = item.get("text", "")
                parts.append(text)
                print(text, end="", file=out, flush=True)
    return "".join(parts)


def estimate_tokens(text: str) -> float:
    if not text:
        return 0.0
    ascii_count = sum(1 for char in text if ord(char) < 128)
    non_ascii_count = len(text) - ascii_count
    return ascii_count / 4.0 + non_ascii_count / 1.8


def _configure_quiet_litert_logs() -> None:
    os.environ.setdefault("GLOG_minloglevel", "2")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("ABSL_MIN_LOG_LEVEL", "2")


def _import_litert_lm() -> Any:
    try:
        import litert_lm
    except ImportError as exc:
        raise RuntimeError(
            "litert_lm is not installed. Install it with: python3 -m pip install -e '.[bench]'"
        ) from exc

    if hasattr(litert_lm, "set_min_log_severity") and hasattr(litert_lm, "LogSeverity"):
        litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)
    return litert_lm


def _engine_kwargs(
    litert_lm: Any,
    backend: str,
    enable_mtp: bool,
    compiled_cache_dir: Optional[Path],
) -> dict[str, Any]:
    engine_kwargs = {
        "backend": _backend_value(litert_lm, backend),
        "enable_speculative_decoding": enable_mtp,
    }
    if compiled_cache_dir is not None:
        engine_kwargs["cache_dir"] = str(compiled_cache_dir.expanduser())
    return engine_kwargs


def _run_single_engine(
    *,
    litert_lm: Any,
    model_path: Path,
    model_key: str,
    backend: str,
    enable_mtp: bool,
    prompts: list[str],
    rounds: int,
    warmups: int,
    preview_chars: int,
    compiled_cache_dir: Optional[Path],
) -> list[RunRecord]:
    engine_kwargs = _engine_kwargs(litert_lm, backend, enable_mtp, compiled_cache_dir)

    load_start = time.perf_counter()
    with litert_lm.Engine(str(model_path), **engine_kwargs) as engine:
        load_seconds = time.perf_counter() - load_start

        for warmup_index in range(warmups):
            with engine.create_conversation() as conversation:
                collect_text(conversation.send_message_async(f"短くOKと返してください。#{warmup_index}"))

        records: list[RunRecord] = []
        for round_index in range(rounds):
            for prompt_index, prompt in enumerate(prompts):
                with engine.create_conversation() as conversation:
                    start = time.perf_counter()
                    text = collect_text(conversation.send_message_async(prompt))
                    elapsed = time.perf_counter() - start

                chars = len(text)
                token_estimate = estimate_tokens(text)
                records.append(
                    RunRecord(
                        model=model_key,
                        backend=backend,
                        mtp=enable_mtp,
                        prompt_index=prompt_index,
                        round_index=round_index,
                        load_seconds=load_seconds,
                        generation_seconds=elapsed,
                        output_chars=chars,
                        chars_per_second=chars / elapsed if elapsed else 0.0,
                        estimated_tokens=token_estimate,
                        estimated_tokens_per_second=token_estimate / elapsed if elapsed else 0.0,
                        preview=text[:preview_chars],
                    )
                )
    return records


def run_benchmark(args: argparse.Namespace) -> int:
    model = get_model_spec(args.model)
    prompts = get_prompts(args.prompt_set)

    if args.dry_run:
        payload = {
            "dry_run": True,
            "model": asdict(model),
            "backend": args.backend,
            "prompt_set": args.prompt_set,
            "rounds": args.rounds,
            "warmups": args.warmups,
            "modes": args.mode,
            "environment": collect_environment(),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    _configure_quiet_litert_logs()
    litert_lm = _import_litert_lm()

    model_path = resolve_model_path(model, args.model_path, args.hf_cache_dir)
    modes = [False, True] if args.mode == "both" else [args.mode == "mtp"]
    records: list[RunRecord] = []

    for enable_mtp in modes:
        print(f"\nRunning model={model.key} backend={args.backend} mtp={enable_mtp}", flush=True)
        records.extend(
            _run_single_engine(
                litert_lm=litert_lm,
                model_path=model_path,
                model_key=model.key,
                backend=args.backend,
                enable_mtp=enable_mtp,
                prompts=prompts,
                rounds=args.rounds,
                warmups=args.warmups,
                preview_chars=args.preview_chars,
                compiled_cache_dir=args.compiled_cache_dir,
            )
        )

    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": asdict(model),
        "model_path": str(model_path),
        "prompt_set": args.prompt_set,
        "prompt_count": len(prompts),
        "environment": collect_environment(),
        "records": [asdict(record) for record in records],
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {args.output}")

    print(render_summary(payload))
    return 0


def _chat_modes(mode: str) -> list[bool]:
    if mode == "compare":
        return [False, True]
    return [mode == "mtp"]


def format_chat_stats(stats_by_mode: dict[bool, ChatTurnStats]) -> str:
    lines = []
    if False in stats_by_mode:
        stats = stats_by_mode[False]
        tokens_per_second = stats.estimated_tokens / stats.seconds if stats.seconds else 0.0
        lines.append(
            f"baseline: {stats.seconds:.2f}s, "
            f"{tokens_per_second:.1f} est tok/s, {stats.output_chars} chars"
        )
    if True in stats_by_mode:
        stats = stats_by_mode[True]
        tokens_per_second = stats.estimated_tokens / stats.seconds if stats.seconds else 0.0
        lines.append(
            f"mtp: {stats.seconds:.2f}s, "
            f"{tokens_per_second:.1f} est tok/s, {stats.output_chars} chars"
        )

    off = stats_by_mode.get(False)
    on = stats_by_mode.get(True)
    if off and on:
        off_tps = off.estimated_tokens / off.seconds if off.seconds else 0.0
        on_tps = on.estimated_tokens / on.seconds if on.seconds else 0.0
        if off_tps:
            lines.append(f"estimated speed ratio: {on_tps / off_tps:.2f}x")

    return "\n".join(lines)


def _warm_up_engine(engine: Any, warmups: int) -> None:
    for warmup_index in range(warmups):
        with engine.create_conversation() as conversation:
            collect_text(conversation.send_message_async(f"短くOKと返してください。#{warmup_index}"))


def run_chat(
    args: argparse.Namespace,
    *,
    input_func: Callable[[str], str] = input,
    out: TextIO = sys.stdout,
) -> int:
    model = get_model_spec(args.model)

    if args.dry_run:
        payload = {
            "dry_run": True,
            "model": asdict(model),
            "backend": args.backend,
            "chat_mode": args.mode,
            "warmups": args.warmups,
            "environment": collect_environment(),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=out)
        return 0

    _configure_quiet_litert_logs()
    litert_lm = _import_litert_lm()
    model_path = resolve_model_path(model, args.model_path, args.hf_cache_dir)
    modes = _chat_modes(args.mode)

    print(
        f"LiteRT-LM chat: model={model.key} backend={args.backend} mode={args.mode}",
        file=out,
        flush=True,
    )
    print("Type /bye, /exit, /quit, or press Ctrl-D to stop.", file=out, flush=True)

    with ExitStack() as stack:
        conversations: dict[bool, Any] = {}
        for enable_mtp in modes:
            label = "mtp" if enable_mtp else "baseline"
            print(f"\nLoading {label} engine...", file=out, flush=True)
            engine = stack.enter_context(
                litert_lm.Engine(
                    str(model_path),
                    **_engine_kwargs(litert_lm, args.backend, enable_mtp, args.compiled_cache_dir),
                )
            )
            _warm_up_engine(engine, args.warmups)
            conversations[enable_mtp] = stack.enter_context(engine.create_conversation())

        while True:
            try:
                prompt = input_func("\nYou > ")
            except EOFError:
                print("", file=out)
                break

            prompt = prompt.strip()
            if not prompt:
                continue
            if prompt.lower() in {"/bye", "/exit", "/quit"}:
                break

            turn_stats: dict[bool, ChatTurnStats] = {}
            for enable_mtp in modes:
                if args.mode == "compare":
                    label = "MTP on" if enable_mtp else "baseline / MTP off"
                    print(f"\n[{label}]", file=out, flush=True)
                else:
                    label = "Gemma MTP" if enable_mtp else "Gemma baseline"
                    print(f"\n{label} > ", end="", file=out, flush=True)

                start = time.perf_counter()
                text = stream_text(conversations[enable_mtp].send_message_async(prompt), out)
                elapsed = time.perf_counter() - start
                print("", file=out)

                turn_stats[enable_mtp] = ChatTurnStats(
                    seconds=elapsed,
                    output_chars=len(text),
                    estimated_tokens=estimate_tokens(text),
                )

            print("\n" + format_chat_stats(turn_stats), file=out, flush=True)

    return 0


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def render_summary(payload: dict[str, Any]) -> str:
    records = payload.get("records", [])
    by_mode: dict[bool, list[dict[str, Any]]] = {False: [], True: []}
    for record in records:
        by_mode[bool(record["mtp"])].append(record)

    lines = [
        "\n| MTP | runs | mean seconds | mean chars/sec | est tokens/sec |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for mtp in (False, True):
        group = by_mode[mtp]
        if not group:
            continue
        lines.append(
            "| {mtp} | {runs} | {seconds:.2f} | {cps:.1f} | {tps:.1f} |".format(
                mtp="on" if mtp else "off",
                runs=len(group),
                seconds=_mean([item["generation_seconds"] for item in group]),
                cps=_mean([item["chars_per_second"] for item in group]),
                tps=_mean([item["estimated_tokens_per_second"] for item in group]),
            )
        )

    off = by_mode[False]
    on = by_mode[True]
    if off and on:
        off_tps = _mean([item["estimated_tokens_per_second"] for item in off])
        on_tps = _mean([item["estimated_tokens_per_second"] for item in on])
        if off_tps:
            lines.append(f"\nEstimated MTP speed ratio: {on_tps / off_tps:.2f}x")

    return "\n".join(lines)


def download_model(args: argparse.Namespace) -> int:
    model = get_model_spec(args.model)
    path = resolve_model_path(model, None, args.hf_cache_dir)
    print(path)
    return 0


def render_report(args: argparse.Namespace) -> int:
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    summary = render_summary(payload)
    print(summary)
    if args.output:
        lines = [
            "# Gemma 4 MTP Benchmark Result",
            "",
            f"- Model: {payload['model']['label']}",
            f"- Prompt set: {payload['prompt_set']}",
            f"- Created at: {payload['created_at']}",
            "",
            summary.strip(),
            "",
            "Note: token/sec is estimated from output text length because LiteRT-LM "
            "streaming chunks do not expose token counts.",
            "",
        ]
        args.output.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gemma4-mtp-bench",
        description="Benchmark Gemma 4 LiteRT-LM with MTP on and off.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Print machine and dependency diagnostics.")

    download = subparsers.add_parser("download", help="Download a LiteRT-LM Gemma 4 model.")
    download.add_argument("--model", choices=sorted(MODELS), default="e2b")
    download.add_argument("--hf-cache-dir", type=Path)

    run = subparsers.add_parser("run", help="Run the MTP on/off benchmark.")
    run.add_argument("--model", choices=sorted(MODELS), default="e2b")
    run.add_argument("--model-path", type=Path)
    run.add_argument("--hf-cache-dir", type=Path)
    run.add_argument("--compiled-cache-dir", type=Path)
    run.add_argument("--backend", choices=["cpu", "gpu"], default="gpu")
    run.add_argument("--mode", choices=["both", "baseline", "mtp"], default="both")
    run.add_argument(
        "--prompt-set",
        choices=sorted(list_prompt_sets().split(", ")),
        default="coding",
    )
    run.add_argument("--rounds", type=int, default=1)
    run.add_argument("--warmups", type=int, default=1)
    run.add_argument("--preview-chars", type=int, default=360)
    run.add_argument("--output", type=Path)
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without loading a model.",
    )

    chat = subparsers.add_parser("chat", help="Chat interactively with LiteRT-LM MTP on/off.")
    chat.add_argument("--model", choices=sorted(MODELS), default="e2b")
    chat.add_argument("--model-path", type=Path)
    chat.add_argument("--hf-cache-dir", type=Path)
    chat.add_argument("--compiled-cache-dir", type=Path)
    chat.add_argument("--backend", choices=["cpu", "gpu"], default="gpu")
    chat.add_argument("--mode", choices=["baseline", "mtp", "compare"], default="mtp")
    chat.add_argument("--warmups", type=int, default=1)
    chat.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate chat configuration without loading a model.",
    )

    report = subparsers.add_parser("report", help="Render a Markdown summary from a JSON result.")
    report.add_argument("input", type=Path)
    report.add_argument("--output", type=Path)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return print_doctor()
        if args.command == "download":
            return download_model(args)
        if args.command == "run":
            return run_benchmark(args)
        if args.command == "chat":
            return run_chat(args)
        if args.command == "report":
            return render_report(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
