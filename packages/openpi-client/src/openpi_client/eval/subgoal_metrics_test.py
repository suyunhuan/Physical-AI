import math

from openpi_client.eval import subgoal_metrics
import pytest


def _atoms(count):
    return subgoal_metrics.make_goal_atoms([("holds", "obj{}".format(index)) for index in range(count)])


def _episode(episode_id, trace, end_to_end_success):
    tracker = subgoal_metrics.EpisodeSubgoalTracker(_atoms(len(trace[0])), episode_id=episode_id)
    for statuses in trace:
        tracker.record(statuses)
    return tracker.finalize(end_to_end_success=end_to_end_success)


def test_make_goal_atoms_canonicalizes_and_keeps_duplicates_distinct():
    atoms = subgoal_metrics.make_goal_atoms([("On", "Bowl", "Plate"), ("on", "bowl", "plate")])

    assert [atom.atom_id for atom in atoms] == ["00:on-bowl-plate", "01:on-bowl-plate"]
    assert atoms[0].predicate == ("on", "bowl", "plate")


def test_make_goal_atoms_rejects_empty_goal():
    with pytest.raises(ValueError, match="at least one predicate"):
        subgoal_metrics.make_goal_atoms([])


def test_tracker_rejects_empty_atom_set():
    with pytest.raises(ValueError, match="empty atom set"):
        subgoal_metrics.EpisodeSubgoalTracker([], episode_id="e")


def test_tracker_rejects_status_count_mismatch():
    tracker = subgoal_metrics.EpisodeSubgoalTracker(_atoms(2), episode_id="e")

    with pytest.raises(ValueError, match="must stay fixed"):
        tracker.record([True])


def test_tracker_rejects_none_status():
    tracker = subgoal_metrics.EpisodeSubgoalTracker(_atoms(1), episode_id="e")

    with pytest.raises(ValueError, match="returned None"):
        tracker.record([None])


def test_tracker_rejects_finalize_without_samples():
    tracker = subgoal_metrics.EpisodeSubgoalTracker(_atoms(1), episode_id="e")

    with pytest.raises(ValueError, match="without any recorded"):
        tracker.finalize(end_to_end_success=False)


def test_first_achievement_and_progress_use_baseline_as_step_zero():
    metrics = _episode(
        "e",
        [[False, False, False], [True, False, False], [True, True, False], [True, True, True]],
        end_to_end_success=True,
    )

    assert metrics.num_sampled_steps == 4
    assert metrics.first_achieved_step == (1, 2, 3)
    assert metrics.ever_achieved == (True, True, True)
    assert metrics.subgoal_success_rate == 1.0
    assert metrics.final_progress == 1.0
    assert metrics.max_progress == 1.0
    assert math.isclose(metrics.progress_auc, (0 + 1 / 3 + 2 / 3 + 1) / 4)
    assert metrics.regression_transitions == 0
    assert metrics.done_atom_mismatch is False


def test_atom_satisfied_at_baseline_has_first_achieved_step_zero():
    metrics = _episode("e", [[True, False], [True, False]], end_to_end_success=False)

    assert metrics.first_achieved_step == (0, None)
    assert metrics.subgoal_success_rate == 0.5


def test_unachieved_atom_keeps_none_instead_of_max_steps():
    metrics = _episode("e", [[False], [False], [False]], end_to_end_success=False)

    assert metrics.first_achieved_step == (None,)
    assert metrics.ever_achieved == (False,)
    assert metrics.subgoal_success_rate == 0.0
    assert metrics.progress_auc == 0.0


def test_ever_achieved_survives_regression_but_regression_is_reported():
    metrics = _episode("e", [[False], [True], [False]], end_to_end_success=False)

    assert metrics.ever_achieved == (True,)
    assert metrics.final_progress == 0.0
    assert metrics.max_progress == 1.0
    assert metrics.regressed == (True,)
    assert metrics.first_regression_step == (2,)
    assert metrics.regression_transitions == 1


def test_repeated_regressions_are_counted_per_transition():
    metrics = _episode("e", [[True], [False], [True], [False]], end_to_end_success=False)

    assert metrics.regression_transitions == 2
    assert metrics.first_regression_step == (1,)


def test_done_atom_mismatch_flags_disagreement_with_environment():
    metrics = _episode("e", [[False, False], [True, False]], end_to_end_success=True)

    assert metrics.done_atom_mismatch is True


def test_termination_reason_is_carried_and_counted():
    tracker = subgoal_metrics.EpisodeSubgoalTracker(_atoms(1), episode_id="e")
    tracker.record([False])
    metrics = tracker.finalize(end_to_end_success=False, termination_reason="RuntimeError: server gone")

    assert metrics.termination_reason == "RuntimeError: server gone"

    aggregate = subgoal_metrics.aggregate_episode_metrics([metrics, _episode("f", [[False]], False)])

    assert aggregate.abnormally_terminated_episodes == 1


def test_aggregate_reports_macro_and_micro_separately():
    episodes = [
        _episode("a", [[False] * 3, [True, False, False], [True, True, False]], end_to_end_success=False),
        _episode("b", [[False], [True]], end_to_end_success=True),
    ]

    aggregate = subgoal_metrics.aggregate_episode_metrics(episodes)

    assert aggregate.num_episodes == 2
    assert aggregate.end_to_end_success_rate == 0.5
    # Macro weights episodes equally; micro weights atoms equally (2/3 and 1/1 -> 3/4).
    assert math.isclose(aggregate.subgoal_success_rate_macro, (2 / 3 + 1.0) / 2)
    assert math.isclose(aggregate.subgoal_success_rate_micro, 3 / 4)
    assert aggregate.instrumentation_coverage == 1.0
    assert math.isclose(aggregate.achieved_atom_coverage, 3 / 4)


def test_aggregate_keeps_uninstrumented_episodes_in_the_end_to_end_denominator():
    episodes = [_episode("a", [[False], [True]], end_to_end_success=True)]

    aggregate = subgoal_metrics.aggregate_episode_metrics(
        episodes,
        num_uninstrumented_episodes=3,
        uninstrumented_end_to_end_successes=1,
        uninstrumented_reasons=["adapter raised"],
    )

    assert aggregate.num_episodes == 4
    assert aggregate.end_to_end_success_rate == 0.5
    assert aggregate.instrumentation_coverage == 0.25
    assert aggregate.subgoal_success_rate_macro == 1.0
    assert aggregate.uninstrumented_reasons == ("adapter raised",)


def test_aggregate_rejects_inconsistent_uninstrumented_counts():
    with pytest.raises(ValueError, match="More uninstrumented successes"):
        subgoal_metrics.aggregate_episode_metrics(
            [], num_uninstrumented_episodes=1, uninstrumented_end_to_end_successes=2
        )


def test_aggregate_rejects_zero_episodes():
    with pytest.raises(ValueError, match="zero episodes"):
        subgoal_metrics.aggregate_episode_metrics([])


def test_aggregate_without_instrumented_episodes_returns_none_instead_of_dividing_by_zero():
    aggregate = subgoal_metrics.aggregate_episode_metrics(
        [], num_uninstrumented_episodes=2, uninstrumented_end_to_end_successes=0
    )

    assert aggregate.end_to_end_success_rate == 0.0
    assert aggregate.instrumentation_coverage == 0.0
    assert aggregate.subgoal_success_rate_macro is None
    assert aggregate.subgoal_success_rate_micro is None
    assert aggregate.episode_regression_rate is None
    assert aggregate.achieved_atom_coverage is None


def test_aggregate_regression_rates_are_atom_and_episode_level():
    episodes = [
        _episode("a", [[True, True], [False, False]], end_to_end_success=False),
        _episode("b", [[False, False], [False, False]], end_to_end_success=False),
    ]

    aggregate = subgoal_metrics.aggregate_episode_metrics(episodes)

    assert aggregate.regressed_atom_rate == 0.5
    assert aggregate.episode_regression_rate == 0.5
    assert aggregate.regression_transitions_total == 2
