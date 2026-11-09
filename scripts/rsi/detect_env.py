#!/usr/bin/env python3
"""Print local env capabilities for openpi / B1K runs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from openpi.rsi.env_detect import detect_env, format_report  # noqa: E402


def main() -> int:
    report = detect_env(ROOT)
    print(format_report(report))
    # Non-zero if user asked for GPU mode implicitly? Keep 0; pipeline decides.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
