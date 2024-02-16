from prefect import flow, get_run_logger
from prefect.utilities.processutils import run_process
import sys


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


@flow(name="Podman flow")
async def launch_podman_flow(
    image_name: str,
    image_tag: str,
    command: str,
    volumes: list = [],
    network: str = "",
    env_vars: dict = {},
    ):

    logger = setup_logger()

    cmd = [
        'flows/podman/bash_run_podman.sh',
        f'{image_name}:{image_tag}',
        command,
        ' '.join(volumes),
        network,
        ' '.join(f'{k}={v}' for k, v in env_vars.items())
        ]
    process = await run_process(cmd, stream_output=True)

    pass