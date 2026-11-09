"""Dry-run preflight for the wheeled-bimanual household minimal loop.

Stdlib only, so it runs on a bare VM before any openpi dependency is installed.
It never downloads weights, never trains and never touches hardware: every check
is either a local probe or a static read of files already in the repo.

Usage:
    python3 scripts/rsi/wheeled_bimanual_preflight.py
    python3 scripts/rsi/wheeled_bimanual_preflight.py --json
"""

import argparse
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = REPO_ROOT / "rsi" / "plans" / "wheeled_bimanual_v0_schema.json"

PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"
INFO = "INFO"

# Image slots are fixed by the pi0 family; see src/openpi/policies/libero_policy.py.
REQUIRED_IMAGE_SLOTS = ("base_0_rgb", "left_wrist_0_rgb", "right_wrist_0_rgb")

# Mirrors requires-python in pyproject.toml.
MIN_PYTHON = (3, 11)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, check_id: str, status: str, detail: str, *, action: str = "") -> None:
        self.rows.append({"check": check_id, "status": status, "detail": detail, "action": action})

    @property
    def failed(self) -> list[dict]:
        return [r for r in self.rows if r["status"] == FAIL]

    @property
    def blocked(self) -> list[dict]:
        return [r for r in self.rows if r["status"] == BLOCKED]


def make_bool_mask(*dims: int) -> tuple[bool, ...]:
    """Local replica of ``openpi.transforms.make_bool_mask``.

    Duplicated on purpose: importing openpi requires jax, which is exactly what
    this preflight runs before.
    """
    result: list[bool] = []
    for dim in dims:
        if dim > 0:
            result.extend([True] * dim)
        else:
            result.extend([False] * (-dim))
    return tuple(result)


def check_replica_matches_upstream(checks: Checks) -> None:
    source = REPO_ROOT / "src" / "openpi" / "transforms.py"
    if not source.is_file():
        checks.add("mask.replica", FAIL, f"missing {source.relative_to(REPO_ROOT)}")
        return
    text = source.read_text(encoding="utf-8")
    # The upstream docstring examples double as the contract this replica must honour.
    examples = {
        "make_bool_mask(2, -2, 2) == (True, True, False, False, True, True)": make_bool_mask(2, -2, 2)
        == (True, True, False, False, True, True),
        "make_bool_mask(2, 0, 2) == (True, True, True, True)": make_bool_mask(2, 0, 2) == (True, True, True, True),
    }
    missing = [line for line in examples if line not in text]
    wrong = [line for line, ok in examples.items() if not ok]
    if missing:
        checks.add(
            "mask.replica",
            FAIL,
            f"upstream docstring examples changed, replica may be stale: {missing}",
            action="re-read src/openpi/transforms.py and update make_bool_mask in this script",
        )
        return
    if wrong:
        checks.add("mask.replica", FAIL, f"replica disagrees with upstream examples: {wrong}")
        return
    checks.add("mask.replica", PASS, "replica reproduces both upstream make_bool_mask docstring examples")


def check_environment(checks: Checks) -> None:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    wanted = ".".join(str(part) for part in MIN_PYTHON)
    if tuple(sys.version_info[:2]) >= MIN_PYTHON:
        checks.add("env.python", PASS, f"python {version} satisfies requires-python >={wanted}")
    else:
        checks.add("env.python", FAIL, f"python {version} is below requires-python >={wanted}")

    uv = shutil.which("uv")
    if uv:
        checks.add("env.uv", PASS, f"uv at {uv}")
    else:
        checks.add(
            "env.uv",
            BLOCKED,
            "uv not installed, so `uv venv` / `uv sync` cannot run",
            action="install uv, then `uv venv --python 3.11 && uv sync`",
        )

    if shutil.which("nvidia-smi"):
        checks.add("env.gpu", PASS, "nvidia-smi present")
    else:
        checks.add(
            "env.gpu",
            BLOCKED,
            "no nvidia-smi: no GPU for pi0 inference and none for Isaac Sim / OmniGibson",
            action="schedule the loop on a CUDA host before any rollout",
        )

    free = shutil.disk_usage(REPO_ROOT)
    checks.add(
        "env.resources",
        INFO,
        f"cpu={os.cpu_count()} disk_free={free.free // 2**30}GiB",
    )


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout


def check_submodules(checks: Checks) -> None:
    out = _git(["submodule", "status"])
    if not out.strip():
        checks.add("repo.submodules", INFO, "no submodules reported")
        return
    uninitialized = [line.strip().split()[1] for line in out.splitlines() if line.startswith("-")]
    if uninitialized:
        checks.add(
            "repo.submodules",
            BLOCKED,
            f"not checked out: {', '.join(uninitialized)}",
            action="git submodule update --init --recursive",
        )
    else:
        checks.add("repo.submodules", PASS, "all submodules checked out")


def check_openpi_importable(checks: Checks) -> None:
    if importlib.util.find_spec("openpi") is None:
        checks.add(
            "repo.openpi_import",
            BLOCKED,
            "openpi is not importable, so no config or transform can be executed",
            action="uv sync && uv pip install -e .",
        )
    else:
        checks.add("repo.openpi_import", PASS, "openpi importable")


def check_registered_configs(checks: Checks, wanted: list[str]) -> None:
    config_py = REPO_ROOT / "src" / "openpi" / "training" / "config.py"
    if not config_py.is_file():
        checks.add("repo.configs", FAIL, f"missing {config_py.relative_to(REPO_ROOT)}")
        return
    registered = set(re.findall(r'name="([a-z0-9_]+)"', config_py.read_text(encoding="utf-8")))
    missing = [name for name in wanted if name not in registered]
    if missing:
        checks.add(
            "repo.configs",
            FAIL,
            f"reference configs absent from config.py: {', '.join(missing)}",
            action="fix reference_configs in the schema, or register the configs",
        )
    else:
        checks.add("repo.configs", PASS, f"reference configs registered: {', '.join(wanted)}")


def check_image_slots(checks: Checks, slots: dict) -> None:
    policy_py = REPO_ROOT / "src" / "openpi" / "policies" / "libero_policy.py"
    if not policy_py.is_file():
        checks.add("repo.image_slots", FAIL, f"missing {policy_py.relative_to(REPO_ROOT)}")
        return
    text = policy_py.read_text(encoding="utf-8")
    absent = [slot for slot in REQUIRED_IMAGE_SLOTS if f'"{slot}"' not in text]
    if absent:
        checks.add(
            "repo.image_slots",
            FAIL,
            f"slot names not found in libero_policy.py: {', '.join(absent)}",
            action="re-read the policy adapter; the model image contract may have moved",
        )
        return
    unknown = sorted(set(slots) - set(REQUIRED_IMAGE_SLOTS))
    unmapped = [slot for slot in REQUIRED_IMAGE_SLOTS if slot not in slots]
    if unknown or unmapped:
        checks.add(
            "repo.image_slots",
            FAIL,
            f"schema slot mapping mismatch: unknown={unknown} unmapped={unmapped}",
        )
        return
    checks.add("repo.image_slots", PASS, "all three model image slots mapped to named sensors")


def check_schema(checks: Checks, schema: dict) -> None:
    physical_dim = schema["physical_dim"]
    model_action_dim = schema["model_action_dim"]
    fields = schema["fields"]

    if physical_dim > model_action_dim:
        checks.add(
            "schema.action_dim",
            FAIL,
            f"physical_dim {physical_dim} exceeds model action_dim {model_action_dim}",
        )
    else:
        pad = model_action_dim - physical_dim
        checks.add(
            "schema.action_dim",
            PASS,
            f"physical_dim {physical_dim} fits action_dim {model_action_dim} with {pad} padding dims",
        )

    slots: list[str | None] = [None] * physical_dim
    overlaps: list[str] = []
    out_of_range: list[str] = []
    for field in fields:
        start, size = field["start"], field["size"]
        if start < 0 or start + size > physical_dim:
            out_of_range.append(f"{field['name']}[{start}:{start + size}]")
            continue
        for idx in range(start, start + size):
            if slots[idx] is not None:
                overlaps.append(f"{field['name']} collides with {slots[idx]} at index {idx}")
            slots[idx] = field["name"]
    gaps = [idx for idx, owner in enumerate(slots) if owner is None]

    problems = out_of_range + overlaps + ([f"unassigned indices {gaps}"] if gaps else [])
    if problems:
        checks.add("schema.layout", FAIL, "; ".join(problems))
    else:
        checks.add("schema.layout", PASS, f"{len(fields)} fields tile indices 0..{physical_dim - 1} exactly once")

    spaces = {field["action_space"] for field in fields}
    illegal = spaces - {"delta", "absolute"}
    if illegal:
        checks.add("schema.action_space", FAIL, f"unknown action_space values: {sorted(illegal)}")
        return
    checks.add("schema.action_space", PASS, "every field declares delta or absolute")

    declared = make_bool_mask(*schema["delta_mask_spec"])
    derived: list[bool] = []
    for field in sorted(fields, key=lambda f: f["start"]):
        derived.extend([field["action_space"] == "delta"] * field["size"])
    derived_mask = tuple(derived)

    if len(declared) != physical_dim:
        checks.add(
            "schema.delta_mask",
            FAIL,
            f"delta_mask_spec expands to {len(declared)} dims, expected {physical_dim}",
        )
        return
    if declared != derived_mask:
        diff = [idx for idx, (a, b) in enumerate(zip(declared, derived_mask, strict=True)) if a != b]
        checks.add(
            "schema.delta_mask",
            FAIL,
            f"delta_mask_spec disagrees with per-field action_space at indices {diff}",
            action="fix delta_mask_spec or the field action_space values",
        )
        return
    delta_fields = [f["name"] for f in fields if f["action_space"] == "delta"]
    checks.add(
        "schema.delta_mask",
        PASS,
        f"make_bool_mask{tuple(schema['delta_mask_spec'])} matches declared delta fields: {', '.join(delta_fields)}",
    )


def check_rsi_artifacts(checks: Checks) -> None:
    for rel in ("rsi/leaderboard.md", "rsi/leaderboards/log.md", "rsi/experiments/experiment-tree.md"):
        path = REPO_ROOT / rel
        if path.is_file():
            checks.add(f"rsi.{pathlib.Path(rel).stem}", PASS, f"{rel} present")
        else:
            checks.add(
                f"rsi.{pathlib.Path(rel).stem}",
                BLOCKED,
                f"{rel} missing, results have nowhere to be logged",
                action=f"create {rel} before reporting any score",
            )

    plans = sorted((REPO_ROOT / "rsi" / "plans").glob("*.md"))
    if plans:
        checks.add("rsi.plans", PASS, f"{len(plans)} plan file(s): {', '.join(p.name for p in plans)}")
    else:
        checks.add(
            "rsi.plans",
            BLOCKED,
            "rsi/plans holds no plan document",
            action="land and approve a plan before any rollout",
        )


def check_sim_entrypoint(checks: Checks) -> None:
    for module in ("omnigibson", "bddl", "libero", "mani_skill", "habitat"):
        if importlib.util.find_spec(module) is not None:
            checks.add(f"sim.{module}", PASS, f"{module} importable")
        else:
            checks.add(
                f"sim.{module}",
                BLOCKED,
                f"{module} not installed",
                action="pick one simulator, pin its version, then install it on a GPU host",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=pathlib.Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    args = parser.parse_args()

    if not args.schema.is_file():
        print(f"schema not found: {args.schema}", file=sys.stderr)
        return 2
    schema = json.loads(args.schema.read_text(encoding="utf-8"))

    checks = Checks()
    check_environment(checks)
    check_submodules(checks)
    check_openpi_importable(checks)
    check_replica_matches_upstream(checks)
    check_registered_configs(checks, list(schema.get("reference_configs", [])))
    check_image_slots(checks, schema.get("image_slots", {}))
    check_schema(checks, schema)
    check_rsi_artifacts(checks)
    check_sim_entrypoint(checks)

    exit_code = 1 if checks.failed else 0

    if args.json:
        print(
            json.dumps(
                {
                    "schema_id": schema.get("schema_id"),
                    "mode": "dry-run",
                    "checks": checks.rows,
                    "failed": len(checks.failed),
                    "blocked": len(checks.blocked),
                    "exit_code": exit_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return exit_code

    width = max(len(row["check"]) for row in checks.rows)
    print(f"wheeled-bimanual preflight (dry-run) schema={schema.get('schema_id')}")
    print("-" * 78)
    for row in checks.rows:
        print(f"{row['status']:<8} {row['check']:<{width}}  {row['detail']}")
        if row["action"]:
            print(f"{'':<8} {'':<{width}}  -> {row['action']}")
    print("-" * 78)
    print(f"failed={len(checks.failed)} blocked={len(checks.blocked)} total={len(checks.rows)}")
    if checks.blocked:
        print("blocked checks are human action items, not script errors; no rollout may be reported until cleared")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
