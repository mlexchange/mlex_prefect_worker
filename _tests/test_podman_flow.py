import sys
from pathlib import Path
from types import SimpleNamespace


import pytest

from flows.podman.schema import PodmanParams
import flows.podman.podman_flows as podman_flows


@pytest.mark.asyncio
async def test_launch_podman_without_podman(monkeypatch, tmp_path):
    # Fake run context to provide a flow_run id
    monkeypatch.setattr(
        podman_flows.context,
        "get_run_context",
        lambda: SimpleNamespace(flow_run=SimpleNamespace(id="fake-podman-flow")),
    )

    # Patch run_process to avoid invoking podman; return success
    async def fake_run_process(cmd, stream_output=True):
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(podman_flows, "run_process", fake_run_process)

    # Patch add_credentials_to_io_parameters to be a no-op
    monkeypatch.setattr(
        podman_flows,
        "add_credentials_to_io_parameters",
        lambda params: params,
    )

    # Patch get_additional_env_vars_for_container to return a predictable dict
    monkeypatch.setattr(podman_flows, "get_additional_env_vars_for_container", lambda: {"EXTRA": "1"})

    # Patch setup_logger to avoid requiring a Prefect run context
    import logging
    monkeypatch.setattr(podman_flows, "setup_logger", lambda: logging.getLogger("test"))

    params = {
        "io_parameters": {"uid_retrieve": "", "uid_save": ""}
    }

    pp = PodmanParams(
        image_name="test/image",
        image_tag="latest",
        command="echo",
        params=params,
        volumes=[],
        network="",
        env_vars={},
    )

    result = await podman_flows.launch_podman.__wrapped__(pp, prev_flow_run_id="")

    assert result == "fake-podman-flow"
    # Ensure additional env vars were merged into the PodmanParams
    assert pp.env_vars.get("EXTRA") == "1"
