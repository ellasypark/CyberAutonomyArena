from __future__ import annotations

import os
from pathlib import Path

from ....config import ExperimentManagerConfig


def mhbench_cli_env(cfg: ExperimentManagerConfig, **overrides: str) -> dict[str, str]:
    """Build an environment that exposes MHBench's venv executables to its CLI."""
    env = os.environ.copy()
    scripts_dir = "Scripts" if os.name == "nt" else "bin"
    venv_bin = Path(cfg.mhbench_dir) / ".venv" / scripts_dir
    env["PATH"] = os.pathsep.join(filter(None, (str(venv_bin), env.get("PATH", ""))))
    env.update(overrides)
    return env
