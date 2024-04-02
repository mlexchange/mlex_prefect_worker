#!/bin/bash

# Check if all arguments are provided
if [ $# -ne 8 ]; then
    echo "Usage: $0 <job_name> <num_nodes> <partitions> <reservations> <max_time> <conda_env> <python_file> <yaml_file>"
    exit 1
fi

# Assign arguments to variables
job_name=$1
num_nodes=$2
partitions=$3
reservations=$4
max_time=$5
conda_env=$6
python_file=$7
yaml_file=$8

# Create a temporary Slurm batch script
BATCH_SCRIPT=$(mktemp)

# Write the Slurm batch script
echo "#!/bin/bash" > $BATCH_SCRIPT

if [ "$partitions" = "" ]
then
    echo "Partitions is unset or empty"
else
    echo "#SBATCH --partition=$partitions" >> $BATCH_SCRIPT
fi

if [ "$reservations" = "" ]
then
    echo "Reservations is unset or empty"
else
    echo "#SBATCH --reservation=$reservations" >> $BATCH_SCRIPT
fi

echo "#SBATCH --nodes=$num_nodes" >> $BATCH_SCRIPT
echo "#SBATCH --job-name=$job_name" >> $BATCH_SCRIPT
echo "#SBATCH --time=$max_time" >> $BATCH_SCRIPT
echo "module load python" >> $BATCH_SCRIPT
echo "conda activate $conda_env" >> $BATCH_SCRIPT
echo "srun python $python_file $yaml_file" >> $BATCH_SCRIPT

# Submit the Slurm batch script and capture the job ID
JOB_ID=$(sbatch $BATCH_SCRIPT | awk '{print $4}')

# Remove the temporary Slurm batch script
rm $BATCH_SCRIPT

# Print the job ID
echo "Submitted job with ID $JOB_ID"

# Track the progress of the job
while true; do
    # Get the job status
    JOB_STATUS=$(sacct -j $JOB_ID --format=State --noheader | head -1 | awk '{print $1}')

    if [[ $JOB_STATUS == *"COMPLETED"* ]]; then
        # If the job is completed, break the loop
        echo "Job $JOB_ID has completed"
        break
    elif [[ $JOB_STATUS == *"FAILED"* ]]; then
        # If the job has failed, print an error message and exit with a non-zero status
        echo "Job $JOB_ID has failed" >&2
        exit 1
    else
        # If the job is neither completed nor failed, print its status
        echo "Job $JOB_ID is $JOB_STATUS"
    fi
    sleep 10
done
