from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import build_scientific_reports_latex_package as base


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "submission_package" / "scientific_reports_20260709_sr_balanced_candidate_v3"
SRC_DIR = ROOT / "submission_package" / "scientific_reports_20260708_latex_candidate_v1"
FIG_SRC = ROOT / "figures" / "paper_figures"
TABLE_SRC = ROOT / "results" / "paper_tables"
BOOTSTRAP_SRC = ROOT / "results" / "statistical_uncertainty"
IOTID_REPEATED_SRC = ROOT / "results" / "iotid20_repeated_split"


MAIN_FIGURES = [
    "figure1_study_validation_framework.png",
    "figure1_study_validation_framework.tiff",
    "figure2_ciciot_performance_rare_recall.png",
    "figure2_ciciot_performance_rare_recall.tiff",
    "figure3_iotid20_repeated_split.png",
    "figure3_iotid20_repeated_split.tiff",
    "figure4_nbaiot_unseen_device.png",
    "figure4_nbaiot_unseen_device.tiff",
    "supplementary_figure_s1_ciciot_shap_top_features.png",
    "supplementary_figure_s1_ciciot_shap_top_features.tiff",
    "supplementary_figure_s2_ciciot_alpha_sensitivity.png",
    "supplementary_figure_s2_ciciot_alpha_sensitivity.tiff",
]


def copy_source_package() -> list[str]:
    if not SRC_DIR.exists():
        base.main()
    resolved_out = OUT_DIR.resolve()
    package_root = (ROOT / "submission_package").resolve()
    if package_root not in resolved_out.parents:
        raise RuntimeError(f"Refusing to write outside submission_package: {resolved_out}")
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    shutil.copytree(SRC_DIR, OUT_DIR)
    return ["Copied Scientific Reports template support files from candidate v1."]


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def combine_vertical(src_names: list[str], dst_stem: str, panel_labels: list[str]) -> None:
    images = [Image.open(FIG_SRC / name).convert("RGB") for name in src_names]
    max_width = max(img.width for img in images)
    label_h = 56
    gap = 34
    margin = 18
    panels: list[Image.Image] = []
    font = safe_font(32)
    for label, img in zip(panel_labels, images):
        if img.width != max_width:
            height = int(img.height * max_width / img.width)
            img = img.resize((max_width, height), Image.LANCZOS)
        panel = Image.new("RGB", (max_width + margin * 2, img.height + label_h + margin), "white")
        draw = ImageDraw.Draw(panel)
        draw.text((margin, 10), label, fill=(20, 20, 20), font=font)
        panel.paste(img, (margin, label_h))
        panels.append(panel)

    total_h = sum(p.height for p in panels) + gap * (len(panels) - 1)
    total_w = max(p.width for p in panels)
    canvas = Image.new("RGB", (total_w, total_h), "white")
    y = 0
    for panel in panels:
        canvas.paste(panel, ((total_w - panel.width) // 2, y))
        y += panel.height + gap

    fig_dir = OUT_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    png_path = fig_dir / f"{dst_stem}.png"
    tiff_path = fig_dir / f"{dst_stem}.tiff"
    canvas.save(png_path, dpi=(300, 300))
    canvas.save(tiff_path, dpi=(300, 300), compression="tiff_lzw")


def prepare_figures() -> None:
    fig_dir = OUT_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    combine_vertical(
        ["figure1_validation_design.png", "figure2_validation_controlled_ensemble.png"],
        "figure1_study_validation_framework",
        ["a", "b"],
    )
    combine_vertical(
        ["figure3_ciciot_main_metrics.png", "figure4_ciciot_rare_attack_recall.png"],
        "figure2_ciciot_performance_rare_recall",
        ["a", "b"],
    )
    for src, dst in [
        ("figure5_iotid20_repeated_split", "figure3_iotid20_repeated_split"),
        ("figure6_nbaiot_unseen_device", "figure4_nbaiot_unseen_device"),
        ("supplementary_figure_s1_ciciot_shap_top_features", "supplementary_figure_s1_ciciot_shap_top_features"),
        ("supplementary_figure_s2_ciciot_alpha_sensitivity", "supplementary_figure_s2_ciciot_alpha_sensitivity"),
    ]:
        for ext in [".png", ".tiff"]:
            shutil.copy2(FIG_SRC / f"{src}{ext}", fig_dir / f"{dst}{ext}")


def figure_block(filename: str, label: str, caption: str, width: str = r"\linewidth") -> str:
    return rf"""
\begin{{figure}}[H]
\centering
\includegraphics[width={width}]{{figures/{filename}}}
\caption{{\textbf{{{caption}}}}}
\label{{{label}}}
\end{{figure}}
"""


def fmt(value: str | float, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def tex_escape(text: str) -> str:
    return base.tex_escape(text)


def table3_iotid() -> str:
    rows = base.read_csv_rows(TABLE_SRC / "table3_iotid20_replication.csv")
    keep = {
        "iotid_fine_lgbm_full",
        "iotid_fine_lgbm_mi_top10_flat",
        "iotid_fine_lgbm_weighted",
        "iotid_fine_lgbm_mi_top10_weighted",
        "iotid_fine_lgbm_xgb_validation_ensemble",
    }
    lines = []
    for row in rows:
        if row["run_id"] not in keep:
            continue
        lines.append(
            rf"{tex_escape(row['model'])} & {row['n_splits']} & {fmt(row['mean_macro_f1'])} & "
            rf"{fmt(row['mean_minority_recall'])} & {fmt(row['mean_pr_auc_macro'])} \\"
        )
    return rf"""
\begin{{table}}[H]
\centering
\caption{{\textbf{{IoTID20 repeated holdout summary.}}}}
\label{{tab:iotid}}
\small
\begin{{tabularx}}{{\linewidth}}{{L{{4.4cm}} c c c c}}
\toprule
Model & Splits & Mean Macro-F1 & Mean minority recall & Mean PR-AUC \\
\midrule
{chr(10).join(lines)}
\bottomrule
\end{{tabularx}}
\end{{table}}
"""


def table4_nbaiot() -> str:
    rows = base.read_csv_rows(TABLE_SRC / "table4_nbaiot_unseen_device_summary.csv")
    lines = [
        rf"{tex_escape(row['task'])} & {row['folds']} & {fmt(row['mean_macro_f1'])} & "
        rf"{fmt(row['min_macro_f1'])} & {fmt(row['mean_present_macro_f1'])} & "
        rf"{fmt(row['min_present_class_recall'])} \\"
        for row in rows
    ]
    return rf"""
\begin{{table}}[H]
\centering
\caption{{\textbf{{N-BaIoT leave one device out summary.}}}}
\label{{tab:nbaiot}}
\small
\begin{{tabularx}}{{\linewidth}}{{L{{2.0cm}} c c c c c}}
\toprule
Task & Folds & Mean Macro-F1 & Min Macro-F1 & Mean present Macro-F1 & Min present recall \\
\midrule
{chr(10).join(lines)}
\bottomrule
\end{{tabularx}}
\end{{table}}
"""


def replace_figure(tex: str, label: str, replacement: str) -> str:
    label_text = rf"\label{{{label}}}"
    label_pos = tex.find(label_text)
    if label_pos == -1:
        raise ValueError(f"Missing figure label: {label}")
    start = tex.rfind(r"\begin{figure}[H]", 0, label_pos)
    end = tex.find(r"\end{figure}", label_pos)
    if start == -1 or end == -1:
        raise ValueError(f"Could not locate figure block for {label}")
    end += len(r"\end{figure}")
    while start > 0 and tex[start - 1] == "\n":
        start -= 1
    while end < len(tex) and tex[end : end + 1] == "\n":
        end += 1
    return tex[:start] + "\n" + replacement + "\n" + tex[end:]


def remove_figure(tex: str, label: str) -> str:
    return replace_figure(tex, label, "")


def replace_section(tex: str, section_name: str, next_section: str, replacement: str) -> str:
    pattern = rf"\\section\*\{{{re.escape(section_name)}\}}[\s\S]*?(?=\\section\*\{{{re.escape(next_section)}\}})"
    return re.sub(pattern, lambda _m: replacement, tex, count=1)


def clean_main_tex(tex: str) -> str:
    table_map = {
        "5": "4",
        "6": "5",
        "7": "6",
        "8": "7",
        "9": "8",
        "10": "9",
        "11": "10",
        "12": "11",
        "13": "12",
        "14": "13",
        "15": "14",
        "16": "15",
        "17": "16",
        "18": "7",
        "19": "17",
    }

    def plural_table_repl(match: re.Match[str]) -> str:
        first, second = match.group(1), match.group(2)
        return f"Supplementary Tables S{table_map.get(first, first)} and S{table_map.get(second, second)}"

    def table_repl(match: re.Match[str]) -> str:
        num = match.group(1)
        return f"Supplementary Table S{table_map.get(num, num)}"

    tex = re.sub(r"Supplementary Tables S(\d+) and S(\d+)", plural_table_repl, tex)
    tex = re.sub(r"Supplementary Table S(\d+)", table_repl, tex)
    tex = tex.replace("Supplementary Figure S1 and Supplementary Table S4", "Supplementary Figure S1 and Supplementary Table S4")
    tex = tex.replace(r"Figure~\ref{fig:method}", r"Figure~\ref{fig:design}")
    tex = tex.replace(r"Figure~\ref{fig:ciciot-rare}", r"Figure~\ref{fig:ciciot-main}")

    tex = replace_figure(
        tex,
        "fig:design",
        figure_block(
            "figure1_study_validation_framework.png",
            "fig:design",
            "Study and validation control framework.",
            width=r"0.98\linewidth",
        ),
    )
    tex = remove_figure(tex, "fig:method")
    tex = replace_figure(
        tex,
        "fig:ciciot-main",
        figure_block(
            "figure2_ciciot_performance_rare_recall.png",
            "fig:ciciot-main",
            "Primary CICIoT2023 public subsample performance and rare label recall.",
            width=r"0.98\linewidth",
        ),
    )
    tex = remove_figure(tex, "fig:ciciot-rare")
    tex = replace_figure(
        tex,
        "fig:iotid",
        figure_block(
            "figure3_iotid20_repeated_split.png",
            "fig:iotid",
            "IoTID20 repeated split validation.",
            width=r"0.98\linewidth",
        )
        + "\n"
        + table3_iotid(),
    )
    tex = replace_figure(
        tex,
        "fig:nbaiot",
        figure_block(
            "figure4_nbaiot_unseen_device.png",
            "fig:nbaiot",
            "N-BaIoT leave one device out validation.",
            width=r"0.98\linewidth",
        )
        + "\n"
        + table4_nbaiot(),
    )

    algorithm_prose = (
        "Operationally, validation controlled ensemble selection used a fixed six step sequence. "
        "First, the CICIoT2023 public subsample training file was divided into fitting and internal validation subsets by stratified sampling. "
        "Second, Borderline-SMOTE LightGBM and class weighted XGBoost were fitted only on the fitting subset. "
        r"Third, candidate values of $\alpha$ from 0.00 to 1.00 were evaluated on the internal validation subset. "
        r"Fourth, the selected $\alpha$ was frozen before any test set prediction was inspected. "
        "Finally, both components were refitted on the full training split and evaluated once on the frozen CICIoT2023 public subsample test split."
    )
    tex = re.sub(
        r"\n\\begin\{center\}\s*\\noindent\\textbf\{Algorithm 1[\s\S]*?\\end\{center\}\n",
        lambda _m: "\n" + algorithm_prose + "\n",
        tex,
        count=1,
    )

    tex = re.sub(
        r"A wider model family screen is reported[\s\S]*?promoted to the primary model\.",
        (
            "Additional model family, SMOTEENN, class wise diagnostic and rare prior screens are reported "
            "in Supplementary Tables S12 to S17. These analyses are treated as diagnostics rather than "
            "as replacements for the frozen CICIoT2023 public subsample comparison."
        ),
        tex,
        count=1,
    )
    tex = re.sub(
        r"Class wise diagnostics are expanded[\s\S]*?primary Macro-F1 model\.",
        (
            "Class wise diagnostics and the recall sensitive rare prior screen are reported in "
            "Supplementary Tables S13, S14 and S17. They support the same interpretation: the selected "
            "ensemble improves several rare labels, but some rare labels remain only partially recovered."
        ),
        tex,
        count=1,
    )
    tex = re.sub(
        r"Supplementary Table S15 reports the repeated split class wise IoTID20 diagnostics[\s\S]*?dataset universal superiority\.",
        (
            "Supplementary Table S15 reports repeated split class wise IoTID20 diagnostics. "
            "The per class pattern is uneven, which is why the claim is written as split stable "
            "imbalance aware recall rather than dataset universal superiority."
        ),
        tex,
        count=1,
    )
    tex = tex.replace(
        "SHAP analysis performed at the component level is reported in Supplementary Figure S1 and Supplementary Table S4.",
        "Component level SHAP analysis is reported in Supplementary Figure S1 and Supplementary Table S4.",
    )

    discussion = r"""\section*{Discussion}

The CICIoT2023 public subsample results support validation controlled imbalance handling as a useful evaluation discipline for fine grained IoT intrusion detection. The main gain is not a claim that a new architecture dominates the field; it is that model weights, imbalance treatment and feature choices are fixed before the frozen test split is evaluated, and the result is judged with Macro-F1, minority recall, macro precision recall area and paired uncertainty rather than headline accuracy alone. Under this discipline, the validation selected ensemble improved the lowest support CICIoT2023 public subsample class while preserving a stronger overall Macro-F1 operating point than either a flat baseline or a recall only component. This is also why published high accuracy or detection rate studies are treated as benchmark context rather than direct leaderboard comparators: their datasets, label granularity, task definitions and split protocols differ from the present public subsample study.

The IoTID20 repeated holdouts limit the claim in a constructive way. They support a split stable imbalance aware recall pattern, but they do not support universal ensemble superiority. The stronger IoTID20 route was a compact top ten weighted LightGBM model, while the validation controlled ensemble remained close. This pattern indicates that class weighting under validation control is the transferable element, whereas the best architecture can shift with feature space, label set and dataset size. In practical terms, the framework provides a selection discipline for choosing among operating points, not a guarantee that probability mixing is always the best deployment model.

N-BaIoT adds a device boundary rather than a stronger claim of real world deployment. Binary and attack family tasks were nearly saturated in the capped leave one device out setting, which may reflect strong separability in engineered traffic statistics and should be read as an upper bound check. Fine grained attack labels were more heterogeneous across held out devices, making them the more informative boundary result. The study therefore supports a reproducible validation framework for imbalanced public IoT intrusion detection, while leaving concept drift, live traffic, wider multi dataset benchmarking, richer sequence or graph features and prospective deployment validation as necessary future tests.

"""
    tex = replace_section(tex, "Discussion", "Conclusion", discussion)
    tex = tex.replace(
        "Runtime summaries are reported in Supplementary Table S7.",
        "Runtime and model complexity records are reported in Supplementary Table S7.",
    )
    return tex


def build_main_tex() -> str:
    return clean_main_tex(base.generate_main_tex())


def section_block(tex: str, heading: str) -> str:
    pattern = rf"\\section\*\{{{re.escape(heading)}\}}[\s\S]*?(?=\\section\*\{{Supplementary Table S\d+\.|\\section\*\{{Supplementary Figure S\d+\.|\\section\*\{{Reproduction commands\}}|\\end\{{document\}})"
    match = re.search(pattern, tex)
    if not match:
        raise ValueError(f"Missing supplementary section: {heading}")
    return match.group(0).strip()


def build_supplementary_tex() -> str:
    src = base.generate_supplementary_tex()
    header = src[: src.index(r"\section*{Supplementary Table S0.")]
    repro = src[src.index(r"\section*{Reproduction commands}") :]
    blocks = [
        section_block(src, "Supplementary Figure S1. CICIoT2023 SHAP feature contributions"),
        section_block(src, "Supplementary Figure S2. CICIoT2023 alpha sensitivity"),
        section_block(src, "Supplementary Table S0. CICIoT2023 public subsample baseline variants").replace(
            "Supplementary Table S0. CICIoT2023 public subsample baseline variants",
            "Supplementary Table S1. CICIoT2023 baseline variants",
        ),
        section_block(src, "Supplementary Table S2. IoTID20 split-bootstrap deltas"),
        section_block(src, "Supplementary Table S3. IoTID20 exact sign-flip tests"),
        section_block(src, "Supplementary Table S5. CICIoT2023 SHAP feature contributions").replace(
            "Supplementary Table S5.", "Supplementary Table S4."
        ),
        section_block(src, "Supplementary Table S6. CICIoT2023 bootstrap summary").replace(
            "Supplementary Table S6.", "Supplementary Table S5."
        ),
        section_block(src, "Supplementary Table S7. CICIoT2023 alpha grid").replace(
            "Supplementary Table S7.", "Supplementary Table S6."
        ),
        section_block(src, "Supplementary Table S18. Runtime and model complexity").replace(
            "Supplementary Table S18.", "Supplementary Table S7."
        ),
        section_block(src, "Supplementary Table S9. Hyperparameters and implementation details").replace(
            "Supplementary Table S9.", "Supplementary Table S8."
        ),
        section_block(src, "Supplementary Table S10. Short labels for Figure 4").replace(
            "Supplementary Table S10. Short labels for Figure 4",
            "Supplementary Table S9. Short labels for Figure 2b",
        ),
        section_block(src, "Supplementary Table S11. Device codes for Figure 6").replace(
            "Supplementary Table S11. Device codes for Figure 6",
            "Supplementary Table S10. Device codes for Figure 4",
        ),
        section_block(src, "Supplementary Table S12. Benchmark context against recent intrusion detection studies").replace(
            "Supplementary Table S12.", "Supplementary Table S11."
        ),
        section_block(src, "Supplementary Table S13. Model family and baseline screen").replace(
            "Supplementary Table S13.", "Supplementary Table S12."
        ),
        section_block(src, "Supplementary Table S14. CICIoT2023 public subsample hardest and easiest class diagnostics").replace(
            "Supplementary Table S14.", "Supplementary Table S13."
        ),
        section_block(src, "Supplementary Table S15. CICIoT2023 public subsample low support class diagnostics").replace(
            "Supplementary Table S15.", "Supplementary Table S14."
        ),
        section_block(src, "Supplementary Table S16. IoTID20 repeated split class wise diagnostics").replace(
            "Supplementary Table S16.", "Supplementary Table S15."
        ),
        section_block(src, "Supplementary Table S17. N-BaIoT cap sensitivity").replace(
            "Supplementary Table S17.", "Supplementary Table S16."
        ),
        section_block(src, "Supplementary Table S19. CICIoT2023 rare prior operating point screen").replace(
            "Supplementary Table S19.", "Supplementary Table S17."
        ),
    ]
    body = "\n\n".join(blocks)
    return header + body + "\n\n" + repro


def update_readme(notes: list[str]) -> str:
    note_text = "\n".join(f"- {note}" for note in notes)
    return rf"""# Scientific Reports LaTeX Candidate v3

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

- `main.tex`: main article source using `\documentclass[fleqn,10pt]{{wlscirep}}`.
- `supplementary_information.tex`: supplementary source with independent Supplementary Table and Supplementary Figure numbering.
- `cover_letter.md`: draft cover letter.
- `figures/`: PNG files referenced by the TeX files plus TIFF upload versions.
- `supplementary_tables/`: source CSV and markdown records.
- `checksums.txt`: SHA-256 checksums.

## Template support

{note_text}

## Remaining submission blocker

The code availability section still needs an active public repository URL or archive DOI before portal submission.
"""


def compile_tex(tex_name: str) -> bool:
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", tex_name]
    try:
        result = subprocess.run(cmd, cwd=OUT_DIR, text=True, capture_output=True, timeout=180)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0:
        return True

    pdflatex = ["pdflatex", "-interaction=nonstopmode", tex_name]
    ok = True
    for _ in range(2):
        try:
            run = subprocess.run(pdflatex, cwd=OUT_DIR, text=True, capture_output=True, timeout=180)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        ok = ok and run.returncode == 0
    return ok


def cleanup_latex_aux() -> None:
    for pattern in ["*.aux", "*.fdb_latexmk", "*.fls", "*.log", "*.out", "*.synctex.gz"]:
        for path in OUT_DIR.glob(pattern):
            path.unlink(missing_ok=True)


def write_checksums() -> None:
    rows = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "checksums.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(f"{digest}  {path.relative_to(OUT_DIR).as_posix()}")
    (OUT_DIR / "checksums.txt").write_text("\n".join(rows), encoding="utf-8")


def create_zip() -> Path:
    zip_path = OUT_DIR.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(OUT_DIR.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(OUT_DIR))
    return zip_path


def main() -> None:
    notes = copy_source_package()
    prepare_figures()
    (OUT_DIR / "main.tex").write_text(build_main_tex(), encoding="utf-8", newline="\n")
    (OUT_DIR / "supplementary_information.tex").write_text(build_supplementary_tex(), encoding="utf-8", newline="\n")
    (OUT_DIR / "README_SUBMISSION.md").write_text(update_readme(notes), encoding="utf-8", newline="\n")

    for obsolete in [
        "figure1_validation_design",
        "figure2_validation_controlled_ensemble",
        "figure3_ciciot_main_metrics",
        "figure4_ciciot_rare_attack_recall",
        "figure5_iotid20_repeated_split",
        "figure6_nbaiot_unseen_device",
    ]:
        for ext in [".png", ".tiff"]:
            path = OUT_DIR / "figures" / f"{obsolete}{ext}"
            path.unlink(missing_ok=True)

    main_ok = compile_tex("main.tex")
    supp_ok = compile_tex("supplementary_information.tex")
    cleanup_latex_aux()
    write_checksums()
    zip_path = create_zip()
    print(f"Wrote {OUT_DIR}")
    print(f"Created {zip_path}")
    print(f"main compile: {'ok' if main_ok else 'not verified'}")
    print(f"supplement compile: {'ok' if supp_ok else 'not verified'}")


if __name__ == "__main__":
    sys.exit(main())
