import sys
import tempfile

import yaml
from prefect import context, flow, get_run_logger
from prefect.utilities.processutils import run_process

from flows.conda.schema import CondaParams


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


@flow(name="launch_conda")
async def launch_conda(
    conda_params: CondaParams,
    prev_flow_run_id: str = None,
):
    logger = setup_logger()

    if prev_flow_run_id is None and conda_params.params["io_parameters"]["uid_retrieve"] is None:
        # Append the previous flow run id to parameters if provided
        conda_params.params["io_parameters"]["uid_retrieve"] = prev_flow_run_id

    current_flow_run_id = str(context.get_run_context().flow_run.id)

    # Append current flow run id
    conda_params.params["io_parameters"]["uid_save"] = current_flow_run_id

    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        yaml.dump(conda_params.params, temp_file)
        # Define conda command
        cmd = [
            "flows/conda/run_conda.sh",
            conda_params.conda_env_name,
            conda_params.python_file_name,
            temp_file.name,
        ]
        logger.info(f"Launching with command: {cmd}")
        await run_process(cmd, stream_output=True)

    return current_flow_run_id


if __name__ == "__main__":
    import asyncio

    asyncio.run(launch_conda("dlsia", params={"foo": "bar"}))
