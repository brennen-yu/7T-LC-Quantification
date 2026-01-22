"""
7T LC Quantification Pipeline

A pipeline for atlas-based locus coeruleus (LC) localization and
signal extraction from 7T quantitative MRI data.

Example usage:
    from src import DEFAULT_CONFIG, load_nifti, compute_cnr

    config = DEFAULT_CONFIG
    lc_atlas = load_nifti(config.lc_atlas_path)
    # ...
"""

# Configuration
from .config import DEFAULT_CONFIG, PipelineConfig

# I/O utilities
from .io import (
    ensure_output_dirs,
    find_bids_files,
    find_contrast_file,
    list_processed_subjects,
    list_subjects,
    load_nifti,
)

# Preprocessing
from .preprocessing import (
    apply_transforms,
    get_mni_template,
    register_subject,
    register_to_mni,
)

# ROI utilities
from .roi import (
    create_pontine_reference_roi,
    load_or_create_reference_roi,
    threshold_probabilistic_atlas,
)

# Signal extraction
from .extraction import (
    compute_cnr,
    extract_roi_stats,
    extract_subject_cnr,
)

# Visualization
from .visualization import (
    plot_cnr_summary,
    plot_contrast_comparison,
    plot_registration_qc,
    plot_roi_overlay,
    plot_slice_visualization,
)

__all__ = [
    # Config
    "DEFAULT_CONFIG",
    "PipelineConfig",
    # I/O
    "load_nifti",
    "find_bids_files",
    "find_contrast_file",
    "ensure_output_dirs",
    "list_subjects",
    "list_processed_subjects",
    # Preprocessing
    "register_to_mni",
    "apply_transforms",
    "register_subject",
    "get_mni_template",
    # ROI
    "create_pontine_reference_roi",
    "load_or_create_reference_roi",
    "threshold_probabilistic_atlas",
    # Extraction
    "extract_roi_stats",
    "compute_cnr",
    "extract_subject_cnr",
    # Visualization
    "plot_roi_overlay",
    "plot_slice_visualization",
    "plot_contrast_comparison",
    "plot_registration_qc",
    "plot_cnr_summary",
]
