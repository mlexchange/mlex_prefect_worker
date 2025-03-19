from enum import Enum

from prefect import flow, get_run_logger

from flows.conda.conda_flows import launch_conda
from flows.docker.docker_flows import launch_docker
from flows.podman.podman_flows import launch_podman
from flows.slurm.slurm_flows import launch_slurm


class FlowType(str, Enum):
    podman = "podman"
    conda = "conda"
    slurm = "slurm"
    docker = "docker"


@flow(name="Parent flow")
async def launch_parent_flow(
    flow_type: FlowType,
    params_list: list[dict],
):
    prefect_logger = get_run_logger()

    flow_run_id = ""
    for params in params_list:
        if flow_type == FlowType.podman:
            flow_run_id = await launch_podman(
                podman_params=params, prev_flow_run_id=flow_run_id
            )
        elif flow_type == FlowType.conda:
            flow_run_id = await launch_conda(
                conda_params=params, prev_flow_run_id=flow_run_id
            )
        elif flow_type == FlowType.slurm:
            flow_run_id = await launch_slurm(
                slurm_params=params, prev_flow_run_id=flow_run_id
            )
        elif flow_type == FlowType.docker:
            flow_run_id = await launch_docker(
                docker_params=params, prev_flow_run_id=flow_run_id
            )
        else:
            prefect_logger.error("Flow type not supported")
            raise ValueError("Flow type not supported")

    pass
