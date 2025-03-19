#!/bin/bash

# Load environment variables from .env file
source .env

echo "Executing Folder: ${PWD}"
# Initialize conda
source "$CONDA_PATH/etc/profile.d/conda.sh"

# Start the worker command in the background, capture its PID, and assign the log file
(
    export PREFECT_WORK_DIR=$PREFECT_WORK_DIR
    prefect config set PREFECT_API_URL=$PREFECT_API_URL

    prefect work-pool create mlex_pool --type "process"
    prefect work-pool set-concurrency-limit mlex_pool $PREFECT_WORK_POOL_CONCURRENCY
    prefect deploy --all

    # Create a log file
    log_file="process$$.log"

    # Start the worker process, redirecting stdout and stderr to a temporary log file
    prefect worker start --pool mlex_pool --limit $PREFECT_WORKER_LIMIT --with-healthcheck &> "process_temp.log" &
    pid_worker=$!

    # Rename the log file to include the actual PID of the worker process
    log_file="process${pid_worker}.log"
    mv "process_temp.log" "$log_file"

    echo "Started Prefect worker with PID: $pid_worker and logging to $log_file"
)
