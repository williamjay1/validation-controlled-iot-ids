# Hyperparameter Table

## Shared Settings

| Setting | Value |
|---|---|
| Random seed | 42 |
| Feature preprocessing | Numeric features only; no scaling for tree models |
| Label encoding | Fitted on training labels only |
| CICIoT ensemble alpha grid | 0.00 to 1.00, step 0.05 |
| CICIoT selected alpha | 0.50 |
| IoTID20 selected alpha | 0.80 for Macro-F1 objective |
| CICIoT paired row bootstrap resamples | 2,000 for the current Scientific Reports candidate |
| IoTID20 split bootstrap resamples | 10,000 over 10 repeated holdouts |

## LightGBM

| Parameter | Value |
|---|---|
| objective | binary or multiclass by task |
| n_estimators | 220 |
| learning_rate | 0.06 |
| num_leaves | 63 |
| max_depth | -1 |
| min_child_samples | 40 |
| subsample | 0.9 |
| colsample_bytree | 0.9 |
| reg_lambda | 1.0 |
| n_jobs | -1 |

## XGBoost

| Parameter | Value |
|---|---|
| objective | binary:logistic or multi:softprob by task |
| n_estimators | 220 |
| max_depth | 7 |
| learning_rate | 0.08 |
| subsample | 0.9 |
| colsample_bytree | 0.9 |
| tree_method | hist |
| eval_metric | logloss or mlogloss |
| n_jobs | -1 |

## Random Forest / ExtraTrees Screening

| Model | Key settings |
|---|---|
| RandomForestClassifier | n_estimators=160, min_samples_leaf=2, n_jobs=-1 |
| ExtraTreesClassifier | n_estimators=180, min_samples_leaf=2, n_jobs=-1 |

## CatBoost Screening

| Parameter | Value |
|---|---|
| iterations | 220 |
| depth | 7 |
| learning_rate | 0.08 |
| loss_function | Logloss or MultiClass |
| allow_writing_files | False |
| thread_count | -1 |

## Oversampling

| Strategy | Implementation |
|---|---|
| Random oversampling | imbalanced-learn RandomOverSampler |
| SMOTE | imbalanced-learn SMOTE |
| Borderline-SMOTE | imbalanced-learn BorderlineSMOTE |
| CICIoT fine-class oversampling floor | 2,500 rows per minority class |
| CICIoT fine-class oversampling cap | 12,000 rows per minority class |
| SMOTE/Borderline-SMOTE k_neighbors | Adaptive: max(1, min(5, smallest training-class count - 1)) |
| Borderline-SMOTE m_neighbors | imbalanced-learn default |
