from __future__ import annotations  # The LIBERO eval container runs Python 3.8.

import collections
import dataclasses
import json
import logging
import math
import pathlib

import imageio
from libero.libero import benchmark
from libero.libero import get_libero_path
from libero.libero.envs import OffScreenRenderEnv
import numpy as np
from openpi_client import image_tools
from openpi_client import websocket_client_policy as _websocket_client_policy
from openpi_client.eval import libero_subgoal
from openpi_client.eval import subgoal_metrics
import tqdm
import tyro

LIBERO_DUMMY_ACTION = [0.0] * 6 + [-1.0]
LIBERO_ENV_RESOLUTION = 256  # resolution used to render training data


@dataclasses.dataclass
class Args:
    #################################################################################################################
    # Model server parameters
    #################################################################################################################
    host: str = "0.0.0.0"
    port: int = 8000
    resize_size: int = 224
    replan_steps: int = 5

    #################################################################################################################
    # LIBERO environment-specific parameters
    #################################################################################################################
    task_suite_name: str = (
        "libero_spatial"  # Task suite. Options: libero_spatial, libero_object, libero_goal, libero_10, libero_90
    )
    num_steps_wait: int = 10  # Number of steps to wait for objects to stabilize i n sim
    num_trials_per_task: int = 50  # Number of rollouts per task

    #################################################################################################################
    # Utils
    #################################################################################################################
    video_out_path: str = "data/libero/videos"  # Path to save videos

    seed: int = 7  # Random Seed (for reproducibility)

    #################################################################################################################
    # Subgoal-level metrics
    #
    # Off by default: reading the BDDL goal atoms relies on LIBERO internals that have not been
    # exercised against a running simulator yet. Enabling it never changes the rollout or the
    # end-to-end success criterion, so turning the flag back off is a complete rollback.
    #################################################################################################################
    report_subgoal_metrics: bool = False
    subgoal_metrics_out_path: str = "data/libero/subgoal_metrics"  # Directory for subgoal metric reports


def _sample_goal_atoms(tracker, monitor) -> str | None:
    """Samples every goal atom once. Returns None on success, or a failure reason.

    Instrumentation failures must not be reported as policy failures, so the caller drops the
    tracker and keeps the rollout running instead of letting the exception abort the episode.
    """
    try:
        tracker.record(monitor.read_statuses())
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    return None


def eval_libero(args: Args) -> None:
    # Set random seed
    np.random.seed(args.seed)

    # Initialize LIBERO task suite
    benchmark_dict = benchmark.get_benchmark_dict()
    task_suite = benchmark_dict[args.task_suite_name]()
    num_tasks_in_suite = task_suite.n_tasks
    logging.info(f"Task suite: {args.task_suite_name}")

    pathlib.Path(args.video_out_path).mkdir(parents=True, exist_ok=True)

    if args.task_suite_name == "libero_spatial":
        max_steps = 220  # longest training demo has 193 steps
    elif args.task_suite_name == "libero_object":
        max_steps = 280  # longest training demo has 254 steps
    elif args.task_suite_name == "libero_goal":
        max_steps = 300  # longest training demo has 270 steps
    elif args.task_suite_name == "libero_10":
        max_steps = 520  # longest training demo has 505 steps
    elif args.task_suite_name == "libero_90":
        max_steps = 400  # longest training demo has 373 steps
    else:
        raise ValueError(f"Unknown task suite: {args.task_suite_name}")

    client = _websocket_client_policy.WebsocketClientPolicy(args.host, args.port)

    # Start evaluation
    total_episodes, total_successes = 0, 0
    episode_subgoal_metrics = []
    uninstrumented_episodes, uninstrumented_successes = 0, 0
    uninstrumented_reasons = []
    subgoal_out_dir = pathlib.Path(args.subgoal_metrics_out_path)
    episodes_jsonl_path = subgoal_out_dir / f"{args.task_suite_name}_episodes.jsonl"
    if args.report_subgoal_metrics:
        subgoal_out_dir.mkdir(parents=True, exist_ok=True)
        # Start a fresh trace so a rerun is never silently appended to an earlier one.
        episodes_jsonl_path.unlink(missing_ok=True)

    for task_id in tqdm.tqdm(range(num_tasks_in_suite)):
        # Get task
        task = task_suite.get_task(task_id)

        # Get default LIBERO initial states
        initial_states = task_suite.get_task_init_states(task_id)

        # Initialize LIBERO environment and task description
        env, task_description = _get_libero_env(task, LIBERO_ENV_RESOLUTION, args.seed)

        # Start episodes
        task_episodes, task_successes = 0, 0
        for episode_idx in tqdm.tqdm(range(args.num_trials_per_task)):
            logging.info(f"\nTask: {task_description}")

            # Reset environment
            env.reset()
            action_plan = collections.deque()

            # Set initial states
            obs = env.set_init_state(initial_states[episode_idx])

            # Setup
            t = 0
            done = False
            replay_images = []

            episode_id = f"{args.task_suite_name}/task-{task_id}/episode-{episode_idx}"
            monitor, tracker, instrumentation_error = None, None, None
            if args.report_subgoal_metrics:
                try:
                    monitor = libero_subgoal.LiberoGoalMonitor(env)
                    tracker = monitor.make_tracker(episode_id)
                except Exception as e:
                    instrumentation_error = f"{type(e).__name__}: {e}"
                    logging.error(f"Could not read BDDL goal atoms for {episode_id}: {instrumentation_error}")

            logging.info(f"Starting episode {task_episodes + 1}...")
            while t < max_steps + args.num_steps_wait:
                try:
                    # IMPORTANT: Do nothing for the first few timesteps because the simulator drops objects
                    # and we need to wait for them to fall
                    if t < args.num_steps_wait:
                        obs, reward, done, info = env.step(LIBERO_DUMMY_ACTION)
                        t += 1
                        continue

                    # Baseline atom readout, taken once the scene has settled and before the
                    # first policy action. Warm-up steps are never sampled, so dropping objects
                    # cannot show up as subgoal progress or as a regression.
                    if tracker is not None and tracker.num_sampled_steps == 0:
                        instrumentation_error = _sample_goal_atoms(tracker, monitor)
                        if instrumentation_error is not None:
                            logging.error(f"Disabling subgoal metrics for {episode_id}: {instrumentation_error}")
                            monitor, tracker = None, None

                    # Get preprocessed image
                    # IMPORTANT: rotate 180 degrees to match train preprocessing
                    img = np.ascontiguousarray(obs["agentview_image"][::-1, ::-1])
                    wrist_img = np.ascontiguousarray(obs["robot0_eye_in_hand_image"][::-1, ::-1])
                    img = image_tools.convert_to_uint8(
                        image_tools.resize_with_pad(img, args.resize_size, args.resize_size)
                    )
                    wrist_img = image_tools.convert_to_uint8(
                        image_tools.resize_with_pad(wrist_img, args.resize_size, args.resize_size)
                    )

                    # Save preprocessed image for replay video
                    replay_images.append(img)

                    if not action_plan:
                        # Finished executing previous action chunk -- compute new chunk
                        # Prepare observations dict
                        element = {
                            "observation/image": img,
                            "observation/wrist_image": wrist_img,
                            "observation/state": np.concatenate(
                                (
                                    obs["robot0_eef_pos"],
                                    _quat2axisangle(obs["robot0_eef_quat"]),
                                    obs["robot0_gripper_qpos"],
                                )
                            ),
                            "prompt": str(task_description),
                        }

                        # Query model to get action
                        action_chunk = client.infer(element)["actions"]
                        assert len(action_chunk) >= args.replan_steps, (
                            f"We want to replan every {args.replan_steps} steps, but policy only predicts {len(action_chunk)} steps."
                        )
                        action_plan.extend(action_chunk[: args.replan_steps])

                    action = action_plan.popleft()

                    # Execute action in environment
                    obs, reward, done, info = env.step(action.tolist())

                    if tracker is not None:
                        instrumentation_error = _sample_goal_atoms(tracker, monitor)
                        if instrumentation_error is not None:
                            logging.error(f"Disabling subgoal metrics for {episode_id}: {instrumentation_error}")
                            monitor, tracker = None, None

                    if done:
                        task_successes += 1
                        total_successes += 1
                        break
                    t += 1

                except Exception as e:
                    logging.error(f"Caught exception: {e}")
                    break

            task_episodes += 1
            total_episodes += 1

            if args.report_subgoal_metrics:
                if tracker is not None and tracker.num_sampled_steps > 0:
                    metrics = tracker.finalize(end_to_end_success=bool(done))
                    episode_subgoal_metrics.append(metrics)
                    with episodes_jsonl_path.open("a") as f:
                        f.write(json.dumps(metrics.to_dict(), sort_keys=True) + "\n")
                    logging.info(
                        f"Subgoal: {metrics.num_ever_achieved}/{metrics.num_atoms} atoms ever achieved, "
                        f"final progress {metrics.final_progress:.2f}, regressions {metrics.regression_transitions}"
                    )
                    if metrics.done_atom_mismatch:
                        logging.error(f"{episode_id}: env reported success while some goal atom read false")
                else:
                    # Keep the episode in the end-to-end denominator so a broken readout cannot
                    # quietly shrink the reported suite.
                    uninstrumented_episodes += 1
                    uninstrumented_successes += int(bool(done))
                    uninstrumented_reasons.append(f"{episode_id}: {instrumentation_error or 'no atom readout'}")

            # Save a replay video of the episode
            suffix = "success" if done else "failure"
            task_segment = task_description.replace(" ", "_")
            imageio.mimwrite(
                pathlib.Path(args.video_out_path) / f"rollout_{task_segment}_{suffix}.mp4",
                [np.asarray(x) for x in replay_images],
                fps=10,
            )

            # Log current results
            logging.info(f"Success: {done}")
            logging.info(f"# episodes completed so far: {total_episodes}")
            logging.info(f"# successes: {total_successes} ({total_successes / total_episodes * 100:.1f}%)")

        # Log final results
        logging.info(f"Current task success rate: {float(task_successes) / float(task_episodes)}")
        logging.info(f"Current total success rate: {float(total_successes) / float(total_episodes)}")

    logging.info(f"Total success rate: {float(total_successes) / float(total_episodes)}")
    logging.info(f"Total episodes: {total_episodes}")

    if args.report_subgoal_metrics:
        _report_subgoal_summary(
            args,
            episode_subgoal_metrics,
            subgoal_out_dir,
            uninstrumented_episodes=uninstrumented_episodes,
            uninstrumented_successes=uninstrumented_successes,
            uninstrumented_reasons=uninstrumented_reasons,
        )


def _report_subgoal_summary(
    args: Args,
    episodes: list,
    out_dir: pathlib.Path,
    *,
    uninstrumented_episodes: int,
    uninstrumented_successes: int,
    uninstrumented_reasons: list,
) -> None:
    """Writes the suite-level subgoal summary next to the end-to-end success rate."""
    aggregate = subgoal_metrics.aggregate_episode_metrics(
        episodes,
        num_uninstrumented_episodes=uninstrumented_episodes,
        uninstrumented_end_to_end_successes=uninstrumented_successes,
        uninstrumented_reasons=uninstrumented_reasons,
    )
    summary = {"task_suite_name": args.task_suite_name, "seed": args.seed, "aggregate": aggregate.to_dict()}
    (out_dir / f"{args.task_suite_name}_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))

    logging.info(f"End-to-end success rate: {aggregate.end_to_end_success_rate}")
    logging.info(f"Subgoal success rate (macro): {aggregate.subgoal_success_rate_macro}")
    logging.info(f"Subgoal success rate (micro): {aggregate.subgoal_success_rate_micro}")
    logging.info(f"Mean final progress: {aggregate.final_progress_macro}")
    logging.info(f"Regressed atom rate: {aggregate.regressed_atom_rate}")
    logging.info(f"Subgoal instrumentation coverage: {aggregate.instrumentation_coverage}")
    if aggregate.instrumentation_coverage < 1.0:
        logging.error(
            f"Subgoal metrics cover only {aggregate.num_instrumented_episodes}/{aggregate.num_episodes} episodes; "
            "they describe a subset and must not be reported as suite-level subgoal results."
        )
    if aggregate.done_atom_mismatch_episodes:
        logging.error(
            f"{aggregate.done_atom_mismatch_episodes} episodes disagreed with the environment success bit; "
            "the atom readout is unreliable for this run."
        )


def _get_libero_env(task, resolution, seed):
    """Initializes and returns the LIBERO environment, along with the task description."""
    task_description = task.language
    task_bddl_file = pathlib.Path(get_libero_path("bddl_files")) / task.problem_folder / task.bddl_file
    env_args = {"bddl_file_name": task_bddl_file, "camera_heights": resolution, "camera_widths": resolution}
    env = OffScreenRenderEnv(**env_args)
    env.seed(seed)  # IMPORTANT: seed seems to affect object positions even when using fixed initial state
    return env, task_description


def _quat2axisangle(quat):
    """
    Copied from robosuite: https://github.com/ARISE-Initiative/robosuite/blob/eafb81f54ffc104f905ee48a16bb15f059176ad3/robosuite/utils/transform_utils.py#L490C1-L512C55
    """
    # clip quaternion
    if quat[3] > 1.0:
        quat[3] = 1.0
    elif quat[3] < -1.0:
        quat[3] = -1.0

    den = np.sqrt(1.0 - quat[3] * quat[3])
    if math.isclose(den, 0.0):
        # This is (close to) a zero degree rotation, immediately return
        return np.zeros(3)

    return (quat[:3] * 2.0 * math.acos(quat[3])) / den


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tyro.cli(eval_libero)
