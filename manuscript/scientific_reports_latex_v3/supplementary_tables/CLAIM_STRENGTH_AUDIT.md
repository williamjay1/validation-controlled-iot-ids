# Claim Strength Audit

Checked against generated results on 2026-07-09.

## Strong Claims

| Claim | Strength | Evidence |
|---|---|---|
| The validation-weighted ensemble improves the CICIoT2023 public subsample test result over flat LightGBM. | Strong | Table 1; ensemble Macro-F1 0.8828 vs 0.8612, minority recall 0.5131 vs 0.1910, macro PR-AUC 0.9219 vs 0.8863. |
| The CICIoT2023 public subsample gain is stable under paired bootstrap resampling of the frozen test set. | Strong | Bootstrap 2,000 resamples; Macro-F1 delta 95% CI 0.0186 to 0.0246; minority recall delta 0.2635 to 0.3837. |
| Rare CICIoT2023 attack classes benefit materially from the ensemble. | Strong | Uploading_Attack, Recon-PingSweep, Backdoor_Malware, and XSS recall all improve versus flat LightGBM. |
| IoTID20 supports a split stable imbalance aware recall pattern. | Strong but scoped | Across 10 stratified holdout splits, top ten weighted LightGBM improved Macro-F1 by 0.0140 (95% split bootstrap CI 0.0117 to 0.0165) and minority recall by 0.2129 (0.2075 to 0.2178) versus flat LightGBM. |
| N-BaIoT capped leave one device out validation supports strong binary and family level unseen device detection under the 20k cap. | Strong but scoped | Binary Macro-F1 0.9998; family Macro-F1 0.9999 across nine held out devices, interpreted as capped sample upper bound evidence. |

## Moderate Claims

| Claim | Strength | Evidence and caution |
|---|---|---|
| Fine grained N-BaIoT attack detection generalizes across unseen devices. | Moderate | Present class Macro-F1 is high at 0.9867, but conservative Macro-F1 is 0.9435 and the weakest present class recall is 0.6917. |
| IoTID20 favors a compact weighted LightGBM rather than the ensemble. | Moderate | Repeated splits show top ten weighted LightGBM has the highest mean Macro-F1 (0.6222), while the validation ensemble is very close (0.6220) and usually selects an LGBM heavy alpha. |
| SHAP features are behaviorally plausible. | Moderate | Top features align with timing, protocol, flag/count, and packet-size behavior, but explanation is for the LightGBM component rather than the full ensemble. |

## Claims That Must Be Downgraded

| Do not write | Safer wording |
|---|---|
| The proposed model is universally robust across IoT devices. | The evaluated models show strong average unseen-device performance with device- and class-specific heterogeneity. |
| The ensemble is best across all datasets. | The ensemble is best on the main CICIoT2023 experiment; IoTID20 favors a compact weighted LightGBM variant. |
| The complete original CICIoT2023 corpus was used. | The full downloaded public Hugging Face CICIoT2023 public subsample was used, with original CICIoT2023 cited for provenance. |
| N-BaIoT was fully exhaustively evaluated. | N-BaIoT was evaluated with a capped leave one device out design and a 20,000 row per file cap. |
| SHAP explains the full ensemble. | SHAP explains the Borderline-SMOTE LightGBM component of the ensemble. |

## Missing Before Submission

- Public repository or archive DOI for code and generated result tables.
- Public repository or archive DOI remains the main pre submission blocker.
- Final cross-check that every numeric claim in the manuscript appears in a generated CSV or result ledger.
