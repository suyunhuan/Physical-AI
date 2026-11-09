#!/usr/bin/env python3
"""Launch real openpi training for the first-idea checklist smoke config.

Safety gates:
- Requires CUDA GPU unless ALLOW_CPU_JAX=1
- Requires DOWNLOAD_WEIGHTS=1 OR an existing local cache of the checkpoint
- Does not robot-deploy

Example (Linux + CUDA):
  DOWNLOAD_WEIGHTS=1 uv run python scripts/rsi/run_openpi_train.py \\
      --config pi0_libero_checklist_smoke
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from openpi.rsi.env_detect import detect_env  # noqa: E402

DEFAULT_WEIGHT_URI = "gs://openpi-assets/checkpoints/pi0_base/params"


def _cache_path_for_gs(uri: str) -> Path:
    # Mirrors openpi.shared.download layout: cache / netloc / path
    from urllib.parse import urlparse

    parsed = urlparse(uri)
    cache = Path(os.environ.get("OPENPI_DATA_HOME", "~/.cache/openpi")).expanduser()
    return (cache / parsed.netloc / parsed.path.strip("/")).resolve()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="pi0_libero_checklist_smoke")
    ap.add_argument("--exp-name", default="rsi_checklist_smoke")
    ap.add_argument("--dry-run", action="store_true", help="Only print the command")
    ap.add_argument("--allow-cpu", action="store_true", help="Override CUDA requirement (slow)")
    args = ap.parse_args()

    env = detect_env(ROOT)
    print("=== env ===")
    for m in env.messages:
        print("*", m)

    allow_cpu = args.allow_cpu or os.environ.get("ALLOW_CPU_JAX", "0") in {"1", "true", "TRUE"}
    download = os.environ.get("DOWNLOAD_WEIGHTS", "0") in {"1", "true", "TRUE", "yes", "YES"}
    local = _cache_path_for_gs(DEFAULT_WEIGHT_URI)

    uv = shutil.which("uv")
    if uv:
        cmd = [
            uv,
            "run",
            "scripts/train.py",
            args.config,
            f"--exp-name={args.exp_name}",
        ]
    else:
        cmd = [sys.executable, "scripts/train.py", args.config, f"--exp-name={args.exp_name}"]

    print("=== launch ===")
    print(" ".join(cmd))
    if args.dry_run:
        print("dry-run: not executing (skipped CUDA/weight gates)")
        if not env.cuda_visible:
            print("note: real run would fail without CUDA unless --allow-cpu / ALLOW_CPU_JAX=1")
        if not local.exists() and not download:
            print(f"note: real run needs DOWNLOAD_WEIGHTS=1 or cache at {local}")
        return 0

    if not env.cuda_visible and not allow_cpu:
        print(
            "ERROR: No CUDA GPU detected. Refusing openpi π0 train.\n"
            "  - On Apple Silicon Mac: use `python scripts/rsi/run_local_pipeline.py --mode mac`\n"
            "    (MLX/MPS checklist path — protocol parity only; not full π0)\n"
            "  - Or CPU stub: `python scripts/rsi/run_local_pipeline.py --mode cpu-stub`\n"
            "  - On Linux+CUDA: ensure nvidia drivers + JAX CUDA are installed\n"
            "  - Override (not recommended): ALLOW_CPU_JAX=1 or --allow-cpu",
            file=sys.stderr,
        )
        return 2

    if not local.exists() and not download:
        print(
            "ERROR: Checkpoint not in cache and DOWNLOAD_WEIGHTS is not set.\n"
            f"  Expected cache path: {local}\n"
            "  To allow download (large): DOWNLOAD_WEIGHTS=1 \\\n"
            f"    uv run python scripts/rsi/run_openpi_train.py --config {args.config}\n"
            "  Or pre-populate OPENPI_DATA_HOME with pi0_base/params.",
            file=sys.stderr,
        )
        return 3

    if env.disk_free_gb < 20 and download:
        print(
            f"ERROR: Only {env.disk_free_gb:.1f} GiB free; refusing weight download. Free disk or set OPENPI_DATA_HOME.",
            file=sys.stderr,
        )
        return 4

    # Ensure download helper can run when user opted in (openpi uses maybe_download internally)
    env_vars = os.environ.copy()
    if download:
        env_vars.setdefault("DOWNLOAD_WEIGHTS", "1")
    return subprocess.call(cmd, cwd=ROOT, env=env_vars)


if __name__ == "__main__":
    raise SystemExit(main())
