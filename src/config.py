"""
Centralized configuration for the 7T LC Quantification pipeline.

Usage:
    from src.config import DEFAULT_CONFIG, PipelineConfig

    # Use defaults (auto-detects container vs local)
    config = DEFAULT_CONFIG

    # Or customize
    config = PipelineConfig(lc_probability_threshold=0.3)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


def _in_container() -> bool:
    """
    Detect if running inside Apptainer/Docker container with standard bind mounts.
    Checks if /data and /outputs exist AND if /outputs is writable.
    """
    data_path = Path("/data")
    out_path = Path("/outputs")
    
    if data_path.is_dir() and out_path.is_dir():
        # Check writability of /outputs to distinguish 'our' container from generic read-only ones
        return os.access(out_path, os.W_OK)
        
    return False


def _get_project_root() -> Path:
    """Get project root for local development."""
    return Path(__file__).resolve().parent.parent


def _get_data_dir() -> Path:
    if _in_container():
        return Path("/data")
    return _get_project_root() / "data/bids_input"


def _get_output_dir() -> Path:
    if _in_container():
        return Path("/outputs/results")
    return _get_project_root() / "outputs/results"


def _get_figures_dir() -> Path:
    if _in_container():
        return Path("/outputs/figures")
    return _get_project_root() / "outputs/figures"


def _get_atlas_dir() -> Path:
    if _in_container():
        return Path("/atlases/ye_2021/LC_7T_prob")
    return _get_project_root() / "atlases/ye_2021/LC_7T_prob"


def _get_reg_iterations() -> Tuple[int, ...]:
    """
    Get registration iterations from environment variable or default.

    Env var: ANTS_REG_ITERATIONS
    Example: "10,0,0" (Fast Debug Mode) vs "100,70,50,20" (Production)
    """
    env_val = os.environ.get("ANTS_REG_ITERATIONS")
    if env_val:
        try:
            return tuple(int(x.strip()) for x in env_val.split(","))
        except ValueError:
            raise ValueError(
                f"Invalid ANTS_REG_ITERATIONS='{env_val}'. "
                "Expected comma-separated integers (e.g., '10,0,0')."
            )

    # Default: Production Settings
    return (100, 70, 50, 20)


@dataclass
class PipelineConfig:
    """Configuration for the LC quantification pipeline.

    Paths are auto-detected based on environment:
    - Container mode: Uses /data, /outputs, /atlases bind mount points
    - Local mode: Uses paths relative to project root
    """

    # Paths (auto-detected based on environment)
    data_dir: Path = field(default_factory=_get_data_dir)
    output_dir: Path = field(default_factory=_get_output_dir)
    figures_dir: Path = field(default_factory=_get_figures_dir)
    atlas_dir: Path = field(default_factory=_get_atlas_dir)

    # Atlas files
    lc_atlas_filename: str = "LCTMP_n53_5SD_prob25.nii.gz"
    reference_roi_filename: str = "pontine_reference_MNI.nii.gz"
    mni_template_filename: str = "mni_icbm152_t1_tal_nlin_asym_09b_hires_FSL_bbox_struc_brain_CSFin.nii"

    # Thresholds
    lc_probability_threshold: float = 0.5

    # Reference region defaults (geometric fallback)
    reference_center_mni: Tuple[float, float, float] = (0.0, -30.0, -28.0)
    reference_radius_mm: float = 3.0

    # Registration parameters (ANTs SyN)
    registration_type: str = "SyN"
    syn_metric: str = "CC"
    syn_sampling: int = 4
    
    # Iterations: Default to Production, but allow ENV override
    reg_iterations: Tuple[int, ...] = field(default_factory=_get_reg_iterations)

    # Contrast patterns for BIDS discovery (Updated for AHEAD dataset filenames)
    contrast_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        "T1w": ["mod-t1w_orient-std_brain.nii.gz"],
        "R1": ["mod-r1map_orient-std_brain.nii.gz"],
        "R2star": ["mod-r2starmap_orient-std_brain.nii.gz"],
        "QSM": ["mod-qsm_orient-std_brain.nii.gz"],
        "T2starw": ["mod-t2starmap_orient-std_brain.nii.gz"],
        "T1map": ["mod-t1map_orient-std_brain.nii.gz"],
    })

    @property
    def lc_atlas_path(self) -> Path:
        """Full path to LC atlas file."""
        return self.atlas_dir / self.lc_atlas_filename

    @property
    def reference_roi_path(self) -> Path:
        """Full path to reference ROI file."""
        return self.atlas_dir / self.reference_roi_filename

    @property
    def mni_template_path(self) -> Path:
        """Full path to MNI template file."""
        return self.atlas_dir / self.mni_template_filename



# Default instance for easy import
DEFAULT_CONFIG = PipelineConfig()
