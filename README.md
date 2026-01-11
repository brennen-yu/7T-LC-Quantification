# 7T LC Quantification Pipeline

## Project Overview

This project implements a preliminary quantification pipeline for the locus coeruleus (LC) using 7T MRI data. It is designed to demonstrate technical competence in handling high-field brainstem imaging data, registration to standard space, and atlas-based ROI extraction.

The long-term goal (PhD research) is to investigate whether individual differences in LC microstructure predict stable variation in dream phenomenology. This repository serves as the technical foundation for that work.

## Dataset

We utilize the **AHEAD (Amsterdam Ultra-high field adult lifespan database)** dataset:
- **N:** 105 subjects
- **Field strength:** 7 Tesla
- **Sequence:** MP2RAGEME (multi-echo MP2RAGE)
- **Resolution:** Submillimeter
- **Age range:** 18-80 years
- **Available maps:** T1-weighted, R1, R2*, T2*, QSM
- **Download:** [https://doi.org/10.21942/uva.12080624](https://doi.org/10.21942/uva.12080624)

This project primarily uses the **R2* maps** due to their sensitivity to iron (neuromelanin-iron complexes in the LC).

## Pipeline Steps

1.  **Data Loading:** Load 7T structural MRI data (T1w, R2*).
2.  **Preprocessing:** Register subject data to MNI standard space using ANTs (via `antspyx`).
3.  **Atlas Application:** Apply a published LC atlas (e.g., Keren et al. or Dahl et al.) to the registered data.
4.  **Extraction:** Extract quantitative metrics (R2* values) from the LC region.
5.  **Visualization:** Generate figures showing the LC atlas overlay and signal extraction results.

## Setup Instructions

### 1. Environment Setup

Create a Python environment (conda or venv) and install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Data Download

1.  Visit the [AHEAD dataset repository](https://doi.org/10.21942/uva.12080624).
2.  Download the data for at least one subject (including T1w and R2* maps).
3.  Place the data in the `data/` directory. See `data/README.md` for the expected structure.

### 3. LC Atlas

Download a standard space LC atlas (e.g., Keren et al. 2009 or Dahl et al. 2019) and place it in the `atlases/` directory.

### 4. Running the Pipeline

The workflow is organized into Jupyter notebooks in the `notebooks/` directory:

1.  `01_setup_and_data_exploration.ipynb`: Verify setup and visualize raw data.
2.  `02_registration_to_mni.ipynb`: Register 7T data to MNI space.
3.  `03_atlas_application.ipynb`: Load and inspect the LC atlas.
4.  `04_lc_extraction_and_visualization.ipynb`: Extract metrics and create final figures.

Run them in order:

```bash
jupyter notebook
```
