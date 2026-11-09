"""CPU unit tests for checklist Q-score and policy training smoke."""

from __future__ import annotations

from openpi.rsi.checklist_policy import ChecklistPolicy, filter_by_subgoal_coverage, generate_demo_batch, train_logistic
from openpi.rsi.subgoal_checklist import Checklist, Subgoal, end_to_end_success, q_score
from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE, evaluate_suite


def test_q_score_partial_credit():
    c = Checklist("t", [Subgoal("a", True), Subgoal("b", False), Subgoal("c", True)])
    assert abs(q_score(c) - 2 / 3) < 1e-9
    assert end_to_end_success(c) is False


def test_fixed_suite_size():
    assert len(FIXED_EVAL_SUITE) == 8


def test_train_and_eval_smoke():
    pol = ChecklistPolicy.baseline_open_loop()
    xs, ys = generate_demo_batch(pol, n_samples=200, seed=0)
    xs, ys, stats = filter_by_subgoal_coverage(xs, ys, min_positive_rate=0.3)
    assert stats["kept"] > 0
    trained, hist = train_logistic(xs, ys, steps=40, lr=0.3, seed=0)
    assert len(hist) >= 1
    rows = evaluate_suite(trained.as_fn(), mode="checklist", episodes_per_task=1)
    assert len(rows) == 8
    assert all("q_score" in r for r in rows)
