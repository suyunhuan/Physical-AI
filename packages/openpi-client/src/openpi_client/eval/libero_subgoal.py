"""Adapter that exposes LIBERO BDDL goal atoms as a subgoal readout.

LIBERO defines task success as the conjunction of the predicates in the BDDL goal:
``bddl_base_domain.py:807`` sets ``done = self._check_success()``, and each problem subclass
(e.g. ``libero_tabletop_manipulation.py:135-143``) implements ``_check_success`` by ANDing
``_eval_predicate(state)`` over ``parsed_problem["goal_state"]``. Reading the same predicates
individually therefore yields a per-atom progress trace that is consistent with the
environment's own success bit by construction.

Those entry points (``env.env``, ``parsed_problem``, ``_eval_predicate``) are LIBERO
internals rather than a supported API, and the predicate tuple layout comes from the
external ``bddl`` parser. All of that is confined to this adapter and both lookups are
injectable, so the metric code never depends on LIBERO and stays testable without a
simulator. The environment is duck-typed: nothing here imports ``libero`` or ``robosuite``.
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional, Sequence, Tuple

from openpi_client.eval import subgoal_metrics

__all__ = ["LiberoGoalMonitor", "default_goal_provider", "default_predicate_evaluator"]

# LIBERO's `_eval_predicate` only handles unary `(name, obj)` and binary `(name, obj, obj)`
# predicates and silently returns None for anything else; we refuse those instead.
_SUPPORTED_ARITIES = (2, 3)


def default_goal_provider(env: Any) -> Sequence[Sequence[Any]]:
    """Reads the BDDL goal conjunction off a LIBERO ``ControlEnv``."""
    return env.env.parsed_problem["goal_state"]


def default_predicate_evaluator(env: Any, predicate: Sequence[Any]) -> Any:
    """Evaluates a single BDDL predicate against the current simulator state."""
    return env.env._eval_predicate(predicate)  # noqa: SLF001


class LiberoGoalMonitor:
    """Reads the individual BDDL goal atoms of one LIBERO task.

    The monitor keeps the raw predicate tuples for evaluation (object names must be passed
    back to LIBERO unchanged) and derives canonical atom ids only for reporting.
    """

    def __init__(
        self,
        env: Any,
        goal_provider: Optional[Callable[[Any], Sequence[Sequence[Any]]]] = None,
        predicate_evaluator: Optional[Callable[[Any, Sequence[Any]], Any]] = None,
    ):
        self._env = env
        self._evaluate = predicate_evaluator or default_predicate_evaluator

        raw_goal = (goal_provider or default_goal_provider)(env)
        if raw_goal is None:
            raise ValueError("The environment exposed no BDDL goal state.")
        predicates: List[Tuple[Any, ...]] = [tuple(predicate) for predicate in raw_goal]
        if not predicates:
            raise ValueError("The BDDL goal state is empty; refusing to report subgoal metrics for it.")
        for position, predicate in enumerate(predicates):
            if len(predicate) not in _SUPPORTED_ARITIES:
                raise ValueError(
                    "Goal atom {} has unsupported arity {} ({!r}); LIBERO can only evaluate unary and "
                    "binary predicates.".format(position, len(predicate), predicate)
                )
        self._predicates = tuple(predicates)
        self._atoms = tuple(subgoal_metrics.make_goal_atoms(predicates))

    @property
    def atoms(self) -> Tuple[subgoal_metrics.GoalAtom, ...]:
        return self._atoms

    def read_statuses(self) -> List[bool]:
        """Evaluates every goal atom once, in goal order."""
        statuses = []
        for atom, predicate in zip(self._atoms, self._predicates):
            value = self._evaluate(self._env, predicate)
            if value is None:
                raise ValueError(
                    "Goal atom {} evaluated to None; LIBERO could not evaluate the predicate, and "
                    "treating that as unsatisfied would understate progress.".format(atom.atom_id)
                )
            statuses.append(bool(value))
        return statuses

    def make_tracker(self, episode_id: str) -> subgoal_metrics.EpisodeSubgoalTracker:
        return subgoal_metrics.EpisodeSubgoalTracker(self._atoms, episode_id=episode_id)
