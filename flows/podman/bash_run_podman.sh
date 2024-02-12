#!/bin/bash

# Check if an argument was provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <image_uri> <command>"
    exit 1
fi

image_uri=$1
command=$2

# Run the Podman container
podman run "$image_uri" /bin/sh -c "$command"

# Check if the Podman command was successful
if [ "$?" -ne 0 ]; then
    echo "Failed to run Podman container"
    exit 1
fi

echo "Successfully launched Podman container"