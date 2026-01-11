# Data Directory

This directory should contain the downloaded AHEAD dataset files.

## Expected Structure

```
data/
├── sub-<id>/
│   ├── ses-<id>/
│   │   ├── anat/
│   │   │   ├── sub-<id>_ses-<id>_acq-mp2rageme_run-1_T1w.nii.gz
│   │   │   ├── sub-<id>_ses-<id>_acq-mp2rageme_run-1_R2star.nii.gz
│   │   │   └── ...
│   │   └── ...
│   └── ...
└── ...
```

Note: This directory is ignored by git to avoid committing large data files.
