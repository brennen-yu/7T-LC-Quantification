import nibabel as nib
import os
import glob

def load_nifti(file_path):
    """
    Load a NIfTI file.
    
    Args:
        file_path (str): Path to the NIfTI file.
        
    Returns:
        nib.Nifti1Image: The loaded NIfTI image.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    img = nib.load(file_path)
    return img

def find_bids_files(data_dir, subject_id, suffix):
    """
    Find files in a BIDS-like structure.
    
    Args:
        data_dir (str): Root data directory.
        subject_id (str): Subject ID (e.g., 'sub-01').
        suffix (str): File suffix to search for (e.g., 'T1w.nii.gz').
        
    Returns:
        list: List of matching file paths.
    """
    search_pattern = os.path.join(data_dir, subject_id, '**', f'*{suffix}')
    files = glob.glob(search_pattern, recursive=True)
    return files
