# LC Atlases

This directory is for storing the Locus Coeruleus atlas files.

## Recommended Atlas: Ye et al. (2021) / Dahl et al.

This is a probabilistic LC atlas derived from 7T MRI data.

**Download:** [https://www.nitrc.org/projects/lc_7t_prob](https://www.nitrc.org/projects/lc_7t_prob)

1.  Go to the NITRC page.
2.  Download `LC_7T_prob_v1_060220.zip` (or newer).
3.  Unzip the contents.
4.  Locate the MNI-space atlas file (usually named something like `LC_prob_MNI_...nii.gz`).
5.  Place the NIfTI file in this directory (`atlases/`).

## Alternative: Keren et al. (2009)

If you have access to the Keren et al. 2009 atlas (often shared privately or found in other repositories), you can place it here.

## Usage

Update `src/extraction.py` or the notebooks to point to the correct filename of the atlas you downloaded.
