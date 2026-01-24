"""
Registration pipeline for 7T LC quantification.

This script handles the computationally expensive registration step for batch
processing on HPC clusters (SLURM/Apptainer). Each subject is registered to
MNI space independently.

Extraction (CNR computation) is handled separately in Notebook 04, which:
- Loads the atlas once
- Loops through all registered subjects
- Computes CNR and saves results

This separation is intentional: registration is CPU-intensive and parallelizes
well across SLURM array jobs, while extraction is fast and benefits from
loading the atlas only once.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add project root to path (assuming script is in src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DEFAULT_CONFIG
from src.io import ensure_output_dirs, load_nifti
from src.preprocessing import register_subject, get_mni_template
from src.visualization import plot_registration_qc

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="7T LC Pipeline Runner")
    parser.add_argument("--subject", required=True, help="Subject ID (e.g., sub-0001)")
    parser.add_argument("--skip_registration", action="store_true", help="Skip registration if already done")
    args = parser.parse_args()

    sub_id = args.subject
    logger.info(f"Starting pipeline for {sub_id}")
    
    # 1. Setup & Checks
    config = DEFAULT_CONFIG
    ensure_output_dirs(config)
    
    # Define subject-specific output directory
    sub_output_dir = config.output_dir / sub_id
    sub_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Registration (The heavy lifting)
    # Check if registration outputs already exist
    t1w_mni_path = sub_output_dir / f"{sub_id}_T1w_MNI.nii.gz"
    
    if args.skip_registration and t1w_mni_path.exists():
        logger.info(f"Skipping registration for {sub_id} (found existing output)")
        reg_results = {
            'success': True,
            'T1w_MNI': t1w_mni_path,
            # We assume other contrasts exist if T1w exists for now
        }
    else:
        logger.info(f"Running ANTs registration for {sub_id}...")
        try:
            # Load template
            fixed = get_mni_template() 
            
            # Run registration
            reg_results = register_subject(sub_id, fixed, config)
            
            if not reg_results['success']:
                logger.error(f"Registration failed for {sub_id}")
                sys.exit(1)
                
            logger.info("Registration completed successfully")
            
            # QC Plot
            qc_path = config.figures_dir / f"{sub_id}_registration_qc.png"
            warped_t1w = load_nifti(reg_results['T1w_MNI'])
            plot_registration_qc(warped_t1w, sub_id, qc_path)
            logger.info(f"QC plot saved to {qc_path}")
            
        except Exception as e:
            logger.exception(f"Registration crashed: {e}")
            sys.exit(1)

    # Extraction is done post-hoc in Notebook 04 after all subjects complete.
    # This is more efficient: load atlas once, loop through all subjects.

    logger.info(f"Registration pipeline finished for {sub_id}")

if __name__ == "__main__":
    main()
