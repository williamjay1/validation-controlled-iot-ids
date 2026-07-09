# Final Readiness Audit

Checked on 2026-07-01.

## Current Status

Status: scientific-content-ready package, not portal-submission-final.

The experimental evidence is strong enough for a Scientific Reports or PLOS ONE style manuscript draft. The current primary route is Scientific Reports. A Scientific Reports style pass was completed after benchmarking six recent Scientific Reports IDS or IDS-review articles. The package is not portal-submission-final because author metadata, author declarations, public code/archive link, and final visual DOCX QA still require completion. See `docs/SCIENTIFIC_REPORTS_GO_NO_GO_20260701.md` for the current decision memo.

## Completed

| Area | Status | Evidence |
|---|---|---|
| Data acquisition | Complete | CICIoT2023 public subsample, IoTID20 mirror, and UCI N-BaIoT are downloaded locally. |
| Main experiment | Complete | CICIoT2023 confirmatory full downloaded subsample and ensemble run completed. |
| External/boundary validation | Complete | IoTID20 holdout and N-BaIoT 20k leave-one-device-out validation completed. |
| Uncertainty | Complete for main result | CICIoT2023 paired bootstrap with 300 resamples completed. |
| Explainability | Complete for component-level interpretation | SHAP analysis for the Borderline-SMOTE LightGBM component completed. |
| Tables | Complete for draft | Five paper tables generated under `results/paper_tables/`. |
| Figures | Complete for draft | Six 300 dpi PNG/TIFF figure pairs generated under `figures/paper_figures/`, including a new validation-design Figure 1. |
| Manuscript | Complete for Scientific Reports draft | `manuscript/scientific_reports_draft.md` updated with expanded Scientific Reports-style Introduction and Discussion, a Study design subsection, inline numbered citations, 20k N-BaIoT results, DOI-audited references, Statistical analysis, Data availability, Code availability, ethics, competing interests, and AI/tool-use disclosure. |
| Supplementary material | Complete for draft | `manuscript/supplementary_materials.md` lists table sources, bootstrap samples, reproducibility files, and reproduction commands. |
| Reproducibility scripts | Compiled | `python -m compileall -q scripts` passed. |
| Submission package | Generated | `submission_package/scientific_reports_20260701_submission_candidate_v4/` and zipped copy created. |
| Word submission drafts | Generated with structural QA | Main manuscript, supplementary information, and cover letter DOCX files generated under `submission_package/scientific_reports_20260630_submission_docs/`; see `docs/DOCX_QA_AUDIT_20260701_STYLE_PASS.md`. |

## Latest Package

- Folder: `submission_package/scientific_reports_20260701_submission_candidate_v4/`
- Zip: `submission_package/scientific_reports_20260701_submission_candidate_v4.zip`
- Contents: manuscript, DOCX files, supplementary material, five paper tables, six PNG figures, six TIFF figures, audit documents, README, requirements, analysis scripts, generated result tables, bootstrap outputs, and checksum records.

## DOCX Render Caveat

DOCX page-level visual render QA could not be completed. LibreOffice was available at `C:\Program Files\LibreOffice\program\soffice.exe`, but headless rendering timed out without PNG output. Structural DOCX checks passed, but final page review should be performed in Word or LibreOffice after author metadata is filled.

## Submission Blockers

| Blocker | Why it needs human input |
|---|---|
| Author list, affiliations, corresponding author | Cannot be inferred safely. |
| Author contributions | Requires agreement among authors. |
| Funding and acknowledgements | Requires project-specific information. |
| Public code repository or archive DOI | Requires account/repository choice and upload decision. |
| Cover letter sender details | Requires corresponding author name, affiliation, and email. |

## Go/No-Go Decision

Scientific readiness: GO.

Portal submission: NO-GO until author metadata, author declarations, the public code URL or archive DOI, and final visual DOCX QA are completed.

## Optional Strengthening

| Addition | Value |
|---|---|
| Full-archive N-BaIoT sensitivity run | Would remove the 20,000-row per-file cap limitation, but current evidence is already usable if the cap is disclosed. |
| IoTID20 repeated-split or bootstrap sensitivity | Would strengthen the secondary dataset result, but the main claim does not depend on IoTID20 dominance. |
| Word `.docx` conversion | Useful for direct submission, but should be done after author metadata is finalized. |
| Public repository plus Zenodo DOI | Needed for final submission and code availability compliance. |

## Final Verdict

Proceed with the Scientific Reports route as the primary manuscript. The core claim should remain:

Validation-weighted ensembling improves rare-class CICIoT2023 fine-grained IoT intrusion detection under leakage-controlled evaluation, while IoTID20 and N-BaIoT define the external and unseen-device boundaries of that claim.
