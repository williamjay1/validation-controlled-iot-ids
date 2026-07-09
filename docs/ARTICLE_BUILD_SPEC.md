# Article Build Spec

## Target Route

Primary target: Scientific Reports.

Fallback target: PLOS ONE, with the same experiments but a stronger emphasis on reproducibility and fewer novelty claims.

## Working Title

A validation-weighted ensemble for imbalance-aware fine-grained IoT intrusion detection with unseen-device validation

## One-Sentence Contribution

This study shows that a validation-selected probability ensemble can improve rare-class detection on a fine-grained CICIoT2023 subsample while independent IoTID20 and N-BaIoT experiments define where the imbalance-aware pattern generalizes and where it does not.

## Central Research Question

Can imbalance-aware model selection improve fine-grained IoT intrusion detection without relying on accuracy-only claims, and does the pattern persist under independent-dataset and unseen-device validation?

## Evidence Spine

| Evidence block | Result | Role in manuscript |
|---|---|---|
| CICIoT2023 full downloaded subsample | Ensemble Macro-F1 0.8828 vs flat LightGBM 0.8612; minority recall 0.5131 vs 0.1910; macro PR-AUC 0.9219 vs 0.8863 | Main positive result |
| CICIoT2023 paired bootstrap | Macro-F1 improvement 95% CI 0.0188 to 0.0246; minority-recall improvement 95% CI 0.2557 to 0.3851 | Uncertainty and stability evidence |
| CICIoT2023 rare classes | Uploading_Attack recall 0.1910 to 0.5131; Recon-PingSweep 0.4065 to 0.6667; Backdoor_Malware 0.4719 to 0.6406; XSS 0.3827 to 0.5761 | Security relevance beyond aggregate accuracy |
| IoTID20 holdout | Weighted LightGBM top ten Macro-F1 0.6209 vs flat 0.6103; minority recall 0.4908 vs 0.2637; ensemble not best | Boundary evidence and external replication |
| N-BaIoT leave-one-device-out 20k cap | Binary Macro-F1 0.9998; family Macro-F1 0.9999; fine-grained attack conservative Macro-F1 0.9435 and present-class Macro-F1 0.9867 | Entity-held-out validation and limits |
| SHAP component explanation | Timing, header, protocol, flag/count, flow-duration, and packet-size features dominate | Mechanistic plausibility and reviewer readability |

## Main Claim

Validation-weighted ensembling of complementary imbalance strategies improved fine-grained CICIoT2023 rare-attack detection under a frozen test design, and the broader imbalance-aware pattern was corroborated but bounded by IoTID20 and N-BaIoT validation.

## Section Purpose Map

| Section | Purpose | Must include |
|---|---|---|
| Abstract | State problem, design, main numbers, boundary | CICIoT gains, IoTID20 non-dominance, N-BaIoT unseen-device result |
| Introduction | Motivate fine-grained IDS and class imbalance | Accuracy insufficiency, dataset roles, contribution list |
| Results opening | Explain validation sequence | Figure 1, staged CICIoT2023-IoTID20-N-BaIoT design |
| Results 1 | Establish main CICIoT performance gain | Table 1, Figure 2, bootstrap intervals |
| Results 2 | Show rare-class security relevance | Table 2, Figure 3 |
| Results 3 | External replication boundary | Table 3, Figure 4, ensemble not best on IoTID20 |
| Results 4 | Device-held-out generalization | Table 4, Figure 5, present-class metric note |
| Results 5 | Feature contribution | Table 5, Figure 6 |
| Discussion | Interpret tradeoffs and prevent overclaiming | No universal robustness, no all-dataset dominance |
| Methods | Make the experiment reproducible | Data sources, splits, validation-only alpha selection, metrics, versions |

## Figure Narrative Map

| Figure | Intended reader takeaway |
|---|---|
| Figure 1 | The study is a staged validation design, not a single leaderboard experiment. |
| Figure 2 | The ensemble is the strongest CICIoT operating point across Macro-F1, minority recall, and PR-AUC. |
| Figure 3 | The aggregate gain is driven by meaningful recall improvement on rare attacks. |
| Figure 4 | IoTID20 supports imbalance-aware weighting but not universal ensemble dominance. |
| Figure 5 | N-BaIoT binary/family generalization is near saturated, while fine-grained attack performance varies by held-out device and weakest class. |
| Figure 6 | The LightGBM component relies on interpretable timing, protocol, flag/count, and packet-size traffic features. |

## Reviewer Risk Controls

| Risk | Control |
|---|---|
| Public mirror may be seen as incomplete CICIoT2023 | Always say "public subsample mirror" and disclose row counts. |
| Test leakage concern | State that feature ranking, oversampling, model fitting, and alpha selection used training/validation data only. |
| N-BaIoT near-perfect results may look inflated | Emphasize leave-one-device-out design, 20k per-file cap, and fine-grained weak-class recall. |
| IoTID20 does not favor the ensemble | Present this as boundary evidence, not failure. |
| Lack of public code DOI | Mark as required before submission; do not claim archived code yet. |

## Final Submission Gate

The paper is submission-ready only after author metadata, public code/data availability links, supplementary tables, and a citation-formatted reference list are finalized.
