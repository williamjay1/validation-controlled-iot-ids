# CICIoT2023 Bootstrap Uncertainty

- Ensemble alpha selected from the internal validation split: 0.50
- Bootstrap design: paired row bootstrap on the frozen CICIoT2023 test file.
- Confidence intervals are percentile intervals.
- PR-AUC is not bootstrapped here because multiclass PR-AUC resampling is computationally expensive; point estimates remain in the main result tables.

## Delta Intervals

| quantity                 |   point_estimate |   ci_low_2_5 |   ci_high_97_5 |   n_bootstrap |
|:-------------------------|-----------------:|-------------:|---------------:|--------------:|
| delta_macro_f1           |        0.0215643 |    0.0185705 |      0.0246242 |          2000 |
| delta_balanced_accuracy  |        0.0437292 |    0.0410084 |      0.0465219 |          2000 |
| delta_minority_recall    |        0.322097  |    0.263533  |      0.383675  |          2000 |
| delta_worst_class_recall |        0.322097  |    0.263533  |      0.379849  |          2000 |
