# CICIoT2023 Rare Prior Tuning Ledger

## Data

- Train sampling argument: 220000
- Test sampling argument: 80000
- Rare class scopes were defined from the fit portion of the training split.
- Multipliers and ensemble weights were selected only on the internal validation split.
- Constrained recall objective allowed at most 0.0120 validation Macro-F1 drop.

## Rare Scopes

- `lowest_support`: Uploading_Attack
- `lowest_4_support`: Uploading_Attack, Recon-PingSweep, Backdoor_Malware, XSS
- `lowest_8_support`: Uploading_Attack, Recon-PingSweep, Backdoor_Malware, XSS, SqlInjection, CommandInjection, BrowserHijacking, DictionaryBruteForce

## Test Results

| run_id                                               | objective                   |   alpha_lgbm | rare_scope     |   rare_multiplier |   accuracy |   balanced_accuracy |   f1_macro |   minority_recall_mean |   worst_class_recall | worst_class_label   |   pr_auc_macro |   train_seconds |   inference_ms_per_1000 |
|:-----------------------------------------------------|:----------------------------|-------------:|:---------------|------------------:|-----------:|--------------------:|-----------:|-----------------------:|---------------------:|:--------------------|---------------:|----------------:|------------------------:|
| fine_lgbm_xgb_rare_prior_macro_f1                    | macro_f1                    |          0.5 | lowest_support |                 1 |   0.944987 |            0.877933 |   0.88754  |               0.573333 |             0.553846 | Recon-PingSweep     |       0.915232 |         68.8432 |                 69.7802 |
| fine_lgbm_xgb_rare_prior_macro_f1_plus_minority      | macro_f1_plus_minority      |          0.5 | lowest_support |                 4 |   0.944724 |            0.877516 |   0.880264 |               0.6      |             0.539216 | XSS                 |       0.914926 |         68.8432 |                 69.7802 |
| fine_lgbm_xgb_rare_prior_recall_sensitive            | recall_sensitive            |          0.5 | lowest_support |                 6 |   0.944587 |            0.878252 |   0.878725 |               0.64     |             0.534314 | XSS                 |       0.914737 |         68.8432 |                 69.7802 |
| fine_lgbm_xgb_rare_prior_minority_recall_constrained | minority_recall_constrained |          0.5 | lowest_support |                 6 |   0.944587 |            0.878252 |   0.878725 |               0.64     |             0.534314 | XSS                 |       0.914737 |         68.8432 |                 69.7802 |

## Best Validation Rows

|   alpha_lgbm | rare_scope     |   rare_multiplier |   accuracy |   balanced_accuracy |   f1_macro |   minority_recall_mean |   worst_class_recall |   pr_auc_macro |   composite_score |   recall_weighted_score |
|-------------:|:---------------|------------------:|-----------:|--------------------:|-----------:|-----------------------:|---------------------:|---------------:|------------------:|------------------------:|
|         0.5  | lowest_support |                 6 |   0.943432 |            0.876387 |   0.87941  |               0.710526 |             0.525    |       0.912029 |          0.936253 |                 1.03573 |
|         0.45 | lowest_support |                 6 |   0.942659 |            0.876699 |   0.877151 |               0.710526 |             0.525    |       0.912199 |          0.933993 |                 1.03347 |
|         0.5  | lowest_support |                 4 |   0.943659 |            0.876006 |   0.882269 |               0.684211 |             0.533333 |       0.912056 |          0.937006 |                 1.0328  |
|         0.4  | lowest_support |                 5 |   0.942273 |            0.877859 |   0.875506 |               0.710526 |             0.525    |       0.912034 |          0.932348 |                 1.03182 |
|         0.5  | lowest_support |                 5 |   0.9435   |            0.875915 |   0.880513 |               0.684211 |             0.533333 |       0.912052 |          0.93525  |                 1.03104 |
|         0.4  | lowest_support |                 6 |   0.942227 |            0.877835 |   0.874702 |               0.710526 |             0.525    |       0.912003 |          0.931544 |                 1.03102 |
|         0.45 | lowest_support |                 4 |   0.942818 |            0.876275 |   0.879221 |               0.684211 |             0.533333 |       0.912203 |          0.933958 |                 1.02975 |
|         0.35 | lowest_support |                 5 |   0.941886 |            0.87799  |   0.873108 |               0.710526 |             0.533333 |       0.911761 |          0.92995  |                 1.02942 |
|         0.35 | lowest_support |                 6 |   0.941818 |            0.877961 |   0.872603 |               0.710526 |             0.533333 |       0.911749 |          0.929445 |                 1.02892 |
|         0.45 | lowest_support |                 5 |   0.94275  |            0.876246 |   0.87822  |               0.684211 |             0.533333 |       0.912204 |          0.932957 |                 1.02875 |
|         0.5  | lowest_support |                 3 |   0.943818 |            0.875356 |   0.883954 |               0.657895 |             0.533333 |       0.912078 |          0.936586 |                 1.02869 |
|         0.3  | lowest_support |                 4 |   0.941295 |            0.878591 |   0.872118 |               0.710526 |             0.541667 |       0.911458 |          0.92896  |                 1.02843 |
|         0.8  | lowest_support |                 5 |   0.94275  |            0.861771 |   0.877897 |               0.684211 |             0.318841 |       0.909026 |          0.932634 |                 1.02842 |
|         0.55 | lowest_support |                 4 |   0.943455 |            0.869436 |   0.877829 |               0.684211 |             0.434783 |       0.91151  |          0.932566 |                 1.02836 |
|         0.85 | lowest_support |                 6 |   0.942591 |            0.860876 |   0.877249 |               0.684211 |             0.304348 |       0.908523 |          0.931986 |                 1.02778 |
|         0.75 | lowest_support |                 5 |   0.942977 |            0.862941 |   0.877244 |               0.684211 |             0.333333 |       0.909504 |          0.931981 |                 1.02777 |
|         0.8  | lowest_support |                 6 |   0.942727 |            0.861752 |   0.87688  |               0.684211 |             0.318841 |       0.909029 |          0.931617 |                 1.02741 |
|         0.3  | lowest_support |                 5 |   0.941227 |            0.878562 |   0.870968 |               0.710526 |             0.541667 |       0.911445 |          0.92781  |                 1.02728 |
|         0.4  | lowest_support |                 4 |   0.942318 |            0.877369 |   0.87673  |               0.684211 |             0.533333 |       0.91204  |          0.931466 |                 1.02726 |
|         0.65 | lowest_support |                 5 |   0.943409 |            0.86552  |   0.876596 |               0.684211 |             0.362319 |       0.910374 |          0.931332 |                 1.02712 |

## Claim Control

- This experiment is a validation selected operating point, not a new model architecture.
- If test Macro-F1 drops more than the primary ensemble, report it as a recall sensitive variant only.
- If validation chooses multiplier 1.0, rare prior calibration should not be claimed as useful.
