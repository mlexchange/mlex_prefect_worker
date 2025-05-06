import tempfile
import docker
import yaml
from prefect import context, flow
from prefect.states import Failed

from flows.docker.schema import DockerParams
from flows.logger import setup_logger


@flow(name="Docker flow")
async def launch_docker(
    docker_params: DockerParams,
    prev_flow_run_id: str = "",
):
    logger = setup_logger()

    if (
        prev_flow_run_id != ""
        and docker_params.params["io_parameters"]["uid_retrieve"] == ""
    ):
        # Append the previous flow run id to parameters if provided
        docker_params.params["io_parameters"]["uid_retrieve"] = prev_flow_run_id

    current_flow_run_id = str(context.get_run_context().flow_run.id)

    # Append current flow run id
    docker_params.params["io_parameters"]["uid_save"] = current_flow_run_id

    # Create temporary file for parameters
    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        yaml.dump(docker_params.params, temp_file)
        temp_file.flush()  # Ensure data is written to disk
        logger.info(f"Parameters file: {temp_file.name}")

        # Prepare volume bindings
        volumes = {}
        for volume in docker_params.volumes:
            host_path, container_path = volume.split(":", 1)
            volumes[host_path] = {"bind": container_path, "mode": "rw"}
        
        # Add the parameters file volume
        volumes[temp_file.name] = {"bind": "/app/work/config/params.yaml", "mode": "ro"}
        
        # Prepare the command
        command = f"{docker_params.command} /app/work/config/params.yaml"
        
        # Initialize Docker client
        client = docker.from_env()
        
        try:
            logger.info(f"Running container from {docker_params.image_name}:{docker_params.image_tag}")
            
            # Run the container
            container = client.containers.run(
                image=f"{docker_params.image_name}:{docker_params.image_tag}",
                command=["/bin/sh", "-c", command],
                volumes=volumes,
                environment=docker_params.env_vars,
                network=docker_params.network if docker_params.network else None,
                detach=True,  # Run in background
            )
            
            # Stream logs
            for log in container.logs(stream=True, follow=True):
                logger.info(log.decode().strip())
            
            # Wait for container to complete
            result = container.wait()
            
            # Get the exit code
            exit_code = result.get("StatusCode", -1)
            
            # Remove the container
            container.remove()
            
            if exit_code != 0:
                return Failed(message=f"Docker container exited with code {exit_code}")
                
        except docker.errors.APIError as e:
            logger.error(f"Docker API error: {e}")
            return Failed(message=f"Docker API error: {e}")
        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {e}")
            return Failed(message=f"Container error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Failed(message=f"Unexpected error: {e}")

    return current_flow_run_id
