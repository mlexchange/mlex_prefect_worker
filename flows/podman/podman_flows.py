import subprocess
from prefect import flow


@flow(name="Podman flow")
def launch_podman_flow(
    image_name: str,
    image_tag: str,
    command: str
    ):

    cmd = ['flows/podman/bash_run_podman.sh', f'{image_name}:{image_tag}', command]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f'Failed to run Podman command: {result.stderr}')

    return result.stdout.strip()