# CICIoT2023 Confirmatory Result Ledger

## Top Fine-Grained Runs

| run_id                     | task   | model_name   | imbalance        | feature_strategy   | top_k   |   n_features |   accuracy |   balanced_accuracy |   f1_macro |   f1_weighted |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:---------------------------|:-------|:-------------|:-----------------|:-------------------|:--------|-------------:|-----------:|--------------------:|-----------:|--------------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| fine_lgbm_borderline_smote | fine   | lgbm         | borderline_smote | all                |         |           46 |   0.947701 |            0.849523 |   0.867376 |      0.946118 |               0.258427 |             0.258427 | Uploading_Attack    |       0.89326  |         156.747 |                171.496  |
| fine_lgbm_smote            | fine   | lgbm         | smote            | all                |         |           46 |   0.946883 |            0.845226 |   0.86225  |      0.945291 |               0.209738 |             0.209738 | Uploading_Attack    |       0.890166 |         136.334 |                159.579  |
| fine_lgbm_full             | fine   | lgbm         | none             | all                |         |           46 |   0.946162 |            0.844591 |   0.861196 |      0.944523 |               0.191011 |             0.191011 | Uploading_Attack    |       0.886277 |         136.103 |                161.256  |
| fine_lgbm_random_over      | fine   | lgbm         | random_over      | all                |         |           46 |   0.946529 |            0.843937 |   0.860249 |      0.944955 |               0.224719 |             0.224719 | Uploading_Attack    |       0.884141 |         135.337 |                164.467  |
| fine_xgb_full_weighted     | fine   | xgb          | class_weight     | all                |         |           46 |   0.935856 |            0.898058 |   0.845265 |      0.940604 |               0.659176 |             0.63786  | XSS                 |       0.920308 |         277.982 |                 27.5615 |

## Main Comparisons Against Flat LightGBM Baseline

- `fine_lgbm_borderline_smote`: Macro-F1 delta +0.0062, minority-recall delta +0.0674, features 46.
- `fine_lgbm_smote`: Macro-F1 delta +0.0011, minority-recall delta +0.0187, features 46.
- `fine_lgbm_random_over`: Macro-F1 delta -0.0009, minority-recall delta +0.0337, features 46.
- `fine_xgb_full_weighted`: Macro-F1 delta -0.0159, minority-recall delta +0.4682, features 46.

## Claim Control

- Strong claims are not allowed from this quick stage alone.
- A publishable claim needs either full CICIoT2023 confirmation, external IoTID20/Edge-IIoTset validation, or N-BaIoT unseen-device validation.
- If a lightweight/top-k run preserves Macro-F1 with lower latency, it can support a feature-efficient auxiliary claim.
- If hierarchical classification beats the flat 34-class baseline on Macro-F1 or rare-class recall, it can become an independent paper route.
