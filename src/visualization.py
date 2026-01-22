"""
Visualization utilities for the 7T LC Quantification pipeline.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from nilearn import plotting


def plot_roi_overlay(
    background_img: nib.Nifti1Image,
    roi_img: nib.Nifti1Image,
    title: str = "ROI Overlay",
    output_path: Optional[str | Path] = None,
    cut_coords: Optional[Tuple[float, ...]] = None,
    display_mode: str = "ortho",
    cmap: str = "autumn",
    alpha: float = 0.7,
) -> None:
    """
    Plot ROI overlaid on background image.

    Args:
        background_img: Background image (e.g., T1w or MNI template).
        roi_img: ROI mask to overlay.
        title: Plot title.
        output_path: Path to save figure. If None, displays interactively.
        cut_coords: Coordinates for slices. If None, auto-selected.
        display_mode: View mode ('ortho', 'x', 'y', 'z', or 'mosaic').
        cmap: Colormap for ROI (default 'autumn' for red/yellow).
        alpha: ROI transparency (0-1).
    """
    display = plotting.plot_roi(
        roi_img,
        bg_img=background_img,
        title=title,
        display_mode=display_mode,
        cut_coords=cut_coords,
        cmap=cmap,
        alpha=alpha,
    )

    if output_path:
        display.savefig(output_path)
        plt.close()
    else:
        plt.show()


def plot_slice_visualization(
    img: nib.Nifti1Image,
    title: str = "Slice View",
    output_path: Optional[str | Path] = None,
    cmap: str = "gray",
    display_mode: str = "ortho",
    dim: float = -1,
    cut_coords: Optional[Tuple[float, ...]] = None,
) -> None:
    """
    Basic anatomical slice visualization.

    Args:
        img: NIfTI image to display.
        title: Plot title.
        output_path: Path to save figure. If None, displays interactively.
        cmap: Colormap.
        display_mode: View mode ('ortho', 'x', 'y', 'z', or 'mosaic').
        dim: Dimming factor for background.
        cut_coords: Coordinates for slices. If None, auto-selected.
    """
    display = plotting.plot_anat(
        img,
        title=title,
        display_mode=display_mode,
        dim=dim,
        cmap=cmap,
        cut_coords=cut_coords,
    )

    if output_path:
        display.savefig(output_path)
        plt.close()
    else:
        plt.show()


def plot_contrast_comparison(
    images: Dict[str, nib.Nifti1Image],
    slice_idx: int,
    output_path: Optional[str | Path] = None,
    suptitle: str = "Contrast Comparison",
    figsize_per_image: Tuple[int, int] = (4, 4),
) -> None:
    """
    Plot multiple contrasts side-by-side at the same axial slice.

    Args:
        images: Dict of {name: nib.Nifti1Image}.
        slice_idx: Axial slice index to display.
        output_path: Path to save figure. If None, displays interactively.
        suptitle: Super title for figure.
        figsize_per_image: Figure size per image (width, height).
    """
    n_contrasts = len(images)
    if n_contrasts == 0:
        return

    fig, axes = plt.subplots(
        1, n_contrasts,
        figsize=(figsize_per_image[0] * n_contrasts, figsize_per_image[1])
    )

    if n_contrasts == 1:
        axes = [axes]

    for ax, (name, img) in zip(axes, images.items()):
        data = img.get_fdata()

        # Ensure slice index is within bounds
        z_idx = min(slice_idx, data.shape[2] - 1)
        slice_data = data[:, :, z_idx]

        # Robust percentile scaling
        valid_data = slice_data[slice_data > 0]
        if len(valid_data) > 0:
            vmin, vmax = np.percentile(valid_data, [2, 98])
        else:
            vmin, vmax = 0, 1

        ax.imshow(slice_data.T, origin="lower", cmap="gray", vmin=vmin, vmax=vmax)
        ax.set_title(f"{name}\nz={z_idx}")
        ax.axis("off")

    plt.suptitle(suptitle, y=1.02)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_registration_qc(
    warped_img: nib.Nifti1Image,
    subject_id: str,
    output_path: Optional[str | Path] = None,
    z_coords: Tuple[int, ...] = (-25, -30, -35),
) -> None:
    """
    Generate QC figure for registration at brainstem levels.

    Args:
        warped_img: Warped T1w image in MNI space.
        subject_id: Subject ID for title.
        output_path: Path to save figure. If None, displays interactively.
        z_coords: MNI z-coordinates to display (default: brainstem levels).
    """
    fig, axes = plt.subplots(1, len(z_coords), figsize=(5 * len(z_coords), 5))

    if len(z_coords) == 1:
        axes = [axes]

    titles = ["Brainstem", "Pons", "Lower Pons"]

    for i, (z, title) in enumerate(zip(z_coords, titles)):
        display = plotting.plot_anat(
            warped_img,
            cut_coords=(z,),
            display_mode="z",
            axes=axes[i],
            title=f"{title} (z={z})",
            draw_cross=False,
        )

    plt.suptitle(f"{subject_id} - Warped to MNI (Brainstem Slices)", y=1.02)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()


def plot_cnr_summary(
    df,
    output_path: Optional[str | Path] = None,
    title: str = "LC Contrast-to-Noise Ratio by Map Type",
) -> None:
    """
    Plot CNR summary across contrasts.

    Args:
        df: DataFrame with 'contrast' and 'cnr' columns.
        output_path: Path to save figure. If None, displays interactively.
        title: Plot title.
    """
    import seaborn as sns

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Box plot
    ax1 = axes[0]
    sns.boxplot(data=df, x="contrast", y="cnr", ax=ax1)
    ax1.axhline(y=0, color="red", linestyle="--", alpha=0.7, label="No contrast")
    ax1.set_xlabel("Contrast Type")
    ax1.set_ylabel("CNR (LC vs Reference)")
    ax1.set_title(title)
    ax1.legend()

    # Bar plot with error bars
    ax2 = axes[1]
    summary = df.groupby("contrast")["cnr"].agg(["mean", "std", "count"])
    summary.plot(kind="bar", y="mean", yerr="std", ax=ax2, capsize=4, legend=False)
    ax2.axhline(y=0, color="red", linestyle="--", alpha=0.7)
    ax2.set_xlabel("Contrast Type")
    ax2.set_ylabel("Mean CNR ± SD")
    ax2.set_title("Mean LC CNR Across AHEAD Contrasts")
    ax2.tick_params(axis="x", rotation=0)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
