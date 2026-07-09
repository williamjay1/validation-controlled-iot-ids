# Experiment Design Gate

## Scope

This first executable stage runs CICIoT2023 quick experiments before manuscript drafting.

## Data

- Train rows used: 220,000
- Test rows used: 79,999
- Train sampling argument: 220000
- Test sampling argument: 80000
- Feature columns: 46
- Binary target: `label`
- Attack-class target: `attack_class`
- Fine-grained target: `Label`

## Experiment Matrix

1. Binary attack detection with weighted LightGBM.
2. 8-class attack category classification with and without class weights.
3. Flat 34-class fine-grained classification baseline.
4. Imbalance handling: class weight, random oversampling, SMOTE, Borderline-SMOTE.
5. Feature-efficient variants: MI top-20/top-10 and LightGBM-importance top-20/top-10.
6. Model family check: RF, ExtraTrees, XGBoost, CatBoost when enabled.
7. Hierarchical classifier: binary gate -> attack class -> per-category fine label.

## Primary Metrics

- Fine-grained task: Macro-F1, minority recall mean, worst-class recall, macro PR-AUC.
- Binary task: PR-AUC, ROC-AUC, false positive rate, MCC.
- Lightweight task: Macro-F1 and PR-AUC retention, feature count, inference time.

## Red-Risk Controls

- The test split from the Hugging Face mirror is kept frozen.
- Feature selection is fitted only on the training split.
- Metrics include Macro-F1 and classwise recall, not only accuracy.
- Claims from this quick stage must be treated as preliminary until full-data or external validation is complete.
