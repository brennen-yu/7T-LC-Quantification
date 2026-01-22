"""
Centralized configuration for the 7T LC Quantification pipeline.

Usage:
    from src.config import DEFAULT_CONFIG, PipelineConfig

    # Use defaults
    config = DEFAULT_CONFIG

    # Or customize
    config = PipelineConfig(lc_probability_threshold=0.3)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class PipelineConfig:
    """Configuration for the LC quantification pipeline."""

    # Paths (relative to project root)
    data_dir: Path = field(default_factory=lambda: Path("data"))
    output_dir: Path = field(default_factory=lambda: Path("outputs/results"))
    figures_dir: Path = field(default_factory=lambda: Path("outputs/figures"))
    atlas_dir: Path = field(default_factory=lambda: Path("atlases"))

    # Atlas files
    lc_atlas_filename: str = "LC_prob_MNI.nii.gz"
    reference_roi_filename: str = "pontine_reference_MNI.nii.gz"

    # Thresholds
    lc_probability_threshold: float = 0.5

    # Reference region defaults (geometric fallback)
    reference_center_mni: Tuple[float, float, float] = (0.0, -30.0, -28.0)
    reference_radius_mm: float = 3.0

    # Registration parameters (ANTs SyN)
    registration_type: str = "SyN"
    syn_metric: str = "CC"
    syn_sampling: int = 4
    reg_iterations: Tuple[int, ...] = (100, 70, 50, 20)

    # Contrast patterns for BIDS discovery
    contrast_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        "T1w": ["T1w.nii.gz", "UNIT1.nii.gz"],
        "R1": ["R1map.nii.gz", "R1.nii.gz"],
        "R2star": ["R2starmap.nii.gz", "R2star.nii.gz"],
        "QSM": ["QSM.nii.gz", "Chimap.nii.gz"],
        "T2starw": ["T2starw.nii.gz"],
    })

    @property
    def lc_atlas_path(self) -> Path:
        """Full path to LC atlas file."""
        return self.atlas_dir / self.lc_atlas_filename

    @property
    def reference_roi_path(self) -> Path:
        """Full path to reference ROI file."""
        return self.atlas_dir / self.reference_roi_filename


# Default instance for easy import
DEFAULT_CONFIG = PipelineConfig()
