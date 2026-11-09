"""Environment detection for local openpi / B1K runs (Mac vs CUDA Linux)."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class EnvReport:
    system: str
    machine: str
    python: str
    has_nvidia_smi: bool
    cuda_visible: bool
    gpu_names: list[str]
    jax_devices: list[str]
    jax_error: str | None
    disk_free_gb: float
    openpi_cache: str
    b1k_root: str | None
    b1k_importable: bool
    download_weights_env: bool
    recommended_mode: str
    messages: list[str]


def _disk_free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024**3)


def _gpu_names_from_nvidia_smi() -> tuple[bool, list[str]]:
    if shutil.which("nvidia-smi") is None:
        return False, []
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        names = [line.strip() for line in out.splitlines() if line.strip()]
        return True, names
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return True, [f"<nvidia-smi error: {e}>"]


def _jax_devices() -> tuple[list[str], str | None]:
    try:
        import jax

        return [f"{d.platform}:{d}" for d in jax.devices()], None
    except Exception as e:  # noqa: BLE001 - report any import/runtime issue
        return [], str(e)


def _b1k_status() -> tuple[str | None, bool]:
    root = os.environ.get("B1K_ROOT") or os.environ.get("BEHAVIOR_ROOT")
    importable = False
    for mod in ("omnigibson", "behavior_eval", "BEHAVIOR"):
        try:
            __import__(mod)
            importable = True
            break
        except Exception:
            continue
    if root and Path(root).exists():
        return root, importable or True
    return root, importable


def detect_env(repo_root: Path | None = None) -> EnvReport:
    repo_root = repo_root or Path.cwd()
    has_smi, gpu_names = _gpu_names_from_nvidia_smi()
    jax_devs, jax_err = _jax_devices()
    cuda_visible = any("gpu" in d.lower() or "cuda" in d.lower() for d in jax_devs) or (
        has_smi and bool(gpu_names) and not gpu_names[0].startswith("<nvidia-smi error")
    )
    b1k_root, b1k_ok = _b1k_status()
    cache = Path(os.environ.get("OPENPI_DATA_HOME", "~/.cache/openpi")).expanduser()
    download = os.environ.get("DOWNLOAD_WEIGHTS", "0") in {"1", "true", "TRUE", "yes", "YES"}
    messages: list[str] = []
    system = platform.system()

    if system == "Darwin":
        messages.append(
            "检测到 macOS：openpi 官方训练/评测面向 Linux + NVIDIA CUDA；"
            "本机请用 --mode cpu-stub / dry-run。完整 π0 训练请到 CUDA Linux。"
        )
        recommended = "cpu-stub"
    elif not cuda_visible:
        messages.append("未检测到可用 CUDA GPU。拒绝启动真实 openpi 训练（除非 ALLOW_CPU_JAX=1，仍极慢且不推荐）。")
        recommended = "cpu-stub"
    else:
        recommended = "openpi-gpu"
        messages.append("检测到 CUDA GPU：可运行 scripts/rsi/run_openpi_train.py（需 DOWNLOAD_WEIGHTS=1 或本地缓存权重）。")

    if not b1k_ok:
        messages.append(
            "未检测到 B1K/OmniGibson（设置 B1K_ROOT 或安装官方 BEHAVIOR 栈）。"
            "可用 --mode b1k-protocol 做协议干跑，或 wheeled suite 作为对齐评测。"
        )

    free_gb = _disk_free_gb(repo_root)
    if free_gb < 40:
        messages.append(f"磁盘剩余约 {free_gb:.1f} GiB：拉取 π0 权重/数据前建议 ≥40 GiB 可用空间。")

    return EnvReport(
        system=system,
        machine=platform.machine(),
        python=platform.python_version(),
        has_nvidia_smi=has_smi,
        cuda_visible=cuda_visible,
        gpu_names=gpu_names,
        jax_devices=jax_devs,
        jax_error=jax_err,
        disk_free_gb=round(free_gb, 2),
        openpi_cache=str(cache),
        b1k_root=b1k_root,
        b1k_importable=b1k_ok,
        download_weights_env=download,
        recommended_mode=recommended,
        messages=messages,
    )


def report_as_dict(report: EnvReport) -> dict:
    return asdict(report)


def format_report(report: EnvReport) -> str:
    return json.dumps(report_as_dict(report), indent=2, ensure_ascii=False)
