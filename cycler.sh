#! /bin/bash 

# Check if halt file exists
if [[ -f halt ]]
then
    echo "Exiting..." && exit 0
fi

# Set up environmental variables
NODES=$(echo $SLURM_NNODES)
CPT=$(echo $SLURM_JOB_CPUS_PER_NODE)
JOBID=$(echo $SLURM_JOB_ID)
JOBNAME=$(echo $SLURM_JOB_NAME)

# Get prefix & iteration
META=`echo $JOBNAME | cut -d'-' -f3`
PREFIX=`echo $JOBNAME | cut -d'-' -f1`
ITERATION=`echo $JOBNAME | cut -d'-' -f2`
ITERATION=`echo $ITERATION | cut -d'-' -f1`
PREVITER=$((ITERATION - 1))
NEXTITER=$((ITERATION + 1))
echo "Jobname:" $JOBNAME

# Check that files from previous iteration exist
checkpoint=$(echo $PREFIX"_"$PREVITER".chk")
restart=$(echo $PREFIX"_"$PREVITER".xml")
trajectory=$(echo $PREFIX"_"$PREVITER".dcd")
if [[ ! -e "$checkpoint" ]]
then
    echo "An error occurred in iteration "$PREVITER". Exiting..." && exit 0
fi 
if [[ ! -e "$restart" ]]
then
    echo "An error occurred in iteration "$PREVITER". Exiting..." && exit 0
fi
if [[ ! -e "$trajectory" ]]
then
    echo "An error occurred in iteration "$PREVITER". Exiting..." && exit 0
fi

# Submit next job
NEXTJOBN=$(echo ${PREFIX}-${NEXTITER})
BNEXTJOB=$(echo $NEXTJOBN})

if [[ -v META ]]
then
    NEXTJOBN=$(echo ${NEXTJOBN}-$META)
fi

echo "Nodes:" $NODES "CPT:" $CPT "JobID:" $JOBID
echo "Partition:" $PARTITION "Time limit:" $TIMELIMIT "Memory:" $MEM "Driver:" $DRIVER
echo "Prefix:" $PREFIX "Current teration:" $ITERATION "Next iteration:" $NEXTITER

sbatch --partition $PARTITION --time $TIMELIMIT -c $CPT --overcommit --gres gpu:$NODES --mem $MEM --job-name $NEXTJOBN --dependency afterany:$JOBID --error $NEXTJOBN.err --output $NEXTJOBN.out $DRIVER

# Start current job
dhm=$(date +%k%M) # date hour minute
scontrol show jobid -dd $SLURM_JOB_ID > slurm-${SLURM_JOB_ID}_${dhm}.jobinfo
nvidia-smi -q -g 0 -d UTILIZATION > nvidia-${SLURM_JOB_ID}_${dhm}.jobinfo

module load cuda/9.0 gcc
module load openmm/7.2.1

python ${PREFIX}.py ${PREFIX} ${ITERATION}

exit 0
