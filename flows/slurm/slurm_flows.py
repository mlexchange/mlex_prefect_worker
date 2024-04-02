# TODO: Check pyslurm: https://github.com/PySlurm/pyslurm/tree/main
import sys
import tempfile

import yaml
from prefect import context, flow, get_run_logger
from prefect.states import Failed
from prefect.utilities.processutils import run_process

from flows.slurm.schema import SlurmParams


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


@flow(name="launch_slurm")
async def launch_slurm(
    slurm_params: SlurmParams,
    prev_flow_run_id: str = None,
):
    logger = setup_logger()

    if prev_flow_run_id:
        # Append the previous flow run id to parameters if provided
        slurm_params.params["io_parameters"]["uid_retrieve"] = prev_flow_run_id

    current_flow_run_id = str(context.get_run_context().flow_run.id)

    # Append current flow run id
    slurm_params.params["io_parameters"]["uid_save"] = current_flow_run_id

    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        yaml.dump(slurm_params.params, temp_file)
        # Define conda command
        cmd = [
            "flows/slurm/run_slurm.sh",
            slurm_params.job_name,
            str(slurm_params.num_nodes),
            ",".join(slurm_params.partitions),
            ",".join(slurm_params.reservations),
            slurm_params.max_time,
            slurm_params.conda_env_name,
            slurm_params.python_file_name,
            temp_file.name,
        ]
        logger.info(f"Launching with command: {cmd}")
        process = await run_process(cmd, stream_output=True)

    if process.returncode != 0:
        return Failed(message="Podman command failed")
    pass

    return current_flow_run_id
