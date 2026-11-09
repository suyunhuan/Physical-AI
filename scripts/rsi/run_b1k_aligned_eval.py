#!/usr/bin/env python3
"""B1K-aligned eval entry.

Modes:
  --protocol   metric-aligned wheeled dual-arm suite (always works, CPU)
  --official   attempt real B1K/OmniGibson eval if installed; else fail clearly
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from openpi.rsi.b1k_adapter import probe_b1k, run_protocol_eval  # noqa: E402
from openpi.rsi.env_detect import detect_env  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", action="store_true", default=True)
    ap.add_argument("--official", action="store_true", help="Require real B1K install")
    ap.add_argument("--episodes-per-task", type=int, default=3)
    ap.add_argument("--out", type=Path, default=ROOT / "rsi" / "experiments" / "b1k-protocol-metrics.json")
    args = ap.parse_args()

    env = detect_env(ROOT)
    print(json.dumps({"recommended_mode": env.recommended_mode, "cuda": env.cuda_visible}, ensure_ascii=False))

    if args.official:
        probe = probe_b1k()
        print(json.dumps(probe.__dict__, ensure_ascii=False, indent=2))
        if not probe.available:
            print("ERROR: official B1K requested but not available.", file=sys.stderr)
            print(probe.detail, file=sys.stderr)
            return 2
        if probe.official_eval_cmd:
            print("Running official cmd:", probe.official_eval_cmd)
            return subprocess.call(probe.official_eval_cmd, cwd=ROOT)
        print("ERROR: B1K present but no eval cmd wired yet; update b1k_adapter.probe_b1k().", file=sys.stderr)
        return 3

    result = run_protocol_eval(episodes_per_task=args.episodes_per_task, out=args.out)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
