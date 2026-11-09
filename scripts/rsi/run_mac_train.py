#!/usr/bin/env python3
"""Apple Silicon train/eval for the checklist + gated-recovery idea.

Uses MLX (preferred) or PyTorch MPS for the lightweight checklist head.
Preserves the same FIXED_EVAL_SUITE protocol as the CPU stub / B1K-protocol path.
Does NOT download π0 CUDA weights.

Example:
  python3 scripts/rsi/run_mac_train.py --backend auto --train-steps 200
  python3 scripts/rsi/run_mac_train.py --backend mlx --parity-check
"""

from __future__ import annotations

import argparse
import json
import sys
import time
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
    train_logistic_auto,
)
from openpi.rsi.env_detect import detect_env, format_report  # noqa: E402
from openpi.rsi.mac_backend import detect_mac_backend, resolve_backend  # noqa: E402
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


def plot_mac(history, baseline_agg, trained_agg, backend: str, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    steps = [h["step"] for h in history]
    ax[0].plot(steps, [h["loss"] for h in history], marker="o")
    ax[0].set_title(f"Train loss ({backend})")
    ax[0].set_xlabel("step")
    ax[0].set_ylabel("loss")
    ax[1].plot(steps, [h["acc"] for h in history], marker="o", color="tab:green")
    ax[1].set_title(f"Train accuracy ({backend})")
    ax[1].set_xlabel("step")
    ax[1].set_ylabel("acc")
    fig.tight_layout()
    p1 = out_dir / "mac_train_curves.png"
    fig.savefig(p1, dpi=140)
    plt.close(fig)
    paths.append(p1)

    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["mean Q-score", "E2E success"]
    b = [baseline_agg["mean_q_score"], baseline_agg["e2e_success_rate"]]
    t = [trained_agg["mean_q_score"], trained_agg["e2e_success_rate"]]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, b, width=0.36, label="baseline open-loop")
    ax.bar(x + 0.18, t, width=0.36, label=f"checklist ({backend})")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_title("Mac Silicon — wheeled dual-arm suite")
    ax.legend()
    fig.tight_layout()
    p2 = out_dir / "mac_suite_metrics.png"
    fig.savefig(p2, dpi=140)
    plt.close(fig)
    paths.append(p2)

    tasks = list(baseline_agg["per_task"].keys())
    bq = [baseline_agg["per_task"][t]["mean_q_score"] for t in tasks]
    tq = [trained_agg["per_task"][t]["mean_q_score"] for t in tasks]
    fig, ax = plt.subplots(figsize=(11, 4))
    x = np.arange(len(tasks))
    ax.bar(x - 0.18, bq, width=0.36, label="baseline")
    ax.bar(x + 0.18, tq, width=0.36, label=f"checklist ({backend})")
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("mean Q-score")
    ax.set_ylim(0, 1)
    ax.set_title("Per-task Q-score (Mac protocol)")
    ax.legend()
    fig.tight_layout()
    p3 = out_dir / "mac_per_task_qscore.png"
    fig.savefig(p3, dpi=140)
    plt.close(fig)
    paths.append(p3)
    return paths


def parity_check(xs: np.ndarray, ys: np.ndarray, *, steps: int, lr: float, seed: int) -> dict:
    """Compare CPU vs preferred Mac backend on loss trajectory shape + eval keys."""
    cpu_pol, cpu_hist = train_logistic(xs, ys, steps=steps, lr=lr, seed=seed)
    mac_pol, mac_hist, backend = train_logistic_auto(xs, ys, backend="auto", steps=steps, lr=lr, seed=seed)
    cpu_rows = evaluate_suite(cpu_pol.as_fn(), mode="checklist", episodes_per_task=1)
    mac_rows = evaluate_suite(mac_pol.as_fn(), mode="checklist", episodes_per_task=1)
    keys_ok = all(set(r.keys()) == set(cpu_rows[0].keys()) for r in mac_rows)
    # Protocol parity: same suite size + metric keys; weights need not be bit-identical across backends.
    return {
        "backend": backend,
        "suite_size_match": len(cpu_rows) == len(mac_rows) == len(FIXED_EVAL_SUITE),
        "metric_keys_match": keys_ok,
        "cpu_final_loss": cpu_hist[-1]["loss"],
        "mac_final_loss": mac_hist[-1]["loss"],
        "cpu_final_acc": cpu_hist[-1]["acc"],
        "mac_final_acc": mac_hist[-1]["acc"],
        "weight_l2_delta": float(np.linalg.norm(cpu_pol.weights - mac_pol.weights)),
        "ok": keys_ok and len(cpu_rows) == len(mac_rows) == len(FIXED_EVAL_SUITE),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="auto", choices=["auto", "mlx", "mps", "cpu"])
    ap.add_argument("--train-steps", type=int, default=200)
    ap.add_argument("--episodes-per-task", type=int, default=3)
    ap.add_argument("--out-dir", type=Path, default=ROOT / "rsi" / "experiments" / "mac-silicon-artifacts")
    ap.add_argument("--media-dir", type=Path, default=None)
    ap.add_argument("--parity-check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = detect_env(ROOT)
    mac = detect_mac_backend()
    print(format_report(env))
    print("=== mac backend ===")
    print(json.dumps(mac.__dict__, indent=2, ensure_ascii=False))

    if args.dry_run:
        try:
            chosen = resolve_backend(args.backend)
        except RuntimeError as e:
            print("dry-run backend resolve failed:", e)
            return 2
        print(f"dry-run OK — would train checklist head on backend={chosen}")
        print("π0 openpi JAX CUDA: NOT runnable on Mac (documented gap).")
        return 0

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    base_pol = ChecklistPolicy.baseline_open_loop()
    xs, ys = generate_demo_batch(base_pol, n_samples=800, seed=7)
    xs_f, ys_f, filter_stats = filter_by_subgoal_coverage(xs, ys, min_positive_rate=0.4)

    parity = None
    if args.parity_check:
        parity = parity_check(xs_f, ys_f, steps=min(80, args.train_steps), lr=0.25, seed=1)
        print("parity:", json.dumps(parity, ensure_ascii=False))
        if not parity["ok"]:
            print("ERROR: protocol parity check failed", file=sys.stderr)
            return 5

    t0 = time.perf_counter()
    trained, history, backend = train_logistic_auto(
        xs_f, ys_f, backend=args.backend, steps=args.train_steps, lr=0.25, seed=1
    )
    train_s = time.perf_counter() - t0

    baseline_rows = evaluate_suite(base_pol.as_fn(), mode="baseline", episodes_per_task=args.episodes_per_task)
    trained_rows = evaluate_suite(trained.as_fn(), mode="checklist", episodes_per_task=args.episodes_per_task)
    baseline_agg = aggregate(baseline_rows)
    trained_agg = aggregate(trained_rows)
    plot_paths = plot_mac(history, baseline_agg, trained_agg, backend, out_dir)

    if args.media_dir:
        media = Path(args.media_dir)
        media.mkdir(parents=True, exist_ok=True)
        for p in plot_paths:
            (media / p.name).write_bytes(p.read_bytes())

    metrics = {
        "idea": "subgoal_checklist_gated_recovery",
        "platform": "apple_silicon",
        "backend": backend,
        "train_seconds": round(train_s, 3),
        "memory_gb": mac.memory_gb,
        "gaps_vs_cuda": mac.gaps_vs_cuda,
        "filter_stats": filter_stats,
        "train": {
            "steps": args.train_steps,
            "device": backend,
            "history_tail": history[-3:],
            "weights": trained.weights.tolist(),
        },
        "baseline": baseline_agg,
        "checklist_gated": trained_agg,
        "delta": {
            "mean_q_score": trained_agg["mean_q_score"] - baseline_agg["mean_q_score"],
            "e2e_success_rate": trained_agg["e2e_success_rate"] - baseline_agg["e2e_success_rate"],
        },
        "parity": parity,
        "suite_size": len(FIXED_EVAL_SUITE),
        "plots": [str(p) for p in plot_paths],
        "openpi_pi0": "not_runnable_on_mac",
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "ok": True,
                "backend": backend,
                "out_dir": str(out_dir),
                "delta": metrics["delta"],
                "train_seconds": metrics["train_seconds"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
