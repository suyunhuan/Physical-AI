"""Fixed-protocol subgoal-level metrics for long-horizon rollouts.

A long-horizon episode is monitored through a set of *goal atoms*: boolean symbolic
conditions whose conjunction defines task success. Sampling every atom once per policy
step turns a single success bit into an execution-monitoring trace, which is what the
RSI protocol requires alongside the end-to-end completion rate.

This module is deliberately policy-, simulator- and framework-agnostic: it only consumes
a stable list of atom ids plus one boolean vector per sampled step. Anything that knows
how to produce those vectors (LIBERO BDDL predicates, a TAMP symbolic state, a learned
predicate estimator) can reuse the same metric definitions. It must stay importable on
the Python 3.8 interpreters used by the evaluation containers, so it depends on the
standard library only.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "AggregateSubgoalMetrics",
    "EpisodeSubgoalMetrics",
    "EpisodeSubgoalTracker",
    "GoalAtom",
    "aggregate_episode_metrics",
    "make_goal_atoms",
]


@dataclasses.dataclass(frozen=True)
class GoalAtom:
    """One symbolic goal condition, identified by a stable id across episodes."""

    index: int
    atom_id: str
    predicate: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return {"index": self.index, "atom_id": self.atom_id, "predicate": list(self.predicate)}


def make_goal_atoms(predicates: Sequence[Sequence[Any]]) -> List[GoalAtom]:
    """Builds goal atoms from raw predicate tuples, e.g. ``[("on", "bowl", "plate")]``.

    The atom id embeds the positional index so that two structurally identical predicates
    in the same goal remain distinguishable.
    """
    if not predicates:
        raise ValueError("A goal must contain at least one predicate; refusing to build an empty atom set.")

    atoms = []
    for index, predicate in enumerate(predicates):
        tokens = tuple(str(token).strip().lower() for token in predicate)
        if not tokens:
            raise ValueError("Encountered an empty predicate at index {}.".format(index))
        atoms.append(GoalAtom(index=index, atom_id="{:02d}:{}".format(index, "-".join(tokens)), predicate=tokens))
    return atoms


@dataclasses.dataclass(frozen=True)
class EpisodeSubgoalMetrics:
    """Per-episode subgoal metrics under the fixed protocol.

    Step indexing: step 0 is the baseline sampled once the scene has settled and before
    the first policy action; step ``t > 0`` is sampled right after the ``t``-th policy
    action. Warm-up actions are not sampled and never count as regressions.
    """

    episode_id: str
    atom_ids: Tuple[str, ...]
    num_atoms: int
    num_sampled_steps: int
    end_to_end_success: bool
    # Set when the rollout ended on an infrastructure failure (policy server down, inference
    # timeout) rather than on the task outcome. Such an episode stalls for reasons that have
    # nothing to do with the policy, so its progress trace must carry that marker.
    termination_reason: Optional[str]
    # Atom i is "ever achieved" if it held at any sampled step, including the baseline.
    ever_achieved: Tuple[bool, ...]
    first_achieved_step: Tuple[Optional[int], ...]
    # Fraction of atoms holding simultaneously, at the last / best / averaged sampled step.
    final_progress: float
    max_progress: float
    progress_auc: float
    subgoal_success_rate: float
    regressed: Tuple[bool, ...]
    first_regression_step: Tuple[Optional[int], ...]
    regression_transitions: int
    # True when the environment reported success while some atom read false: the adapter
    # and the environment disagree, which invalidates the atom readout rather than the policy.
    done_atom_mismatch: bool

    @property
    def num_ever_achieved(self) -> int:
        return sum(self.ever_achieved)

    @property
    def num_regressed(self) -> int:
        return sum(self.regressed)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "atom_ids": list(self.atom_ids),
            "num_atoms": self.num_atoms,
            "num_sampled_steps": self.num_sampled_steps,
            "end_to_end_success": self.end_to_end_success,
            "termination_reason": self.termination_reason,
            "ever_achieved": list(self.ever_achieved),
            "first_achieved_step": list(self.first_achieved_step),
            "final_progress": self.final_progress,
            "max_progress": self.max_progress,
            "progress_auc": self.progress_auc,
            "subgoal_success_rate": self.subgoal_success_rate,
            "regressed": list(self.regressed),
            "first_regression_step": list(self.first_regression_step),
            "regression_transitions": self.regression_transitions,
            "done_atom_mismatch": self.done_atom_mismatch,
        }


class EpisodeSubgoalTracker:
    """Accumulates per-step atom readouts for a single episode."""

    def __init__(self, atoms: Sequence[GoalAtom], episode_id: str):
        if not atoms:
            raise ValueError("Cannot track an episode with an empty atom set.")
        self._atoms = tuple(atoms)
        self._episode_id = episode_id
        self._trace: List[Tuple[bool, ...]] = []

    @property
    def num_sampled_steps(self) -> int:
        return len(self._trace)

    def record(self, statuses: Sequence[Any]) -> None:
        """Records one atom readout. The first call is the baseline at step 0."""
        if len(statuses) != len(self._atoms):
            raise ValueError(
                "Expected {} atom statuses but got {}; the atom set must stay fixed within an episode.".format(
                    len(self._atoms), len(statuses)
                )
            )
        for position, status in enumerate(statuses):
            if status is None:
                raise ValueError(
                    "Atom {} returned None instead of a boolean; refusing to treat an unevaluated "
                    "predicate as unsatisfied.".format(self._atoms[position].atom_id)
                )
        self._trace.append(tuple(bool(status) for status in statuses))

    def finalize(self, end_to_end_success: bool, termination_reason: Optional[str] = None) -> EpisodeSubgoalMetrics:
        if not self._trace:
            raise ValueError("Cannot finalize an episode without any recorded atom readout.")

        num_atoms = len(self._atoms)
        ever_achieved = []
        first_achieved_step: List[Optional[int]] = []
        regressed = []
        first_regression_step: List[Optional[int]] = []
        regression_transitions = 0

        for position in range(num_atoms):
            column = [step[position] for step in self._trace]
            achieved_steps = [step for step, value in enumerate(column) if value]
            ever_achieved.append(bool(achieved_steps))
            first_achieved_step.append(achieved_steps[0] if achieved_steps else None)

            regression_steps = [step for step in range(1, len(column)) if column[step - 1] and not column[step]]
            regressed.append(bool(regression_steps))
            first_regression_step.append(regression_steps[0] if regression_steps else None)
            regression_transitions += len(regression_steps)

        progress = [sum(step) / num_atoms for step in self._trace]

        return EpisodeSubgoalMetrics(
            episode_id=self._episode_id,
            atom_ids=tuple(atom.atom_id for atom in self._atoms),
            num_atoms=num_atoms,
            num_sampled_steps=len(self._trace),
            end_to_end_success=bool(end_to_end_success),
            termination_reason=termination_reason,
            ever_achieved=tuple(ever_achieved),
            first_achieved_step=tuple(first_achieved_step),
            final_progress=progress[-1],
            max_progress=max(progress),
            progress_auc=sum(progress) / len(progress),
            subgoal_success_rate=sum(ever_achieved) / num_atoms,
            regressed=tuple(regressed),
            first_regression_step=tuple(first_regression_step),
            regression_transitions=regression_transitions,
            done_atom_mismatch=bool(end_to_end_success) and not all(self._trace[-1]),
        )


@dataclasses.dataclass(frozen=True)
class AggregateSubgoalMetrics:
    """Suite-level roll-up.

    The end-to-end success rate covers every attempted episode. Subgoal metrics can only
    cover instrumented episodes, so ``instrumentation_coverage`` is always reported next
    to them: a coverage below 1.0 means the subgoal numbers describe a subset and must not
    be read as suite-level results.
    """

    num_episodes: int
    num_instrumented_episodes: int
    num_uninstrumented_episodes: int
    instrumentation_coverage: float
    end_to_end_success_rate: float
    # Macro averages weight every episode equally; micro averages weight every atom equally
    # and therefore lean towards tasks with more goal atoms. Both are reported on purpose.
    subgoal_success_rate_macro: Optional[float]
    subgoal_success_rate_micro: Optional[float]
    final_progress_macro: Optional[float]
    max_progress_macro: Optional[float]
    progress_auc_macro: Optional[float]
    regressed_atom_rate: Optional[float]
    episode_regression_rate: Optional[float]
    regression_transitions_total: int
    # Mean first-achievement step over achieved atoms only; the coverage states what
    # fraction of atoms that mean is computed over, so it cannot be read as "all atoms".
    mean_first_achieved_step_over_achieved: Optional[float]
    achieved_atom_coverage: Optional[float]
    done_atom_mismatch_episodes: int
    # Instrumented episodes cut short by an infrastructure failure. Their progress traces are
    # included, so a non-zero count means part of the subgoal numbers reflects aborted rollouts.
    abnormally_terminated_episodes: int
    uninstrumented_reasons: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


def aggregate_episode_metrics(
    episodes: Sequence[EpisodeSubgoalMetrics],
    num_uninstrumented_episodes: int = 0,
    uninstrumented_end_to_end_successes: int = 0,
    uninstrumented_reasons: Sequence[str] = (),
) -> AggregateSubgoalMetrics:
    """Aggregates per-episode metrics under the fixed protocol.

    Episodes whose atom readout failed are passed in as counts only. They still count as
    attempts for the end-to-end rate, so a broken adapter cannot silently shrink the
    denominator.
    """
    if num_uninstrumented_episodes < 0 or uninstrumented_end_to_end_successes < 0:
        raise ValueError("Uninstrumented episode counts must be non-negative.")
    if uninstrumented_end_to_end_successes > num_uninstrumented_episodes:
        raise ValueError("More uninstrumented successes than uninstrumented episodes.")

    num_instrumented = len(episodes)
    num_episodes = num_instrumented + num_uninstrumented_episodes
    if num_episodes == 0:
        raise ValueError("Cannot aggregate zero episodes.")

    successes = sum(1 for episode in episodes if episode.end_to_end_success) + uninstrumented_end_to_end_successes
    total_atoms = sum(episode.num_atoms for episode in episodes)

    def _mean(values: Sequence[float]) -> Optional[float]:
        return sum(values) / len(values) if values else None

    first_achieved_steps = [step for episode in episodes for step in episode.first_achieved_step if step is not None]

    return AggregateSubgoalMetrics(
        num_episodes=num_episodes,
        num_instrumented_episodes=num_instrumented,
        num_uninstrumented_episodes=num_uninstrumented_episodes,
        instrumentation_coverage=num_instrumented / num_episodes,
        end_to_end_success_rate=successes / num_episodes,
        subgoal_success_rate_macro=_mean([episode.subgoal_success_rate for episode in episodes]),
        subgoal_success_rate_micro=(
            sum(episode.num_ever_achieved for episode in episodes) / total_atoms if total_atoms else None
        ),
        final_progress_macro=_mean([episode.final_progress for episode in episodes]),
        max_progress_macro=_mean([episode.max_progress for episode in episodes]),
        progress_auc_macro=_mean([episode.progress_auc for episode in episodes]),
        regressed_atom_rate=(sum(episode.num_regressed for episode in episodes) / total_atoms if total_atoms else None),
        episode_regression_rate=(
            sum(1 for episode in episodes if episode.num_regressed) / num_instrumented if num_instrumented else None
        ),
        regression_transitions_total=sum(episode.regression_transitions for episode in episodes),
        mean_first_achieved_step_over_achieved=_mean(first_achieved_steps),
        achieved_atom_coverage=(len(first_achieved_steps) / total_atoms if total_atoms else None),
        done_atom_mismatch_episodes=sum(1 for episode in episodes if episode.done_atom_mismatch),
        abnormally_terminated_episodes=sum(1 for episode in episodes if episode.termination_reason),
        uninstrumented_reasons=tuple(uninstrumented_reasons),
    )
