#!/bin/bash
#SBATCH --job-name=LC_Quant
#SBATCH -N1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --array=0-104
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.err
#SBATCH --mail-type=BEGIN,END,FAIL

# ---------------------------------------------------------------------
# PACE SLURM Script for 7T LC Quantification
# ---------------------------------------------------------------------

# 1. Environment Setup
# Apptainer is typically available by default on ICE compute nodes
# module load apptainer                  # Uncomment if 'apptainer' command is not found

# Configure Apptainer to use Scratch for tmp/cache (Fixes 'container_p_join' errors)
export APPTAINER_TMPDIR=$SLURM_SUBMIT_DIR/tmp
export APPTAINER_CACHEDIR=$SLURM_SUBMIT_DIR/cache
mkdir -p $APPTAINER_TMPDIR
mkdir -p $APPTAINER_CACHEDIR

# Define paths
PROJECT_DIR=$SLURM_SUBMIT_DIR
SIF_IMAGE="$PROJECT_DIR/lc_pipeline.sif"
DATA_DIR="$PROJECT_DIR/data/bids_input"
OUTPUT_DIR="$PROJECT_DIR/outputs"        # Bind parent so both results/ and figures/ are accessible
ATLAS_DIR="$PROJECT_DIR/atlases"

# 2. Derive Subject ID from Array Task ID
# This turns "0" into "sub-0000", "25" into "sub-0025", "104" into "sub-0104"
SUB_ID=$(printf "sub-%04d" $SLURM_ARRAY_TASK_ID)

echo "Starting job for $SUB_ID on $(hostname)"
echo "Time: $(date)"

# Tell ANTs/ITK how many threads to use (matches --cpus-per-task)
# APPTAINERENV_ prefix passes these into the container
export APPTAINERENV_ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=$SLURM_CPUS_PER_TASK
export APPTAINERENV_OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# 3. Create Subject Output Directory (inside results/ and figures/)
mkdir -p "$OUTPUT_DIR/results/$SUB_ID"
mkdir -p "$OUTPUT_DIR/figures"

# 4. Run the Pipeline inside Apptainer
# We bind mount:
#   - local data -> /data
#   - local outputs -> /outputs
#   - local atlases -> /atlases
# This ensures the container sees the HPC files at the expected internal paths.

srun apptainer exec \
    --bind "$DATA_DIR":/data \
    --bind "$OUTPUT_DIR":/outputs \
    --bind "$ATLAS_DIR":/atlases \
    "$SIF_IMAGE" \
    python src/pipeline_runner.py --subject "$SUB_ID"

echo "Finished job for $SUB_ID"
