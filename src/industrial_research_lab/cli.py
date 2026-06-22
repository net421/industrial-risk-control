"""Command-line entry point for portfolio experiment profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import PROFILES, run_profile


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("--profile", choices=sorted(PROFILES), default="ci")
    command.add_argument("--output", type=Path)
    command.add_argument("--max-minutes", type=float)
    command.add_argument("--fresh", action="store_true", help="Ignore an existing checkpoint")
    return command


def main() -> int:
    args = parser().parse_args()
    output = args.output or Path("artifacts") / f"{args.profile}-local"
    result = run_profile(
        PROFILES[args.profile],
        output,
        max_minutes=args.max_minutes,
        resume=not args.fresh,
    )
    print(json.dumps({
        "profile": result["profile"],
        "status": result["status"],
        "stop_reason": result["stop_reason"],
        "infrastructure_pass": result["infrastructure_pass"],
        "total_trajectories": result["total_trajectories"],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0 if result["infrastructure_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
