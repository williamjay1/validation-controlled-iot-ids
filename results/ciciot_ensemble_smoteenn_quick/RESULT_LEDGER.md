# CICIoT2023 SMOTEENN Three Component Ensemble Ledger

## Data

- Train sampling argument: 220000
- Test sampling argument: 80000
- Weight selection used only an internal validation split from the training file.

## Test Results

| run_id                                                 | objective              |   w_lgbm_borderline |   w_xgb_weighted |   w_lgbm_smoteenn |   accuracy |   balanced_accuracy |   f1_macro |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:-------------------------------------------------------|:-----------------------|--------------------:|-----------------:|------------------:|-----------:|--------------------:|-----------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| fine_lgbm_xgb_smoteenn_ensemble_macro_f1               | macro_f1               |                 0.5 |              0.5 |                 0 |   0.944987 |            0.877933 |    0.88754 |               0.573333 |             0.553846 | Recon-PingSweep     |       0.915232 |         310.705 |                 155.923 |
| fine_lgbm_xgb_smoteenn_ensemble_macro_f1_plus_minority | macro_f1_plus_minority |                 0.5 |              0.5 |                 0 |   0.944987 |            0.877933 |    0.88754 |               0.573333 |             0.553846 | Recon-PingSweep     |       0.915232 |         310.705 |                 155.923 |
| fine_lgbm_xgb_smoteenn_ensemble_recall_sensitive       | recall_sensitive       |                 0.5 |              0.5 |                 0 |   0.944987 |            0.877933 |    0.88754 |               0.573333 |             0.553846 | Recon-PingSweep     |       0.915232 |         310.705 |                 155.923 |

## Best Validation Weights

|   w_lgbm_borderline |   w_xgb_weighted |   w_lgbm_smoteenn |   f1_macro |   minority_recall_mean |   pr_auc_macro |   composite_score |   recall_weighted_score |
|--------------------:|-----------------:|------------------:|-----------:|-----------------------:|---------------:|------------------:|------------------------:|
|                0.5  |             0.5  |              0    |   0.886507 |               0.578947 |       0.912097 |          0.932823 |                0.979139 |
|                0.8  |             0.2  |              0    |   0.881201 |               0.605263 |       0.908962 |          0.929622 |                0.978043 |
|                0.85 |             0.15 |              0    |   0.880913 |               0.605263 |       0.908427 |          0.929334 |                0.977755 |
|                0.75 |             0.2  |              0.05 |   0.880853 |               0.605263 |       0.908508 |          0.929274 |                0.977695 |
|                0.7  |             0.25 |              0.05 |   0.880672 |               0.605263 |       0.909056 |          0.929093 |                0.977514 |
|                0.7  |             0.1  |              0.2  |   0.876372 |               0.631579 |       0.902691 |          0.926899 |                0.977425 |
|                0.95 |             0.05 |              0    |   0.880483 |               0.605263 |       0.906493 |          0.928904 |                0.977325 |
|                0.85 |             0.1  |              0.05 |   0.880418 |               0.605263 |       0.906651 |          0.928839 |                0.97726  |
|                0.9  |             0.1  |              0    |   0.880416 |               0.605263 |       0.907605 |          0.928837 |                0.977258 |
|                0.9  |             0.05 |              0.05 |   0.880365 |               0.605263 |       0.905177 |          0.928786 |                0.977208 |
|                0.75 |             0.15 |              0.1  |   0.88034  |               0.605263 |       0.906518 |          0.928761 |                0.977182 |
|                0.45 |             0.55 |              0    |   0.884434 |               0.578947 |       0.912213 |          0.93075  |                0.977065 |
|                0.8  |             0.15 |              0.05 |   0.880133 |               0.605263 |       0.907747 |          0.928554 |                0.976975 |
|                0.6  |             0.3  |              0.1  |   0.88013  |               0.605263 |       0.909042 |          0.928551 |                0.976972 |
|                0.95 |             0    |              0.05 |   0.880112 |               0.605263 |       0.903039 |          0.928533 |                0.976955 |
|                0.65 |             0.25 |              0.1  |   0.880086 |               0.605263 |       0.908279 |          0.928507 |                0.976928 |
|                1    |             0    |              0    |   0.879859 |               0.605263 |       0.904356 |          0.92828  |                0.976701 |
|                0.7  |             0.2  |              0.1  |   0.879651 |               0.605263 |       0.907539 |          0.928073 |                0.976494 |
|                0.85 |             0.05 |              0.1  |   0.879275 |               0.605263 |       0.903472 |          0.927697 |                0.976118 |
|                0.6  |             0.25 |              0.15 |   0.879253 |               0.605263 |       0.90749  |          0.927674 |                0.976095 |

## Claim Control

- If the recall sensitive operating point sacrifices Macro-F1, it should be written as an optional operating point.
- A stronger manuscript claim requires full train/test confirmation and comparison against the current two component ensemble.
