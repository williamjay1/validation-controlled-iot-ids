# IoTID20 Quick Result Ledger

| run_id                                    | model_name   | imbalance        | feature_strategy   |   top_k |   n_features |   accuracy |   balanced_accuracy |   f1_macro |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:------------------------------------------|:-------------|:-----------------|:-------------------|--------:|-------------:|-----------:|--------------------:|-----------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| iotid_fine_lgbm_mi_top10_weighted         | lgbm         | class_weight     | mi                 |      10 |           10 |   0.64859  |            0.65206  |   0.62089  |               0.490838 |             0.283172 | Mirai-HTTP Flooding |       0.678402 |         9.94984 |               20.3956   |
| iotid_fine_lgbm_weighted                  | lgbm         | class_weight     | all                |     nan |           22 |   0.645538 |            0.648455 |   0.618564 |               0.498648 |             0.285561 | Mirai-HTTP Flooding |       0.676769 |        14.1434  |               20.9166   |
| iotid_fine_lgbm_importance_top10_weighted | lgbm         | class_weight     | importance         |      10 |           10 |   0.644739 |            0.647357 |   0.617707 |               0.494142 |             0.292488 | Mirai-HTTP Flooding |       0.676248 |        10.6688  |               20.2442   |
| iotid_fine_xgb_weighted                   | xgb          | class_weight     | all                |     nan |           22 |   0.645372 |            0.649791 |   0.617651 |               0.480324 |             0.290159 | Mirai-HTTP Flooding |       0.6764   |        21.4708  |                7.35148  |
| iotid_fine_catboost_weighted              | catboost     | class_weight     | all                |     nan |           22 |   0.649591 |            0.655605 |   0.616309 |               0.450436 |             0.218679 | Mirai-HTTP Flooding |       0.6786   |        56.8768  |                0.641245 |
| iotid_fine_lgbm_full                      | lgbm         | none             | all                |     nan |           22 |   0.663089 |            0.599407 |   0.610265 |               0.263743 |             0.251618 | Mirai-Ackflooding   |       0.67844  |        13.9837  |               21.5329   |
| iotid_fine_lgbm_random_over               | lgbm         | random_over      | all                |     nan |           22 |   0.663089 |            0.599407 |   0.610265 |               0.263743 |             0.251618 | Mirai-Ackflooding   |       0.67844  |        13.9139  |               20.8449   |
| iotid_fine_lgbm_smote                     | lgbm         | smote            | all                |     nan |           22 |   0.663089 |            0.599407 |   0.610265 |               0.263743 |             0.251618 | Mirai-Ackflooding   |       0.67844  |        13.9971  |               21.243    |
| iotid_fine_lgbm_borderline_smote          | lgbm         | borderline_smote | all                |     nan |           22 |   0.663089 |            0.599407 |   0.610265 |               0.263743 |             0.251618 | Mirai-Ackflooding   |       0.67844  |        14.2198  |               22.111    |
| iotid_fine_rf_weighted                    | rf           | class_weight     | all                |     nan |           22 |   0.632498 |            0.626192 |   0.605364 |               0.46891  |             0.315001 | Mirai-HTTP Flooding |       0.656184 |        15.0473  |                6.97097  |

## Comparisons Against IoTID20 Flat LightGBM

- `iotid_fine_lgbm_mi_top10_weighted`: Macro-F1 delta +0.0106, minority-recall delta +0.2271, features 10.
- `iotid_fine_lgbm_weighted`: Macro-F1 delta +0.0083, minority-recall delta +0.2349, features 22.
- `iotid_fine_lgbm_importance_top10_weighted`: Macro-F1 delta +0.0074, minority-recall delta +0.2304, features 10.
- `iotid_fine_xgb_weighted`: Macro-F1 delta +0.0074, minority-recall delta +0.2166, features 22.
- `iotid_fine_catboost_weighted`: Macro-F1 delta +0.0060, minority-recall delta +0.1867, features 22.
- `iotid_fine_lgbm_random_over`: Macro-F1 delta +0.0000, minority-recall delta +0.0000, features 22.
- `iotid_fine_lgbm_smote`: Macro-F1 delta +0.0000, minority-recall delta +0.0000, features 22.
- `iotid_fine_lgbm_borderline_smote`: Macro-F1 delta +0.0000, minority-recall delta +0.0000, features 22.
- `iotid_fine_rf_weighted`: Macro-F1 delta -0.0049, minority-recall delta +0.2052, features 22.
