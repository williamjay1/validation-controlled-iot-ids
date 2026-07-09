# Reproducibility smoke test, 2026-07-09

This note records the lightweight verification performed on a clean extraction of the release package at:

`D:\codex\sci\_repro_smoke_validation_iot_ids`

The smoke test verifies package integrity, dependency import, public quick data download, figure rebuilding and reduced-size training runs. It is not intended to reproduce the final manuscript metrics, which require the full commands documented in the README and manuscript.

## Environment

- Python: 3.12.13
- Operating system used for the smoke test: Windows
- Package environment: project virtual environment with `requirements.txt`

## Checks completed

| Check | Command or action | Result |
|---|---|---|
| Clean zip extraction | Extracted `validation-controlled-iot-ids_v1.0.0_github_ready.zip` to a fresh directory | Passed |
| Python syntax compilation | `python -m compileall -q scripts` | Passed |
| Dependency imports | Imported numpy, pandas, sklearn, scipy, lightgbm, xgboost, imblearn, matplotlib, seaborn, shap, catboost, requests, huggingface_hub, pyarrow and tqdm | Passed |
| Quick public data download | `python scripts/download_datasets.py --quick` | Passed; CICIoT2023 public subsample and IoTID20 mirror downloaded |
| Figure and table rebuild from packaged results | `python scripts/make_result_figures.py` | Passed |
| CICIoT reduced training smoke test | `python scripts/run_ciciot_recall_aware_ensemble.py --train-n 2000 --test-n 1000 --out-dir smoke_ciciot` | Passed after v1.0.2 summary-table guard fix |
| IoTID20 reduced repeated split smoke test | `python scripts/run_iotid20_repeated_split_uncertainty.py --max-rows 1000 --n-splits 2 --bootstrap-reps 20 --out-dir smoke_iotid20` | Passed |
| N-BaIoT script syntax | `python -m py_compile scripts/run_nbaiot_unseen_device.py scripts/download_datasets.py` | Passed |
| N-BaIoT source availability check | HTTP HEAD to UCI archive URL | Passed with HTTP 200 |

## v1.0.2 fix

The reduced CICIoT smoke test exposed a summary-writing edge case: small validation samples may not contain enough class coverage for macro PR-AUC to be computed, so `pr_auc_macro` can be absent from the validation alpha grid. The v1.0.2 code now fills missing summary columns with `NaN` and reports the real feature count in the validation grid.

This fix does not change the manuscript's stored result CSV files or reported metrics. It improves reduced-size and diagnostic reproducibility.

## Full reproduction note

The full manuscript commands remain those listed in `README.md`. Full reproduction can require substantial download time and compute time, especially for N-BaIoT extraction and leave-one-device-out experiments. The smoke test confirms that the package wiring, quick public data download, main model code paths and output generation are functional.
