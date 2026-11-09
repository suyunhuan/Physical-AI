"""Tiny checklist-conditioned policy head (CPU / numpy).

Stand-in for a frozen VLA action chunk + light ranking head.
Features: [difficulty, subgoal_progress, subgoal_idx_norm, bias]
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from openpi.rsi.wheeled_bimanual_sim import HouseholdTask


@dataclass
class ChecklistPolicy:
    weights: np.ndarray  # shape (4,)
    name: str = "checklist_mlp"

    @classmethod
    def zeros(cls) -> "ChecklistPolicy":
        return cls(weights=np.zeros(4, dtype=np.float64))

    @classmethod
    def baseline_open_loop(cls) -> "ChecklistPolicy":
        # Mild positive logit so baseline has non-trivial success
        return cls(weights=np.array([0.2, 0.1, 0.0, 0.4], dtype=np.float64), name="baseline")

    def features(self, task: HouseholdTask, subgoal_idx: int, state: np.ndarray) -> np.ndarray:
        n = max(len(task.subgoal_names) - 1, 1)
        return np.array(
            [
                float(state[0]),  # difficulty
                float(state[2]),  # completed fraction so far
                subgoal_idx / n,
                1.0,  # bias
            ],
            dtype=np.float64,
        )

    def logit(self, task: HouseholdTask, subgoal_idx: int, state: np.ndarray) -> float:
        x = self.features(task, subgoal_idx, state)
        return float(self.weights @ x)

    def as_fn(self):
        def _fn(task, subgoal_idx, state):
            return self.logit(task, subgoal_idx, state)

        return _fn


def generate_demo_batch(
    policy: ChecklistPolicy,
    *,
    n_samples: int = 512,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Synthetic demos labeled by whether a subgoal *should* succeed under teacher.

    Teacher: higher weight on progress + lower difficulty sensitivity.
    """
    from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE

    rng = np.random.default_rng(seed)
    teacher = ChecklistPolicy(weights=np.array([-0.8, 1.2, 0.3, 1.0], dtype=np.float64), name="teacher")
    xs, ys = [], []
    tasks = list(FIXED_EVAL_SUITE)
    for _ in range(n_samples):
        task = tasks[int(rng.integers(0, len(tasks)))]
        idx = int(rng.integers(0, len(task.subgoal_names)))
        completed_frac = float(rng.random())
        state = np.array([task.difficulty, idx / max(len(task.subgoal_names) - 1, 1), completed_frac])
        x = policy.features(task, idx, state)
        # label from teacher success probability (hard label)
        t_logit = teacher.logit(task, idx, state)
        p = 1.0 / (1.0 + np.exp(-(t_logit - 1.5 * task.difficulty)))
        y = 1.0 if rng.random() < p else 0.0
        xs.append(x)
        ys.append(y)
    return np.stack(xs), np.asarray(ys, dtype=np.float64)


def filter_by_subgoal_coverage(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    min_positive_rate: float = 0.35,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Data recipe lever: keep batches where positive (successful subgoal) rate is adequate.

    For this synthetic setup we filter *rows* that are positive OR keep negatives with
    probability scaled so overall positive rate >= min_positive_rate when possible.
    """
    pos = ys > 0.5
    n_pos = int(pos.sum())
    n_neg = int((~pos).sum())
    if n_pos == 0:
        return xs, ys, {"kept": len(ys), "positive_rate": 0.0, "filtered": True}
    # Keep all positives; downsample negatives
    target_neg = int(n_pos * (1.0 - min_positive_rate) / max(min_positive_rate, 1e-6))
    target_neg = min(n_neg, max(target_neg, 0))
    neg_idx = np.flatnonzero(~pos)
    rng = np.random.default_rng(0)
    keep_neg = neg_idx if target_neg >= n_neg else rng.choice(neg_idx, size=target_neg, replace=False)
    keep = np.concatenate([np.flatnonzero(pos), keep_neg])
    keep.sort()
    xs_f, ys_f = xs[keep], ys[keep]
    return xs_f, ys_f, {
        "kept": int(len(ys_f)),
        "positive_rate": float(ys_f.mean()) if len(ys_f) else 0.0,
        "n_pos": n_pos,
        "n_neg_kept": int(len(keep_neg)),
        "filtered": True,
    }


def train_logistic(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    steps: int = 400,
    lr: float = 0.2,
    seed: int = 0,
) -> tuple[ChecklistPolicy, list[dict]]:
    """Minimal CPU training: logistic regression via SGD."""
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 0.05, size=xs.shape[1])
    history: list[dict] = []
    n = len(ys)
    for step in range(steps):
        # mini-batch
        idx = rng.choice(n, size=min(64, n), replace=False)
        xb, yb = xs[idx], ys[idx]
        logits = xb @ w
        probs = 1.0 / (1.0 + np.exp(-logits))
        grad = xb.T @ (probs - yb) / len(yb)
        w -= lr * grad
        if step % 20 == 0 or step == steps - 1:
            p_all = 1.0 / (1.0 + np.exp(-(xs @ w)))
            loss = float(-np.mean(ys * np.log(p_all + 1e-8) + (1 - ys) * np.log(1 - p_all + 1e-8)))
            acc = float(((p_all > 0.5) == (ys > 0.5)).mean())
            history.append({"step": step, "loss": loss, "acc": acc})
    return ChecklistPolicy(weights=w, name="trained_checklist"), history
