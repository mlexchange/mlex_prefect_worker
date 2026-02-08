import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from flows.docker.schema import DockerParams
import flows.docker.docker_flows as docker_flows


@pytest.mark.asyncio
async def test_launch_docker_without_docker(monkeypatch, tmp_path):
    # Fake run context to provide a flow_run id
    monkeypatch.setattr(
        docker_flows.context,
        "get_run_context",
        lambda: SimpleNamespace(flow_run=SimpleNamespace(id="fake-flow-id")),
    )

    # Patch run_process to avoid invoking docker; return success
    async def fake_run_process(cmd, stream_output=True):
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(docker_flows, "run_process", fake_run_process)

    # Patch add_credentials_to_io_parameters to be a no-op
    monkeypatch.setattr(
        docker_flows,
        "add_credentials_to_io_parameters",
        lambda params: params,
    )

    # Patch get_additional_env_vars_for_container to return a predictable dict
    monkeypatch.setattr(docker_flows, "get_additional_env_vars_for_container", lambda: {"EXTRA": "1"})
    # Patch setup_logger to avoid requiring a Prefect run context
    import logging
    monkeypatch.setattr(docker_flows, "setup_logger", lambda: logging.getLogger("test"))

    params = {
        "io_parameters": {"uid_retrieve": "", "uid_save": ""}
    }

    dp = DockerParams(
        image_name="test/image",
        image_tag="latest",
        command="echo",
        params=params,
        volumes=[],
        network="",
        env_vars={},
    )

    # Call the original wrapped function to avoid Prefect runtime
    result = await docker_flows.launch_docker.__wrapped__(dp, prev_flow_run_id="")

    assert result == "fake-flow-id"
    # Ensure additional env vars were merged into the DockerParams
    assert dp.env_vars.get("EXTRA") == "1"
