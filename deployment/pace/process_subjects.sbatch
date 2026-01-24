#!/bin/bash
#SBATCH --job-name=LC_Quant
#SBATCH -N1 --ntasks-per-node=1          # 1 node, 1 process (ANTs is multi-threaded, not distributed)
#SBATCH --cpus-per-task=4                # ANTs benefits from multi-core
#SBATCH --mem=16G                        # 7T data is large
#SBATCH --time=02:00:00                  # 2 hours per subject should be plenty
#SBATCH --array=0-104                    # Array for subjects sub-0000 to sub-0104
#SBATCH --output=logs/%x_%A_%a.out       # Standard output logging
#SBATCH --error=logs/%x_%A_%a.err        # Error logging
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences

# ---------------------------------------------------------------------
# PACE SLURM Script for 7T LC Quantification
# ---------------------------------------------------------------------

# 1. Environment Setup
# Apptainer is typically available by default on ICE compute nodes
# module load apptainer                  # Uncomment if 'apptainer' command is not found

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
