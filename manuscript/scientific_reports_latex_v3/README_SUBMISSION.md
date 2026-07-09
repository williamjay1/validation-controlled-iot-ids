# Scientific Reports LaTeX Candidate v3

Generated: 2026-07-09

This package restores a Scientific Reports style main article plus supplementary information structure. The main article contains four figures and four tables, for eight display items total.

## Main display items

- Figure 1: study design plus validation control framework.
- Table 1: dataset roles and validation design.
- Figure 2: CICIoT2023 public subsample main metrics plus rare label recall.
- Table 2: CICIoT2023 public subsample main results.
- Figure 3: IoTID20 repeated split validation.
- Table 3: IoTID20 repeated holdout summary.
- Figure 4: N-BaIoT leave one device out validation.
- Table 4: N-BaIoT leave one device out summary.

## Supplementary routing

- Supplementary Figures S1 and S2 contain SHAP and alpha sensitivity.
- Supplementary Tables S1 to S17 contain baseline variants, bootstrap records, exact sign flip tests, runtime and complexity, hyperparameters, short label maps, benchmark context, model family screens, class wise diagnostics, N-BaIoT cap sensitivity and rare prior screens.
- Long result ledgers and implementation records are no longer embedded in the main article.

## Files

- `main.tex`: main article source using `\documentclass[fleqn,10pt]{wlscirep}`.
- `supplementary_information.tex`: supplementary source with independent Supplementary Table and Supplementary Figure numbering.
- `cover_letter.md`: draft cover letter.
- `figures/`: PNG files referenced by the TeX files plus TIFF upload versions.
- `supplementary_tables/`: source CSV and markdown records.
- `checksums.txt`: SHA-256 checksums.

## Template support

- Copied Scientific Reports template support files from candidate v1.

## Remaining submission blocker

The code availability section still needs an active public repository URL or archive DOI before portal submission.
