"""
File I/O utilities for the 7T LC Quantification pipeline.
"""

import os
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

import nibabel as nib

if TYPE_CHECKING:
    from .config import PipelineConfig


def load_nifti(file_path: str | Path) -> nib.Nifti1Image:
    """
    Load a NIfTI file.

    Args:
        file_path: Path to the NIfTI file.

    Returns:
        The loaded NIfTI image.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return nib.load(file_path)


def find_bids_files(
    data_dir: str | Path,
    subject_id: str,
    suffix: str,
) -> List[Path]:
    """
    Find files in a BIDS-like structure.

    Args:
        data_dir: Root data directory.
        subject_id: Subject ID (e.g., 'sub-01').
        suffix: File suffix to search for (e.g., 'T1w.nii.gz').

    Returns:
        List of matching file paths.
    """
    import glob

    data_dir = Path(data_dir)
    search_pattern = str(data_dir / subject_id / "**" / f"*{suffix}")
    files = glob.glob(search_pattern, recursive=True)
    return [Path(f) for f in files]


def find_contrast_file(
    data_dir: str | Path,
    subject_id: str,
    patterns: List[str],
) -> Optional[Path]:
    """
    Find the first file matching any pattern for a subject.

    Searches recursively within the subject's directory.

    Args:
        data_dir: Root data directory.
        subject_id: Subject ID (e.g., 'sub-01').
        patterns: List of filename patterns to match (e.g., ['T1w.nii.gz', 'UNIT1.nii.gz']).

    Returns:
        Path to the first matching file, or None if no match found.
    """
    sub_dir = Path(data_dir) / subject_id
    if not sub_dir.exists():
        return None

    for root, _, files in os.walk(sub_dir):
        for filename in files:
            for pattern in patterns:
                if filename.endswith(pattern):
                    return Path(root) / filename
    return None


def ensure_output_dirs(config: "PipelineConfig") -> None:
    """
    Create output directories if they don't exist.

    Args:
        config: Pipeline configuration with output_dir and figures_dir paths.
    """
    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.figures_dir.mkdir(parents=True, exist_ok=True)


def list_subjects(data_dir: str | Path) -> List[str]:
    """
    Return sorted list of subject IDs in a BIDS directory.

    Finds all directories starting with 'sub-'.

    Args:
        data_dir: Root data directory.

    Returns:
        Sorted list of subject IDs (e.g., ['sub-01', 'sub-02', ...]).
    """
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []

    return sorted([
        d.name for d in data_dir.iterdir()
        if d.is_dir() and d.name.startswith("sub-")
    ])


def list_processed_subjects(output_dir: str | Path) -> List[str]:
    """
    Return sorted list of processed subject IDs.

    Finds all directories starting with 'sub-' in the output directory.

    Args:
        output_dir: Output results directory.

    Returns:
        Sorted list of processed subject IDs.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        return []

    return sorted([
        d.name for d in output_dir.iterdir()
        if d.is_dir() and d.name.startswith("sub-")
    ])
