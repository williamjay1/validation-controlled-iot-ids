# CICIoT2023 Quick Result Ledger

## Top Fine-Grained Runs

| run_id                              | task   | model_name   | imbalance        | feature_strategy   |   top_k |   n_features |   accuracy |   balanced_accuracy |   f1_macro |   f1_weighted |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:------------------------------------|:-------|:-------------|:-----------------|:-------------------|--------:|-------------:|-----------:|--------------------:|-----------:|--------------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| fine_lgbm_random_over               | fine   | lgbm         | random_over      | all                |     nan |           46 |   0.942482 |            0.860391 |   0.882048 |      0.940965 |              0.482143  |            0.397959  | Recon-PingSweep     |       0.906827 |        27.834   |                129.122  |
| fine_lgbm_borderline_smote          | fine   | lgbm         | borderline_smote | all                |     nan |           46 |   0.942399 |            0.858085 |   0.879696 |      0.940817 |              0.446429  |            0.387755  | Recon-PingSweep     |       0.905785 |        30.9983  |                139.3    |
| fine_lgbm_smote                     | fine   | lgbm         | smote            | all                |     nan |           46 |   0.942399 |            0.858637 |   0.876161 |      0.94093  |              0.446429  |            0.387755  | Recon-PingSweep     |       0.903173 |        30.9263  |                136.792  |
| fine_xgb_full_weighted              | fine   | xgb          | class_weight     | all                |     nan |           46 |   0.936616 |            0.881772 |   0.863681 |      0.937978 |              0.553571  |            0.553571  | Uploading_Attack    |       0.912728 |        45.3632  |                 23.9513 |
| fine_hier_lgbm_top20_weighted       | fine   | lgbm         | class_weight     | importance         |      20 |           20 |   0.937416 |            0.853446 |   0.856541 |      0.935941 |              0.553571  |            0.326531  | Recon-PingSweep     |     nan        |        14.4735  |               1175.8    |
| fine_lgbm_full                      | fine   | lgbm         | none             | all                |     nan |           46 |   0.940016 |            0.827543 |   0.84733  |      0.937881 |              0.125     |            0.125     | Uploading_Attack    |       0.874722 |        27.0733  |                134.501  |
| fine_lgbm_full_weighted             | fine   | lgbm         | class_weight     | all                |     nan |           46 |   0.935149 |            0.841282 |   0.843161 |      0.935377 |              0.107143  |            0.107143  | Uploading_Attack    |       0.869121 |        26.5797  |                129.809  |
| fine_rf_full_weighted               | fine   | rf           | class_weight     | all                |     nan |           46 |   0.921932 |            0.853521 |   0.84214  |      0.923413 |              0.553571  |            0.295918  | Recon-PingSweep     |       0.870246 |         8.06511 |                 16.6128 |
| fine_lgbm_importance_top20_weighted | fine   | lgbm         | class_weight     | importance         |      20 |           20 |   0.933799 |            0.841398 |   0.842039 |      0.934146 |              0.178571  |            0.178571  | Uploading_Attack    |       0.869132 |        25.2604  |                153.264  |
| fine_lgbm_mi_top20_weighted         | fine   | lgbm         | class_weight     | mi                 |      20 |           20 |   0.929482 |            0.835537 |   0.835908 |      0.929944 |              0.142857  |            0.142857  | Uploading_Attack    |       0.860853 |        22.449   |                131.397  |
| fine_lgbm_mi_top20                  | fine   | lgbm         | none             | mi                 |      20 |           20 |   0.934632 |            0.81707  |   0.835306 |      0.932188 |              0.0535714 |            0.0535714 | Uploading_Attack    |       0.864531 |        25.9343  |                127.246  |
| fine_lgbm_importance_top10_weighted | fine   | lgbm         | class_weight     | importance         |      10 |           10 |   0.930566 |            0.837427 |   0.834613 |      0.931279 |              0.142857  |            0.142857  | Uploading_Attack    |       0.864618 |        18.0855  |                134.806  |

## Main Comparisons Against Flat LightGBM Baseline

- `fine_lgbm_random_over`: Macro-F1 delta +0.0347, minority-recall delta +0.3571, features 46.
- `fine_lgbm_borderline_smote`: Macro-F1 delta +0.0324, minority-recall delta +0.3214, features 46.
- `fine_lgbm_smote`: Macro-F1 delta +0.0288, minority-recall delta +0.3214, features 46.
- `fine_xgb_full_weighted`: Macro-F1 delta +0.0164, minority-recall delta +0.4286, features 46.
- `fine_hier_lgbm_top20_weighted`: Macro-F1 delta +0.0092, minority-recall delta +0.4286, features 20.
- `fine_lgbm_full_weighted`: Macro-F1 delta -0.0042, minority-recall delta -0.0179, features 46.
- `fine_rf_full_weighted`: Macro-F1 delta -0.0052, minority-recall delta +0.4286, features 46.
- `fine_lgbm_importance_top20_weighted`: Macro-F1 delta -0.0053, minority-recall delta +0.0536, features 20.
- `fine_lgbm_mi_top20_weighted`: Macro-F1 delta -0.0114, minority-recall delta +0.0179, features 20.
- `fine_lgbm_mi_top20`: Macro-F1 delta -0.0120, minority-recall delta -0.0714, features 20.
- `fine_lgbm_importance_top10_weighted`: Macro-F1 delta -0.0127, minority-recall delta +0.0179, features 10.
- `fine_lgbm_mi_top10_weighted`: Macro-F1 delta -0.0518, minority-recall delta -0.0536, features 10.
- `fine_catboost_full_weighted`: Macro-F1 delta -0.0553, minority-recall delta +0.1607, features 46.
- `fine_extratrees_full_weighted`: Macro-F1 delta -0.0766, minority-recall delta +0.1071, features 46.

## Claim Control

- Strong claims are not allowed from this quick stage alone.
- A publishable claim needs either full CICIoT2023 confirmation, external IoTID20/Edge-IIoTset validation, or N-BaIoT unseen-device validation.
- If a lightweight/top-k run preserves Macro-F1 with lower latency, it can support a feature-efficient auxiliary claim.
- If hierarchical classification beats the flat 34-class baseline on Macro-F1 or rare-class recall, it can become an independent paper route.
