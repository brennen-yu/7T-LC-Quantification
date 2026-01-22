# Code Modularization Design

**Date:** 2026-01-21
**Status:** Approved
**Goal:** Fix all identified bugs and properly restructure code so that `src/` contains all logic and notebooks serve as thin orchestration layers.

---

## Context

A code review identified several issues:

1. **Code duplication** — `find_contrast_file()` defined in multiple notebooks
2. **Inconsistent registration params** — `src/preprocessing.py` uses ANTs defaults while notebook uses optimized parameters
3. **No configuration file** — Paths, thresholds, atlas filenames scattered throughout
4. **Silent failures** — Missing files cause meaningless results instead of errors
5. **Missing directory creation** — `savefig()` fails if output directories don't exist
6. **Hardcoded values** — Not container-ready
7. **No type hints** — Reduced IDE support and documentation
8. **Geometric reference region** — Hardcoded coordinates, assumes 1mm resolution

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Configuration | Python `config.py` module | Integrates with `src/`, easy to override programmatically |
| Reference region | Support both geometric and custom | Keeps pipeline working, allows future upgrade to anatomical atlas |
| Error handling | Fail fast (exceptions) | Development phase; silent failures are worse than crashes |

---

## Module Structure

```
src/
├── __init__.py          # Export public API
├── config.py            # NEW: Centralized configuration
├── io.py                # File I/O (add find_contrast_file, ensure_directories)
├── preprocessing.py     # Registration (improved register_subject)
├── extraction.py        # ROI stats + CNR calculation (add compute_cnr)
├── roi.py               # NEW: ROI creation (create_pontine_reference_roi)
└── visualization.py     # Plotting utilities (minor fixes)
```

---

## Module Specifications

### `src/config.py` (NEW)

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class PipelineConfig:
    # Paths (relative to project root)
    data_dir: Path = Path("data")
    output_dir: Path = Path("outputs/results")
    figures_dir: Path = Path("outputs/figures")
    atlas_dir: Path = Path("atlases")

    # Atlas files
    lc_atlas_filename: str = "LC_prob_MNI.nii.gz"
    reference_roi_filename: str = "pontine_reference_MNI.nii.gz"

    # Thresholds
    lc_probability_threshold: float = 0.5

    # Reference region defaults (geometric fallback)
    reference_center_mni: tuple = (0, -30, -28)
    reference_radius_mm: float = 3.0

    # Registration parameters
    registration_type: str = "SyN"
    syn_metric: str = "CC"
    syn_sampling: int = 4
    reg_iterations: tuple = (100, 70, 50, 20)

    # Contrast patterns for BIDS discovery
    contrast_patterns: dict = field(default_factory=lambda: {
        "T1w": ["T1w.nii.gz", "UNIT1.nii.gz"],
        "R1": ["R1map.nii.gz", "R1.nii.gz"],
        "R2star": ["R2starmap.nii.gz", "R2star.nii.gz"],
        "QSM": ["QSM.nii.gz", "Chimap.nii.gz"],
        "T2starw": ["T2starw.nii.gz"],
    })

DEFAULT_CONFIG = PipelineConfig()
```

---

### `src/io.py`

**Additions:**
- `find_contrast_file(data_dir, subject_id, patterns) -> Optional[Path]` — consolidated from notebooks
- `ensure_output_dirs(config) -> None` — creates output directories
- `list_subjects(data_dir) -> List[str]` — returns sorted subject IDs

**Improvements:**
- Type hints on all functions
- `load_nifti()` returns typed `nib.Nifti1Image`

---

### `src/preprocessing.py`

**Changes:**
- `register_to_mni()` — uses config parameters (`syn_metric`, `reg_iterations`, etc.) instead of ANTs defaults
- `apply_transforms()` — explicit `interpolator` parameter
- `register_subject()` — NEW high-level function consolidated from notebook 02; raises `FileNotFoundError` if T1w missing

---

### `src/roi.py` (NEW)

**Functions:**
- `create_pontine_reference_roi(shape, affine, exclude_mask, center_mni, radius_mm, config)` — configurable geometric sphere, handles non-1mm resolutions
- `load_or_create_reference_roi(lc_atlas_img, config)` — loads from file or creates geometric fallback

---

### `src/extraction.py`

**Changes:**
- `extract_roi_stats()` — configurable threshold parameter, NaN filtering, raises `ValueError` on empty ROI
- `compute_cnr()` — NEW function consolidated from notebook 04; proper error handling, no silent failures

---

### `src/visualization.py`

**Changes:**
- `plot_roi_overlay()` — changed default cmap from `'Paired'` to `'autumn'`; added `cut_coords`, `alpha` parameters
- `plot_slice_visualization()` — added `output_path` parameter to avoid blocking
- `plot_contrast_comparison()` — NEW function for multi-contrast side-by-side views

---

## Notebook Restructuring

Notebooks become thin orchestration layers that import from `src/`.

### Notebook 01: Setup and Data Exploration

**Before:** Defines `find_contrast_file()` inline, hardcoded paths, missing `os.makedirs()`

**After:**
```python
from src.config import DEFAULT_CONFIG
from src.io import load_nifti, find_contrast_file, list_subjects, ensure_output_dirs
from src.visualization import plot_contrast_comparison

config = DEFAULT_CONFIG
ensure_output_dirs(config)

subjects = list_subjects(config.data_dir)
```

---

### Notebook 02: Registration to MNI

**Before:** Defines `register_subject()` (60+ lines), duplicates `find_contrast_file()`, `results` may be undefined

**After:**
```python
from src.config import DEFAULT_CONFIG
from src.io import list_subjects, ensure_output_dirs
from src.preprocessing import register_subject

config = DEFAULT_CONFIG
ensure_output_dirs(config)

subjects = list_subjects(config.data_dir)
if not subjects:
    raise ValueError("No subjects found. Download AHEAD data first.")

results = register_subject(subjects[0], fixed_img, config)
```

---

### Notebook 03: Atlas Application

**Before:** Defines `create_pontine_reference_roi()` inline, hardcoded atlas filename

**After:**
```python
from src.config import DEFAULT_CONFIG
from src.io import load_nifti, ensure_output_dirs
from src.roi import load_or_create_reference_roi

config = DEFAULT_CONFIG

lc_atlas_path = config.atlas_dir / config.lc_atlas_filename
if not lc_atlas_path.exists():
    raise FileNotFoundError(f"LC atlas not found: {lc_atlas_path}")

lc_atlas_img = load_nifti(lc_atlas_path)
ref_img = load_or_create_reference_roi(lc_atlas_img, config)
```

---

### Notebook 04: LC Extraction

**Before:** Defines `compute_cnr()` inline, fallback `ref_mask = lc_mask` produces meaningless CNR

**After:**
```python
from src.config import DEFAULT_CONFIG
from src.io import load_nifti, ensure_output_dirs
from src.extraction import compute_cnr
from src.roi import load_or_create_reference_roi

config = DEFAULT_CONFIG

lc_atlas_img = load_nifti(config.atlas_dir / config.lc_atlas_filename)
ref_img = load_or_create_reference_roi(lc_atlas_img, config)

lc_mask = (lc_atlas_img.get_fdata() > config.lc_probability_threshold).astype(int)
ref_mask = ref_img.get_fdata()

stats = compute_cnr(contrast_img, lc_mask, ref_mask)
```

---

## Implementation Order

| Step | Task | Rationale |
|------|------|-----------|
| 1 | Create `src/config.py` | Foundation — other modules depend on it |
| 2 | Update `src/io.py` | Add `find_contrast_file()`, `ensure_output_dirs()`, `list_subjects()` |
| 3 | Create `src/roi.py` | New module, no dependencies on existing code |
| 4 | Update `src/extraction.py` | Add `compute_cnr()`, improve `extract_roi_stats()` |
| 5 | Update `src/preprocessing.py` | Sync with notebook params, add `register_subject()` |
| 6 | Update `src/visualization.py` | Minor fixes, add `plot_contrast_comparison()` |
| 7 | Update `src/__init__.py` | Export public API |
| 8 | Refactor Notebook 01 | Uses `io`, `config`, `visualization` |
| 9 | Refactor Notebook 02 | Uses `preprocessing`, `io`, `config` |
| 10 | Refactor Notebook 03 | Uses `roi`, `io`, `config` |
| 11 | Refactor Notebook 04 | Uses `extraction`, `roi`, `io`, `config` |

**Testing:** After each `src/` module update, verify imports work. After each notebook refactor, run the notebook to confirm no regressions.

---

## Summary of Changes

| Location | Lines Removed | Functions Added/Moved |
|----------|---------------|----------------------|
| `src/config.py` | — | NEW: `PipelineConfig`, `DEFAULT_CONFIG` |
| `src/io.py` | — | ADD: `find_contrast_file()`, `ensure_output_dirs()`, `list_subjects()` |
| `src/roi.py` | — | NEW: `create_pontine_reference_roi()`, `load_or_create_reference_roi()` |
| `src/extraction.py` | — | ADD: `compute_cnr()`; IMPROVE: `extract_roi_stats()` |
| `src/preprocessing.py` | — | ADD: `register_subject()`; IMPROVE: `register_to_mni()` |
| `src/visualization.py` | — | ADD: `plot_contrast_comparison()`; FIX: cmap, output_path |
| Notebook 01 | ~20 | `find_contrast_file()` → `io.py` |
| Notebook 02 | ~60 | `register_subject()` → `preprocessing.py` |
| Notebook 03 | ~30 | `create_pontine_reference_roi()` → `roi.py` |
| Notebook 04 | ~20 | `compute_cnr()` → `extraction.py` |
