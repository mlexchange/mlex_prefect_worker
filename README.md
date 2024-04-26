# mlex_prefect_worker

This repository contains the necessary scripts and configuration files to start a Prefect process worker with conda, Podman and Slurm flows.

## Getting Started

1. Create a conda environment with the required packages:

    ```bash
    conda create --name myenv python=3.11
    ```

2. Activate the conda environment:

    ```bash
    conda activate myenv
    ```

3. Install the package. This will install dependencies.

    ```bash
    python -m pip install .
    ```

4. Change permissions for the shell scripts to make them executable:

    ```bash
    chmod +x start_worker.sh
    chmod +x flows/podman/bash_run_podman.sh
    ```

5. Run the `start_worker.sh` script to start the Prefect worker:

    ```bash
    ./start_worker.sh
    ```

## Copyright
MLExchange Copyright (c) 2024, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of
any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at
IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative 
works, and perform publicly and display publicly, and to permit others to do so.
