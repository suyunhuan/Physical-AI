"""Closed-loop wheeled dual-arm household task suite (CPU sim stub).

Not a substitute for B1K OmniGibson. Provides a *fixed* eval口径 for RSI:
end-to-end success + Q-score (subgoal fraction) on wheeled-bimanual household chains.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from openpi.rsi.subgoal_checklist import Checklist, Subgoal, summarize_episode


@dataclass(frozen=True)
class HouseholdTask:
    task_id: str
    instruction: str
    subgoal_names: tuple[str, ...]
    # difficulty in [0,1]: higher => baseline fails more often
    difficulty: float


FIXED_EVAL_SUITE: tuple[HouseholdTask, ...] = (
    HouseholdTask(
        "wb_kitchen_cup_to_sink",
        "Navigate to counter, pick cup with right arm, place in sink.",
        ("navigate_counter", "grasp_cup_right", "transport", "place_sink"),
        0.35,
    ),
    HouseholdTask(
        "wb_open_drawer_stow_bowl",
        "Open drawer with left arm, pick bowl with right, stow, close drawer.",
        ("navigate_cabinet", "open_drawer_left", "grasp_bowl_right", "stow", "close_drawer"),
        0.55,
    ),
    HouseholdTask(
        "wb_table_clear_two_items",
        "Clear plate then cup from table to tray using dual-arm sequence.",
        ("navigate_table", "pick_plate", "place_tray", "pick_cup", "place_tray_2"),
        0.45,
    ),
    HouseholdTask(
        "wb_fridge_fetch_bottle",
        "Open fridge, fetch bottle, close fridge, place on table.",
        ("navigate_fridge", "open_fridge", "grasp_bottle", "close_fridge", "place_table"),
        0.60,
    ),
    HouseholdTask(
        "wb_wipe_spill_then_bin",
        "Pick sponge, wipe spill, dispose sponge in bin.",
        ("navigate_spill", "grasp_sponge", "wipe", "navigate_bin", "dispose"),
        0.50,
    ),
    HouseholdTask(
        "wb_dual_handover_pot",
        "Left arm lifts pot lid, right arm moves pot to stove, left closes.",
        ("navigate_stove", "lift_lid_left", "move_pot_right", "place_stove", "close_lid"),
        0.65,
    ),
    HouseholdTask(
        "wb_laundry_basket_transfer",
        "Cross-room: fetch basket, load shirt, return to laundry area.",
        ("navigate_bedroom", "grasp_basket", "pick_shirt", "navigate_laundry", "unload"),
        0.70,
    ),
    HouseholdTask(
        "wb_multi_room_deliver_mug",
        "Find mug in kitchen, deliver to desk in study.",
        ("navigate_kitchen", "locate_mug", "grasp_mug", "navigate_study", "place_desk"),
        0.58,
    ),
)


def _seed_for(task_id: str, episode: int, salt: str) -> int:
    h = hashlib.md5(f"{task_id}:{episode}:{salt}".encode()).hexdigest()
    return int(h[:8], 16)


def run_closed_loop(
    task: HouseholdTask,
    *,
    mode: str,
    policy_fn,
    episode: int = 0,
    recovery_boost: float = 0.35,
) -> dict:
    """Run one episode.

    mode:
      - baseline: independent Bernoulli per subgoal (open-loop VLA proxy)
      - checklist: same, but gated recovery retries failed subgoal once
    policy_fn(task, subgoal_idx, state_vec) -> success_logit in R
    """
    checklist = Checklist(
        task_id=task.task_id,
        subgoals=[Subgoal(name=n) for n in task.subgoal_names],
    )
    rng = np.random.default_rng(_seed_for(task.task_id, episode, mode))
    recoveries = 0
    steps = 0

    for i, sg in enumerate(checklist.subgoals):
        steps += 1
        state = np.array(
            [task.difficulty, i / max(len(checklist.subgoals) - 1, 1), checklist.completed / max(checklist.total, 1)],
            dtype=np.float64,
        )
        logit = float(policy_fn(task, i, state))
        # Map logit + difficulty to success probability
        p = 1.0 / (1.0 + np.exp(-(logit - 1.5 * task.difficulty)))
        p = float(np.clip(p, 0.05, 0.95))
        ok = rng.random() < p
        if (not ok) and mode == "checklist":
            # Gated recovery: one retry with boosted logit (OopsieRecover-inspired)
            recoveries += 1
            steps += 1
            state_r = state.copy()
            state_r[2] = checklist.completed / max(checklist.total, 1)
            logit_r = float(policy_fn(task, i, state_r)) + recovery_boost
            p_r = 1.0 / (1.0 + np.exp(-(logit_r - 1.5 * task.difficulty)))
            p_r = float(np.clip(p_r, 0.05, 0.95))
            ok = rng.random() < p_r
        if ok:
            sg.done = True
        else:
            # Long-horizon abort: remaining subgoals stay failed (cascade)
            break

    summary = summarize_episode(checklist)
    summary.update(
        {
            "mode": mode,
            "episode": episode,
            "difficulty": task.difficulty,
            "instruction": task.instruction,
            "recoveries": recoveries,
            "steps": steps,
        }
    )
    return summary


def evaluate_suite(policy_fn, *, mode: str, episodes_per_task: int = 5) -> list[dict]:
    rows: list[dict] = []
    for task in FIXED_EVAL_SUITE:
        for ep in range(episodes_per_task):
            rows.append(run_closed_loop(task, mode=mode, policy_fn=policy_fn, episode=ep))
    return rows
