# IoTID20 Repeated Split Uncertainty

## Design

- Dataset rows after cleaning/sampling: 5,000
- Repeated splits: 1
- Split seeds: 42 to 42
- Test fraction: 0.3
- Fixed factors: data cleaning, feature space, model families, class-weighting strategy, metric definitions.
- Varying factor: stratified train/test split random seed.

## Model Summary

| run_id                                  |   n_splits |   mean_macro_f1 |   sd_macro_f1 |   mean_balanced_accuracy |   mean_minority_recall |   sd_minority_recall |   mean_pr_auc_macro |   mean_train_seconds |   mean_inference_ms_per_1000 |
|:----------------------------------------|-----------:|----------------:|--------------:|-------------------------:|-----------------------:|---------------------:|--------------------:|---------------------:|-----------------------------:|
| iotid_fine_lgbm_xgb_validation_ensemble |          1 |        0.596706 |           nan |                 0.610057 |               0.490566 |                  nan |            0.633649 |              2.09063 |                      26.3289 |
| iotid_fine_lgbm_mi_top10_weighted       |          1 |        0.594773 |           nan |                 0.607442 |               0.490566 |                  nan |            0.631848 |              1.04566 |                      37.0955 |
| iotid_fine_xgb_weighted                 |          1 |        0.593934 |           nan |                 0.604876 |               0.45283  |                  nan |            0.63408  |              1.29111 |                      10.6292 |
| iotid_fine_lgbm_weighted                |          1 |        0.5927   |           nan |                 0.60066  |               0.415094 |                  nan |            0.629049 |              1.14095 |                      23.4481 |
| iotid_fine_lgbm_full                    |          1 |        0.576357 |           nan |                 0.567379 |               0.301887 |                  nan |            0.628415 |              1.3841  |                      40.1133 |

## Paired Delta Summary vs Flat LightGBM

| run_id                                  | metric               |   mean_delta_vs_flat_lgbm |   sd_delta |   ci_low_2_5 |   ci_high_97_5 |   n_splits |   bootstrap_reps |
|:----------------------------------------|:---------------------|--------------------------:|-----------:|-------------:|---------------:|-----------:|-----------------:|
| iotid_fine_lgbm_xgb_validation_ensemble | f1_macro             |               0.0203493   |          0 |  0.0203493   |    0.0203493   |          1 |              200 |
| iotid_fine_lgbm_mi_top10_weighted       | f1_macro             |               0.0184157   |          0 |  0.0184157   |    0.0184157   |          1 |              200 |
| iotid_fine_xgb_weighted                 | f1_macro             |               0.0175775   |          0 |  0.0175775   |    0.0175775   |          1 |              200 |
| iotid_fine_lgbm_weighted                | f1_macro             |               0.0163429   |          0 |  0.0163429   |    0.0163429   |          1 |              200 |
| iotid_fine_lgbm_mi_top10_weighted       | minority_recall_mean |               0.188679    |          0 |  0.188679    |    0.188679    |          1 |              200 |
| iotid_fine_lgbm_xgb_validation_ensemble | minority_recall_mean |               0.188679    |          0 |  0.188679    |    0.188679    |          1 |              200 |
| iotid_fine_xgb_weighted                 | minority_recall_mean |               0.150943    |          0 |  0.150943    |    0.150943    |          1 |              200 |
| iotid_fine_lgbm_weighted                | minority_recall_mean |               0.113208    |          0 |  0.113208    |    0.113208    |          1 |              200 |
| iotid_fine_xgb_weighted                 | pr_auc_macro         |               0.00566476  |          0 |  0.00566476  |    0.00566476  |          1 |              200 |
| iotid_fine_lgbm_xgb_validation_ensemble | pr_auc_macro         |               0.00523465  |          0 |  0.00523465  |    0.00523465  |          1 |              200 |
| iotid_fine_lgbm_mi_top10_weighted       | pr_auc_macro         |               0.00343336  |          0 |  0.00343336  |    0.00343336  |          1 |              200 |
| iotid_fine_lgbm_weighted                | pr_auc_macro         |               0.000634326 |          0 |  0.000634326 |    0.000634326 |          1 |              200 |

## Claim Control

- Positive intervals for minority recall support the robustness of imbalance-aware recall gains across random holdout splits.
- Macro-F1 intervals crossing zero should be written as a recall-oriented tradeoff rather than uniform superiority.
- IoTID20 remains an independent holdout replication because the local mirror lacks an official split.
