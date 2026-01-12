# Project Plan: 7T LC Quantification Pipeline

## Goal

Demonstrate technical competence for MPI-CBS PhD interview by building a reproducible 7T LC localization pipeline and documenting contrast limitations of available data.

## Timeline: ~2 Weeks

### Week 1: Infrastructure & Single Subject

**Days 1-2: Environment Setup**
- [ ] Set up Python environment with ANTs, nibabel, nilearn
- [ ] Download 1-3 AHEAD subjects for development
- [ ] Download Ye et al. 7T LC atlas
- [ ] Verify data loading works

**Days 3-4: Registration Pipeline**
- [ ] Implement T1w → MNI registration using ANTs SyN
- [ ] Test on single subject, visually verify alignment
- [ ] Apply transforms to R1, R2*, QSM maps
- [ ] Document registration parameters

**Days 5-7: Atlas Application & Extraction**
- [ ] Load and threshold LC atlas
- [ ] Define pontine reference region (or use existing mask)
- [ ] Implement signal extraction function
- [ ] Compute CNR for all contrasts on test subjects
- [ ] Generate QC overlay figures

### Week 2: Scale Up & Documentation

**Days 8-10: Batch Processing**
- [ ] Process all 105 AHEAD subjects (or subset)
- [ ] Implement QC checks and flagging
- [ ] Compile results into summary CSV

**Days 11-12: Analysis & Visualization**
- [ ] Generate CNR comparison figures
- [ ] Age-stratified exploratory analysis (if time permits)
- [ ] Create summary statistics table

**Days 13-14: Documentation & Polish**
- [ ] Finalize README and methods docs
- [ ] Clean up notebooks
- [ ] Prepare 2-3 key figures for presentation
- [ ] Write brief summary of findings

## Deliverables

### Primary (Must Have)
1. **Working pipeline**: Registration → Atlas → Extraction
2. **CNR evaluation**: Documenting that R1/R2*/QSM show no LC contrast
3. **QC figures**: Atlas overlay on representative subjects
4. **README**: Clear framing of project goals and findings

### Secondary (Nice to Have)
- Docker/Singularity container
- Age-stratified analysis
- Multiple atlas comparison (Keren vs Ye)
- Full 105-subject processing

## Key Figures for Presentation

1. **Atlas overlay on T1w**: Shows accurate registration and LC localization
2. **CNR by contrast type**: Box plot showing all contrasts near zero
3. **Pipeline diagram**: Visual workflow summary

## Talking Points for Interview

1. "I built a reproducible pipeline for 7T LC analysis using the best available public data"
2. "The available contrasts (R1, R2*, QSM) don't show LC signal—this is expected based on the literature and motivates the need for MTsat"
3. "The pipeline infrastructure (registration, atlas application, QC framework) transfers directly to the PhD work"
4. "I understand *why* different sequences produce different contrasts—MT effects are key for neuromelanin"

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Registration failures | Manual QC, adjust parameters, exclude problematic subjects |
| Atlas misalignment | Use multiple atlases, report sensitivity |
| No time for full dataset | Prioritize quality over quantity; 10-20 subjects is sufficient |
| Compute limitations | Use subset, document scalability plan |

## Success Criteria

**Minimum viable**: 
- Pipeline runs on 5+ subjects
- CNR computed for all contrasts
- 1-2 QC figures generated
- README clearly explains findings

**Stretch goal**:
- Full 105 subjects processed
- Age-stratified analysis
- Containerized pipeline
