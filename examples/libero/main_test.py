"""Integration test for the LIBERO eval loop, driven by a stubbed environment.

LIBERO, robosuite and MuJoCo are not installed outside the eval container, so this test
replaces them with a scripted fake environment whose BDDL goal atoms flip on a fixed
schedule. That exercises the real `eval_libero` rollout loop, the subgoal instrumentation
and the report writing without a simulator, a GPU or policy weights.

The default pytest run does not collect `examples/`, so run it explicitly:

    uv run pytest examples/libero/main_test.py
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import pathlib
import sys
import types

import numpy as np
import pytest

_GOAL_STATE = [("open", "cabinet"), ("on", "bowl", "plate")]
# Atom truth per policy step; index 0 is the baseline before the first policy action. Atom 0
# opens at policy step 1, atom 1 only at step 3, which is when LIBERO would report `done`.
_ATOM_SCHEDULE = [(False, False), (True, False), (True, False), (True, True)]


def _install_libero_stubs() -> None:
    """Registers import-time stubs for the LIBERO modules `main.py` imports."""
    if "libero" in sys.modules:
        return
    libero = types.ModuleType("libero")
    libero_libero = types.ModuleType("libero.libero")
    libero_benchmark = types.ModuleType("libero.libero.benchmark")
    libero_envs = types.ModuleType("libero.libero.envs")
    libero_benchmark.get_benchmark_dict = dict
    libero_libero.benchmark = libero_benchmark
    libero_libero.get_libero_path = lambda _name: "/nonexistent"
    libero_envs.OffScreenRenderEnv = object
    libero.libero = libero_libero
    sys.modules.update(
        {
            "libero": libero,
            "libero.libero": libero_libero,
            "libero.libero.benchmark": libero_benchmark,
            "libero.libero.envs": libero_envs,
        }
    )


def _load_main():
    _install_libero_stubs()
    spec = importlib.util.spec_from_file_location("libero_eval_main", pathlib.Path(__file__).parent / "main.py")
    module = importlib.util.module_from_spec(spec)
    # `main.py` defers annotations, so dataclasses resolves them through sys.modules.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


main = _load_main()


class _FakeProblem:
    def __init__(self, goal_state):
        self.parsed_problem = {} if goal_state is None else {"goal_state": goal_state}
        self.policy_steps = 0

    def _eval_predicate(self, state):
        schedule = _ATOM_SCHEDULE[min(self.policy_steps, len(_ATOM_SCHEDULE) - 1)]
        return schedule[_GOAL_STATE.index(tuple(state))]


class _FakeEnv:
    """Mimics the parts of LIBERO's `OffScreenRenderEnv` that `eval_libero` touches."""

    def __init__(self, goal_state=_GOAL_STATE, **_kwargs):
        self.env = _FakeProblem(goal_state)

    def seed(self, _seed):
        pass

    def reset(self):
        return self._obs()

    def set_init_state(self, _state):
        return self._obs()

    def step(self, action):
        is_warmup = list(action) == main.LIBERO_DUMMY_ACTION
        if not is_warmup:
            self.env.policy_steps += 1
        # LIBERO derives `done` from the same predicates it exposes; the fake mirrors that.
        done = all(self.env._eval_predicate(state) for state in _GOAL_STATE)  # noqa: SLF001
        return self._obs(), 0.0, done, {}

    def _obs(self):
        image = np.zeros((main.LIBERO_ENV_RESOLUTION, main.LIBERO_ENV_RESOLUTION, 3), dtype=np.uint8)
        return {
            "agentview_image": image,
            "robot0_eye_in_hand_image": image,
            "robot0_eef_pos": np.zeros(3),
            "robot0_eef_quat": np.array([0.0, 0.0, 0.0, 1.0]),
            "robot0_gripper_qpos": np.zeros(2),
        }


class _FakeTask:
    language = "open the cabinet and put the bowl on the plate"
    problem_folder = "stub"
    bddl_file = "stub.bddl"


class _FakeTaskSuite:
    n_tasks = 1

    def get_task(self, _task_id):
        return _FakeTask()

    def get_task_init_states(self, _task_id):
        return [None]


class _FakePolicyClient:
    def __init__(self, *_args, **_kwargs):
        pass

    def infer(self, _element):
        return {"actions": np.zeros((5, 7))}


@pytest.fixture
def patched_main(monkeypatch, tmp_path):
    monkeypatch.setattr(main.benchmark, "get_benchmark_dict", lambda: {"libero_spatial": _FakeTaskSuite})
    monkeypatch.setattr(main, "get_libero_path", lambda _name: str(tmp_path))
    monkeypatch.setattr(main, "OffScreenRenderEnv", _FakeEnv)
    monkeypatch.setattr(main._websocket_client_policy, "WebsocketClientPolicy", _FakePolicyClient)  # noqa: SLF001
    monkeypatch.setattr(main.imageio, "mimwrite", lambda *_args, **_kwargs: None)
    return main


def _args(tmp_path, **overrides):
    return dataclasses.replace(
        main.Args(
            num_trials_per_task=1,
            num_steps_wait=2,
            video_out_path=str(tmp_path / "videos"),
            subgoal_metrics_out_path=str(tmp_path / "subgoal"),
        ),
        **overrides,
    )


def test_subgoal_metrics_disabled_by_default_writes_nothing(patched_main, tmp_path):
    patched_main.eval_libero(_args(tmp_path))

    assert not (tmp_path / "subgoal").exists()


def test_enabled_subgoal_metrics_track_the_bddl_goal_atoms(patched_main, tmp_path):
    out_dir = tmp_path / "subgoal"
    patched_main.eval_libero(_args(tmp_path, report_subgoal_metrics=True))

    episodes = [json.loads(line) for line in (out_dir / "libero_spatial_episodes.jsonl").read_text().splitlines()]
    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["atom_ids"] == ["00:open-cabinet", "01:on-bowl-plate"]
    # Baseline plus the three policy steps it took to satisfy both atoms.
    assert episode["num_sampled_steps"] == 4
    assert episode["first_achieved_step"] == [1, 3]
    assert episode["end_to_end_success"] is True
    assert episode["final_progress"] == 1.0
    assert episode["regression_transitions"] == 0
    assert episode["done_atom_mismatch"] is False

    summary = json.loads((out_dir / "libero_spatial_summary.json").read_text())["aggregate"]
    assert summary["num_episodes"] == 1
    assert summary["end_to_end_success_rate"] == 1.0
    assert summary["subgoal_success_rate_macro"] == 1.0
    assert summary["subgoal_success_rate_micro"] == 1.0
    assert summary["instrumentation_coverage"] == 1.0


def test_rerun_does_not_append_to_the_previous_episode_trace(patched_main, tmp_path):
    args = _args(tmp_path, report_subgoal_metrics=True)
    patched_main.eval_libero(args)
    patched_main.eval_libero(args)

    lines = (tmp_path / "subgoal" / "libero_spatial_episodes.jsonl").read_text().splitlines()
    assert len(lines) == 1


def test_unreadable_goal_state_is_reported_as_uninstrumented_not_as_failure(patched_main, tmp_path, monkeypatch):
    monkeypatch.setattr(main, "OffScreenRenderEnv", lambda **kwargs: _FakeEnv(goal_state=None, **kwargs))

    patched_main.eval_libero(_args(tmp_path, report_subgoal_metrics=True))

    summary = json.loads((tmp_path / "subgoal" / "libero_spatial_summary.json").read_text())["aggregate"]
    # The rollout itself still succeeded, so the instrumentation failure must not look like a
    # policy failure, and the episode must stay in the end-to-end denominator.
    assert summary["num_episodes"] == 1
    assert summary["end_to_end_success_rate"] == 1.0
    assert summary["num_uninstrumented_episodes"] == 1
    assert summary["instrumentation_coverage"] == 0.0
    assert summary["subgoal_success_rate_macro"] is None
    assert len(summary["uninstrumented_reasons"]) == 1


def test_predicate_readout_failure_does_not_abort_the_rollout(patched_main, tmp_path, monkeypatch):
    def broken_evaluator(_env, _predicate):
        raise RuntimeError("predicate backend unavailable")

    monkeypatch.setattr(main.libero_subgoal, "default_predicate_evaluator", broken_evaluator)

    patched_main.eval_libero(_args(tmp_path, report_subgoal_metrics=True))

    summary = json.loads((tmp_path / "subgoal" / "libero_spatial_summary.json").read_text())["aggregate"]
    assert summary["num_uninstrumented_episodes"] == 1
    assert summary["end_to_end_success_rate"] == 1.0
