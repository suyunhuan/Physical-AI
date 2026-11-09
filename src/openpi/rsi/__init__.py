"""RSI helpers for long-horizon household evaluation and light training.

This package is intentionally dependency-light (numpy) so it can run without
GPU / full openpi JAX stacks. Full π0 fine-tuning remains gated on GPU + weights.
"""

from openpi.rsi.subgoal_checklist import q_score, summarize_episode
from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE, run_closed_loop

__all__ = [
    "q_score",
    "summarize_episode",
    "FIXED_EVAL_SUITE",
    "run_closed_loop",
]
