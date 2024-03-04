from enum import Enum

from prefect import context, flow, get_run_logger

from flows.podman.podman_flows import launch_podman_flow


class FlowType(str, Enum):
    podman = "podman"
    slurm = "slurm"


@flow(name="Parent flow")
async def launch_parent_flow(
    flow_type: FlowType,
    params_list: list[dict],
):
    prefect_logger = get_run_logger()
    flow_run_id = context.get_run_context().flow_run.id

    for params in params_list:
        if flow_type == FlowType.podman:
            await launch_podman_flow(parent_run_id=flow_run_id, **params)
        elif flow_type == FlowType.slurm:
            pass
        else:
            prefect_logger.error("Flow type not supported")
            raise ValueError("Flow type not supported")

    pass
