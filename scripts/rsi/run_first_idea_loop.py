#!/usr/bin/env python3
"""First RSI idea loop: subgoal checklist + gated recovery on wheeled dual-arm household suite.

Runs on CPU without openpi GPU weights. Emits metrics JSON + plots.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from openpi.rsi.checklist_policy import (  # noqa: E402
    ChecklistPolicy,
    filter_by_subgoal_coverage,
    generate_demo_batch,
    train_logistic,
)
from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE, evaluate_suite  # noqa: E402


def aggregate(rows: list[dict]) -> dict:
    q = np.array([r["q_score"] for r in rows], dtype=np.float64)
    e2e = np.array([1.0 if r["e2e_success"] else 0.0 for r in rows], dtype=np.float64)
    by_task: dict[str, dict] = {}
    for r in rows:
        tid = r["task_id"]
        by_task.setdefault(tid, {"q": [], "e2e": []})
        by_task[tid]["q"].append(r["q_score"])
        by_task[tid]["e2e"].append(1.0 if r["e2e_success"] else 0.0)
    return {
        "n_episodes": len(rows),
        "mean_q_score": float(q.mean()),
        "std_q_score": float(q.std()),
        "e2e_success_rate": float(e2e.mean()),
        "per_task": {
            tid: {
                "mean_q_score": float(np.mean(v["q"])),
                "e2e_success_rate": float(np.mean(v["e2e"])),
            }
            for tid, v in by_task.items()
        },
    }


def plot_results(history, baseline_agg, trained_agg, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    # 1) training curves
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    steps = [h["step"] for h in history]
    ax[0].plot(steps, [h["loss"] for h in history], marker="o")
    ax[0].set_title("Train loss (CPU logistic)")
    ax[0].set_xlabel("step")
    ax[0].set_ylabel("loss")
    ax[1].plot(steps, [h["acc"] for h in history], marker="o", color="tab:green")
    ax[1].set_title("Train accuracy")
    ax[1].set_xlabel("step")
    ax[1].set_ylabel("acc")
    fig.tight_layout()
    p1 = out_dir / "train_curves.png"
    fig.savefig(p1, dpi=140)
    plt.close(fig)
    paths.append(p1)

    # 2) baseline vs checklist metrics
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["mean Q-score", "E2E success"]
    b = [baseline_agg["mean_q_score"], baseline_agg["e2e_success_rate"]]
    t = [trained_agg["mean_q_score"], trained_agg["e2e_success_rate"]]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, b, width=0.36, label="baseline open-loop")
    ax.bar(x + 0.18, t, width=0.36, label="checklist+gated recovery")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_title("Fixed wheeled dual-arm household suite")
    ax.legend()
    fig.tight_layout()
    p2 = out_dir / "suite_metrics.png"
    fig.savefig(p2, dpi=140)
    plt.close(fig)
    paths.append(p2)

    # 3) per-task Q-score
    tasks = list(baseline_agg["per_task"].keys())
    bq = [baseline_agg["per_task"][t]["mean_q_score"] for t in tasks]
    tq = [trained_agg["per_task"][t]["mean_q_score"] for t in tasks]
    fig, ax = plt.subplots(figsize=(11, 4))
    x = np.arange(len(tasks))
    ax.bar(x - 0.18, bq, width=0.36, label="baseline")
    ax.bar(x + 0.18, tq, width=0.36, label="checklist")
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("mean Q-score")
    ax.set_ylim(0, 1)
    ax.set_title("Per-task Q-score (subgoal fraction)")
    ax.legend()
    fig.tight_layout()
    p3 = out_dir / "per_task_qscore.png"
    fig.savefig(p3, dpi=140)
    plt.close(fig)
    paths.append(p3)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=ROOT / "rsi" / "experiments" / "first-idea-artifacts")
    ap.add_argument("--media-dir", type=Path, default=None)
    ap.add_argument("--train-steps", type=int, default=400)
    ap.add_argument("--episodes-per-task", type=int, default=5)
    args = ap.parse_args()
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    blockers = []
    try:
        import subprocess

        r = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if r.returncode != 0:
            blockers.append("No GPU (nvidia-smi failed): cannot run π0/openpi weight fine-tune.")
    except FileNotFoundError:
        blockers.append("No GPU / nvidia-smi missing: π0 fine-tune blocked; CPU checklist smoke train only.")

    # --- data plan execution (synthetic) ---
    base_pol = ChecklistPolicy.baseline_open_loop()
    xs, ys = generate_demo_batch(base_pol, n_samples=800, seed=7)
    xs_f, ys_f, filter_stats = filter_by_subgoal_coverage(xs, ys, min_positive_rate=0.4)

    # --- train ---
    trained, history = train_logistic(xs_f, ys_f, steps=args.train_steps, lr=0.25, seed=1)

    # --- fixed eval ---
    baseline_rows = evaluate_suite(base_pol.as_fn(), mode="baseline", episodes_per_task=args.episodes_per_task)
    trained_rows = evaluate_suite(trained.as_fn(), mode="checklist", episodes_per_task=args.episodes_per_task)
    baseline_agg = aggregate(baseline_rows)
    trained_agg = aggregate(trained_rows)

    plot_paths = plot_results(history, baseline_agg, trained_agg, out_dir)
    if args.media_dir:
        media = Path(args.media_dir)
        media.mkdir(parents=True, exist_ok=True)
        for p in plot_paths:
            target = media / p.name
            target.write_bytes(p.read_bytes())

    metrics = {
        "idea": "subgoal_checklist_gated_recovery",
        "H": {
            "task_slice": "8 wheeled dual-arm household long-horizon chains",
            "embodiment": "wheeled_base + bimanual grippers (abstract sim)",
            "data_recipe": "synthetic demos + subgoal-coverage filter (>=0.4 positive)",
            "eval": "FIXED_EVAL_SUITE, 5 episodes/task, E2E + Q-score",
        },
        "blockers": blockers,
        "filter_stats": filter_stats,
        "train": {
            "steps": args.train_steps,
            "device": "cpu",
            "history_tail": history[-3:],
            "weights": trained.weights.tolist(),
        },
        "baseline": baseline_agg,
        "checklist_gated": trained_agg,
        "delta": {
            "mean_q_score": trained_agg["mean_q_score"] - baseline_agg["mean_q_score"],
            "e2e_success_rate": trained_agg["e2e_success_rate"] - baseline_agg["e2e_success_rate"],
        },
        "suite_size": len(FIXED_EVAL_SUITE),
        "plots": [str(p) for p in plot_paths],
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "baseline_episodes.json").write_text(json.dumps(baseline_rows, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "checklist_episodes.json").write_text(json.dumps(trained_rows, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "out_dir": str(out_dir), "delta": metrics["delta"], "blockers": blockers}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
