"""Protocol-parity tests for Mac backends (skip if MLX/MPS missing)."""

from __future__ import annotations

import numpy as np
import pytest

from openpi.rsi.checklist_policy import (
    ChecklistPolicy,
    filter_by_subgoal_coverage,
    generate_demo_batch,
    train_logistic,
    train_logistic_auto,
)
from openpi.rsi.mac_backend import detect_mac_backend, resolve_backend
from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE, evaluate_suite


def test_detect_mac_backend_fields():
    r = detect_mac_backend()
    assert hasattr(r, "preferred")
    assert isinstance(r.gaps_vs_cuda, list)
    assert r.openpi_pi0_runnable is False or r.apple_silicon is False


def test_protocol_parity_cpu_auto():
    pol = ChecklistPolicy.baseline_open_loop()
    xs, ys = generate_demo_batch(pol, n_samples=160, seed=3)
    xs, ys, _ = filter_by_subgoal_coverage(xs, ys, min_positive_rate=0.3)
    cpu_pol, _ = train_logistic(xs, ys, steps=40, lr=0.3, seed=0)
    mac_pol, _, backend = train_logistic_auto(xs, ys, backend="cpu", steps=40, lr=0.3, seed=0)
    assert backend == "cpu"
    cpu_rows = evaluate_suite(cpu_pol.as_fn(), mode="checklist", episodes_per_task=1)
    mac_rows = evaluate_suite(mac_pol.as_fn(), mode="checklist", episodes_per_task=1)
    assert len(cpu_rows) == len(mac_rows) == len(FIXED_EVAL_SUITE)
    assert set(cpu_rows[0]) == set(mac_rows[0])
    assert np.allclose(cpu_pol.weights, mac_pol.weights, atol=1e-9)


def test_mlx_or_mps_smoke_if_available():
    report = detect_mac_backend()
    if not report.apple_silicon:
        pytest.skip("not Apple Silicon")
    if report.preferred == "cpu":
        pytest.skip("neither MLX nor MPS available")
    backend = resolve_backend("auto")
    pol = ChecklistPolicy.baseline_open_loop()
    xs, ys = generate_demo_batch(pol, n_samples=120, seed=1)
    xs, ys, _ = filter_by_subgoal_coverage(xs, ys, min_positive_rate=0.3)
    trained, hist, used = train_logistic_auto(xs, ys, backend=backend, steps=30, lr=0.3, seed=0)
    assert used == backend
    assert hist and "backend" in hist[-1]
    rows = evaluate_suite(trained.as_fn(), mode="checklist", episodes_per_task=1)
    assert len(rows) == 8
    assert all("q_score" in r and "e2e_success" in r for r in rows)
