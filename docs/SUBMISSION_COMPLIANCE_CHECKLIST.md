# Submission Compliance Checklist

Official pages checked on 2026-06-30:

- Scientific Reports: https://www.nature.com/srep/author-instructions/submission-guidelines
- PLOS ONE: https://journals.plos.org/plosone/s/submission-guidelines

## Scientific Reports Route

| Item | Status | Action |
|---|---|---|
| Title | Complete for draft | 12 words; within the Scientific Reports recommendation |
| Abstract | Complete for draft | 164 words; unstructured and within the recommendation |
| Main text structure | Complete for draft | Current order: Introduction, Results, Discussion, Methods |
| Figures | Drafted | Five 300 dpi PNG/TIFF figures generated |
| Tables | Drafted | CSV tables generated; convert to manuscript tables or supplementary files |
| Data availability | Complete for draft | Public dataset links and access date added; final check before submission |
| Code availability | Drafted, blocked by public release | Create GitHub/Zenodo repository and add URL/DOI |
| Author contributions | Missing | Add after author list is fixed |
| Competing interests | Drafted | Current statement: no competing interests |
| Ethics | Drafted | States no human participants, human tissue, or animal subjects |
| AI/tool disclosure | Drafted | Added under declarations; final author approval still required |
| Supplementary information | Complete for draft | Table sources, bootstrap samples, hyperparameters, reproduction commands, and reproducibility files listed |

## PLOS ONE Route

| Item | Status | Action |
|---|---|---|
| Style | Convertible | Use standard Introduction, Materials and methods, Results, Discussion |
| Statistical reporting | Partly complete | CICIoT bootstrap intervals added; consider IoTID20 repeated split or bootstrap |
| Reproducibility | Needs strengthening | Public code, pinned environment, exact data hashes or file sizes |
| Data availability | Drafted | PLOS requires no restriction language; provide direct public links |
| Software versions | Drafted | Ensure versions in manuscript match `requirements.txt` |
| Negative results | Present | Preserve IoTID20 ensemble boundary and N-BaIoT weak-device heterogeneity |

## Recommended Before Submission

1. Decide whether to keep the N-BaIoT 20,000-row per-file cap as the submitted computational design or run a full-archive sensitivity check.
2. Export tables to Word-compatible format.
3. Create a public repository and archive release.
4. Replace all placeholder author, affiliation, contribution, funding, and acknowledgement fields.
5. Perform final DOCX visual review in Word or LibreOffice after author metadata is filled.
