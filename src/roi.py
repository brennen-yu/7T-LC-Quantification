"""
ROI creation and management for the 7T LC Quantification pipeline.
"""

from pathlib import Path
from typing import Optional, Tuple, TYPE_CHECKING

import nibabel as nib
import numpy as np

if TYPE_CHECKING:
    from .config import PipelineConfig


def create_pontine_reference_roi(
    shape: Tuple[int, int, int],
    affine: np.ndarray,
    exclude_mask: Optional[np.ndarray] = None,
    center_mni: Optional[Tuple[float, float, float]] = None,
    radius_mm: Optional[float] = None,
    config: Optional["PipelineConfig"] = None,
) -> np.ndarray:
    """
    Create a spherical pontine tegmentum reference region.

    The reference region is placed in the central pons, ventral and medial
    to the LC. This geometric approach is a simple fallback; for more
    anatomically precise definitions, use an atlas-based reference mask.

    Args:
        shape: Output array shape (must match target space).
        affine: Affine matrix for MNI coordinate conversion.
        exclude_mask: Optional mask of voxels to exclude (e.g., LC region).
        center_mni: Sphere center in MNI coordinates. If None, uses config default.
        radius_mm: Sphere radius in mm. If None, uses config default.
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.

    Returns:
        Binary mask as numpy array (float32, values 0 or 1).
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    center_mni = center_mni if center_mni is not None else config.reference_center_mni
    radius_mm = radius_mm if radius_mm is not None else config.reference_radius_mm

    ref_mask = np.zeros(shape, dtype=np.float32)

    # Convert MNI coordinates to voxel indices
    center_mni_homog = np.array([center_mni[0], center_mni[1], center_mni[2], 1.0])
    inv_affine = np.linalg.inv(affine)
    center_vox = inv_affine @ center_mni_homog
    cx, cy, cz = int(round(center_vox[0])), int(round(center_vox[1])), int(round(center_vox[2]))

    # Get voxel size to convert mm radius to voxels
    # Use geometric mean of voxel dimensions for non-isotropic data
    voxel_dims = np.abs(np.diag(affine)[:3])
    voxel_size = np.cbrt(np.prod(voxel_dims))  # Geometric mean
    radius_vox = int(np.ceil(radius_mm / voxel_size))

    # Create spherical ROI
    for x in range(max(0, cx - radius_vox), min(shape[0], cx + radius_vox + 1)):
        for y in range(max(0, cy - radius_vox), min(shape[1], cy + radius_vox + 1)):
            for z in range(max(0, cz - radius_vox), min(shape[2], cz + radius_vox + 1)):
                # Calculate distance in mm (accounting for anisotropic voxels)
                dx_mm = (x - cx) * voxel_dims[0]
                dy_mm = (y - cy) * voxel_dims[1]
                dz_mm = (z - cz) * voxel_dims[2]
                dist_mm = np.sqrt(dx_mm**2 + dy_mm**2 + dz_mm**2)

                if dist_mm <= radius_mm:
                    ref_mask[x, y, z] = 1.0

    # Exclude LC voxels if provided
    if exclude_mask is not None:
        ref_mask[exclude_mask > 0] = 0

    return ref_mask


def load_or_create_reference_roi(
    lc_atlas_img: nib.Nifti1Image,
    config: Optional["PipelineConfig"] = None,
    custom_ref_path: Optional[str | Path] = None,
) -> nib.Nifti1Image:
    """
    Load reference ROI from file, or create geometric fallback.

    Priority:
    1. If custom_ref_path is provided and exists, load it
    2. If config.reference_roi_path exists, load it
    3. Create geometric sphere and save for future use

    Args:
        lc_atlas_img: LC atlas (used for shape/affine and exclusion mask).
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.
        custom_ref_path: Optional path to a custom reference mask.

    Returns:
        Reference ROI as NIfTI image in same space as LC atlas.
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    # Option 1: Custom path provided
    if custom_ref_path is not None:
        custom_ref_path = Path(custom_ref_path)
        if custom_ref_path.exists():
            return nib.load(custom_ref_path)
        raise FileNotFoundError(f"Custom reference ROI not found: {custom_ref_path}")

    # Option 2: Default path exists
    ref_path = config.reference_roi_path
    if ref_path.exists():
        return nib.load(ref_path)

    # Option 3: Create geometric reference
    lc_data = lc_atlas_img.get_fdata()
    lc_binary = lc_data > 0.1  # Exclude any voxel with LC probability > 10%

    ref_mask = create_pontine_reference_roi(
        shape=lc_data.shape,
        affine=lc_atlas_img.affine,
        exclude_mask=lc_binary,
        config=config,
    )

    ref_img = nib.Nifti1Image(ref_mask, lc_atlas_img.affine, lc_atlas_img.header)

    # Save for reuse
    config.atlas_dir.mkdir(parents=True, exist_ok=True)
    nib.save(ref_img, ref_path)

    return ref_img


def threshold_probabilistic_atlas(
    atlas_img: nib.Nifti1Image,
    threshold: float,
) -> np.ndarray:
    """
    Create binary mask from probabilistic atlas at given threshold.

    Args:
        atlas_img: Probabilistic atlas image.
        threshold: Probability threshold (e.g., 0.5 for 50%).

    Returns:
        Binary mask as numpy array (int).
    """
    data = atlas_img.get_fdata()
    return (data > threshold).astype(np.int32)
