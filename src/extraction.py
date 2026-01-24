"""
Signal extraction and CNR computation for the 7T LC Quantification pipeline.
"""

from typing import Dict, Optional, TYPE_CHECKING

import nibabel as nib
import numpy as np
from nilearn import image

if TYPE_CHECKING:
    from .config import PipelineConfig


def extract_roi_stats(
    data_img: nib.Nifti1Image,
    roi_mask_img: nib.Nifti1Image,
    threshold: Optional[float] = None,
    config: Optional["PipelineConfig"] = None,
) -> Dict[str, float]:
    """
    Extract statistics from an ROI.

    Args:
        data_img: Data image (e.g., R2* map).
        roi_mask_img: ROI mask (binary or probabilistic).
        threshold: Probability threshold for mask. If None, uses config default.
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.

    Returns:
        Dict with mean, std, median, min, max, voxel_count.

    Raises:
        ValueError: If ROI has no valid (finite) voxels after masking.
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    threshold = threshold if threshold is not None else config.lc_probability_threshold

    # Resample mask to data space if necessary
    if data_img.shape != roi_mask_img.shape:
        roi_mask_img = image.resample_to_img(
            roi_mask_img, data_img, interpolation="nearest"
        )

    data = data_img.get_fdata()
    mask = roi_mask_img.get_fdata()

    # Threshold probabilistic mask to binary
    binary_mask = mask > threshold

    # Extract values and filter NaN/Inf
    roi_values = data[binary_mask]
    roi_values = roi_values[np.isfinite(roi_values)]

    if len(roi_values) == 0:
        raise ValueError(
            f"No valid voxels in ROI (threshold={threshold}, "
            f"mask voxels={binary_mask.sum()}, finite values=0)"
        )

    return {
        "mean": float(np.mean(roi_values)),
        "std": float(np.std(roi_values)),
        "median": float(np.median(roi_values)),
        "min": float(np.min(roi_values)),
        "max": float(np.max(roi_values)),
        "voxel_count": int(len(roi_values)),
    }


def compute_cnr(
    data_img: nib.Nifti1Image,
    lc_mask: np.ndarray,
    ref_mask: np.ndarray,
) -> Dict[str, float]:
    """
    Compute contrast-to-noise ratio between LC and reference region.

    CNR = (mean_LC - mean_ref) / std_ref

    This is the standard definition used in neuromelanin-sensitive MRI literature.
    A CNR near 0 indicates no meaningful contrast between LC and the reference.

    Args:
        data_img: Data image (e.g., R1 map in MNI space).
        lc_mask: Binary LC mask array (same shape as data_img).
        ref_mask: Binary reference region mask array (same shape as data_img).

    Returns:
        Dict with:
            - mean_lc, std_lc: LC region statistics
            - mean_ref, std_ref: Reference region statistics
            - cnr: Contrast-to-noise ratio
            - contrast_ratio: (mean_lc - mean_ref) / mean_ref
            - lc_voxel_count, ref_voxel_count: Number of valid voxels

    Raises:
        ValueError: If either ROI has no valid voxels, or if reference has zero variance.
    """
    data = data_img.get_fdata()

    # Extract and filter values
    lc_values = data[lc_mask > 0]
    ref_values = data[ref_mask > 0]

    lc_values = lc_values[np.isfinite(lc_values)]
    ref_values = ref_values[np.isfinite(ref_values)]

    if len(lc_values) == 0:
        raise ValueError(
            f"No valid voxels in LC mask (mask voxels={np.sum(lc_mask > 0)}, "
            f"finite values=0)"
        )
    if len(ref_values) == 0:
        raise ValueError(
            f"No valid voxels in reference mask (mask voxels={np.sum(ref_mask > 0)}, "
            f"finite values=0)"
        )

    mean_lc = float(np.mean(lc_values))
    std_lc = float(np.std(lc_values))
    mean_ref = float(np.mean(ref_values))
    std_ref = float(np.std(ref_values))

    if std_ref == 0:
        raise ValueError(
            "Reference region has zero variance (std=0). "
            "This may indicate a masking problem or homogeneous signal."
        )

    cnr = (mean_lc - mean_ref) / std_ref

    # Contrast ratio (relative difference)
    if mean_ref != 0:
        contrast_ratio = (mean_lc - mean_ref) / mean_ref
    else:
        contrast_ratio = float("nan")

    return {
        "mean_lc": mean_lc,
        "std_lc": std_lc,
        "mean_ref": mean_ref,
        "std_ref": std_ref,
        "cnr": float(cnr),
        "contrast_ratio": float(contrast_ratio),
        "lc_voxel_count": int(len(lc_values)),
        "ref_voxel_count": int(len(ref_values)),
    }


def extract_subject_cnr(
    subject_id: str,
    contrasts: list[str],
    lc_mask: np.ndarray,
    ref_mask: np.ndarray,
    config: Optional["PipelineConfig"] = None,
) -> list[Dict]:
    """
    Extract CNR for all available contrasts for a subject.

    Args:
        subject_id: Subject ID (e.g., 'sub-01').
        contrasts: List of contrast names to extract (e.g., ['R1', 'R2star', 'QSM']).
        lc_mask: Binary LC mask array.
        ref_mask: Binary reference region mask array.
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.

    Returns:
        List of dicts, each containing subject_id, contrast, and CNR metrics.

    Raises:
        FileNotFoundError: If no contrasts are found for the subject.
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    from .io import load_nifti

    results = []
    sub_dir = config.output_dir / subject_id

    if not sub_dir.exists():
        raise FileNotFoundError(f"No processed data found for {subject_id}")

    for contrast in contrasts:
        contrast_file = sub_dir / f"{subject_id}_{contrast}_MNI.nii.gz"

        if contrast_file.exists():
            img = load_nifti(contrast_file)
            stats = compute_cnr(img, lc_mask, ref_mask)
            stats["subject_id"] = subject_id
            stats["contrast"] = contrast
            results.append(stats)

    if not results:
        raise FileNotFoundError(
            f"No contrast files found for {subject_id} in {sub_dir}"
        )

    return results