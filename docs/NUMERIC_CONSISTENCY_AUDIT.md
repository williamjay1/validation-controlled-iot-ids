# Numeric Consistency Audit

Checked on 2026-06-30 after the Scientific Reports polish pass.

Status: PASS.

## Files Compared

- Main manuscript: `manuscript/scientific_reports_draft.md`
- CICIoT2023 main table: `results/paper_tables/table1_ciciot_main_results.csv`
- CICIoT2023 rare-class table: `results/paper_tables/table2_ciciot_rare_class_recall.csv`
- IoTID20 table: `results/paper_tables/table3_iotid20_replication.csv`
- N-BaIoT table: `results/paper_tables/table4_nbaiot_unseen_device_summary.csv`
- Bootstrap summary: `results/statistical_uncertainty/ciciot_bootstrap_summary.csv`

## Verified Manuscript Claims

| Claim group | Result |
|---|---|
| CICIoT2023 flat LightGBM and validation-weighted ensemble accuracy, balanced accuracy, Macro-F1, weighted F1, minority recall, and macro PR-AUC | Match |
| CICIoT2023 rare-class recall for Uploading_Attack, Recon-PingSweep, Backdoor_Malware, and XSS | Match |
| IoTID20 flat LightGBM, weighted top-10 LightGBM, and validation-weighted ensemble Macro-F1 and minority recall | Match |
| N-BaIoT binary, family, and fine-grained attack-label summary values | Match |
| CICIoT2023 paired-bootstrap percentile intervals for Macro-F1, balanced accuracy, and minority recall differences | Match |
| Reference count and in-text numbered citation coverage | 10 references with in-text citation coverage |

## Notes

- The main CICIoT2023 result table names the final model `Validation-weighted ensemble`; the rare-class table abbreviates it as `Ensemble`. These are the same operating point in the manuscript.
- The IoTID20 result table names the compact weighted LightGBM model `Weighted LightGBM top-10`; the manuscript describes it as weighted LightGBM with the top 10 mutual-information features.
