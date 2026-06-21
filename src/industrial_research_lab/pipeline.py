"""Checkpointable experiment profiles and artifact generation."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numba
import numpy as np

from .model import ModelConfig, derive_batch_seed, run_batch, warm_numba, wilson_interval


@dataclass(frozen=True)
class RunProfile:
    name: str
    p_values: tuple[float, ...]
    replication_seeds: tuple[int, ...]
    horizon: int
    batch_size: int
    max_batches_per_configuration: int
    max_minutes: float
    reference_runs: int


PROFILES = {
    "ci": RunProfile(
        name="ci",
        p_values=(0.02, 0.10, 0.20),
        replication_seeds=(20260429,),
        horizon=200,
        batch_size=64,
        max_batches_per_configuration=1,
        max_minutes=2.0,
        reference_runs=64,
    ),
    "smoke": RunProfile(
        name="smoke",
        p_values=(0.02, 0.10, 0.20),
        replication_seeds=(20260429, 20260430),
        horizon=500,
        batch_size=1_000,
        max_batches_per_configuration=2,
        max_minutes=15.0,
        reference_runs=64,
    ),
    "full": RunProfile(
        name="full",
        p_values=(0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20),
        replication_seeds=(20260429, 20260430),
        horizon=1_000,
        batch_size=5_000,
        max_batches_per_configuration=10_000,
        max_minutes=90.0,
        reference_runs=32,
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def profile_payload(profile: RunProfile, max_minutes: float) -> dict[str, object]:
    payload = asdict(profile)
    payload["p_values"] = list(profile.p_values)
    payload["replication_seeds"] = list(profile.replication_seeds)
    payload["effective_max_minutes"] = max_minutes
    return payload


def profile_fingerprint(profile: RunProfile) -> str:
    payload = json.dumps(asdict(profile), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def configurations(profile: RunProfile) -> list[dict[str, object]]:
    values = []
    for replication_index, master_seed in enumerate(profile.replication_seeds):
        for configuration_index, p_value in enumerate(profile.p_values):
            values.append({
                "key": f"seed{replication_index}-p{configuration_index}",
                "replication_index": replication_index,
                "master_seed": master_seed,
                "configuration_index": configuration_index,
                "p": p_value,
            })
    return values


def new_accumulator(config: dict[str, object]) -> dict[str, object]:
    return {
        **config,
        "batches": 0,
        "n_runs": 0,
        "collapses": 0,
        "tau_sum": 0,
        "collapsed_tau_sum": 0,
        "collapsed_tau_count": 0,
        "generation_seconds": 0.0,
        "simulation_seconds": 0.0,
        "reference_seconds": 0.0,
        "reference_exact": True,
        "seed_replay_exact": True,
    }


def initial_state(profile: RunProfile, max_minutes: float) -> dict[str, object]:
    return {
        "schema_version": 1,
        "profile": profile.name,
        "profile_fingerprint": profile_fingerprint(profile),
        "effective_max_minutes": max_minutes,
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "status": "running",
        "accumulators": {
            config["key"]: new_accumulator(config) for config in configurations(profile)
        },
        "batch_records": [],
    }


def load_or_create_state(
    checkpoint: Path,
    profile: RunProfile,
    max_minutes: float,
    resume: bool,
) -> dict[str, object]:
    if resume and checkpoint.exists():
        state = json.loads(checkpoint.read_text(encoding="utf-8"))
        if state.get("profile_fingerprint") != profile_fingerprint(profile):
            raise ValueError("checkpoint profile does not match the requested profile")
        state["status"] = "running"
        state["effective_max_minutes"] = max_minutes
        return state
    return initial_state(profile, max_minutes)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(state: dict[str, object], profile: RunProfile, model: ModelConfig) -> list[dict[str, object]]:
    rows = []
    for accumulator in state["accumulators"].values():
        n_runs = int(accumulator["n_runs"])
        if not n_runs:
            continue
        collapses = int(accumulator["collapses"])
        probability = collapses / n_runs
        ci_low, ci_high = wilson_interval(collapses, n_runs)
        collapsed_count = int(accumulator["collapsed_tau_count"])
        rows.append({
            "replication_index": accumulator["replication_index"],
            "master_seed": accumulator["master_seed"],
            "p": accumulator["p"],
            "lambda": model.demand_rate(float(accumulator["p"])),
            "n_runs": n_runs,
            "batches": accumulator["batches"],
            "collapses": collapses,
            "collapse_probability": probability,
            "wilson95_low": ci_low,
            "wilson95_high": ci_high,
            "restricted_mean_tau_Tplus1": int(accumulator["tau_sum"]) / n_runs,
            "conditional_mean_tau": (
                int(accumulator["collapsed_tau_sum"]) / collapsed_count
                if collapsed_count else None
            ),
            "reference_exact": accumulator["reference_exact"],
            "seed_replay_exact": accumulator["seed_replay_exact"],
        })
    return sorted(rows, key=lambda row: (int(row["replication_index"]), float(row["p"])))


def adjacent_differences(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    effects = []
    seeds = sorted({int(row["master_seed"]) for row in summary_rows})
    for seed in seeds:
        rows = [row for row in summary_rows if int(row["master_seed"]) == seed]
        for low, high in zip(rows, rows[1:]):
            effects.append({
                "master_seed": seed,
                "p_low": low["p"],
                "p_high": high["p"],
                "risk_difference": float(high["collapse_probability"]) - float(low["collapse_probability"]),
            })
    return effects


def write_run_artifacts(
    output_dir: Path,
    state: dict[str, object],
    profile: RunProfile,
    model: ModelConfig,
    warmup_seconds: float,
    elapsed_seconds: float,
    stop_reason: str,
) -> dict[str, object]:
    summary_rows = summarize(state, profile, model)
    effects = adjacent_differences(summary_rows)
    accumulators = list(state["accumulators"].values())
    infrastructure_pass = bool(
        summary_rows
        and all(bool(item["reference_exact"]) for item in accumulators)
        and all(bool(item["seed_replay_exact"]) for item in accumulators)
        and all(int(item["n_runs"]) > 0 for item in accumulators)
    )
    total_runs = sum(int(item["n_runs"]) for item in accumulators)
    payload = {
        "schema_version": 1,
        "profile": profile.name,
        "status": state["status"],
        "stop_reason": stop_reason,
        "infrastructure_pass": infrastructure_pass,
        "scientific_status": "engineering_proof_not_publication_evidence",
        "started_utc": state["created_utc"],
        "finished_utc": utc_now(),
        "elapsed_seconds": elapsed_seconds,
        "total_trajectories": total_runs,
        "model": asdict(model),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpus": os.cpu_count(),
            "numpy": np.__version__,
            "numba": numba.__version__,
            "numba_threads": numba.get_num_threads(),
        },
        "jit_warmup_seconds": warmup_seconds,
        "summary": summary_rows,
        "adjacent_risk_differences": effects,
    }
    atomic_json(output_dir / "summary.json", payload)
    atomic_json(output_dir / "config.json", profile_payload(profile, float(state["effective_max_minutes"])))
    write_csv(output_dir / "summary.csv", summary_rows)
    write_csv(output_dir / "batch_metrics.csv", list(state["batch_records"]))

    generation_seconds = sum(float(item["generation_seconds"]) for item in accumulators)
    simulation_seconds = sum(float(item["simulation_seconds"]) for item in accumulators)
    reference_seconds = sum(float(item["reference_seconds"]) for item in accumulators)
    (output_dir / "PERFORMANCE_REPORT.md").write_text(
        "\n".join([
            "# Performance Report",
            "",
            f"- Profile: `{profile.name}`",
            f"- Total trajectories: {total_runs:,}",
            f"- JIT warm-up: {warmup_seconds:.6f} s",
            f"- Input generation: {generation_seconds:.6f} s",
            f"- Numba simulation: {simulation_seconds:.6f} s",
            f"- Reference validation: {reference_seconds:.6f} s",
            f"- End-to-end elapsed: {elapsed_seconds:.6f} s",
            "- Fastmath: disabled",
            "- Parallel RNG inside Numba: disabled",
            "- Batch seeds: deterministic hierarchy recorded in batch_metrics.csv",
            "",
            "Input generation and Numba execution are reported separately. This is an",
            "engineering benchmark, not a general hardware performance claim.",
            "",
        ]),
        encoding="utf-8",
    )
    (output_dir / "VALIDATION_REPORT.md").write_text(
        "\n".join([
            "# Validation Report",
            "",
            f"- Infrastructure pass: {infrastructure_pass}",
            f"- Stop reason: `{stop_reason}`",
            f"- Reference and Numba exact: {all(bool(item['reference_exact']) for item in accumulators)}",
            f"- Fixed-seed input replay exact: {all(bool(item['seed_replay_exact']) for item in accumulators)}",
            f"- Configurations with data: {len(summary_rows)}/{len(accumulators)}",
            "- Wilson 95% intervals: recorded in summary.csv and summary.json",
            "",
            "The run validates deterministic orchestration and numerical agreement. It does",
            "not establish novelty, causal identification, or publication-ready evidence.",
            "",
        ]),
        encoding="utf-8",
    )
    (output_dir / "RUN_REPORT.md").write_text(
        "\n".join([
            "# Automated Research Run",
            "",
            f"**Profile:** `{profile.name}`  ",
            f"**Status:** `{state['status']}`  ",
            f"**Trajectories:** {total_runs:,}  ",
            f"**Elapsed:** {elapsed_seconds / 60.0:.2f} minutes  ",
            f"**Infrastructure gate:** {'PASS' if infrastructure_pass else 'FAIL'}",
            "",
            "This artifact demonstrates a checkpointable, deterministic Monte Carlo pipeline.",
            "Scientific interpretation remains bounded by the frozen protocol and reports.",
            "",
        ]),
        encoding="utf-8",
    )
    write_manifest(output_dir)
    return payload


def write_manifest(output_dir: Path) -> None:
    manifest_path = output_dir / "RUN_MANIFEST.json"
    checksums_path = output_dir / "CHECKSUMS.sha256"
    items = []
    for path in sorted(output_dir.iterdir()):
        if not path.is_file() or path in {manifest_path, checksums_path}:
            continue
        data = path.read_bytes()
        items.append({
            "path": path.name,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    atomic_json(manifest_path, {"generated_utc": utc_now(), "files": items})
    checksums_path.write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in items),
        encoding="utf-8",
    )


def run_profile(
    profile: RunProfile,
    output_dir: Path,
    max_minutes: float | None = None,
    resume: bool = True,
) -> dict[str, object]:
    effective_minutes = max_minutes if max_minutes is not None else profile.max_minutes
    if effective_minutes <= 0:
        raise ValueError("max_minutes must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / "checkpoint.json"
    state = load_or_create_state(checkpoint, profile, effective_minutes, resume)
    model = ModelConfig(horizon=profile.horizon)
    started = time.perf_counter()
    deadline = started + effective_minutes * 60.0
    warmup_seconds = warm_numba()
    stop_reason = "max_batches"
    last_heartbeat = started

    try:
        while True:
            pending = [
                item for item in state["accumulators"].values()
                if int(item["batches"]) < profile.max_batches_per_configuration
            ]
            if not pending:
                break
            if time.perf_counter() >= deadline:
                stop_reason = "time_budget"
                break
            for accumulator in pending:
                if time.perf_counter() >= deadline:
                    stop_reason = "time_budget"
                    break
                batch_index = int(accumulator["batches"])
                batch_seed = derive_batch_seed(
                    int(accumulator["master_seed"]),
                    int(accumulator["replication_index"]),
                    int(accumulator["configuration_index"]),
                    batch_index,
                )
                metrics = run_batch(
                    model,
                    float(accumulator["p"]),
                    profile.batch_size,
                    batch_seed,
                    profile.reference_runs if batch_index == 0 else 0,
                )
                accumulator["batches"] = batch_index + 1
                for key in (
                    "n_runs", "collapses", "tau_sum", "collapsed_tau_sum",
                    "collapsed_tau_count",
                ):
                    accumulator[key] = int(accumulator[key]) + int(metrics[key])
                for key in ("generation_seconds", "simulation_seconds", "reference_seconds"):
                    accumulator[key] = float(accumulator[key]) + float(metrics[key])
                accumulator["reference_exact"] = bool(accumulator["reference_exact"] and metrics["reference_exact"])
                accumulator["seed_replay_exact"] = bool(accumulator["seed_replay_exact"] and metrics["seed_replay_exact"])
                state["batch_records"].append({
                    "configuration_key": accumulator["key"],
                    "master_seed": accumulator["master_seed"],
                    "p": accumulator["p"],
                    "batch_index": batch_index,
                    "batch_seed": batch_seed,
                    **metrics,
                })
                state["updated_utc"] = utc_now()
                atomic_json(checkpoint, state)
                now = time.perf_counter()
                if now - last_heartbeat >= 30.0:
                    completed = sum(int(item["batches"]) for item in state["accumulators"].values())
                    trajectories = sum(int(item["n_runs"]) for item in state["accumulators"].values())
                    print(json.dumps({
                        "profile": profile.name,
                        "elapsed_minutes": round((now - started) / 60.0, 2),
                        "completed_batches": completed,
                        "trajectories": trajectories,
                    }), flush=True)
                    last_heartbeat = now
            if stop_reason == "time_budget":
                break
    except KeyboardInterrupt:
        stop_reason = "interrupted"

    state["status"] = "complete" if stop_reason in {"max_batches", "time_budget"} else "interrupted"
    state["updated_utc"] = utc_now()
    atomic_json(checkpoint, state)
    elapsed_seconds = time.perf_counter() - started
    return write_run_artifacts(
        output_dir,
        state,
        profile,
        model,
        warmup_seconds,
        elapsed_seconds,
        stop_reason,
    )

