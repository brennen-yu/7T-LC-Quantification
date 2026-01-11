# Methods Notes

## Registration Strategy

We use ANTs SyN registration (Symmetric Normalization) to register the high-resolution 7T T1w images to the MNI152 template.

- **Fixed Image:** MNI152 template (e.g., 0.5mm or 1mm resolution).
- **Moving Image:** Subject 7T T1w MP2RAGE UNI image.
- **Transform Application:** The calculated transform (warped field + affine) is applied to the coregistered R2* map.

## LC Atlas

We utilize the [Atlas Name, e.g., Keren et al., 2009] probabilistic atlas of the Locus Coeruleus. 
- **Coordinates:** Defined in MNI space.
- **Thresholding:** We may threshold the probabilistic mask at 0.5 or use weighted averages.

## Signal Extraction

LC signal is quantified as the mean R2* value within the defined ROI. R2* is chosen for its sensitivity to iron content, which is high in the LC due to neuromelanin-iron complexes.
