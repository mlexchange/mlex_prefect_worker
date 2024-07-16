import asyncio
from typing import Optional

from prefect import get_client


async def _schedule(
    deployment_name: str,
    flow_run_name: str,
    parameters: Optional[dict] = None,
    tags: Optional[list] = [],
):
    async with get_client() as client:
        deployment = await client.read_deployment_by_name(deployment_name)
        assert (
            deployment
        ), f"No deployment found in config for deployment_name {deployment_name}"
        flow_run = await client.create_flow_run_from_deployment(
            deployment.id,
            parameters=parameters,
            name=flow_run_name,
            tags=tags,
        )
    return flow_run.id


def schedule_prefect_flow(
    deployment_name: str,
    parameters: Optional[dict] = None,
    flow_run_name: Optional[str] = None,
    tags: Optional[list] = [],
):
    if not flow_run_name:
        model_name = parameters["model_name"]
        flow_run_name = f"{deployment_name}: {model_name}"
    flow_run_id = asyncio.run(
        _schedule(deployment_name, flow_run_name, parameters, tags)
    )
    return flow_run_id


if __name__ == "__main__":
    deployment_name = "launch_conda/launch_conda"
    parameters = {
        "conda_params": {
            "conda_env_name": "tiled_test",
            "python_file_name": "examples/example_job.py",
            "params": {
                "io_parameters": {
                    "uid_retrieve": "example123",
                    "uid_save": "example456",
                }
            },
        }
    }
    flow_run_id = schedule_prefect_flow(deployment_name, parameters, "example_job")
    print(flow_run_id)
