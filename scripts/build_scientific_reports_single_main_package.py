from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

import build_scientific_reports_latex_package as base


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "submission_package" / "scientific_reports_20260708_latex_candidate_v1"
OUT_DIR = ROOT / "submission_package" / "scientific_reports_20260709_single_main_candidate_v2"


TABLE_MAP = {
    "S0": "Table 3",
    "S1": "Table 4",
    "S2": "Table 5",
    "S3": "Table 6",
    "S4": "Table 7",
    "S5": "Table 8",
    "S6": "Table 9",
    "S7": "Table 10",
    "S8": "Table 11",
    "S9": "Table 12",
    "S10": "Table 13",
    "S11": "Table 14",
    "S12": "Table 15",
    "S13": "Table 16",
    "S14": "Table 17",
    "S15": "Table 18",
    "S16": "Table 19",
    "S17": "Table 20",
    "S18": "Table 21",
    "S19": "Table 22",
}


CAPTION_MAP = {
    "Study design and validation roles.": "Study design.",
    "Validation-controlled ensemble framework.": "Validation controlled ensemble framework.",
    "CICIoT2023 public subsample main validation metrics.": "CICIoT2023 main validation metrics.",
    "Rare attack recall on the CICIoT2023 public subsample.": "Rare attack recall.",
    "IoTID20 split stable effects of feature selection and class weighting.": "IoTID20 repeated split deltas.",
    "N-BaIoT capped leave one device out validation.": "N BaIoT leave one device out validation.",
    "Dataset roles and validation design.": "Dataset roles and validation design.",
    "CICIoT2023 public subsample main results.": "CICIoT2023 main results.",
}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def shorten_caption(match: re.Match[str]) -> str:
    full = match.group(1)
    bold = re.match(r"\\textbf\{([^{}]+)\}\s*(.*)", full, flags=re.S)
    if not bold:
        return match.group(0)
    title = bold.group(1).strip()
    short = CAPTION_MAP.get(title, title)
    return rf"\caption{{{short}}}"


def extract_document_body(tex: str) -> str:
    body = tex.split(r"\begin{document}", 1)[1]
    body = body.split(r"\section*{Reproduction commands}", 1)[0]
    body = body.replace(r"\raggedright", "")
    body = body.replace(r"\maketitle", "")
    return body.strip()


def convert_supplement_sections(body: str) -> str:
    body = body.replace(
        "This supplementary file records overflow tables, result sources and reproduction commands for the Scientific Reports LaTeX submission package. Complete CSV files are supplied in the \\path{supplementary_tables/} directory.",
        "This section records the additional result tables, diagnostic checks and reproduction records that support the main evidence chain. Complete CSV source files are supplied in the \\path{result_tables/} directory.",
    )
    body = body.replace("supplementary_tables/", "result_tables/")
    body = body.replace("Supplementary Methods", "Implementation records")
    for key, label in sorted(TABLE_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        body = body.replace(f"Supplementary Table {key}.", f"{label}.")
        body = body.replace(f"Supplementary Tables {key}", f"{label}")
        body = body.replace(f"Supplementary Table {key}", label)
    body = body.replace("Supplementary Figure S1. CICIoT2023 SHAP feature contributions", "Figure 7. CICIoT2023 SHAP feature contributions")
    body = body.replace("Supplementary Figure S2. CICIoT2023 alpha sensitivity", "Figure 8. CICIoT2023 alpha sensitivity")
    body = body.replace("supplementary_figure_s1_ciciot_shap_top_features.png", "figure7_ciciot_shap_top_features.png")
    body = body.replace("supplementary_figure_s2_ciciot_alpha_sensitivity.png", "figure8_ciciot_alpha_sensitivity.png")
    body = body.replace("supplementary", "result")
    body = body.replace("Supplementary", "Additional")
    body = re.sub(
        r"\\section\*\{Figure 7\. CICIoT2023 SHAP feature contributions\}\s*"
        r"\\begin\{center\}\s*\\centering\s*"
        r"\\includegraphics\[width=0\.82\\linewidth\]\{figures/figure7_ciciot_shap_top_features\.png\}\s*"
        r"\\par\\smallskip\s*\\small\s*Mean absolute SHAP values for the highest-ranked features in the CICIoT2023 Borderline-SMOTE LightGBM component\. The analysis is used for component-level attribution, not causal interpretation\.\s*"
        r"\\end\{center\}",
        r"""\\begin{figure}[H]
\\centering
\\includegraphics[width=0.82\\linewidth]{figures/figure7_ciciot_shap_top_features.png}
\\caption{CICIoT2023 SHAP feature contributions.}
\\label{fig:shap}
\\end{figure}""",
        body,
        flags=re.S,
    )
    body = re.sub(
        r"\\section\*\{Figure 8\. CICIoT2023 alpha sensitivity\}\s*"
        r"\\begin\{center\}\s*\\centering\s*"
        r"\\includegraphics\[width=0\.82\\linewidth\]\{figures/figure8_ciciot_alpha_sensitivity\.png\}\s*"
        r"\\par\\smallskip\s*\\small\s*Validation-subsplit Macro-F1, minority recall and macro PR-AUC across candidate ensemble weights\. The selected value was \$\\alpha=0\.50\$ for the Borderline-SMOTE LightGBM component\.\s*"
        r"\\end\{center\}",
        r"""\\begin{figure}[H]
\\centering
\\includegraphics[width=0.82\\linewidth]{figures/figure8_ciciot_alpha_sensitivity.png}
\\caption{CICIoT2023 alpha sensitivity.}
\\label{fig:alpha}
\\end{figure}""",
        body,
        flags=re.S,
    )
    return body


def replace_main_references(tex: str) -> str:
    replacements = {
        "Supplementary Table S12 therefore compares": "Table 15 compares",
        "reported in Supplementary Figure S2": "shown in Figure 8",
        "Supplementary Table S8": "Table 11",
        "Supplementary Table S18": "Table 21",
        "Supplementary Table S13": "Table 16",
        "Supplementary Tables S14 and S15": "Tables 17 and 18",
        "Supplementary Table S19": "Table 22",
        "Supplementary Table S10": "Table 13",
        "Supplementary Table S16": "Table 19",
        "Supplementary Table S11": "Table 14",
        "Supplementary Table S17": "Table 20",
        "Supplementary Figure S1 and Supplementary Table S5": "Figure 7 and Table 8",
        "Supplementary Figure S1": "Figure 7",
        "Supplementary Figure S2": "Figure 8",
        "supplementary_tables/": "result_tables/",
    }
    for old, new in replacements.items():
        tex = tex.replace(old, new)
    tex = tex.replace(
        "A wider model family screen is reported in Table 16.",
        "A wider model family screen is reported in Table 16.",
    )
    tex = tex.replace(
        "These tables report precision, recall and F1",
        "These tables report precision, recall and F1",
    )
    tex = tex.replace("Supplementary", "Additional")
    tex = tex.replace("supplementary", "additional")
    return tex


def build_main() -> str:
    main = base.generate_main_tex()
    supp = base.generate_supplementary_tex()
    main = replace_main_references(main)
    main = re.sub(r"\\caption\{(\\textbf\{[^{}]+\}[^{}]*)\}", shorten_caption, main)
    main = main.replace(r"\usepackage{lineno}", "\\usepackage{lineno}\n\\usepackage{longtable}\n\\setlength{\\LTcapwidth}{\\linewidth}")
    extra = convert_supplement_sections(extract_document_body(supp))
    extra = rf"""
\clearpage
\section*{{Additional results and reproducibility records}}

The following tables and figures are part of the main article file. They are included here to keep the submission as a single正文 manuscript rather than a separate overflow file.

{extra}
"""
    main = main.replace(r"\section*{Discussion}", extra + "\n\n\\section*{Discussion}")
    main = main.replace("single正文", "single text")
    return main


def prepare_package() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    shutil.copytree(SRC_DIR, OUT_DIR)

    for name in ["supplementary_information.tex", "supplementary_information.pdf"]:
        path = OUT_DIR / name
        if path.exists():
            path.unlink()

    supp_dir = OUT_DIR / "supplementary_tables"
    result_dir = OUT_DIR / "result_tables"
    if supp_dir.exists():
        if result_dir.exists():
            shutil.rmtree(result_dir)
        supp_dir.rename(result_dir)

    fig_dir = OUT_DIR / "figures"
    for ext in ["png", "tiff"]:
        old = fig_dir / f"supplementary_figure_s1_ciciot_shap_top_features.{ext}"
        new = fig_dir / f"figure7_ciciot_shap_top_features.{ext}"
        if old.exists():
            old.rename(new)
        old = fig_dir / f"supplementary_figure_s2_ciciot_alpha_sensitivity.{ext}"
        new = fig_dir / f"figure8_ciciot_alpha_sensitivity.{ext}"
        if old.exists():
            old.rename(new)

    write_text(OUT_DIR / "main.tex", build_main())

    readme = (OUT_DIR / "README_SUBMISSION.md").read_text(encoding="utf-8")
    readme = readme.replace("scientific_reports_20260708_latex_candidate_v1", OUT_DIR.name)
    readme = readme.replace("- `supplementary_information.tex`: supplementary information source.\n", "")
    readme = readme.replace("- `supplementary_information.pdf`: compiled supplementary PDF.\n", "")
    readme = readme.replace("supplementary_tables/", "result_tables/")
    readme = readme.replace("Supplementary", "Additional")
    readme = readme.replace("supplementary", "additional")
    readme = readme.replace("source tables used by the manuscript and additional information", "source tables used by the manuscript")
    readme = readme.replace("Additional Tables S1 to S3", "Tables 4 to 6")
    readme = readme.replace("Additional Figure S2", "Figure 8")
    readme = readme.replace("Additional Tables S12 to S19", "Tables 15 to 22")
    readme = readme.replace(
        "- Additional information is supplied as a separate TeX file.",
        "- No separate appendix style TeX/PDF file is supplied; all additional records are included in `main.tex`.",
    )
    readme += "\n\n## Single main text revision\n\nThis v2 package intentionally removes the separate overflow TeX and PDF files. Additional analyses, benchmark context tables, diagnostics, runtime records and reproducibility notes are included in `main.tex` as part of the article file.\n"
    write_text(OUT_DIR / "README_SUBMISSION.md", readme)

    audit = (OUT_DIR / "SREP_INITIAL_SUBMISSION_CHECKLIST_AUDIT.md").read_text(encoding="utf-8")
    audit = audit.replace("scientific_reports_20260708_latex_candidate_v1", OUT_DIR.name)
    audit = audit.replace("- Supplementary source: `supplementary_information.tex`\n", "")
    audit = audit.replace("- Supplementary PDF: `supplementary_information.pdf`\n", "")
    audit = audit.replace("Supplementary information", "Additional main text records")
    audit = audit.replace("supplementary source and PDF are provided", "additional records are included in `main.tex`")
    audit = audit.replace("Supplementary source and PDF are provided", "Additional records are included in `main.tex`")
    audit = audit.replace("supplementary tables", "result tables")
    audit = audit.replace("supplementary", "additional")
    audit = audit.replace(
        "Main text uses six figures and two tables, keeping the main display count at eight items.",
        "Main text uses eight figures and twenty two numbered table or record blocks because this v2 package intentionally consolidates all evidence into one article file.",
    )
    audit = audit.replace(
        "Legends describe the figures and map shortened labels to result tables where needed.",
        "Figure captions are short title style captions; explanatory detail is kept in the surrounding text or numbered table records.",
    )
    audit = audit.replace("- `additional_information.tex` was compiled with `pdflatex` twice after package regeneration.\n", "")
    audit = audit.replace("Main manuscript output: 13 pages.", "Main manuscript output: 21 pages.")
    audit = audit.replace("- Additional main text records output: 9 pages.\n", "")
    audit = audit.replace("additional source", "main source")
    write_text(OUT_DIR / "SREP_INITIAL_SUBMISSION_CHECKLIST_AUDIT.md", audit)


def compile_main() -> None:
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "main.tex"],
        cwd=OUT_DIR,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "main.tex"],
        cwd=OUT_DIR,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def cleanup_aux() -> None:
    for pattern in ["*.aux", "*.log", "*.out", "*.toc", "*.fls", "*.fdb_latexmk", "*.synctex.gz"]:
        for path in OUT_DIR.glob(pattern):
            path.unlink()


def write_checksums() -> None:
    rows = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "checksums.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(f"{digest}  {path.relative_to(OUT_DIR).as_posix()}")
    write_text(OUT_DIR / "checksums.txt", "\n".join(rows))


def main() -> None:
    prepare_package()
    compile_main()
    cleanup_aux()
    write_checksums()
    print(OUT_DIR)


if __name__ == "__main__":
    main()
