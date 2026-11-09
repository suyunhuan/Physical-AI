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
            history.append({"step": step, "loss": loss, "acc": acc, "backend": "cpu"})
    return ChecklistPolicy(weights=w, name="trained_checklist"), history


def train_logistic_mps(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    steps: int = 400,
    lr: float = 0.2,
    seed: int = 0,
) -> tuple[ChecklistPolicy, list[dict]]:
    """Same logistic objective on PyTorch MPS (Apple Silicon)."""
    import torch

    if not (torch.backends.mps.is_available() and torch.backends.mps.is_built()):
        raise RuntimeError("PyTorch MPS is not available on this machine.")

    device = torch.device("mps")
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    x_all = torch.tensor(xs, dtype=torch.float32, device=device)
    y_all = torch.tensor(ys, dtype=torch.float32, device=device)
    w = torch.randn(xs.shape[1], dtype=torch.float32, device=device) * 0.05
    history: list[dict] = []
    n = len(ys)
    for step in range(steps):
        idx = rng.choice(n, size=min(64, n), replace=False)
        xb = x_all[idx]
        yb = y_all[idx]
        logits = xb @ w
        probs = torch.sigmoid(logits)
        grad = xb.T @ (probs - yb) / len(yb)
        w = w - lr * grad
        if step % 20 == 0 or step == steps - 1:
            with torch.no_grad():
                p_all = torch.sigmoid(x_all @ w)
                loss = float(
                    (
                        -(
                            y_all * torch.log(p_all + 1e-8)
                            + (1 - y_all) * torch.log(1 - p_all + 1e-8)
                        ).mean()
                    ).cpu()
                )
                acc = float((((p_all > 0.5) == (y_all > 0.5)).float().mean()).cpu())
            history.append({"step": step, "loss": loss, "acc": acc, "backend": "mps"})
    return ChecklistPolicy(weights=w.detach().cpu().numpy().astype(np.float64), name="trained_checklist_mps"), history


def train_logistic_mlx(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    steps: int = 400,
    lr: float = 0.2,
    seed: int = 0,
) -> tuple[ChecklistPolicy, list[dict]]:
    """Same logistic objective on MLX Metal (preferred Apple Silicon backend)."""
    import mlx.core as mx

    rng = np.random.default_rng(seed)
    # Deterministic-ish init matching CPU scale
    w_np = rng.normal(0, 0.05, size=xs.shape[1]).astype(np.float32)
    w = mx.array(w_np)
    x_all = mx.array(xs.astype(np.float32))
    y_all = mx.array(ys.astype(np.float32))
    history: list[dict] = []
    n = len(ys)
    for step in range(steps):
        idx = rng.choice(n, size=min(64, n), replace=False)
        xb = x_all[idx.tolist()]
        yb = y_all[idx.tolist()]
        logits = xb @ w
        probs = mx.sigmoid(logits)
        grad = (xb.T @ (probs - yb)) / len(yb)
        w = w - lr * grad
        mx.eval(w)
        if step % 20 == 0 or step == steps - 1:
            p_all = mx.sigmoid(x_all @ w)
            mx.eval(p_all)
            p_np = np.array(p_all)
            loss = float(-np.mean(ys * np.log(p_np + 1e-8) + (1 - ys) * np.log(1 - p_np + 1e-8)))
            acc = float(((p_np > 0.5) == (ys > 0.5)).mean())
            history.append({"step": step, "loss": loss, "acc": acc, "backend": "mlx"})
    w_out = np.array(w, dtype=np.float64)
    return ChecklistPolicy(weights=w_out, name="trained_checklist_mlx"), history


def train_logistic_auto(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    backend: str = "auto",
    steps: int = 400,
    lr: float = 0.2,
    seed: int = 0,
) -> tuple[ChecklistPolicy, list[dict], str]:
    """Dispatch to mlx / mps / cpu. Returns (policy, history, backend_used)."""
    from openpi.rsi.mac_backend import resolve_backend

    chosen = resolve_backend(backend)
    if chosen == "mlx":
        pol, hist = train_logistic_mlx(xs, ys, steps=steps, lr=lr, seed=seed)
        return pol, hist, "mlx"
    if chosen == "mps":
        pol, hist = train_logistic_mps(xs, ys, steps=steps, lr=lr, seed=seed)
        return pol, hist, "mps"
    pol, hist = train_logistic(xs, ys, steps=steps, lr=lr, seed=seed)
    return pol, hist, "cpu"
