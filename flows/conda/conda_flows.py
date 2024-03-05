import sys
import tempfile
import yaml
from prefect import flow, get_run_logger
from prefect.utilities.processutils import run_process


class Logger:
    def __init__(self, logger, level="info"):
        self.logger = getattr(logger, level)

    def write(self, message):
        if message != '\n':
            self.logger(message)

    def flush(self):
        pass


def setup_logger():
    '''
    Adopt stdout and stderr to prefect logger
    '''
    prefect_logger = get_run_logger()
    sys.stdout = Logger(prefect_logger, level="info")
    sys.stderr = Logger(prefect_logger, level="error")
    return prefect_logger


@flow(name="launch_conda")
async def launch_conda(
    conda_env_name: str,
    python_file_name: str = "../mlex_dlsia_segmentation_prototype/src/train.py",
    params: dict = {}
):

    logger = setup_logger()
    # logger = get_run_logger()
    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode='w+t') as temp_file:
        yaml.dump(params, temp_file)
        # Define podman command
        cmd = [
            'flows/conda/run_conda.sh',
            conda_env_name,
            python_file_name,
            temp_file.name
            ]
        logger.info(f"Launching with command: {cmd}")
        await run_process(cmd, stream_output=True)


if __name__ == "__main__":
    import asyncio
    asyncio.run(launch_conda("dlsia", params={"foo": "bar"}))
