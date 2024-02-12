import subprocess
from prefect import flow, get_run_logger


@flow(name="Podman flow")
def launch_podman_flow(
    image_name: str,
    image_tag: str,
    command: str
    ):

    logger = get_run_logger()

    cmd = ['flows/podman/bash_run_podman.sh', f'{image_name}:{image_tag}', command]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Log the output of the command
    for line in process.stdout:
        logger.info(line.decode())
    
    # Log the error of the command
    for line in process.stderr:
        logger.error(line.decode())
    
    # Close the file descriptors
    process.stderr.close()
    process.stdout.close()
    
    # Wait for the process to finish
    return_code = process.wait()

    # Raise an exception if the return code is not 0
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
    return return_code