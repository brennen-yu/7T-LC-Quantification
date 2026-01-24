"""
Image preprocessing and registration for the 7T LC Quantification pipeline.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import ants

if TYPE_CHECKING:
    from .config import PipelineConfig


def register_to_mni(
    fixed_image_path: str | Path,
    moving_image_path: str | Path,
    output_prefix: str | Path,
    config: Optional["PipelineConfig"] = None,
) -> Dict[str, Any]:
    """
    Register a moving image to MNI template using ANTs SyN.

    Uses registration parameters from config (syn_metric, reg_iterations, etc.)
    for optimized brainstem alignment.

    Args:
        fixed_image_path: Path to the fixed image (MNI template).
        moving_image_path: Path to the moving image (subject T1w).
        output_prefix: Prefix for output files.
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.

    Returns:
        Dict containing:
            - warped_image: ANTs image object
            - warped_image_path: Path to saved warped image
            - fwdtransforms: List of forward transform files
            - invtransforms: List of inverse transform files
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    fixed = ants.image_read(str(fixed_image_path))
    moving = ants.image_read(str(moving_image_path))

    registration = ants.registration(
        fixed=fixed,
        moving=moving,
        type_of_transform=config.registration_type,
        syn_metric=config.syn_metric,
        syn_sampling=config.syn_sampling,
        reg_iterations=config.reg_iterations,
        verbose=False,
    )

    warped_path = Path(f"{output_prefix}_Warped.nii.gz")
    ants.image_write(registration["warpedmovout"], str(warped_path))

    return {
        "warped_image": registration["warpedmovout"],
        "warped_image_path": warped_path,
        "fwdtransforms": registration["fwdtransforms"],
        "invtransforms": registration["invtransforms"],
    }


def apply_transforms(
    fixed_image_path: str | Path,
    moving_image_path: str | Path,
    transformlist: List[str],
    output_path: str | Path,
    interpolator: str = "linear",
) -> ants.ANTsImage:
    """
    Apply transforms to an image.

    Used to warp other contrasts (R2*, QSM, etc.) using transforms
    computed from T1w registration.

    Args:
        fixed_image_path: Path to the fixed image (defines output space).
        moving_image_path: Path to the moving image to transform.
        transformlist: List of transform files from registration.
        output_path: Path to save the transformed image.
        interpolator: Interpolation method ('linear', 'nearestNeighbor', 'bSpline').

    Returns:
        The transformed ANTs image.
    """
    fixed = ants.image_read(str(fixed_image_path))
    moving = ants.image_read(str(moving_image_path))

    warped = ants.apply_transforms(
        fixed=fixed,
        moving=moving,
        transformlist=transformlist,
        interpolator=interpolator,
    )

    ants.image_write(warped, str(output_path))
    return warped


def register_subject(
    subject_id: str,
    fixed_img: ants.ANTsImage,
    config: Optional["PipelineConfig"] = None,
) -> Dict[str, Any]:
    """
    Register subject T1w to MNI and apply transforms to all contrast maps.

    This is the high-level function for processing a single subject.
    It finds the T1w image, registers it to MNI, then applies the same
    transforms to all other available contrasts.

    Args:
        subject_id: Subject ID (e.g., 'sub-01').
        fixed_img: MNI template as ANTs image object.
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.

    Returns:
        Dict containing:
            - subject_id: The subject ID
            - success: Boolean indicating success
            - T1w_MNI: Path to warped T1w
            - {contrast}_MNI: Paths to warped contrast maps
            - transforms: List of forward transform files

    Raises:
        FileNotFoundError: If T1w image is not found for the subject.
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    from .io import find_contrast_file

    results: Dict[str, Any] = {"subject_id": subject_id, "success": False}

    # Find T1w (required)
    t1w_path = find_contrast_file(
        config.data_dir, subject_id, config.contrast_patterns["T1w"]
    )
    if t1w_path is None:
        raise FileNotFoundError(
            f"T1w image not found for {subject_id}. "
            f"Searched patterns: {config.contrast_patterns['T1w']}"
        )

    moving = ants.image_read(str(t1w_path))

    # Create subject output directory
    sub_out_dir = config.output_dir / subject_id
    sub_out_dir.mkdir(parents=True, exist_ok=True)

    # Register T1w -> MNI
    registration = ants.registration(
        fixed=fixed_img,
        moving=moving,
        type_of_transform=config.registration_type,
        syn_metric=config.syn_metric,
        syn_sampling=config.syn_sampling,
        reg_iterations=config.reg_iterations,
        verbose=False,
    )

    # Save warped T1w
    t1w_mni_path = sub_out_dir / f"{subject_id}_T1w_MNI.nii.gz"
    ants.image_write(registration["warpedmovout"], str(t1w_mni_path))
    results["T1w_MNI"] = t1w_mni_path

    # Apply transforms to other contrasts
    other_contrasts = {
        k: v for k, v in config.contrast_patterns.items() if k != "T1w"
    }

    for contrast_name, patterns in other_contrasts.items():
        contrast_path = find_contrast_file(config.data_dir, subject_id, patterns)

        if contrast_path is not None:
            contrast_img = ants.image_read(str(contrast_path))

            warped = ants.apply_transforms(
                fixed=fixed_img,
                moving=contrast_img,
                transformlist=registration["fwdtransforms"],
                interpolator="linear",
            )

            output_path = sub_out_dir / f"{subject_id}_{contrast_name}_MNI.nii.gz"
            ants.image_write(warped, str(output_path))
            results[f"{contrast_name}_MNI"] = output_path

    results["success"] = True
    results["transforms"] = registration["fwdtransforms"]

    return results


def get_mni_template(config: Optional["PipelineConfig"] = None) -> ants.ANTsImage:
    """
    Load the MNI152 template defined in the configuration.
    
    This should be the specific MNI 2009b template provided with the Ye et al. (2021)
    atlas to ensure correct spatial alignment.

    Args:
        config: Pipeline configuration. If None, uses DEFAULT_CONFIG.

    Returns:
        MNI template as ANTs image object.
    
    Raises:
        FileNotFoundError: If the template file is missing.
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    template_path = config.mni_template_path
    if not template_path.exists():
        raise FileNotFoundError(
            f"MNI Template not found at: {template_path}\n"
            "Please ensure the 'ye_2021' atlas directory is correctly set up."
        )
    
    return ants.image_read(str(template_path))

