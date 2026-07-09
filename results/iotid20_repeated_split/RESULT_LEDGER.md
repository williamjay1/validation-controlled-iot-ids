# IoTID20 Repeated Split Uncertainty

## Design

- Dataset rows after cleaning/sampling: 625,783
- Repeated splits: 10
- Split seeds: 42 to 51
- Test fraction: 0.3
- Fixed factors: data cleaning, feature space, model families, class-weighting strategy, metric definitions.
- Varying factor: stratified train/test split random seed.

## Model Summary

| run_id                                  |   n_splits |   mean_macro_f1 |   sd_macro_f1 |   mean_balanced_accuracy |   mean_minority_recall |   sd_minority_recall |   mean_pr_auc_macro |   mean_train_seconds |   mean_inference_ms_per_1000 |
|:----------------------------------------|-----------:|----------------:|--------------:|-------------------------:|-----------------------:|---------------------:|--------------------:|---------------------:|-----------------------------:|
| iotid_fine_lgbm_mi_top10_weighted       |         10 |        0.622194 |    0.0020554  |                 0.65401  |               0.482022 |           0.00814387 |            0.679958 |              8.28387 |                     18.3717  |
| iotid_fine_lgbm_xgb_validation_ensemble |         10 |        0.621963 |    0.0021821  |                 0.653837 |               0.481947 |           0.00783572 |            0.679917 |             26.3971  |                     12.55    |
| iotid_fine_lgbm_weighted                |         10 |        0.620418 |    0.00146984 |                 0.650527 |               0.485341 |           0.00747906 |            0.678222 |             12.1779  |                     18.9853  |
| iotid_fine_xgb_weighted                 |         10 |        0.619782 |    0.00139373 |                 0.652066 |               0.482352 |           0.00649159 |            0.677507 |             18.6245  |                      6.58472 |
| iotid_fine_lgbm_mi_top10_flat           |         10 |        0.611283 |    0.0043017  |                 0.600506 |               0.267918 |           0.00301872 |            0.68171  |              8.08096 |                     18.3284  |
| iotid_fine_lgbm_full                    |         10 |        0.608152 |    0.00373123 |                 0.597249 |               0.269105 |           0.00298385 |            0.679843 |             11.9267  |                     18.7514  |

## Paired Delta Summary vs Flat LightGBM

| run_id                                  | metric               |   mean_delta_vs_flat_lgbm |    sd_delta |   ci_low_2_5 |   ci_high_97_5 |   n_splits |   bootstrap_reps |
|:----------------------------------------|:---------------------|--------------------------:|------------:|-------------:|---------------:|-----------:|-----------------:|
| iotid_fine_lgbm_mi_top10_weighted       | f1_macro             |               0.0140426   | 0.00411177  |  0.0116969   |    0.0164524   |         10 |            10000 |
| iotid_fine_lgbm_xgb_validation_ensemble | f1_macro             |               0.0138112   | 0.00425129  |  0.0113713   |    0.0163032   |         10 |            10000 |
| iotid_fine_lgbm_weighted                | f1_macro             |               0.0122668   | 0.003686    |  0.0101976   |    0.0144455   |         10 |            10000 |
| iotid_fine_xgb_weighted                 | f1_macro             |               0.0116301   | 0.00386719  |  0.0094397   |    0.0139227   |         10 |            10000 |
| iotid_fine_lgbm_mi_top10_flat           | f1_macro             |               0.0031312   | 0.00187456  |  0.00203721  |    0.00424894  |         10 |            10000 |
| iotid_fine_lgbm_weighted                | minority_recall_mean |               0.216236    | 0.00829149  |  0.21167     |    0.221433    |         10 |            10000 |
| iotid_fine_xgb_weighted                 | minority_recall_mean |               0.213247    | 0.00545356  |  0.209928    |    0.216281    |         10 |            10000 |
| iotid_fine_lgbm_mi_top10_weighted       | minority_recall_mean |               0.212917    | 0.00872375  |  0.207539    |    0.217798    |         10 |            10000 |
| iotid_fine_lgbm_xgb_validation_ensemble | minority_recall_mean |               0.212842    | 0.00819309  |  0.207675    |    0.217287    |         10 |            10000 |
| iotid_fine_lgbm_mi_top10_flat           | minority_recall_mean |              -0.00118654  | 0.000783483 | -0.00166717  |   -0.000750976 |         10 |            10000 |
| iotid_fine_lgbm_mi_top10_flat           | pr_auc_macro         |               0.00186706  | 0.00051872  |  0.00157348  |    0.00218474  |         10 |            10000 |
| iotid_fine_lgbm_mi_top10_weighted       | pr_auc_macro         |               0.000114984 | 0.000527894 | -0.000188551 |    0.000430911 |         10 |            10000 |
| iotid_fine_lgbm_xgb_validation_ensemble | pr_auc_macro         |               7.44242e-05 | 0.000503323 | -0.000212045 |    0.000375885 |         10 |            10000 |
| iotid_fine_lgbm_weighted                | pr_auc_macro         |              -0.00162071  | 0.00029696  | -0.00178213  |   -0.00143373  |         10 |            10000 |
| iotid_fine_xgb_weighted                 | pr_auc_macro         |              -0.00233555  | 0.000558932 | -0.00269218  |   -0.00205089  |         10 |            10000 |

## Exact Sign-Flip Summary vs Flat LightGBM

| run_id                                  | metric               |   mean_delta_vs_flat_lgbm |   positive_splits |   negative_splits |   zero_splits |   n_splits |   exact_two_sided_p |
|:----------------------------------------|:---------------------|--------------------------:|------------------:|------------------:|--------------:|-----------:|--------------------:|
| iotid_fine_lgbm_mi_top10_weighted       | f1_macro             |               0.0140426   |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_xgb_validation_ensemble | f1_macro             |               0.0138112   |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_weighted                | f1_macro             |               0.0122668   |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_xgb_weighted                 | f1_macro             |               0.0116301   |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_mi_top10_flat           | f1_macro             |               0.0031312   |                 9 |                 1 |             0 |         10 |          0.00390625 |
| iotid_fine_lgbm_weighted                | minority_recall_mean |               0.216236    |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_xgb_weighted                 | minority_recall_mean |               0.213247    |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_mi_top10_weighted       | minority_recall_mean |               0.212917    |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_xgb_validation_ensemble | minority_recall_mean |               0.212842    |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_mi_top10_flat           | minority_recall_mean |              -0.00118654  |                 0 |                 9 |             1 |         10 |          0.00390625 |
| iotid_fine_lgbm_mi_top10_flat           | pr_auc_macro         |               0.00186706  |                10 |                 0 |             0 |         10 |          0.00195312 |
| iotid_fine_lgbm_mi_top10_weighted       | pr_auc_macro         |               0.000114984 |                 5 |                 5 |             0 |         10 |          0.515625   |
| iotid_fine_lgbm_xgb_validation_ensemble | pr_auc_macro         |               7.44242e-05 |                 5 |                 5 |             0 |         10 |          0.652344   |
| iotid_fine_lgbm_weighted                | pr_auc_macro         |              -0.00162071  |                 0 |                10 |             0 |         10 |          0.00195312 |
| iotid_fine_xgb_weighted                 | pr_auc_macro         |              -0.00233555  |                 0 |                10 |             0 |         10 |          0.00195312 |

## Claim Control

- Positive intervals for minority recall support the robustness of imbalance-aware recall gains across random holdout splits.
- Positive Macro-F1 intervals support split-stable gains for the tested IoTID20 holdout design, but the gains are modest and should be presented alongside the larger recall gains.
- IoTID20 remains an independent holdout replication because the local mirror lacks an official split.
