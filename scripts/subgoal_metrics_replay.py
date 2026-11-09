"""Deterministic replay check for the subgoal evaluation protocol.

Running a real LIBERO rollout needs a simulator, a GPU and policy weights. This harness
instead replays hand-written atom traces through the exact same tracker and aggregator used
during evaluation, so the metric definitions can be verified on CPU and pinned against
regressions. It verifies the evaluator, not any policy: no success rate produced here says
anything about pi0 / pi0.5.

Usage:
    uv run python scripts/subgoal_metrics_replay.py
    uv run python scripts/subgoal_metrics_replay.py --out-path /tmp/replay.json
"""

import dataclasses
import json
import pathlib

from openpi_client.eval import libero_subgoal
from openpi_client.eval import subgoal_metrics
import tyro

# Scripted episodes. Each trace row is one sampled step: row 0 is the baseline taken after
# the warm-up and before the first policy action. Episode "A" ends with every atom true and
# therefore succeeds end-to-end; it also transiently loses atom 0, which is the regression
# case a single success bit cannot express. Episode "B" stalls after one atom.
SCENARIO_NAME = "scripted-v1"
EPISODES = (
    {
        "episode_id": "scripted-task-0/episode-0",
        "goal_state": (("open", "cabinet"), ("on", "bowl", "plate"), ("turn_on", "stove")),
        "trace": (
            (False, False, False),
            (True, False, False),
            (True, True, False),
            (False, True, False),
            (True, True, True),
        ),
        "end_to_end_success": True,
    },
    {
        "episode_id": "scripted-task-1/episode-0",
        "goal_state": (("open", "drawer"), ("in", "mug", "drawer")),
        "trace": (
            (False, False),
            (True, False),
            (True, False),
        ),
        "end_to_end_success": False,
    },
)

# Hand-derived from the traces above; any change to the metric definitions must break here.
#   end-to-end:      1 of 2 episodes report done                      -> 0.5
#   subgoal micro:   (3 of 3) + (1 of 2) atoms ever achieved          -> 4/5
#   subgoal macro:   mean(3/3, 1/2)                                   -> 0.75
#   progress AUC:    mean(mean(0,1/3,2/3,1/3,1), mean(0,1/2,1/2))     -> 0.4
#   regressed atoms: atom 0 of episode A only, out of 5 atoms         -> 0.2
#   episodes with a regression: 1 of 2                                -> 0.5
EXPECTED_AGGREGATE = {
    "num_episodes": 2,
    "num_instrumented_episodes": 2,
    "instrumentation_coverage": 1.0,
    "end_to_end_success_rate": 0.5,
    "subgoal_success_rate_micro": 0.8,
    "subgoal_success_rate_macro": 0.75,
    "progress_auc_macro": 0.4,
    "final_progress_macro": 0.75,
    "max_progress_macro": 0.75,
    "regressed_atom_rate": 0.2,
    "episode_regression_rate": 0.5,
    "regression_transitions_total": 1,
    "achieved_atom_coverage": 0.8,
    "done_atom_mismatch_episodes": 0,
}
EXPECTED_FIRST_ACHIEVED_STEPS = {
    "scripted-task-0/episode-0": [1, 2, 4],
    "scripted-task-1/episode-0": [1, None],
}
TOLERANCE = 1e-9


@dataclasses.dataclass
class Args:
    out_path: str = ""  # Optional path to write the replay report to.


def _replay() -> list[subgoal_metrics.EpisodeSubgoalMetrics]:
    """Replays each scripted episode through the real monitor and tracker."""
    results = []
    for episode in EPISODES:
        trace = episode["trace"]
        step = {"index": 0}

        # Drive the LIBERO adapter with injected lookups so the replay needs no simulator
        # while still exercising the goal parsing and arity validation it performs.
        def predicate_evaluator(_env, predicate, trace=trace, step=step, goal=episode["goal_state"]) -> bool:
            return trace[step["index"]][goal.index(tuple(predicate))]

        monitor = libero_subgoal.LiberoGoalMonitor(
            env=None,
            goal_provider=lambda _env, goal=episode["goal_state"]: goal,
            predicate_evaluator=predicate_evaluator,
        )
        tracker = monitor.make_tracker(episode["episode_id"])
        for index in range(len(trace)):
            step["index"] = index
            tracker.record(monitor.read_statuses())
        results.append(tracker.finalize(end_to_end_success=episode["end_to_end_success"]))
    return results


def _check(aggregate: subgoal_metrics.AggregateSubgoalMetrics, episodes: list) -> list[str]:
    failures = []
    actual = aggregate.to_dict()
    for key, expected in EXPECTED_AGGREGATE.items():
        value = actual[key]
        if value is None or abs(value - expected) > TOLERANCE:
            failures.append(f"{key}: expected {expected}, got {value}")

    for episode in episodes:
        expected_steps = EXPECTED_FIRST_ACHIEVED_STEPS[episode.episode_id]
        if list(episode.first_achieved_step) != expected_steps:
            failures.append(
                f"{episode.episode_id} first_achieved_step: expected {expected_steps}, "
                f"got {list(episode.first_achieved_step)}"
            )
    return failures


def main(args: Args) -> None:
    episodes = _replay()
    aggregate = subgoal_metrics.aggregate_episode_metrics(episodes)
    report = {
        "scenario": SCENARIO_NAME,
        "note": "Replay of scripted atom traces. Verifies the evaluator only, not any policy.",
        "episodes": [episode.to_dict() for episode in episodes],
        "aggregate": aggregate.to_dict(),
    }
    serialized = json.dumps(report, indent=2, sort_keys=True)
    print(serialized)
    if args.out_path:
        path = pathlib.Path(args.out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(serialized)

    failures = _check(aggregate, episodes)
    if failures:
        raise SystemExit("Subgoal metric replay mismatched the fixed protocol:\n  " + "\n  ".join(failures))
    print(f"\nReplay matched the fixed protocol ({SCENARIO_NAME}): {len(EXPECTED_AGGREGATE)} aggregate fields checked.")


if __name__ == "__main__":
    main(tyro.cli(Args))
