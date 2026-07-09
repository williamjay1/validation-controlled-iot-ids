# Scientific Reports Benchmark Matrix

Date: 2026-07-01

Purpose: benchmark the current IoT IDS manuscript against recent Scientific Reports articles in the same or adjacent topic area. The PDFs, JATS XML files, plain-text extracts, and metadata were downloaded from the official PMC Open Access AWS corpus under `literature/scientific_reports_benchmark/`.

## Downloaded Benchmark Set

| PMCID | Article | DOI | Citation | Local PDF |
|---|---|---|---|---|
| PMC12215491 | Smart deep learning model for enhanced IoT intrusion detection | 10.1038/s41598-025-06363-5 | Sci Rep. 2025 Jul 1;15:20577 | `literature/scientific_reports_benchmark/pdfs/PMC12215491.pdf` |
| PMC12328755 | An attack detection method based on deep learning for internet of things | 10.1038/s41598-025-14808-0 | Sci Rep. 2025 Aug 6;15:28812 | `literature/scientific_reports_benchmark/pdfs/PMC12328755.pdf` |
| PMC12216364 | Improved model for intrusion detection in the Internet of Things | 10.1038/s41598-025-92852-6 | Sci Rep. 2025 Jul 1;15:21547 | `literature/scientific_reports_benchmark/pdfs/PMC12216364.pdf` |
| PMC12218583 | An IoT intrusion detection framework based on feature selection and large language models fine-tuning | 10.1038/s41598-025-08905-3 | Sci Rep. 2025 Jul 1;15:21158 | `literature/scientific_reports_benchmark/pdfs/PMC12218583.pdf` |
| PMC12835135 | Securing IoT networks: a machine learning approach for detecting unusual traffic patterns | 10.1038/s41598-025-33447-z | Sci Rep. 2026;16:3397 | `literature/scientific_reports_benchmark/pdfs/PMC12835135.pdf` |
| PMC13149857 | Supervised machine learning intrusion detection review and multi-criteria evaluation | 10.1038/s41598-026-44773-1 | Sci Rep. 2026;16:14525 | `literature/scientific_reports_benchmark/pdfs/PMC13149857.pdf` |

## Structural Pattern

| Article | Abstract words | Main section order | Figures | Tables | References | Pattern to imitate |
|---|---:|---|---:|---:|---:|---|
| PMC12215491 | 311 | Introduction; Related work; Materials and methods; Results; Discussions; Conclusion | 13 | 10 | 110 | Uses early schematic/framework figures and a large related-work base. |
| PMC12328755 | 169 | Introduction; Related work; Methodology; Datasets and preprocessing; Experimental settings; Experimental results and analysis; Conclusion | 3 | 8 | 31 | Separates dataset preparation, experimental settings, and result interpretation. |
| PMC12216364 | 268 | Introduction; Related work; Proposed model; Conclusion and future works | 11 | 10 | 54 | Uses many method and taxonomy figures, but the result narrative is less clean. |
| PMC12218583 | 240 | Introduction; Related work; Methodology; Results and discussion; Conclusions | 9 | 10 | 47 | Strong framework figure and clear multi-dataset table sequence. |
| PMC12835135 | 246 | Introduction; Related work; Methodology; Results and discussion; Conclusion and future work | 13 | 14 | 41 | Heavy figure/table density; useful for paper packaging, but some sections are mechanical. |
| PMC13149857 | 265 | Introduction; Background; Measures; Datasets; Review; Evaluation framework; Results; Conclusion | 13 | 19 | 120 | Strongest reference model for literature positioning, evaluation criteria, and dataset taxonomy. |

## Lessons for Our Manuscript

1. The current manuscript already follows the formal Scientific Reports article order: Abstract, Introduction, Results, Discussion, Methods, Data availability, Code availability, References, Declarations, and Figure legends.
2. The current manuscript is much thinner than the benchmark set. Our Introduction is about 385 English-token words, while benchmark introductions and related-work sections together usually exceed 1,300 words.
3. The biggest gap is not experimental evidence. It is the reviewer-facing framing: closest literature, evaluation gap, why rare-class recall matters, and why the claim is a validation study rather than another high-accuracy IDS paper.
4. The benchmark articles commonly use an early framework or pipeline figure. Our current Figure 1 is already a results figure; a new Figure 1 should show data sources, train/validation/test separation, imbalance handling, ensemble selection, and external validation.
5. The benchmark papers carry much denser reference lists. Our current 10-reference list is too sparse for Scientific Reports. It should be expanded with IDS surveys, dataset papers, imbalance-learning references, PR-AUC/evaluation references, leakage-control or reproducibility references, and recent Scientific Reports comparators.
6. Many benchmark articles are willing to combine Results and Discussion, but our target route should keep the standard Scientific Reports order and use the Discussion to interpret limits, not repeat metrics.
7. Some benchmark articles overclaim high accuracy on random splits. We should not imitate that weakness. Our stronger angle is explicit test-set freezing, internal validation-only ensemble selection, minority recall, paired bootstrap intervals, and leave-one-device-out validation.

## Direct Diagnosis of the Current Draft

Status: promising scientific-content draft, not yet a polished Scientific Reports submission.

What works:

- The main result is clear and numerically checked: the CICIoT2023 validation-weighted ensemble improves Macro-F1, minority recall, and macro PR-AUC over flat LightGBM.
- The claim is appropriately bounded by IoTID20 and N-BaIoT rather than pretending universal dominance.
- Methods already include leakage-control language, bootstrap uncertainty, public datasets, and reproducibility statements.
- Figures and tables exist in submission-quality raster formats.

What still reads too much like a project report:

- The Introduction compresses field motivation, dataset roles, and contribution into four paragraphs.
- There is no sustained comparison with recent IDS literature or recent Scientific Reports articles.
- The contribution statement is implicit rather than reviewer-visible.
- Results are accurate but need stronger scientific signposting: each subsection should answer a validation question.
- Discussion is cautious but too short to carry the paper's field meaning.
- Methods need a clearer "Study design" subsection before dataset details.
- The reference list is too short for this target.

## Rewrite Target

Maintain the core claim:

> A validation-selected probability ensemble can improve rare-class recall and macro-average performance for fine-grained CICIoT2023 intrusion detection, while independent IoTID20 and leave-one-device-out N-BaIoT experiments define where the claim does and does not generalize.

Required upgrades before saying the manuscript is ready for Scientific Reports portal submission:

1. Expand Introduction into a full literature-positioning section.
2. Add a concise contribution paragraph with 3-4 explicit contributions.
3. Add or generate a pipeline/validation-design figure as the new Figure 1.
4. Reframe Results subsections around validation questions.
5. Expand Discussion with comparison to recent IDS literature, deployment implications, and a sharper limitation paragraph.
6. Expand and DOI-check references.
7. Rebuild DOCX/submission package after author metadata and code availability URL/DOI are finalized.
