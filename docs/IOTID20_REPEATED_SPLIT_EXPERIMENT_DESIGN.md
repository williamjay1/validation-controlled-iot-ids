# IoTID20 Repeated Split Experiment Design

## Route

SCI machine-learning validation experiment.

## Matrix

| Run group | Varying factor | Fixed factors | Expected outcome |
|---|---|---|---|
| IoTID20 repeated split | Stratified split seed, 10 levels | cleaning, metrics, model parameters, feature space | Estimate whether the single 70/30 result is split-stable |

## Models

- Flat LightGBM baseline.
- Class-weighted LightGBM.
- Top-10 mutual-information flat LightGBM.
- Top-10 mutual-information class-weighted LightGBM.
- Class-weighted XGBoost.
- Validation-selected LightGBM/XGBoost probability ensemble.

## Metrics

Primary: Macro-F1, minority-class recall, macro PR-AUC.

Secondary: accuracy, balanced accuracy, worst-class recall, train time, inference time.

## Uncertainty

The script reports per-split metrics and split-level nonparametric bootstrap intervals for paired deltas versus flat LightGBM.
