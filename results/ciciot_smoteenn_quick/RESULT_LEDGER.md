# CICIoT2023 Confirmatory Result Ledger

## Top Fine-Grained Runs

| run_id             | task   | model_name   | imbalance   | feature_strategy   | top_k   |   n_features |   accuracy |   balanced_accuracy |   f1_macro |   f1_weighted |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:-------------------|:-------|:-------------|:------------|:-------------------|:--------|-------------:|-----------:|--------------------:|-----------:|--------------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| fine_lgbm_smoteenn | fine   | lgbm         | smoteenn    | all                |         |           46 |   0.917449 |            0.841228 |   0.808241 |      0.922237 |               0.706667 |              0.47486 | Backdoor_Malware    |       0.849492 |         86.8269 |                 139.478 |


## Claim Control

- Strong claims are not allowed from this quick stage alone.
- A publishable claim needs either full CICIoT2023 confirmation, external IoTID20/Edge-IIoTset validation, or N-BaIoT unseen-device validation.
- If a lightweight/top-k run preserves Macro-F1 with lower latency, it can support a feature-efficient auxiliary claim.
- If hierarchical classification beats the flat 34-class baseline on Macro-F1 or rare-class recall, it can become an independent paper route.
