# Result Ledger

Generated from current result files on 2026-07-09.

## Primary CICIoT2023 Result

Source files:

- `results/ciciot_confirmatory_full/experiment_results.csv`
- `results/ciciot_ensemble_full/experiment_results.csv`
- `results/paper_tables/table1_ciciot_main_results.csv`

| Model | Accuracy | Balanced accuracy | Macro-F1 | Minority recall | Macro PR-AUC |
|---|---:|---:|---:|---:|---:|
| Flat LightGBM | 0.9462 | 0.8446 | 0.8612 | 0.1910 | 0.8863 |
| Borderline-SMOTE LightGBM | 0.9477 | 0.8495 | 0.8674 | 0.2584 | 0.8933 |
| Weighted XGBoost | 0.9359 | 0.8981 | 0.8453 | 0.6592 | 0.9203 |
| Validation-weighted ensemble | 0.9486 | 0.8883 | 0.8828 | 0.5131 | 0.9219 |

Allowed statement: the ensemble is the best current CICIoT2023 operating point because it improves Macro-F1, balanced accuracy, minority recall, and macro PR-AUC relative to flat LightGBM.

## CICIoT2023 Bootstrap Uncertainty

Source file: `results/statistical_uncertainty/ciciot_bootstrap_summary.csv`

| Delta, ensemble minus flat LightGBM | Point estimate | 95% CI |
|---|---:|---|
| Macro-F1 | 0.0216 | 0.0186 to 0.0246 |
| Balanced accuracy | 0.0437 | 0.0410 to 0.0465 |
| Minority recall | 0.3221 | 0.2635 to 0.3837 |
| Worst-class recall | 0.3221 | 0.2635 to 0.3798 |

Allowed statement: paired row bootstrap on the frozen CICIoT2023 test split supports positive ensemble-minus-baseline differences.

## CICIoT2023 Rare-Class Recall

Source file: `results/paper_tables/table2_ciciot_rare_class_recall.csv`

| Class | Flat LightGBM recall | Ensemble recall |
|---|---:|---:|
| Backdoor_Malware | 0.4719 | 0.6406 |
| Recon-PingSweep | 0.4065 | 0.6667 |
| Uploading_Attack | 0.1910 | 0.5131 |
| XSS | 0.3827 | 0.5761 |

Allowed statement: the ensemble materially improves recall for several rare fine-grained attacks.

## IoTID20 Holdout Replication

Source file: `results/paper_tables/table3_iotid20_replication.csv`

| Model | Accuracy | Balanced accuracy | Macro-F1 | Minority recall | Macro PR-AUC |
|---|---:|---:|---:|---:|---:|
| Flat LightGBM | 0.6631 | 0.5994 | 0.6103 | 0.2637 | 0.6784 |
| Weighted LightGBM top ten | 0.6486 | 0.6521 | 0.6209 | 0.4908 | 0.6784 |
| Weighted XGBoost | 0.6318 | 0.6403 | 0.6177 | 0.4803 | 0.6761 |
| Validation-weighted ensemble | 0.6493 | 0.6509 | 0.6202 | 0.4880 | 0.6777 |

Allowed statement: IoTID20 corroborates the value of imbalance-aware weighting and feature efficiency, but it does not support universal ensemble superiority.

## IoTID20 Repeated Split Uncertainty

Source files:

- `results/iotid20_repeated_split/experiment_results.csv`
- `results/iotid20_repeated_split/model_summary.csv`
- `results/iotid20_repeated_split/paired_delta_bootstrap_summary.csv`

Design: 10 stratified 70/30 train-test splits over the IoTID20 preprocessed mirror, seeds 42 through 51, with split-level paired bootstrap intervals for deltas versus flat LightGBM.

| Model | Mean Macro-F1 | SD Macro-F1 | Mean minority recall | SD minority recall | Mean macro PR-AUC |
|---|---:|---:|---:|---:|---:|
| Flat LightGBM | 0.6082 | 0.0037 | 0.2691 | 0.0030 | 0.6798 |
| Weighted LightGBM | 0.6204 | 0.0015 | 0.4853 | 0.0075 | 0.6782 |
| Weighted LightGBM top ten | 0.6222 | 0.0021 | 0.4820 | 0.0081 | 0.6800 |
| Weighted XGBoost | 0.6198 | 0.0014 | 0.4824 | 0.0065 | 0.6775 |
| Validation-weighted ensemble | 0.6220 | 0.0022 | 0.4819 | 0.0078 | 0.6799 |

| Delta versus flat LightGBM | Mean delta | 95% split-bootstrap CI |
|---|---:|---|
| Top ten weighted LightGBM Macro-F1 | +0.0140 | 0.0117 to 0.0165 |
| Top ten weighted LightGBM minority recall | +0.2129 | 0.2075 to 0.2178 |
| Ensemble Macro-F1 | +0.0138 | 0.0114 to 0.0163 |
| Ensemble minority recall | +0.2128 | 0.2077 to 0.2173 |

Allowed statement: repeated IoTID20 holdouts support a split-stable imbalance-aware recall pattern, with modest but consistently positive Macro-F1 gains. The evidence favors a compact weighted LightGBM route on IoTID20 and still does not support universal ensemble superiority.

## N-BaIoT Leave-One-Device-Out Validation

Source files:

- `results/nbaiot_unseen_device_20k/experiment_results.csv`
- `results/nbaiot_unseen_device_20k/classwise_metrics.csv`
- `results/paper_tables/table4_nbaiot_unseen_device_summary.csv`

Design: nine leave-one-device-out folds, 115 numeric features, 20,000-row per-file cap, 1,772,641 rows after cleaning.

| Task | Conservative Macro-F1 mean | Conservative Macro-F1 min | Present-class Macro-F1 mean | Present-class Macro-F1 min | Mean worst present-class recall | Minimum present-class recall |
|---|---:|---:|---:|---:|---:|---:|
| Binary | 0.9998 | 0.9993 | 0.9998 | 0.9993 | 0.9998 | 0.9990 |
| Attack family | 0.9999 | 0.9995 | 0.9999 | 0.9995 | 0.9998 | 0.9990 |
| Fine-grained attack | 0.9435 | 0.7483 | 0.9867 | 0.9621 | 0.8843 | 0.6917 |

Metric note: conservative Macro-F1 follows the standard fold-level prediction output and can be depressed when a held-out device lacks some labels seen in training but the model predicts them. Present-class Macro-F1 averages only classes with nonzero support in the held-out device and is reported alongside worst present-class recall.

Allowed statement: N-BaIoT supports strong binary/family generalization and high average fine-grained attack performance, while weakest-class recall shows meaningful device-level heterogeneity.

## Explainability

Source files:

- `results/paper_tables/table5_ciciot_shap_top_features.csv`
- `results/explainability/ciciot_lgbm_component_shap_importance.csv`

Top feature groups: inter-arrival timing, packet/flow counts, header length, protocol type, reset and synchronize counts, flow duration, packet-size summaries, urgent counts, and rate/magnitude features.

Allowed statement: SHAP analysis provides component-level interpretability for the Borderline-SMOTE LightGBM model inside the final ensemble.
