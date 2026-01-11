import ants
import numpy as np

def register_to_mni(fixed_image_path, moving_image_path, output_prefix):
    """
    Register a moving image to a fixed (template) image using ANTs.
    
    Args:
        fixed_image_path (str): Path to the fixed image (MNI template).
        moving_image_path (str): Path to the moving image (subject T1w).
        output_prefix (str): Prefix for output files.
        
    Returns:
        dict: Dictionary containing warped image and transform paths.
    """
    fixed = ants.image_read(fixed_image_path)
    moving = ants.image_read(moving_image_path)
    
    # SyN registration (rigid + affine + deformable)
    # Using 'SyN' which is symmetric normalization
    mytx = ants.registration(fixed=fixed, moving=moving, type_of_transform='SyN')
    
    # Save warped image
    warped_image_path = f"{output_prefix}_Warped.nii.gz"
    ants.image_write(mytx['warpedmovout'], warped_image_path)
    
    return {
        'warped_image': mytx['warpedmovout'],
        'warped_image_path': warped_image_path,
        'fwdtransforms': mytx['fwdtransforms'],
        'invtransforms': mytx['invtransforms']
    }

def apply_transforms(fixed_image_path, moving_image_path, transformlist, output_path):
    """
    Apply transforms to an image (e.g., applying T1w->MNI transform to R2* map).
    
    Args:
        fixed_image_path (str): Path to the fixed image.
        moving_image_path (str): Path to the moving image.
        transformlist (list): List of transform files.
        output_path (str): Path to save the output.
        
    Returns:
        ants.image: The transformed image.
    """
    fixed = ants.image_read(fixed_image_path)
    moving = ants.image_read(moving_image_path)
    
    warped_image = ants.apply_transforms(fixed=fixed, moving=moving, transformlist=transformlist)
    ants.image_write(warped_image, output_path)
    
    return warped_image
