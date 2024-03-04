import sys
import tempfile
import uuid

import yaml
from prefect import context, flow, get_run_logger
from prefect.states import Failed
from prefect.utilities.processutils import run_process


class Logger:
    def __init__(self, logger, level="info"):
        self.logger = getattr(logger, level)

    def write(self, message):
        if message != "\n":
            self.logger(message)

    def flush(self):
        pass


def setup_logger():
    """
    Adopt stdout and stderr to prefect logger
    """
    prefect_logger = get_run_logger()
    sys.stdout = Logger(prefect_logger, level="info")
    sys.stderr = Logger(prefect_logger, level="error")
    return prefect_logger


@flow(name="Podman flow")
async def launch_podman_flow(
    image_name: str,
    image_tag: str,
    command: str = "python src/train.py /app/work/config/params.yaml",
    params: dict = {},
    volumes: list = [],
    network: str = "",
    env_vars: dict = {},
    parent_run_id: uuid.UUID = None,
):

    logger = setup_logger()

    if parent_run_id:
        # Append parent run id to parameters if provided
        params["uid"] = parent_run_id
    else:
        # Otherwise, append current flow run id
        params["uid"] = context.get_run_context().flow_run.id

    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        yaml.dump(params, temp_file)
        logger.info(f"Parameters file: {temp_file.name}")

        # Mount extra volume with parameters yaml file
        volumes += [f"{temp_file.name}:/app/work/config/params.yaml"]

        # Define podman command
        cmd = [
            "flows/podman/bash_run_podman.sh",
            f"{image_name}:{image_tag}",
            command,
            " ".join(volumes),
            network,
            " ".join(f"{k}={v}" for k, v in env_vars.items()),
        ]
        logger.info(f"Launching with command: {cmd}")
        process = await run_process(cmd, stream_output=True)

    if process.returncode != 0:
        return Failed(message="Podman command failed")
    pass
