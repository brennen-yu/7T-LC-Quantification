import matplotlib.pyplot as plt
from nilearn import plotting

def plot_roi_overlay(background_img, roi_img, title="ROI Overlay", output_path=None):
    """
    Plot ROI overlaid on background image.
    
    Args:
        background_img (nib.Nifti1Image): Background image (e.g., T1w).
        roi_img (nib.Nifti1Image): ROI mask.
        title (str): Plot title.
        output_path (str, optional): Path to save the figure.
    """
    display = plotting.plot_roi(roi_img, bg_img=background_img, title=title, 
                                display_mode='ortho', cut_coords=None, cmap='Paired')
    
    if output_path:
        display.savefig(output_path)
        plt.close()
    else:
        plotting.show()

def plot_slice_visualization(img, title="Slice View", cmap='gray'):
    """
    Basic slice visualization using nilearn.
    """
    plotting.plot_anat(img, title=title, display_mode='ortho', dim=-1, cmap=cmap)
    plotting.show()
