"""Apple Silicon / Mac backend policy for checklist + gated-recovery ops.

Official openpi π0 training is JAX+CUDA on Linux. On Apple Silicon we keep the
*same eval protocol* (FIXED_EVAL_SUITE, Q-score, E2E) and train the lightweight
checklist head on MLX or PyTorch MPS when available.

Backend priority (Mac): mlx > mps > cpu
CUDA Linux still prefers jax/cuda for full π0; this module is the Mac path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

MacBackendName = Literal["mlx", "mps", "cpu", "cuda", "unavailable"]


@dataclass
class MacBackendReport:
    apple_silicon: bool
    metal_available: bool  # Metal present via MLX GPU or MPS
    mlx_available: bool
    mlx_error: str | None
    mps_available: bool
    mps_error: str | None
    torch_available: bool
    jax_metal_available: bool
    jax_metal_error: str | None
    memory_gb: float | None
    preferred: MacBackendName
    openpi_pi0_runnable: bool
    gaps_vs_cuda: list[str]
    messages: list[str]


def _memory_gb() -> float | None:
    try:
        import platform
        import subprocess

        if platform.system() != "Darwin":
            return None
        out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
        return round(int(out) / (1024**3), 2)
    except Exception:  # noqa: BLE001
        return None


def _probe_mlx() -> tuple[bool, str | None]:
    try:
        import mlx.core as mx

        a = mx.ones((2, 2))
        b = a @ a
        mx.eval(b)
        return True, None
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def _probe_mps() -> tuple[bool, bool, str | None]:
    """Returns (torch_available, mps_available, error)."""
    try:
        import torch

        built = bool(torch.backends.mps.is_built())
        avail = bool(torch.backends.mps.is_available())
        if avail:
            x = torch.ones(2, 2, device="mps")
            _ = (x @ x).cpu()
        return True, avail and built, None
    except Exception as e:  # noqa: BLE001
        return False, False, str(e)


def _probe_jax_metal() -> tuple[bool, str | None]:
    try:
        import jax

        backends = {d.platform.lower() for d in jax.devices()}
        # Apple Metal plugin typically shows as "METAL" / "gpu" without CUDA.
        if "metal" in backends:
            return True, None
        # Some builds expose Metal as gpu on Darwin without nvidia.
        import platform

        if platform.system() == "Darwin" and "gpu" in backends:
            return True, "jax reports gpu on Darwin (treat as Metal if plugin installed)"
        return False, f"jax devices={[str(d) for d in jax.devices()]} (no Metal)"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def detect_mac_backend() -> MacBackendReport:
    import platform

    apple = platform.system() == "Darwin" and platform.machine() == "arm64"
    mlx_ok, mlx_err = _probe_mlx()
    torch_ok, mps_ok, mps_err = _probe_mps()
    jax_metal, jax_err = _probe_jax_metal()
    mem = _memory_gb()
    metal = mlx_ok or mps_ok or jax_metal

    gaps = [
        "Official openpi π0/π0.5 JAX trainer (`scripts/train.py`) requires Linux + NVIDIA CUDA; not runnable on Mac.",
        "Full π0 weight fine-tune and LIBERO/B1K GPU sims stay CUDA-only.",
        "JAX Metal plugin (if installed) is experimental and not the supported openpi path.",
        "Mac path trains the checklist head (MLX/MPS/CPU) with protocol-parity eval only.",
    ]
    messages: list[str] = []
    if apple:
        messages.append(f"Apple Silicon detected (arm64); memory≈{mem} GiB." if mem else "Apple Silicon detected (arm64).")
    else:
        messages.append(f"Not Apple Silicon ({platform.system()} {platform.machine()}).")

    if apple:
        if mlx_ok:
            preferred: MacBackendName = "mlx"
            messages.append("MLX Metal GPU usable — preferred Mac backend for checklist smoke train.")
        elif mps_ok:
            preferred = "mps"
            messages.append("PyTorch MPS usable — fallback Mac backend for checklist smoke train.")
        else:
            preferred = "cpu"
            messages.append("No MLX/MPS — falling back to CPU numpy logistic (same protocol).")
        pi0_ok = False
    else:
        preferred = "unavailable"
        messages.append("Mac backend not applicable; use CUDA openpi path on Linux.")
        pi0_ok = False  # CUDA π0 gated elsewhere in env_detect / run_openpi_train

    return MacBackendReport(
        apple_silicon=apple,
        metal_available=metal,
        mlx_available=mlx_ok,
        mlx_error=None if mlx_ok else mlx_err,
        mps_available=mps_ok,
        mps_error=None if mps_ok else mps_err,
        torch_available=torch_ok,
        jax_metal_available=jax_metal,
        jax_metal_error=None if jax_metal else jax_err,
        memory_gb=mem,
        preferred=preferred,
        openpi_pi0_runnable=pi0_ok,
        gaps_vs_cuda=gaps if apple else [],
        messages=messages,
    )


def resolve_backend(requested: str | None = None) -> MacBackendName:
    """Resolve user request against availability. requested: auto|mlx|mps|cpu."""
    report = detect_mac_backend()
    req = (requested or "auto").lower()
    if req in {"auto", "mac"}:
        return report.preferred if report.apple_silicon else "cpu"
    if req == "mlx":
        if not report.mlx_available:
            raise RuntimeError(f"MLX requested but unavailable: {report.mlx_error}")
        return "mlx"
    if req == "mps":
        if not report.mps_available:
            raise RuntimeError(f"MPS requested but unavailable: {report.mps_error}")
        return "mps"
    if req == "cpu":
        return "cpu"
    raise ValueError(f"Unknown backend: {requested}")


def report_as_dict(report: MacBackendReport) -> dict:
    return asdict(report)
