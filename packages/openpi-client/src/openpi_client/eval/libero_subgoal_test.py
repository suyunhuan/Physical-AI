from openpi_client.eval import libero_subgoal
import pytest


class _FakeProblem:
    def __init__(self, goal_state, truth):
        self.parsed_problem = {"goal_state": goal_state}
        self._truth = truth
        self.eval_calls = []

    def _eval_predicate(self, state):
        self.eval_calls.append(tuple(state))
        return self._truth.get(tuple(state))


class _FakeEnv:
    """Mimics LIBERO's ControlEnv, which holds the problem env in `.env`."""

    def __init__(self, goal_state, truth):
        self.env = _FakeProblem(goal_state, truth)


def test_monitor_reads_goal_atoms_through_the_libero_internals():
    goal_state = [("open", "cabinet"), ("on", "bowl", "plate")]
    env = _FakeEnv(goal_state, {("open", "cabinet"): True, ("on", "bowl", "plate"): False})

    monitor = libero_subgoal.LiberoGoalMonitor(env)

    assert [atom.atom_id for atom in monitor.atoms] == ["00:open-cabinet", "01:on-bowl-plate"]
    assert monitor.read_statuses() == [True, False]
    # Predicates must be handed back to LIBERO verbatim, not in canonicalized form.
    assert env.env.eval_calls == [("open", "cabinet"), ("on", "bowl", "plate")]


def test_monitor_passes_original_casing_to_the_evaluator():
    goal_state = [("Open", "Cabinet_1")]
    env = _FakeEnv(goal_state, {("Open", "Cabinet_1"): True})

    monitor = libero_subgoal.LiberoGoalMonitor(env)

    assert monitor.read_statuses() == [True]
    assert monitor.atoms[0].atom_id == "00:open-cabinet_1"


def test_monitor_rejects_unsupported_predicate_arity():
    env = _FakeEnv([("open", "cabinet", "x", "y")], {})

    with pytest.raises(ValueError, match="unsupported arity"):
        libero_subgoal.LiberoGoalMonitor(env)


def test_monitor_rejects_empty_goal_state():
    env = _FakeEnv([], {})

    with pytest.raises(ValueError, match="goal state is empty"):
        libero_subgoal.LiberoGoalMonitor(env)


def test_monitor_rejects_missing_goal_state():
    env = _FakeEnv(None, {})

    with pytest.raises(ValueError, match="no BDDL goal state"):
        libero_subgoal.LiberoGoalMonitor(env)


def test_monitor_refuses_to_treat_unevaluated_predicate_as_unsatisfied():
    env = _FakeEnv([("unknown", "thing")], {})

    monitor = libero_subgoal.LiberoGoalMonitor(env)

    with pytest.raises(ValueError, match="evaluated to None"):
        monitor.read_statuses()


def test_monitor_accepts_injected_providers_without_touching_the_environment():
    sentinel = object()
    calls = []

    def goal_provider(env):
        calls.append(env)
        return [("holds", "cup")]

    def predicate_evaluator(env, predicate):
        calls.append((env, tuple(predicate)))
        return True

    monitor = libero_subgoal.LiberoGoalMonitor(
        sentinel, goal_provider=goal_provider, predicate_evaluator=predicate_evaluator
    )

    assert monitor.read_statuses() == [True]
    assert calls == [sentinel, (sentinel, ("holds", "cup"))]


def test_monitor_tracker_uses_the_monitored_atom_set():
    env = _FakeEnv([("open", "cabinet"), ("on", "bowl", "plate")], {})

    monitor = libero_subgoal.LiberoGoalMonitor(env)
    tracker = monitor.make_tracker("task-0/episode-0")
    tracker.record([False, False])
    tracker.record([True, False])
    metrics = tracker.finalize(end_to_end_success=False)

    assert metrics.episode_id == "task-0/episode-0"
    assert metrics.atom_ids == ("00:open-cabinet", "01:on-bowl-plate")
    assert metrics.first_achieved_step == (1, None)
