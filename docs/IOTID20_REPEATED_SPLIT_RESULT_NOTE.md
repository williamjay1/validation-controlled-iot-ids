# IoTID20 Repeated Split Result Note

Generated on 2026-07-08 from `results/iotid20_repeated_split/`.

## Design

- Dataset: IoTID20 preprocessed mirror, 625,783 usable rows after inf/NA removal.
- Validation: 10 stratified 70/30 train-test splits, seeds 42 through 51.
- Fixed factors: data cleaning, feature space, metric definitions, model hyperparameters, class weighting, and top ten mutual information feature selection procedure.
- Varying factor: split random seed.
- Uncertainty: split-level paired bootstrap with 10,000 resamples for deltas versus flat LightGBM.

## Main Result

The repeated split experiment strengthens the IoTID20 evidence. The top ten mutual information class weighted LightGBM achieved mean Macro-F1 0.6222 (SD 0.0021), mean minority recall 0.4820 (SD 0.0081), and mean macro PR-AUC 0.6800 across 10 splits. The flat LightGBM baseline achieved mean Macro-F1 0.6082 (SD 0.0037), mean minority recall 0.2691 (SD 0.0030), and mean macro PR-AUC 0.6798.

Against flat LightGBM, the top ten weighted LightGBM had a paired Macro-F1 delta of +0.0140 with split bootstrap 95% CI 0.0117 to 0.0165, and a minority recall delta of +0.2129 with 95% CI 0.2075 to 0.2178. The validation selected LGBM/XGBoost ensemble was similar but slightly lower on mean Macro-F1 (0.6220) and minority recall (0.4819); alpha selected the LGBM heavy solution in all 10 splits, including alpha = 1.00 in 7 of 10 splits.

## Claim Impact

- Upgraded: IoTID20 now supports a split-stable imbalance-aware recall pattern, not merely a single 70/30 holdout observation.
- Still bounded: IoTID20 does not support universal ensemble superiority; the most stable IoTID20 model is the compact weighted LightGBM route.
- Wording to use: "Across 10 repeated IoTID20 stratified holdouts, the top ten weighted LightGBM improved Macro-F1 by 0.0140 and minority recall by 0.2129 over flat LightGBM, with split bootstrap intervals excluding zero."
- Wording to avoid: "The ensemble is best across datasets" or "IoTID20 proves external deployment robustness."

## Source Files

- `results/iotid20_repeated_split/experiment_results.csv`
- `results/iotid20_repeated_split/model_summary.csv`
- `results/iotid20_repeated_split/paired_delta_bootstrap_summary.csv`
- `results/iotid20_repeated_split/RESULT_LEDGER.md`
