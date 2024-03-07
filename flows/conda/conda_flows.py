import sys
import tempfile
import uuid

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
    parent_run_id: uuid.UUID = None,
):

    logger = setup_logger()

    if parent_run_id:
        # Append parent run id to parameters if provided
        conda_params.model_params["io_parameters"]["uid"] = parent_run_id
    else:
        # Otherwise, append current flow run id
        conda_params.model_params["io_parameters"][
            "uid"
        ] = context.get_run_context().flow_run.id

    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        yaml.dump(conda_params.model_params, temp_file)
        # Define conda command
        cmd = [
            "flows/conda/run_conda.sh",
            conda_params.conda_env_name,
            conda_params.python_file_name,
            temp_file.name,
        ]
        logger.info(f"Launching with command: {cmd}")
        await run_process(cmd, stream_output=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(launch_conda("dlsia", params={"foo": "bar"}))
