import numpy as np
import nibabel as nib
from nilearn import image, masking

def extract_roi_stats(data_img, roi_mask_img):
    """
    Extract statistics from an ROI.
    
    Args:
        data_img (nib.Nifti1Image): The data image (e.g., R2* map).
        roi_mask_img (nib.Nifti1Image): The ROI mask (binary or probabilistic).
        
    Returns:
        dict: Dictionary containing mean, std, median, etc.
    """
    # Resample mask to data if necessary
    if data_img.shape != roi_mask_img.shape:
        roi_mask_img = image.resample_to_img(roi_mask_img, data_img, interpolation='nearest')
    
    data_data = data_img.get_fdata()
    mask_data = roi_mask_img.get_fdata()
    
    # Threshold mask if it's probabilistic
    binary_mask = mask_data > 0.5
    
    roi_values = data_data[binary_mask]
    
    stats = {
        'mean': np.mean(roi_values),
        'std': np.std(roi_values),
        'median': np.median(roi_values),
        'min': np.min(roi_values),
        'max': np.max(roi_values),
        'voxel_count': len(roi_values)
    }
    
    return stats
