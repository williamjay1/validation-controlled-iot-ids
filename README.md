# Validation controlled imbalance aware learning for IoT intrusion detection

This repository is the reproducibility package for the manuscript:

**Validation controlled imbalance aware learning for fine grained IoT intrusion detection**

Authors: Junjie Zhang and Siyu Wang.

The package contains the executable scripts, pinned Python requirements, generated result tables, figure assets, manuscript source files, and checksum records used for the Scientific Reports submission candidate.

## What is included

- `scripts/`: data download, experiment, uncertainty, explainability, figure generation, and manuscript package scripts.
- `results/`: generated CSV and Markdown result ledgers used in the manuscript.
- `figures/`: publication figure files used by the manuscript.
- `manuscript/scientific_reports_latex_v3/`: LaTeX source, generated PDF, figures, supplementary tables, cover letter, and submission checklist for the current candidate.
- `docs/`: provenance, claim strength, numerical consistency, reference DOI, and submission readiness records.
- `data/DATA_SOURCES.md`: public data source and download notes.

Raw public datasets are **not** stored in this repository. They are downloaded from their public sources by `scripts/download_datasets.py`.

## Environment

Create and activate a Python environment, then install the pinned requirements.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The manuscript experiments were run on Windows 11 with an AMD Ryzen 9 8945HS processor and 31.3 GB RAM. The code should also run on Linux or macOS with equivalent Python packages, but paths in the manuscript audit were generated on Windows.

## Data download

Quick public data download:

```powershell
.\.venv\Scripts\python.exe scripts\download_datasets.py --quick
```

N BaIoT download and extraction:

```powershell
.\.venv\Scripts\python.exe scripts\download_datasets.py --quick --include-nbaiot --extract-nbaiot
```

The raw data files are written under `data/raw/`, which is ignored by git.

## Main reproduction commands

```powershell
.\.venv\Scripts\python.exe scripts\run_ciciot_recall_aware_ensemble.py --out-dir ciciot_ensemble_full
.\.venv\Scripts\python.exe scripts\run_iotid20_repeated_split_uncertainty.py --out-dir iotid20_repeated_split
.\.venv\Scripts\python.exe scripts\run_nbaiot_unseen_device.py --n-per-file 20000 --out-dir nbaiot_unseen_device_20k --run-id nb_binary_lgbm_weighted --run-id nb_family_lgbm_weighted --run-id nb_attack_lgbm_weighted
.\.venv\Scripts\python.exe scripts\run_ciciot_bootstrap_uncertainty.py --n-bootstrap 2000 --out-dir statistical_uncertainty
.\.venv\Scripts\python.exe scripts\run_ciciot_explainability.py --shap-sample 3000
.\.venv\Scripts\python.exe scripts\make_result_figures.py
.\.venv\Scripts\python.exe scripts\build_scientific_reports_balanced_package.py
```

Additional baseline and sensitivity scripts are retained in `scripts/` and their generated outputs are under `results/`.

## Primary manuscript results

- CICIoT2023 public subsample ensemble Macro-F1: 0.8828.
- CICIoT2023 public subsample ensemble minority recall: 0.5131.
- IoTID20 repeated split top ten weighted LightGBM Macro-F1: 0.6222.
- IoTID20 repeated split top ten weighted LightGBM minority recall: 0.4820.
- N BaIoT capped leave one device out fine grained attack Macro-F1: 0.9435.

See `results/`, `docs/RESULT_LEDGER.md`, and `manuscript/scientific_reports_latex_v3/main.tex` for the exact reporting context and limitations.

## Checksums

File hashes for this repository snapshot are recorded in `checksums_sha256.txt`.

## License

Code is released under the MIT License. Manuscript text, figures, and result tables are released under CC BY 4.0 unless a publisher agreement later requires a different submitted manuscript handling policy.

## Citation

Please cite the archived Zenodo release once the DOI is minted. Before journal submission, update `CITATION.cff`, this README, and the manuscript Code availability statement with the final repository URL and DOI.
