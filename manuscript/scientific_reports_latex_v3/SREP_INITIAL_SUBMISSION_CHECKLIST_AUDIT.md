# Scientific Reports Initial Submission Checklist Audit

Package checked: `scientific_reports_20260708_latex_candidate_v1`

Date checked: 2026-07-09

## Manuscript files

- Main manuscript source: `main.tex`
- Main manuscript PDF: `main.pdf`
- Scientific Reports class file: `wlscirep.cls`
- Supplementary source: `supplementary_information.tex`
- Supplementary PDF: `supplementary_information.pdf`
- Cover letter: `cover_letter.md`
- Submission readme: `README_SUBMISSION.md`
- Checksums: `checksums.txt`

## Initial submission checklist

| Item | Status | Notes |
| --- | --- | --- |
| Article type and journal format | Pass | Main manuscript uses `\documentclass[fleqn,10pt]{wlscirep}`. |
| Title page | Pass | Title, authors, affiliations, correspondence, and email information are present. |
| Abstract | Pass | Abstract has no subheadings or citations and stays within the Scientific Reports style. |
| Keywords | Pass | Six keywords are supplied. |
| Main sections | Pass | Introduction, Results, Discussion, Methods, Data availability, Code availability, References, Acknowledgements, Author contributions, and Additional information are included. |
| Figures and tables | Pass | Main text uses six figures and two tables, keeping the main display count at eight items. |
| Figure and table placement | Pass | Figures and tables are placed close to the relevant main text rather than collected only at the end. |
| Figure legends | Pass | Legends describe the figures and map shortened labels to supplementary tables where needed. |
| Supplementary information | Pass | Supplementary source and PDF are provided, including benchmark context, baseline screens, diagnostics, sensitivity analyses, runtime details, and reproduction notes. |
| References | Pass | References are embedded in `main.tex` through `thebibliography`, are ordered by citation sequence, and include DOI or stable URL information where available. No separate `.bib` file is required. |
| Data availability | Pass | Public dataset sources and local processed result files are described. |
| Code availability | Blocker before portal submission | The statement is present, but a public GitHub, Zenodo, OSF, or equivalent archive URL or DOI still must be inserted before actual submission. |
| Competing interests | Pass | A competing interests statement is included. |
| Ethics statement | Pass | The manuscript states that only public benchmark network traffic datasets were used and no human participants or personal data were involved. |
| AI or tool use disclosure | Pass | Tool assisted coding, numerical checking, and language editing are disclosed without claiming authorship. |
| Author contributions | Pass | Contributions for J.Z. and S.W. are included. |
| Funding | Pass | National Social Science Fund of China, General Program, grant 25BGJ089, is included. |
| Reproducibility materials | Pass with repository blocker | Scripts, requirements, result CSV files, figure code, and checksums are described locally. Public archive release is still required. |
| Temporary build files | Pass | Auxiliary LaTeX build files were removed from the package directory after compilation. |

## Verification performed

- `main.tex` was compiled with `pdflatex` twice after package regeneration.
- `supplementary_information.tex` was compiled with `pdflatex` twice after package regeneration.
- Main manuscript output: 13 pages.
- Supplementary information output: 9 pages.
- Local checks found no remaining `TODO` placeholders in the manuscript or supplementary source.
- Local checks found no active `.bib` dependency.
- Local checks found no "will be deposited" wording.
- Local checks found no unsupported "state of the art" or "SOTA" claim in the manuscript source.

## Open blocker before actual submission

The only submission critical blocker is the code availability archive. Before pressing submit, create a public repository or archival record and replace the Code availability placeholder with a live URL or DOI. The archive should include scripts, requirements, result CSV files, figure generation code, figure files, supplementary tables, checksums, and a short reproduction README.
