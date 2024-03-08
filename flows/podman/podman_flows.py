import sys
import tempfile

import yaml
from prefect import context, flow, get_run_logger
from prefect.states import Failed
from prefect.utilities.processutils import run_process

from flows.podman.schema import PodmanParams


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
async def launch_podman(
    podman_params: PodmanParams,
    prev_flow_run_id: str = None,
):
    logger = setup_logger()

    if prev_flow_run_id:
        # Append the previous flow run id to parameters if provided
        podman_params.params["io_parameters"]["uid_retrieve"] = prev_flow_run_id

    current_flow_run_id = str(context.get_run_context().flow_run.id)

    # Append current flow run id
    podman_params.params["io_parameters"]["uid_save"] = current_flow_run_id

    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        yaml.dump(podman_params.params, temp_file)
        logger.info(f"Parameters file: {temp_file.name}")

        # Mount extra volume with parameters yaml file
        volumes = podman_params.volumes + [
            f"{temp_file.name}:/app/work/config/params.yaml"
        ]
        command = f"{podman_params.command} /app/work/config/params.yaml"

        # Define podman command
        cmd = [
            "flows/podman/bash_run_podman.sh",
            f"{podman_params.image_name}:{podman_params.image_tag}",
            command,
            " ".join(volumes),
            podman_params.network,
            " ".join(f"{k}={v}" for k, v in podman_params.env_vars.items()),
        ]
        logger.info(f"Launching with command: {cmd}")
        process = await run_process(cmd, stream_output=True)

    if process.returncode != 0:
        return Failed(message="Podman command failed")

    return current_flow_run_id
