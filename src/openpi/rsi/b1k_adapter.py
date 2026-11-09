"""B1K / BEHAVIOR adapter + protocol dry-run.

Real OmniGibson/BEHAVIOR is external to openpi. This module:
1) probes for a local B1K install (B1K_ROOT / imports);
2) runs a *protocol* dry-run that exercises checklist Q-score reporting
   on wheeled dual-arm household tasks (aligned metrics, not official leaderboard);
3) documents how to plug the official evaluator when available.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from openpi.rsi.env_detect import detect_env
from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE, evaluate_suite
from openpi.rsi.checklist_policy import ChecklistPolicy


@dataclass
class B1KProbe:
    available: bool
    root: str | None
    detail: str
    official_eval_cmd: list[str]


def probe_b1k() -> B1KProbe:
    root = os.environ.get("B1K_ROOT") or os.environ.get("BEHAVIOR_ROOT")
    if root and Path(root).exists():
        return B1KProbe(
            available=True,
            root=root,
            detail=f"Found B1K_ROOT={root}. Wire official challenge eval scripts from this tree.",
            official_eval_cmd=[
                "bash",
                "-lc",
                f"cd {root} && echo 'TODO: replace with official BEHAVIOR challenge eval entrypoint'",
            ],
        )
    # Try common imports without failing hard
    for name in ("omnigibson",):
        try:
            __import__(name)
            return B1KProbe(
                available=True,
                root=root,
                detail=f"Importable module `{name}` present; set B1K_ROOT for challenge assets.",
                official_eval_cmd=["python", "-c", "import omnigibson; print(omnigibson.__file__)"],
            )
        except Exception:
            continue
    return B1KProbe(
        available=False,
        root=root,
        detail=(
            "B1K/OmniGibson not installed. Install per https://behavior.stanford.edu/challenge/ "
            "and export B1K_ROOT=/path/to/behavior. Meanwhile use protocol dry-run "
            "(wheeled dual-arm suite + Q-score)."
        ),
        official_eval_cmd=[],
    )


def run_protocol_eval(*, episodes_per_task: int = 3, out: Path | None = None) -> dict:
    """Metric-aligned protocol eval (not official B1K leaderboard scores)."""
    baseline = ChecklistPolicy.baseline_open_loop()
    rows_b = evaluate_suite(baseline.as_fn(), mode="baseline", episodes_per_task=episodes_per_task)
    # Reuse trained weights file if present from first-idea artifacts
    trained = baseline
    art = Path("rsi/experiments/first-idea-artifacts/metrics.json")
    if art.exists():
        data = json.loads(art.read_text())
        w = data.get("train", {}).get("weights")
        if w:
            trained = ChecklistPolicy(weights=__import__("numpy").asarray(w, dtype=float), name="trained_checklist")
    rows_t = evaluate_suite(trained.as_fn(), mode="checklist", episodes_per_task=episodes_per_task)

    def agg(rows):
        import numpy as np

        q = [r["q_score"] for r in rows]
        e = [1.0 if r["e2e_success"] else 0.0 for r in rows]
        return {
            "n": len(rows),
            "mean_q_score": float(sum(q) / len(q)),
            "e2e_success_rate": float(sum(e) / len(e)),
        }

    probe = probe_b1k()
    env = detect_env()
    result = {
        "protocol": "b1k_aligned_wheeled_bimanual_qscore",
        "official_b1k": asdict(probe),
        "env_recommended_mode": env.recommended_mode,
        "suite": [t.task_id for t in FIXED_EVAL_SUITE],
        "baseline": agg(rows_b),
        "checklist_gated": agg(rows_t),
        "note": "These are protocol metrics, NOT official BEHAVIOR leaderboard numbers.",
    }
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result
