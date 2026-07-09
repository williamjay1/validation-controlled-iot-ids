# SCI Stage Quality Gate

## Current Stage

Status: passed for the Scientific Reports LaTeX candidate. The public GitHub repository and Zenodo archive DOI have been inserted into the manuscript package.

The project has moved from data acquisition and exploratory screening into confirmatory-result packaging. The manuscript may now be drafted, but claims must remain tied to the exact validation design.

## Passed Gates

| Gate | Status | Evidence |
|---|---|---|
| Public data provenance | Passed | CICIoT2023 mirror, IoTID20 mirror, and official UCI N-BaIoT archive downloaded and inventoried |
| Executable pipeline | Passed | Reproducible scripts in `scripts/`; requirements pinned in `requirements.txt` |
| Main-data confirmatory run | Passed | CICIoT full subsample confirmatory run completed |
| Validation-only model selection | Passed | Ensemble alpha selected on internal training validation split, not test split |
| Multi-metric reporting | Passed | Accuracy, balanced accuracy, Macro-F1, weighted F1, minority recall, worst-class recall, PR-AUC |
| External/independent validation | Passed with qualification | IoTID20 repeated holdouts; N-BaIoT capped leave one device out |
| Negative/boundary evidence retained | Passed | IoTID20 ensemble not best; hierarchical route not promoted; weak N-BaIoT devices reported |
| Publication figures | Passed | Six 300 dpi PNG/TIFF figures generated with shortened labels for rare classes and devices |

## Remaining Before Submission

| Item | Needed action |
|---|---|
| Code repository | Completed. Public repository: https://github.com/williamjay1/validation-controlled-iot-ids. Archived DOI: https://doi.org/10.5281/zenodo.21272745 |
| Dataset citation precision | Main manuscript contains numbered references with DOI links where DOI metadata are available and cited references are ordered by first appearance |
| Statistical uncertainty | CICIoT paired row bootstrap increased to 2,000 resamples; IoTID20 repeated split uncertainty completed over 10 stratified holdouts with 10,000 bootstrap resamples and exact sign flip tests |
| Explainability | SHAP/feature-importance figure added for the final ensemble's LightGBM component |
| Supplementary material | Supplementary TeX includes overflow tables, alpha grid, hyperparameters, label maps, N-BaIoT fold outputs and reproduction commands |
| Journal compliance | Manuscript converted to wlscirep template with data availability, code availability, author contributions, funding, competing interests and supplementary file |

## Claim Downgrade Log

| Original possible claim | Downgraded wording |
|---|---|
| The proposed model is robust across IoT devices | The proposed evaluation shows strong average unseen-device performance with heterogeneous fine-grained attack-label behavior |
| The ensemble is best on all datasets | The ensemble is the main CICIoT model; IoTID20 supports the imbalance-aware pattern but favors a lightweight weighted LightGBM variant |
| Oversampling is a separate paper | Oversampling is a component in the final imbalance-aware ensemble |
| Hierarchical classification is a primary contribution | Hierarchical classification is exploratory and supplementary unless optimized further |
| Full CICIoT2023 was used | The full downloaded CICIoT2023 Hugging Face subsample was used; this must not be described as the complete original corpus |
