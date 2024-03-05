#!/bin/bash

# Check if all arguments are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <conda_environment> <python_file> <yaml_file>"
    exit 1
fi

# Assign arguments to variables
conda_environment=$1
python_file=$2
yaml_file=$3

# Activate the conda environment
source activate $conda_environment

echo Calling model with:    python $python_file $yaml_file

# Call python with the python file and yaml file as arguments
python $python_file $yaml_file

# Deactivate the conda environment
conda deactivate