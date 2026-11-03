"""EnvironmentConfig — the environment section of an experiment submission."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, model_validator


from typing import Optional, Literal

class EnvironmentConfig(BaseModel):
    environment_plugin: str
    environment_spec: str

    guardrail_mode: Literal["off", "on"] = "off"
    guardrail_policy: Optional[str] = None

    @model_validator(mode="after")
    def _validate(self) -> "EnvironmentConfig":
        from .plugins.base import EnvironmentPlugin
        from . import plugins

        if self.environment_plugin not in EnvironmentPlugin._registry:
            raise ValueError(
                f"Unknown environment_plugin {self.environment_plugin!r}"
            )

        if self.guardrail_mode == "on" and not self.guardrail_policy:
            raise ValueError(
                "guardrail_policy is required when guardrail_mode='on'"
            )

        return self

    @property
    def resolved_name(self) -> str:
        return self.environment_spec


class DeployedEnvironment(BaseModel):
    """The provisioning result the environment hands back after provision()."""
    topology_spec: str
    ip: Optional[str] = None
    spec: Optional[str] = None
    project_name: Optional[str] = None


def build_environment(value):
    from .plugins.base import EnvironmentPlugin
    from . import plugins

    if isinstance(value, EnvironmentPlugin):
        return value

    cfg = (
        value if isinstance(value, EnvironmentConfig)
        else EnvironmentConfig.model_validate(value)
    )

    plugin_cls = EnvironmentPlugin._registry.get(
        cfg.environment_plugin
    )

    if plugin_cls is None:
        raise ValueError(
            f"Unknown environment_plugin {cfg.environment_plugin!r}"
        )

    kwargs = {
        "type": cfg.environment_plugin,
        "environment_spec": cfg.environment_spec,
    }

    if cfg.environment_plugin == "mhbench":
        kwargs.update(
            guardrail_mode=cfg.guardrail_mode,
            guardrail_policy=cfg.guardrail_policy,
        )
    elif cfg.guardrail_mode != "off":
        raise ValueError(
            "Environment guardrail currently supports MHBench only"
        )

    return plugin_cls(**kwargs)