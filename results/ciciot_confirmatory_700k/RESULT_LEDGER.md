# CICIoT2023 Confirmatory Result Ledger

## Top Fine-Grained Runs

| run_id                     | task   | model_name   | imbalance        | feature_strategy   | top_k   |   n_features |   accuracy |   balanced_accuracy |   f1_macro |   f1_weighted |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:---------------------------|:-------|:-------------|:-----------------|:-------------------|:--------|-------------:|-----------:|--------------------:|-----------:|--------------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| fine_lgbm_borderline_smote | fine   | lgbm         | borderline_smote | all                |         |           46 |   0.945605 |            0.853402 |   0.870623 |      0.944035 |               0.459893 |             0.360784 | XSS                 |       0.897255 |         87.1423 |                153.599  |
| fine_lgbm_smote            | fine   | lgbm         | smote            | all                |         |           46 |   0.946635 |            0.846816 |   0.864509 |      0.944999 |               0.283422 |             0.283422 | Uploading_Attack    |       0.890331 |         88.5309 |                150.677  |
| fine_lgbm_random_over      | fine   | lgbm         | random_over      | all                |         |           46 |   0.946045 |            0.844857 |   0.86201  |      0.944349 |               0.251337 |             0.251337 | Uploading_Attack    |       0.886769 |         85.5564 |                150.619  |
| fine_lgbm_full             | fine   | lgbm         | none             | all                |         |           46 |   0.94479  |            0.841856 |   0.858332 |      0.943106 |               0.13369  |             0.13369  | Uploading_Attack    |       0.887843 |         85.0235 |                153.402  |
| fine_xgb_full_weighted     | fine   | xgb          | class_weight     | all                |         |           46 |   0.93638  |            0.896139 |   0.849109 |      0.940161 |               0.620321 |             0.619608 | XSS                 |       0.918245 |        175.613  |                 27.0479 |

## Main Comparisons Against Flat LightGBM Baseline

- `fine_lgbm_borderline_smote`: Macro-F1 delta +0.0123, minority-recall delta +0.3262, features 46.
- `fine_lgbm_smote`: Macro-F1 delta +0.0062, minority-recall delta +0.1497, features 46.
- `fine_lgbm_random_over`: Macro-F1 delta +0.0037, minority-recall delta +0.1176, features 46.
- `fine_xgb_full_weighted`: Macro-F1 delta -0.0092, minority-recall delta +0.4866, features 46.

## Claim Control

- Strong claims are not allowed from this quick stage alone.
- A publishable claim needs either full CICIoT2023 confirmation, external IoTID20/Edge-IIoTset validation, or N-BaIoT unseen-device validation.
- If a lightweight/top-k run preserves Macro-F1 with lower latency, it can support a feature-efficient auxiliary claim.
- If hierarchical classification beats the flat 34-class baseline on Macro-F1 or rare-class recall, it can become an independent paper route.
