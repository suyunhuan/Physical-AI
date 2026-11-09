"""RSI helpers for long-horizon household evaluation and light training.

This package is intentionally dependency-light (numpy) so it can run without
GPU / full openpi JAX stacks. On Apple Silicon, optional MLX / PyTorch MPS
backends accelerate the checklist head while preserving the same eval protocol.
Full π0 fine-tuning remains gated on Linux CUDA + weights.
"""

from openpi.rsi.subgoal_checklist import q_score, summarize_episode
from openpi.rsi.wheeled_bimanual_sim import FIXED_EVAL_SUITE, run_closed_loop

__all__ = [
    "q_score",
    "summarize_episode",
    "FIXED_EVAL_SUITE",
    "run_closed_loop",
]
