# Methods Notes

## Scientific Rationale

### Why LC Imaging Is Challenging

The locus coeruleus (LC) is a small brainstem nucleus (~2mm diameter, ~15mm length) containing neuromelanin-rich noradrenergic neurons. LC MRI contrast arises from neuromelanin-metal complexes, but **the dominant contrast mechanism is magnetization transfer (MT)**, not relaxation-based contrast.

Key findings from the literature:

> "In our results, we were not able to detect a R1 or R2* increase in the LC region. The lack of R2* contrast in LC was partially unexpected: an R2* increase in the similarly NM-rich SN is well documented... The LC did not show any visible contrast in R2* or R1 compared to its adjacent areas."
> — Priovoulos et al., 2018, NeuroImage

> "In our pilot results... the high-resolution QSM data was not sensitive to the iron binding with neuromelanin in the LC. This may be because the iron linked to the NM is in a different chemical state than other forms of iron that contribute to the QSM contrast."
> — ISMRM 2018 Abstract: "MT and QSM of the Locus Coeruleus and Substantia Nigra"

### R1/R2* vs T1/T2* — What's the Difference?

These are mathematically related:
- **R1 = 1/T1** (longitudinal relaxation rate, in s⁻¹)
- **R2* = 1/T2*** (effective transverse relaxation rate, in s⁻¹)

They measure the same underlying physical property, just expressed differently:
- **Quantitative maps (R1, R2*, T1, T2*)**: Give absolute values in physical units
- **Weighted images (T1w, T2*w)**: Give relative contrast, depends on sequence parameters

**Key implication**: If Priovoulos et al. found no R1 or R2* contrast in LC, this means T1 and T2* maps will also show no contrast—they're measuring the same thing.

### Iron Biochemistry: Why R2*/QSM Fail for LC but Work for Substantia Nigra

Understanding why iron-sensitive contrasts fail for LC requires understanding the underlying biochemistry. This is crucial because it explains why the LC behaves differently from the substantia nigra (SN), despite both containing neuromelanin.

**Key findings from the literature:**

> "In healthy individuals, the total iron amount in the locus coeruleus remains stable throughout life and is lower than that in the substantia nigra, in which there is a linear increase in total iron concentration with age. In the substantia nigra, the concentration of ferritin increases with age; thus, iron could contribute more to neurodegeneration in the substantia nigra than in the locus coeruleus. Additionally, the concentration of neuromelanin-iron complexes, which are the dominant form of iron in catecholaminergic neurons, increases with age in the substantia nigra and locus coeruleus."
> — "Iron imbalance in neurodegeneration"

**What this means for imaging:**

1. **Total iron in LC remains stable throughout life**, unlike the SN where total iron increases linearly with age.

2. **Neuromelanin-iron complexes increase with age** in both LC and SN—these are the dominant form of iron in catecholaminergic neurons.

3. **The iron in these complexes is chelated (bound)**, not free. This is critical:
   - QSM and R2* are sensitive to **paramagnetic susceptibility**
   - Free iron (Fe³⁺) is strongly paramagnetic
   - Neuromelanin-chelated iron is only **weakly paramagnetic**, even at high concentrations
   - The chelation effectively "shields" the iron from susceptibility-based imaging

4. **Ferritin concentration increases with age in SN**, contributing additional susceptibility contrast. The LC has less ferritin-bound iron.

**Why the LC and SN differ on iron-sensitive imaging:**

| Structure | Total Iron | Dominant Form | R2*/QSM Signal |
|-----------|------------|---------------|----------------|
| Substantia Nigra | Increases with age | Mixed (ferritin + NM-bound) | Yes |
| Locus Coeruleus | Stable throughout life | Mostly NM-chelated | No |

**Evidence from postmortem studies:**

"The magnetic susceptibility changes of Locus Coeruleus over tau pathology progression" (QSM study on AD patients) found no significant LC-vs-reference contrast even in postmortem tissue. This is striking because:
- Postmortem imaging eliminates physiological noise
- These were older individuals with significant neuromelanin accumulation
- If NM-iron complexes were susceptibility-visible, they should appear here
- Yet no contrast was observed

**Conclusion**: The absence of LC signal in R2*/QSM isn't a technical limitation or sample size issue—it's a fundamental property of how iron is stored in LC neurons. The iron is chelated, rendering it magnetically "invisible" to susceptibility-based methods.

### Why Does MT Work?

Since iron-based contrast fails, we need a different mechanism. Magnetization transfer (MT) works because it's sensitive to the **macromolecular content** of neuromelanin itself, not its iron.

Neuromelanin has high macromolecular content. MT pulses saturate the macromolecular pool, which exchanges magnetization with free water. This creates contrast in neuromelanin-rich regions (LC, substantia nigra) that is distinct from T1, T2*, or susceptibility effects.

The commonly used "neuromelanin-sensitive" T1-TSE sequence at 3T actually derives much of its LC contrast from incidental MT effects in the turbo spin echo train, not from T1 differences per se. This is why dedicated MT sequences (like MTsat from the MPM protocol) provide superior and more quantitative LC contrast.

### Implications for AHEAD Dataset

AHEAD provides MP2RAGEME-derived quantitative maps:

| Map | What It Measures | LC Contrast? | Evidence |
|-----|------------------|--------------|----------|
| R1 | Longitudinal relaxation (1/T1) | **No** | Priovoulos 2018 |
| R2* | Effective transverse relaxation (1/T2*) | **No** | Priovoulos 2018 |
| QSM | Magnetic susceptibility | **No** | ISMRM 2018 |
| T1w | T1-weighted (MP2RAGE UNI) | **No** | No MT preparation |
| T2*w | T2*-weighted | **No** | Same as R2* |

**Expected outcome**: These contrasts will not show significant LC-vs-reference contrast. This is scientifically correct and motivates the need for MTsat sequences in the PhD protocol.

### What About Age Effects?

One study (Unraveling the contributions to the neuromelanin-MRI contrast, 2020) found:

> "In older individuals T1 lengthening occurs in the LC... Longer T1 in subcortical regions during aging is a common finding and may relate to volume loss, e.g., due to the reduced density of the long projections of the LC."

This means:
- T1 *increases* (R1 *decreases*) with age in LC
- This is likely due to atrophy, not neuromelanin accumulation
- It's a confound, not a useful contrast mechanism

So age-stratification using R1 is unlikely to reveal LC signal—it may actually show the opposite pattern from what neuromelanin accumulation would predict.

## Registration Strategy

### Template Selection
- **Target**: MNI152 ICBM 2009c template
- **Source**: Subject 7T T1w (MP2RAGE UNI image)

### ANTs SyN Registration

We use ANTs Symmetric Normalization (SyN) for nonlinear registration:

```python
import ants

fixed = ants.image_read('MNI152_T1_1mm.nii.gz')
moving = ants.image_read('sub-XX_T1w.nii.gz')

registration = ants.registration(
    fixed=fixed,
    moving=moving,
    type_of_transform='SyN',
    syn_metric='CC',           # Cross-correlation
    syn_sampling=4,
    reg_iterations=(100, 70, 50, 20)
)
```

### Transform Application
The computed transforms (affine + warp field) are applied to all contrast maps (R1, R2*, QSM) to bring them into MNI space for atlas application.

### Brainstem-Specific Considerations
- Brainstem registration is challenging due to lower contrast
- Visual QC is essential
- May need to adjust parameters for problematic subjects

## LC Atlas

### Primary Atlas: Ye et al. (2021) 7T Probabilistic Atlas

- **Source**: [NITRC](https://www.nitrc.org/projects/lc_7t_prob)
- **Space**: MNI152
- **Type**: Probabilistic (voxel values = probability of LC membership)
- **Derivation**: Based on 7T MT-weighted imaging

### Atlas Thresholding
- Threshold at 0.5 for binary mask (primary analysis)
- Sensitivity analysis at 0.25 and 0.75

### Reference Region
For CNR calculation, we define a pontine tegmentum reference region:
- Located ventral and medial to LC
- Similar tissue composition (excluding LC neurons)
- Provides baseline for contrast evaluation

MNI coordinates approximately: x=0, y=-30, z=-28

## Signal Extraction

### Metrics Computed

For each contrast map and each subject:

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| mean_lc | mean(signal in LC ROI) | Average signal in LC |
| mean_ref | mean(signal in reference ROI) | Baseline signal |
| std_ref | std(signal in reference ROI) | Noise estimate |
| CNR | (mean_lc - mean_ref) / std_ref | Contrast-to-noise ratio |
| CR | (mean_lc - mean_ref) / mean_ref | Contrast ratio |

### Expected Results

Based on literature:
- **CNR ≈ 0**: No significant contrast between LC and reference
- **This is the scientifically correct outcome** for non-MT contrasts

A CNR near zero confirms that:
1. The literature is correct about MT being necessary
2. The PhD protocol requiring MTsat is well-motivated
3. Standard quantitative maps cannot substitute for neuromelanin-sensitive sequences

## Quality Control

### Registration QC
- Visual inspection of atlas overlay on T1w
- Check for brainstem alignment specifically
- Flag subjects with poor registration

### Exclusion Criteria
- Motion artifacts in source images
- Failed registration (visual inspection)
- Missing contrast maps

## Deliverables

1. **Working pipeline**: Registration → Atlas application → Signal extraction
2. **Contrast evaluation report**: CNR across all AHEAD contrasts (expected: ~0)
3. **QC figures**: Atlas overlays, signal distributions
4. **Documentation**: Reproducible methods and scientific rationale

## Connection to PhD Work

This pipeline provides:

| This Project | PhD Work |
|--------------|----------|
| ANTs registration to MNI | Same workflow, validated on MTsat |
| 7T LC atlas application | Same atlas, with visible contrast |
| CNR computation code | Applied to MTsat (expecting CNR >> 0) |
| QC framework | Extended for test-retest reliability |
| Containerization | Same infrastructure |

The key difference: PhD work uses **MTsat** which *does* produce LC contrast, allowing meaningful quantification. This preliminary work establishes the infrastructure and empirically motivates that protocol choice.

## Why MPI-CBS and the MPM Protocol?

### Technical Considerations

While the MPM method and hMRI toolbox are open source, successfully applying them to LC imaging at 7T requires:

1. **Protocol optimization**: Acquisition parameters (flip angles, TR, off-resonance frequency for MT pulse, etc.) require careful tuning for quantitative accuracy. These optimizations are developed over years of experience and aren't fully captured in published methods sections.

2. **Brainstem-specific challenges**: The LC sits in a region with:
   - Susceptibility artifacts from nearby air-tissue interfaces
   - Physiological noise from cardiac pulsation and CSF flow
   - Registration difficulties due to small structure size
   - B1+ inhomogeneity at 7T affecting quantitative accuracy

3. **Quality control expertise**: Knowing what artifacts look like, what constitutes acceptable data quality, and how to validate measurements—this institutional knowledge is critical.

4. **Hardware considerations**: MPI-CBS's 7T scanner is optimized for quantitative imaging with appropriate RF coils and shimming procedures.

### Why Not Elsewhere?

Technically, any institution with a 7T scanner could acquire MPM data. However:

- **Protocol development time**: Replicating the optimization work would take 1-2 years
- **Validation**: Without existing expertise, how do you know your measurements are correct?
- **Troubleshooting**: When things go wrong (and they will), institutional knowledge matters
- **Funding model**: Max Planck Society's block funding allows foundational/methodological research without constant grant pressure

### Connection to This Preliminary Work

This project demonstrates:
1. Understanding of *why* MTsat is necessary (not just that it works)
2. Familiarity with 7T data characteristics
3. Pipeline infrastructure that transfers directly
4. Rigorous documentation and reproducibility practices

The goal is to arrive at MPI-CBS ready to contribute, not to learn basics.

## References

- Priovoulos N, Jacobs HIL, Ivanov D, Uludag K, Verhey FRJ, Poser BA (2018). High-resolution in vivo imaging of human locus coeruleus by magnetization transfer MRI at 3T and 7T. *NeuroImage*, 168:427-436.
- Ye R, et al. (2021). Locus Coeruleus Atlas. *NITRC*.
- ISMRM 2018 Abstract: MT and QSM of the Locus Coeruleus and Substantia Nigra.
- Unraveling the contributions to the neuromelanin-MRI contrast (2020). *Brain Structure and Function*.
- "Iron imbalance in neurodegeneration" - Review on iron forms in catecholaminergic neurons.
