import os

import pytest

try:
    import pynvml
except ImportError:  # Apple Silicon / minimal Mac venv — no NVIDIA tooling
    pynvml = None


def set_jax_cpu_backend_if_no_gpu() -> None:
    if pynvml is None:
        # No NVML (typical on Mac). Prefer CPU JAX if tests import jax later.
        os.environ.setdefault("JAX_PLATFORMS", "cpu")
        return
    try:
        pynvml.nvmlInit()
        pynvml.nvmlShutdown()
    except pynvml.NVMLError:
        # No GPU found.
        os.environ["JAX_PLATFORMS"] = "cpu"


def pytest_configure(config: pytest.Config) -> None:
    set_jax_cpu_backend_if_no_gpu()
