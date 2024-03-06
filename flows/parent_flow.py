from enum import Enum
from typing import Union

from prefect import context, flow, get_run_logger

from flows.conda.conda_flows import launch_conda
from flows.conda.schema import CondaParams
from flows.podman.podman_flows import launch_podman
from flows.podman.schema import PodmanParams


class FlowType(str, Enum):
    podman = "podman"
    conda = "conda"


@flow(name="Parent flow")
async def launch_parent_flow(
    flow_type: FlowType,
    params_list: list[Union[PodmanParams, CondaParams]],
):
    prefect_logger = get_run_logger()
    flow_run_id = context.get_run_context().flow_run.id

    for params in params_list:
        if flow_type == FlowType.podman:
            await launch_podman(parent_run_id=flow_run_id, podman_params=params)
        elif flow_type == FlowType.conda:
            await launch_conda(parent_run_id=flow_run_id, conda_params=params)
        else:
            prefect_logger.error("Flow type not supported")
            raise ValueError("Flow type not supported")

    pass
