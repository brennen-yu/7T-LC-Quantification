# 7T LC Quantification Pipeline

## Project Overview

This project implements an atlas-based locus coeruleus (LC) localization pipeline for 7T MRI data. It serves two purposes:

1. **Technical demonstration**: Building reproducible neuroimaging infrastructure for high-field brainstem analysis
2. **Scientific motivation**: Systematically documenting the contrast limitations of publicly available 7T quantitative maps for LC imaging, thereby motivating the need for magnetization transfer (MT) sequences in future work

### Context

The long-term goal (PhD research at MPI-CBS) is to investigate whether individual differences in LC microstructure predict stable variation in dream phenomenology. This requires reliable LC measurements at 7T using MT saturation (MTsat) maps generated via the MPM protocol and hMRI toolbox.

However, no public 7T dataset currently provides both:
- LC-optimized sequences (MT-weighted)
- Test-retest acquisitions for reliability assessment

This preliminary project uses the best available public 7T dataset (AHEAD) to:
- Build the pipeline infrastructure that will transfer to the PhD
- Empirically document which contrasts fail to visualize LC
- Establish QC and atlas-based segmentation workflows

## Key Scientific Background

The locus coeruleus is visible in MRI due to neuromelanin-iron complexes in its noradrenergic neurons. However, **the source of LC contrast is predominantly magnetization transfer (MT) effects**, not relaxation-based or susceptibility contrast:

> "In our results, we were not able to detect a R1 or R2* increase in the LC region... The LC did not show any visible contrast in R2* or R1 compared to its adjacent areas."
> — Priovoulos et al., 2018

- **R1 and R2***: No LC contrast detected (Priovoulos et al., 2018)
- **QSM**: Not sensitive to neuromelanin-bound iron in LC (ISMRM 2018 abstract)
- **MT-weighted sequences**: Best LC visualization at both 3T and 7T (Priovoulos et al., 2018)

**Note**: R1 = 1/T1 and R2* = 1/T2*, so these findings apply equally to T1 and T2* maps.

**Why does LC differ from substantia nigra?** Both contain neuromelanin, but iron storage differs. In LC, total iron remains stable throughout life and is predominantly bound to neuromelanin (chelated). Chelated iron is only weakly paramagnetic—even at high concentrations—rendering it "invisible" to susceptibility-based imaging (R2*, QSM). In contrast, the SN has more free/ferritin-bound iron that increases with age, explaining why iron-sensitive sequences work there but not in LC.

The AHEAD dataset provides R1, R2*, T1w, T2*w, and QSM maps—none of which are expected to show direct LC contrast. This project documents this limitation systematically.

## Dataset

**AHEAD (Amsterdam Ultra-high field adult lifespan database)**
- **N**: 105 subjects (ages 18-80)
- **Field strength**: 7 Tesla
- **Sequence**: MP2RAGEME (multi-echo MP2RAGE)
- **Resolution**: Submillimeter (0.7mm isotropic)
- **Available maps**: T1w, R1, R2*, T2*, QSM
- **Download**: [https://doi.org/10.21942/uva.12080624](https://doi.org/10.21942/uva.12080624)

**What AHEAD lacks**: Dedicated MT-weighted or neuromelanin-sensitive sequences

## Pipeline Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Load 7T Data   │ ──▶ │   Register to   │ ──▶ │   Apply LC      │
│  (T1w, R1, R2*) │     │   MNI Space     │     │   Atlas         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   QC Report &   │ ◀── │   Compute CNR   │ ◀── │  Extract Signal │
│   Figures       │     │   in LC Region  │     │  (all contrasts)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Steps

1. **Data Loading**: Load MP2RAGEME-derived maps (T1w, R1, R2*, QSM)
2. **Registration**: Register to MNI space using ANTs SyN
3. **Atlas Application**: Apply 7T LC probabilistic atlas (Ye et al., 2021)
4. **Signal Extraction**: Extract values from LC ROI across all available contrasts
5. **Contrast Evaluation**: Compute CNR relative to pontine reference region
6. **Documentation**: Generate QC figures and summary statistics

## What This Project Demonstrates

### For the Interview/Presentation

- **7T data handling**: Familiarity with ultra-high field data characteristics
- **Reproducible pipelines**: Containerized, version-controlled workflow
- **Brainstem registration**: Challenging region requiring careful methodology
- **Atlas-based analysis**: Standard approach for small subcortical structures
- **Critical evaluation**: Understanding *why* certain sequences are needed

### What Transfers to PhD

| This Project | PhD Work |
|--------------|----------|
| ANTs registration to MNI | Same workflow, different input |
| 7T LC atlas application | Same atlas, validated on MTsat |
| CNR/signal extraction code | Applied to MTsat maps |
| QC framework | Extended for test-retest |
| Containerization | Same infrastructure |

## Expected Results

Based on the literature, we expect:
- **R2\*, QSM**: No significant LC-vs-reference contrast
- **R1, T1w**: Minimal or absent LC contrast
- **Age effect (exploratory)**: Possibly faint signal in older subjects (more neuromelanin accumulation)

A "negative result" (no LC contrast) is the scientifically correct outcome and motivates the PhD protocol requiring MTsat.

## Setup Instructions

### 1. Environment

```bash
# Create environment
conda create -n lc-pipeline python=3.10
conda activate lc-pipeline

# Install dependencies
pip install -r requirements.txt
```

### 2. Data

1. Download AHEAD data from [https://doi.org/10.21942/uva.12080624](https://doi.org/10.21942/uva.12080624)
2. Place in `data/` directory (see `data/README.md` for structure)

### 3. Atlas

1. Download 7T LC atlas from [NITRC](https://www.nitrc.org/projects/lc_7t_prob)
2. Place in `atlases/` directory

### 4. Run Pipeline

```bash
jupyter notebook
```

Execute notebooks in order:
1. `01_setup_and_data_exploration.ipynb`
2. `02_registration_to_mni.ipynb`
3. `03_atlas_application.ipynb`
4. `04_lc_extraction_and_visualization.ipynb`

## References

- Priovoulos N, Jacobs HIL, Ivanov D, Uludag K, Verhey FRJ, Poser BA (2018). High-resolution in vivo imaging of human locus coeruleus by magnetization transfer MRI at 3T and 7T. *NeuroImage*, 168:427-436.
- Betts MJ, et al. (2019). Locus coeruleus imaging as a biomarker for noradrenergic dysfunction in neurodegenerative diseases. *Brain*, 142(9):2558-2571. [Review]
- Ye R, et al. (2021). Locus Coeruleus Atlas. *NITRC*.
- ISMRM 2018 Abstract: MT and QSM of the Locus Coeruleus and Substantia Nigra.

## License

MIT License - See LICENSE file
