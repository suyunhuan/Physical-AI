#!/usr/bin/env python3
"""One-entry local pipeline for Mac / CUDA Linux.

Modes:
  dry-run       detect env + print commands only
  cpu-stub      first-idea CPU checklist loop (works on Mac Mini)
  mac           Apple Silicon MLX/MPS checklist train+eval (preferred on M-series)
  openpi-gpu    real openpi train (CUDA Linux + DOWNLOAD_WEIGHTS)
  b1k-protocol  B1K-aligned protocol eval (CPU)
  b1k-official  real B1K if installed
  all-safe      dry-run + mac-or-cpu-stub + b1k-protocol (default for Mac)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from openpi.rsi.env_detect import detect_env, format_report  # noqa: E402


def run(cmd: list[str]) -> int:
    print("+", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mode",
        default="all-safe",
        choices=["dry-run", "cpu-stub", "mac", "openpi-gpu", "b1k-protocol", "b1k-official", "all-safe"],
    )
    args = ap.parse_args()
    py = sys.executable
    env = detect_env(ROOT)
    print(format_report(env))

    if args.mode == "dry-run":
        print("\nSuggested next commands:")
        print(f"  {py} scripts/rsi/run_mac_train.py --backend auto --train-steps 200 --parity-check")
        print(f"  {py} scripts/rsi/run_first_idea_loop.py --train-steps 100")
        print(f"  {py} scripts/rsi/run_b1k_aligned_eval.py --protocol")
        print("  DOWNLOAD_WEIGHTS=1 uv run python scripts/rsi/run_openpi_train.py --config pi0_libero_checklist_smoke")
        if env.apple_silicon:
            print(f"\nThis machine: Apple Silicon → preferred mode=mac (backend={env.mac_backend})")
        return 0

    if args.mode == "mac":
        return run(
            [
                py,
                "scripts/rsi/run_mac_train.py",
                "--backend",
                "auto",
                "--train-steps",
                "200",
                "--episodes-per-task",
                "3",
                "--parity-check",
            ]
        )

    if args.mode in {"cpu-stub", "all-safe"}:
        if args.mode == "all-safe" and env.apple_silicon and env.mac_backend in {"mlx", "mps"}:
            rc = run(
                [
                    py,
                    "scripts/rsi/run_mac_train.py",
                    "--backend",
                    "auto",
                    "--train-steps",
                    "200",
                    "--episodes-per-task",
                    "3",
                    "--parity-check",
                ]
            )
        else:
            rc = run([py, "scripts/rsi/run_first_idea_loop.py", "--train-steps", "200", "--episodes-per-task", "3"])
        if rc != 0:
            return rc

    if args.mode in {"b1k-protocol", "all-safe"}:
        rc = run([py, "scripts/rsi/run_b1k_aligned_eval.py", "--protocol"])
        if rc != 0:
            return rc

    if args.mode == "openpi-gpu":
        return run([py, "scripts/rsi/run_openpi_train.py", "--config", "pi0_libero_checklist_smoke"])

    if args.mode == "b1k-official":
        return run([py, "scripts/rsi/run_b1k_aligned_eval.py", "--official"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
