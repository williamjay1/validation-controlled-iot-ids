from __future__ import annotations

import csv
import hashlib
import shutil
import textwrap
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "submission_package" / "scientific_reports_20260708_latex_candidate_v1"
FIG_SRC = ROOT / "figures" / "paper_figures"
TABLE_SRC = ROOT / "results" / "paper_tables"
BOOTSTRAP_SRC = ROOT / "results" / "statistical_uncertainty"
IOTID_REPEATED_SRC = ROOT / "results" / "iotid20_repeated_split"
CICIOT_CONFIRMATORY_SRC = ROOT / "results" / "ciciot_confirmatory_full"
CICIOT_ENSEMBLE_SRC = ROOT / "results" / "ciciot_ensemble_full"
NBAIOT_SRC = ROOT / "results" / "nbaiot_unseen_device_20k"


MAIN_FIGURES = [
    "figure1_validation_design.png",
    "figure1_validation_design.tiff",
    "figure2_validation_controlled_ensemble.png",
    "figure2_validation_controlled_ensemble.tiff",
    "figure3_ciciot_main_metrics.png",
    "figure3_ciciot_main_metrics.tiff",
    "figure4_ciciot_rare_attack_recall.png",
    "figure4_ciciot_rare_attack_recall.tiff",
    "figure5_iotid20_repeated_split.png",
    "figure5_iotid20_repeated_split.tiff",
    "figure6_nbaiot_unseen_device.png",
    "figure6_nbaiot_unseen_device.tiff",
    "supplementary_figure_s1_ciciot_shap_top_features.png",
    "supplementary_figure_s1_ciciot_shap_top_features.tiff",
    "supplementary_figure_s2_ciciot_alpha_sensitivity.png",
    "supplementary_figure_s2_ciciot_alpha_sensitivity.tiff",
]


TEMPLATE_FILES = {
    "wlscirep.cls": "https://raw.githubusercontent.com/mmelgui/Scientific-Report/master/wlscirep.cls",
    "jabbrv.sty": "https://raw.githubusercontent.com/mmelgui/Scientific-Report/master/jabbrv.sty",
    "jabbrv-ltwa-all.ldf": "https://raw.githubusercontent.com/mmelgui/Scientific-Report/master/jabbrv-ltwa-all.ldf",
    "jabbrv-ltwa-en.ldf": "https://raw.githubusercontent.com/mmelgui/Scientific-Report/master/jabbrv-ltwa-en.ldf",
    "naturemag-doi.bst": "https://raw.githubusercontent.com/mmelgui/Scientific-Report/master/naturemag-doi.bst",
}


FALLBACK_WLSCIREP = r"""
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{wlscirep}[2026/07/08 local compatibility class for Scientific Reports submissions]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions*
\LoadClass{article}
\RequirePackage[letterpaper,left=2cm,right=2cm,top=2.25cm,bottom=2.25cm]{geometry}
\RequirePackage{authblk}
\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{booktabs}
\RequirePackage{amsmath,amssymb,amsfonts}
\RequirePackage{caption}
\RequirePackage[colorlinks=true,allcolors=blue]{hyperref}
\RequirePackage[nospace,biblabel]{cite}
\renewcommand\Authfont{\fontsize{12}{12}\selectfont\bfseries}
\renewcommand\Affilfont{\fontsize{10}{12}\selectfont}
\setlength{\affilsep}{1.2em}
\renewcommand{\maketitle}{%
  \begin{flushleft}
  {\Large\bfseries \@title\par}
  \vspace{0.75em}
  {\@author\par}
  \vspace{1em}
  {\bfseries ABSTRACT}\par
  \vspace{0.3em}
  \theabstract
  \vspace{1.2em}
  \end{flushleft}
}
\def\xabstract{abstract}
\long\def\abstract#1\end#2{\def\two{#2}\ifx\two\xabstract
\long\gdef\theabstract{\ignorespaces#1}
\def\go{\end{abstract}}\else
#1\end{#2}
\gdef\theabstract{BADLY FORMED ABSTRACT}\let\go\relax\fi
\go}
"""


REFERENCES = r"""
\begin{thebibliography}{99}

\bibitem{alfuqaha2015iot}
Al-Fuqaha, A., Guizani, M., Mohammadi, M., Aledhari, M. \& Ayyash, M. Internet of Things: A survey on enabling technologies, protocols, and applications. \emph{IEEE Commun. Surv. Tutor.} \textbf{17}, 2347--2376 (2015). doi: \url{https://doi.org/10.1109/COMST.2015.2444095}.

\bibitem{roman2013iotsecurity}
Roman, R., Zhou, J. \& Lopez, J. On the features and challenges of security and privacy in distributed internet of things. \emph{Comput. Netw.} \textbf{57}, 2266--2279 (2013). doi: \url{https://doi.org/10.1016/j.comnet.2012.12.018}.

\bibitem{sicari2015iottrust}
Sicari, S., Rizzardi, A., Grieco, L. A. \& Coen-Porisini, A. Security, privacy and trust in Internet of Things: The road ahead. \emph{Comput. Netw.} \textbf{76}, 146--164 (2015). doi: \url{https://doi.org/10.1016/j.comnet.2014.11.008}.

\bibitem{neto2023ciciot}
Neto, E. C. P. et al. CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment. \emph{Sensors} \textbf{23}, 5941 (2023). doi: \url{https://doi.org/10.3390/s23135941}.

\bibitem{ullah2020iotid20}
Ullah, I. \& Mahmoud, Q. H. A scheme for generating a dataset for anomalous activity detection in IoT networks. In \emph{Advances in Artificial Intelligence}, Lecture Notes in Computer Science \textbf{12109}, 508--520 (Springer, 2020). doi: \url{https://doi.org/10.1007/978-3-030-47358-7_52}.

\bibitem{meidan2018nbaiot}
Meidan, Y. et al. N-BaIoT: Network based detection of IoT botnet attacks using deep autoencoders. \emph{IEEE Pervasive Comput.} \textbf{17}, 12--22 (2018). doi: \url{https://doi.org/10.1109/MPRV.2018.03367731}.

\bibitem{moustafa2015unsw}
Moustafa, N. \& Slay, J. UNSW-NB15: a comprehensive data set for network intrusion detection systems. In \emph{2015 Military Communications and Information Systems Conference}, 1--6 (2015). doi: \url{https://doi.org/10.1109/MilCIS.2015.7348942}.

\bibitem{sharafaldin2018cicids}
Sharafaldin, I., Lashkari, A. H. \& Ghorbani, A. A. Toward generating a new intrusion detection dataset and intrusion traffic characterization. In \emph{Proceedings of the 4th International Conference on Information Systems Security and Privacy}, 108--116 (2018). doi: \url{https://doi.org/10.5220/0006639801080116}.

\bibitem{koroniotis2019botiot}
Koroniotis, N., Moustafa, N., Sitnikova, E. \& Turnbull, B. Towards the development of realistic botnet dataset in the Internet of Things for network forensic analytics: Bot-IoT dataset. \emph{Future Gener. Comput. Syst.} \textbf{100}, 779--796 (2019). doi: \url{https://doi.org/10.1016/j.future.2019.05.041}.

\bibitem{ferrag2022edgeiiot}
Ferrag, M. A., Friha, O., Hamouda, D., Maglaras, L. \& Janicke, H. Edge-IIoTset: A new comprehensive realistic cyber security dataset of IoT and IIoT applications for centralized and federated learning. \emph{IEEE Access} \textbf{10}, 40281--40306 (2022). doi: \url{https://doi.org/10.1109/ACCESS.2022.3165809}.

\bibitem{he2009imbalanced}
He, H. \& Garcia, E. A. Learning from imbalanced data. \emph{IEEE Trans. Knowl. Data Eng.} \textbf{21}, 1263--1284 (2009). doi: \url{https://doi.org/10.1109/TKDE.2008.239}.

\bibitem{branco2016imbalanced}
Branco, P., Torgo, L. \& Ribeiro, R. P. A survey of predictive modeling on imbalanced domains. \emph{ACM Comput. Surv.} \textbf{49}, 1--50 (2016). doi: \url{https://doi.org/10.1145/2907070}.

\bibitem{krawczyk2016imbalanced}
Krawczyk, B. Learning from imbalanced data: open challenges and future directions. \emph{Prog. Artif. Intell.} \textbf{5}, 221--232 (2016). doi: \url{https://doi.org/10.1007/s13748-016-0094-0}.

\bibitem{chen2016xgboost}
Chen, T. \& Guestrin, C. XGBoost: A scalable tree boosting system. In \emph{Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining}, 785--794 (2016). doi: \url{https://doi.org/10.1145/2939672.2939785}.

\bibitem{chawla2002smote}
Chawla, N. V., Bowyer, K. W., Hall, L. O. \& Kegelmeyer, W. P. SMOTE: Synthetic minority over sampling technique. \emph{J. Artif. Intell. Res.} \textbf{16}, 321--357 (2002). doi: \url{https://doi.org/10.1613/jair.953}.

\bibitem{han2005borderline}
Han, H., Wang, W.-Y. \& Mao, B.-H. Borderline-SMOTE: A new over sampling method in imbalanced data sets learning. In \emph{Advances in Intelligent Computing}, Lecture Notes in Computer Science \textbf{3644}, 878--887 (Springer, 2005). doi: \url{https://doi.org/10.1007/11538059_91}.

\bibitem{galar2012ensembles}
Galar, M., Fernandez, A., Barrenechea, E., Bustince, H. \& Herrera, F. A review on ensembles for the class imbalance problem: Bagging, boosting, and hybrid based approaches. \emph{IEEE Trans. Syst. Man Cybern. C} \textbf{42}, 463--484 (2012). doi: \url{https://doi.org/10.1109/TSMCC.2011.2161285}.

\bibitem{alsubaei2025smart}
Alsubaei, F. S. Smart deep learning model for enhanced IoT intrusion detection. \emph{Sci. Rep.} \textbf{15}, 20577 (2025). doi: \url{https://doi.org/10.1038/s41598-025-06363-5}.

\bibitem{yu2025attack}
Yu, Y., Fu, Y., Liu, T., Wang, K. \& An, Y. An attack detection method based on deep learning for internet of things. \emph{Sci. Rep.} \textbf{15}, 28812 (2025). doi: \url{https://doi.org/10.1038/s41598-025-14808-0}.

\bibitem{amine2025improved}
Amine, M. S., Nada, F. A. \& Hosny, K. M. Improved model for intrusion detection in the Internet of Things. \emph{Sci. Rep.} \textbf{15}, 21547 (2025). doi: \url{https://doi.org/10.1038/s41598-025-92852-6}.

\bibitem{ma2025llm}
Ma, H., Zhang, W., Zhang, D. \& Chen, B. An IoT intrusion detection framework based on feature selection and large language models fine-tuning. \emph{Sci. Rep.} \textbf{15}, 21158 (2025). doi: \url{https://doi.org/10.1038/s41598-025-08905-3}.

\bibitem{sarwar2025securing}
Sarwar, N., Alharthi, R. S., Aljohani, M. \& Elhosseini, M. A. Securing IoT networks: a machine learning approach for detecting unusual traffic patterns. \emph{Sci. Rep.} \textbf{15}, 3397 (2025). doi: \url{https://doi.org/10.1038/s41598-025-33447-z}.

\bibitem{singh2025attentional}
Singh, R., Singh Gill, N. \& Gulia, P. Attentional LSTM-ensemble architecture for intrusion detection in smart grids. \emph{Sci. Rep.} \textbf{15}, 41977 (2025). doi: \url{https://doi.org/10.1038/s41598-025-25992-4}.

\bibitem{abushareha2026review}
Abu-Shareha, A. A. et al. Supervised machine learning intrusion detection review and multi criteria evaluation. \emph{Sci. Rep.} \textbf{16}, 14525 (2026). doi: \url{https://doi.org/10.1038/s41598-026-44773-1}.

\bibitem{davis2006pr}
Davis, J. \& Goadrich, M. The relationship between Precision-Recall and ROC curves. In \emph{Proceedings of the 23rd International Conference on Machine Learning}, 233--240 (2006). doi: \url{https://doi.org/10.1145/1143844.1143874}.

\bibitem{saito2015pr}
Saito, T. \& Rehmsmeier, M. The Precision-Recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. \emph{PLoS ONE} \textbf{10}, e0118432 (2015). doi: \url{https://doi.org/10.1371/journal.pone.0118432}.

\bibitem{efron1979bootstrap}
Efron, B. Bootstrap methods: another look at the jackknife. \emph{Ann. Stat.} \textbf{7}, 1--26 (1979). doi: \url{https://doi.org/10.1214/aos/1176344552}.

\bibitem{efron1987bca}
Efron, B. Better bootstrap confidence intervals. \emph{J. Am. Stat. Assoc.} \textbf{82}, 171--185 (1987). doi: \url{https://doi.org/10.1080/01621459.1987.10478410}.

\bibitem{dietterich1998tests}
Dietterich, T. G. Approximate statistical tests for comparing supervised classification learning algorithms. \emph{Neural Comput.} \textbf{10}, 1895--1923 (1998). doi: \url{https://doi.org/10.1162/089976698300017197}.

\bibitem{ernst2004permutation}
Ernst, M. D. Permutation methods: a basis for exact inference. \emph{Stat. Sci.} \textbf{19}, 676--685 (2004). doi: \url{https://doi.org/10.1214/088342304000000396}.

\bibitem{lundberg2020shap}
Lundberg, S. M. et al. From local explanations to global understanding with explainable AI for trees. \emph{Nat. Mach. Intell.} \textbf{2}, 56--67 (2020). doi: \url{https://doi.org/10.1038/s42256-019-0138-9}.

\end{thebibliography}
"""


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_csv_rows_if_exists(path: Path) -> list[dict[str, str]]:
    if path.exists():
        return read_csv_rows(path)
    return []


def fmt(value: str | float, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def fmt_maybe(value: str | float | None, digits: int = 4) -> str:
    if value is None:
        return "--"
    text = str(value).strip()
    if text == "" or text.lower() in {"nan", "none", "not measured", "not aggregated", "--"}:
        return tex_escape(text) if text and text != "nan" else "--"
    try:
        return f"{float(text):.{digits}f}"
    except ValueError:
        return tex_escape(text)


def fmt_signed(value: str | float, digits: int = 4) -> str:
    return f"{float(value):+.{digits}f}"


def fmt_seconds(value: str | float) -> str:
    return f"{float(value):.1f}"


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def row_by(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    for row in rows:
        if row[key] == value:
            return row
    raise KeyError(f"{key}={value}")


def bootstrap_row(rows: list[dict[str, str]], quantity: str) -> dict[str, str]:
    return row_by(rows, "quantity", quantity)


def delta_row(rows: list[dict[str, str]], run_id: str, metric: str) -> dict[str, str]:
    for row in rows:
        if row["run_id"] == run_id and row["metric"] == metric:
            return row
    raise KeyError(f"{run_id}:{metric}")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def figure_block(filename: str, label: str, caption: str, width: str = r"\linewidth") -> str:
    return rf"""
\begin{{figure}}[H]
\centering
\includegraphics[width={width}]{{figures/{filename}}}
\caption{{{caption}}}
\label{{{label}}}
\end{{figure}}
"""


def copy_template_files() -> list[str]:
    notes: list[str] = []
    for name, url in TEMPLATE_FILES.items():
        target = OUT_DIR / name
        try:
            data = urllib.request.urlopen(url, timeout=20).read()
            target.write_bytes(data)
            notes.append(f"downloaded {name} from public Overleaf template mirror")
        except Exception as exc:
            if name == "wlscirep.cls":
                target.write_text(FALLBACK_WLSCIREP.strip() + "\n", encoding="utf-8")
                notes.append(f"used fallback wlscirep.cls because download failed: {exc}")
            else:
                notes.append(f"skipped optional template support file {name}: {exc}")
    cls_path = OUT_DIR / "wlscirep.cls"
    if cls_path.exists():
        cls_text = cls_path.read_text(encoding="utf-8", errors="ignore")
        cls_text = cls_text.replace(
            r"\RequirePackage[superscript,biblabel,nomove]{cite}",
            r"\RequirePackage[nospace,biblabel]{cite}",
        )
        cls_text = cls_text.replace(
            r"\RequirePackage[super,sort&compress]{natbib}",
            r"\RequirePackage[numbers,sort&compress]{natbib}",
        )
        cls_path.write_text(cls_text, encoding="utf-8")
    return notes


def generate_main_tex() -> str:
    ciciot = read_csv_rows(TABLE_SRC / "table1_ciciot_main_results.csv")
    rare = read_csv_rows(TABLE_SRC / "table2_ciciot_rare_class_recall.csv")
    iotid = read_csv_rows(TABLE_SRC / "table3_iotid20_replication.csv")
    nbaiot = read_csv_rows(TABLE_SRC / "table4_nbaiot_unseen_device_summary.csv")
    shap = read_csv_rows(TABLE_SRC / "table5_ciciot_shap_top_features.csv")
    boot = read_csv_rows(BOOTSTRAP_SRC / "ciciot_bootstrap_summary.csv")
    iot_delta = read_csv_rows(IOTID_REPEATED_SRC / "paired_delta_bootstrap_summary.csv")
    iot_sign = read_csv_rows(IOTID_REPEATED_SRC / "paired_delta_signflip_summary.csv")
    ciciot_cost = read_csv_rows(CICIOT_CONFIRMATORY_SRC / "experiment_results.csv")
    ciciot_ens_cost = read_csv_rows(CICIOT_ENSEMBLE_SRC / "experiment_results.csv")
    rare_prior = read_csv_rows_if_exists(ROOT / "results" / "ciciot_rare_prior_tuning_full" / "experiment_results.csv")
    rare_prior_source = "full CICIoT2023 public subsample split"
    if not rare_prior:
        rare_prior = read_csv_rows_if_exists(ROOT / "results" / "ciciot_rare_prior_tuning_quick" / "experiment_results.csv")
        rare_prior_source = "quick stratified screen"
    smoteenn_screen = read_csv_rows_if_exists(ROOT / "results" / "ciciot_smoteenn_quick" / "experiment_results.csv")
    smoteenn_ensemble_screen = read_csv_rows_if_exists(
        ROOT / "results" / "ciciot_ensemble_smoteenn_quick" / "experiment_results.csv"
    )

    flat = row_by(ciciot, "model", "Flat LightGBM")
    bsmote = row_by(ciciot, "model", "Borderline-SMOTE LightGBM")
    xgb = row_by(ciciot, "model", "Weighted XGBoost")
    ens = row_by(ciciot, "model", "Validation-controlled ensemble")
    d_macro = bootstrap_row(boot, "delta_macro_f1")
    d_bal = bootstrap_row(boot, "delta_balanced_accuracy")
    d_min = bootstrap_row(boot, "delta_minority_recall")

    iot_flat = row_by(iotid, "run_id", "iotid_fine_lgbm_full")
    iot_top10_flat = row_by(iotid, "run_id", "iotid_fine_lgbm_mi_top10_flat")
    iot_weighted = row_by(iotid, "run_id", "iotid_fine_lgbm_weighted")
    iot_top10 = row_by(iotid, "run_id", "iotid_fine_lgbm_mi_top10_weighted")
    iot_ens = row_by(iotid, "run_id", "iotid_fine_lgbm_xgb_validation_ensemble")
    iot_d_f1 = delta_row(iot_delta, "iotid_fine_lgbm_mi_top10_weighted", "f1_macro")
    iot_d_min = delta_row(iot_delta, "iotid_fine_lgbm_mi_top10_weighted", "minority_recall_mean")
    iot_d_pr = delta_row(iot_delta, "iotid_fine_lgbm_mi_top10_weighted", "pr_auc_macro")
    iot_top10_flat_d_f1 = delta_row(iot_delta, "iotid_fine_lgbm_mi_top10_flat", "f1_macro")
    iot_top10_flat_d_min = delta_row(iot_delta, "iotid_fine_lgbm_mi_top10_flat", "minority_recall_mean")
    iot_sign_f1 = delta_row(iot_sign, "iotid_fine_lgbm_mi_top10_weighted", "f1_macro")
    iot_sign_min = delta_row(iot_sign, "iotid_fine_lgbm_mi_top10_weighted", "minority_recall_mean")

    nb_attack = row_by(nbaiot, "task", "attack")
    nb_binary = row_by(nbaiot, "task", "binary")
    nb_family = row_by(nbaiot, "task", "family")
    cost_flat = row_by(ciciot_cost, "run_id", "fine_lgbm_full")
    cost_ens = row_by(ciciot_ens_cost, "objective", "macro_f1")

    top_features = ", ".join(tex_escape(row["feature"]) for row in shap[:8])
    upload_flat = next(r for r in rare if r["class_label"] == "Uploading_Attack" and r["model"] == "Flat LightGBM")
    upload_ens = next(r for r in rare if r["class_label"] == "Uploading_Attack" and r["model"] == "Ensemble")
    ping_flat = next(r for r in rare if r["class_label"] == "Recon-PingSweep" and r["model"] == "Flat LightGBM")
    ping_ens = next(r for r in rare if r["class_label"] == "Recon-PingSweep" and r["model"] == "Ensemble")
    backdoor_flat = next(r for r in rare if r["class_label"] == "Backdoor_Malware" and r["model"] == "Flat LightGBM")
    backdoor_ens = next(r for r in rare if r["class_label"] == "Backdoor_Malware" and r["model"] == "Ensemble")
    xss_flat = next(r for r in rare if r["class_label"] == "XSS" and r["model"] == "Flat LightGBM")
    xss_ens = next(r for r in rare if r["class_label"] == "XSS" and r["model"] == "Ensemble")

    rare_prior_text = ""
    if rare_prior:
        recall_row = next(
            (
                r
                for r in rare_prior
                if r.get("objective") in {"minority_recall_constrained", "recall_sensitive"}
            ),
            rare_prior[-1],
        )
        rare_prior_text = (
            " A validation selected rare prior operating point is reported in Supplementary Table S19. "
            f"On the {rare_prior_source}, it used a multiplier of {fmt(recall_row['rare_multiplier'], 2)} "
            f"for the {tex_escape(recall_row['rare_scope'])} scope and produced Macro-F1 {fmt(recall_row['f1_macro'])} "
            f"with minority recall {fmt(recall_row['minority_recall_mean'])}. "
            "This is treated as a recall sensitive operating point rather than as the primary Macro-F1 model."
        )
    smoteenn_text = ""
    if smoteenn_screen:
        smoteenn_row = smoteenn_screen[0]
        smoteenn_text = (
            f" The SMOTEENN screen in Supplementary Table S13 increased minority recall to {fmt(smoteenn_row['minority_recall_mean'])} "
            f"on the quick CICIoT2023 public subsample screen, but Macro-F1 was {fmt(smoteenn_row['f1_macro'])}. "
        )
        if smoteenn_ensemble_screen:
            three_row = smoteenn_ensemble_screen[0]
            smoteenn_text += (
                f"The three component validation grid assigned SMOTEENN weight {fmt(three_row['w_lgbm_smoteenn'], 2)}, "
                "so this route was retained as a diagnostic screen rather than promoted to the primary model."
            )

    ciciot_rows = "\n".join(
        [
            rf"{tex_escape(flat['model'])} & {fmt(flat['accuracy'])} & {fmt(flat['balanced_accuracy'])} & {fmt(flat['macro_f1'])} & {fmt(flat['minority_recall'])} & {fmt(flat['pr_auc_macro'])} \\",
            rf"{tex_escape(bsmote['model'])} & {fmt(bsmote['accuracy'])} & {fmt(bsmote['balanced_accuracy'])} & {fmt(bsmote['macro_f1'])} & {fmt(bsmote['minority_recall'])} & {fmt(bsmote['pr_auc_macro'])} \\",
            rf"{tex_escape(xgb['model'])} & {fmt(xgb['accuracy'])} & {fmt(xgb['balanced_accuracy'])} & {fmt(xgb['macro_f1'])} & {fmt(xgb['minority_recall'])} & {fmt(xgb['pr_auc_macro'])} \\",
            rf"{tex_escape(ens['model'])} & {fmt(ens['accuracy'])} & {fmt(ens['balanced_accuracy'])} & {fmt(ens['macro_f1'])} & {fmt(ens['minority_recall'])} & {fmt(ens['pr_auc_macro'])} \\",
            rf"Ensemble minus flat LightGBM & n/a & {fmt_signed(d_bal['point_estimate'])} & {fmt_signed(d_macro['point_estimate'])} & {fmt_signed(d_min['point_estimate'])} & n/a \\",
        ]
    )

    fig1 = figure_block(
        "figure1_validation_design.png",
        "fig:design",
        r"\textbf{Study design and validation roles.} The CICIoT2023 public subsample was used as the primary benchmark, IoTID20 as the repeated holdout stability check and N-BaIoT as the capped unseen device boundary check. Each dataset contributes a distinct part of the evidence chain.",
    )
    fig2 = figure_block(
        "figure2_validation_controlled_ensemble.png",
        "fig:method",
        r"\textbf{Validation-controlled ensemble framework.} Training, internal validation and frozen test evaluation are separated. The dashed barrier indicates that no test information flows back into alpha selection.",
        width=r"0.98\linewidth",
    )
    fig3 = figure_block(
        "figure3_ciciot_main_metrics.png",
        "fig:ciciot-main",
        r"\textbf{CICIoT2023 public subsample main validation metrics.} Macro-F1, minority recall and macro PR-AUC are shown for the flat baseline, two imbalance aware components and the validation controlled ensemble on the frozen public subsample test split.",
    )
    fig4 = figure_block(
        "figure4_ciciot_rare_attack_recall.png",
        "fig:ciciot-rare",
        r"\textbf{Rare attack recall on the CICIoT2023 public subsample.} The bars compare flat LightGBM, two imbalance treatments and the selected ensemble for the four lowest support attack labels. Short labels keep the plot readable; original CICIoT2023 labels are mapped in Supplementary Table S10.",
    )
    fig5 = figure_block(
        "figure5_iotid20_repeated_split.png",
        "fig:iotid",
        r"\textbf{IoTID20 split stable effects of feature selection and class weighting.} Point estimates and 95\% split bootstrap intervals are shown relative to flat LightGBM across 10 stratified 70/30 holdouts. The near zero top ten flat result shows that feature selection alone did not improve minority recall.",
    )
    fig6 = figure_block(
        "figure6_nbaiot_unseen_device.png",
        "fig:nbaiot",
        r"\textbf{N-BaIoT capped leave one device out validation.} Present class Macro-F1 and worst present class recall are shown for each held out device under binary, attack family and fine grained attack label settings. Device codes D1 to D9 are mapped to original device names in Supplementary Table S11.",
    )

    return rf"""
\documentclass[fleqn,10pt]{{wlscirep}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{tabularx}}
\usepackage{{array}}
\usepackage{{booktabs}}
\usepackage{{url}}
\usepackage{{float}}
\usepackage{{amsmath}}
\usepackage{{lineno}}
\newcolumntype{{Y}}{{>{{\raggedright\arraybackslash}}X}}
\newcolumntype{{L}}[1]{{>{{\raggedright\arraybackslash}}p{{#1}}}}
\Urlmuskip=0mu plus 1mu
\emergencystretch=3em

\title{{Validation controlled imbalance aware learning for fine grained IoT intrusion detection}}

\author[1,2]{{Junjie Zhang}}
\author[1,*]{{Siyu Wang}}
\affil[1]{{Shanghai Academy of Global Governance \& Area Studies, Shanghai International Studies University, Shanghai 201620, China; Junjie Zhang: junjiezhang2024@shisu.edu.cn; junjiezhang1720@163.com}}
\affil[2]{{School of Economics and Finance, Shanghai International Studies University, Shanghai 201620, China}}
\affil[*]{{Correspondence: Siyu Wang, wangsiyu\_real@126.com}}

\begin{{abstract}}
Fine grained Internet of Things intrusion detection remains difficult because high aggregate accuracy can hide weak recall for rare attack labels. We evaluate validation controlled imbalance handling with a probability ensemble whose mixing weight is selected only on an internal validation split. On the CICIoT2023 public subsample, the selected ensemble increased Macro-F1 from {fmt(flat['macro_f1'])} to {fmt(ens['macro_f1'])} and minority recall, defined as recall for the lowest support test class, from {fmt(flat['minority_recall'])} to {fmt(ens['minority_recall'])}. IoTID20 repeated holdouts supported a split stable recall pattern: top ten weighted LightGBM improved Macro-F1 by {fmt(iot_d_f1['mean_delta_vs_flat_lgbm'])} and minority recall by {fmt(iot_d_min['mean_delta_vs_flat_lgbm'])} relative to flat LightGBM, but did not support universal ensemble superiority. In N-BaIoT, binary and family tasks were near saturated under a capped leave one device out setting, whereas fine grained attack labels were more device dependent. The results support validation controlled imbalance handling as a reproducible evaluation discipline, rather than a universal claim for one ensemble across datasets.
\end{{abstract}}

\begin{{document}}
\raggedbottom
\sloppy
\maketitle
\thispagestyle{{empty}}

\noindent\textbf{{Keywords:}} Internet of Things; intrusion detection; class imbalance; rare attack recognition; ensemble learning; external validation

\section*{{Introduction}}

Internet of Things (IoT) systems are now embedded in homes, healthcare, transportation, manufacturing and smart city infrastructure \cite{{alfuqaha2015iot,roman2013iotsecurity,sicari2015iottrust}}. Intrusion detection in these environments cannot stop at benign versus malicious separation. Fine grained attack recognition matters because reconnaissance, spoofing, denial of service and malware related events call for different mitigation decisions. High overall accuracy can still leave rare attack categories poorly recognized.

Public intrusion detection datasets have made reproducible IoT and network security evaluation more feasible, including CICIoT2023, IoTID20, N-BaIoT, UNSW-NB15, CICIDS2017, Bot-IoT and Edge-IIoTset \cite{{neto2023ciciot,ullah2020iotid20,meidan2018nbaiot,moustafa2015unsw,sharafaldin2018cicids,koroniotis2019botiot,ferrag2022edgeiiot}}. These datasets also expose a persistent evaluation problem: aggregate scores can obscure weak recognition of low support labels.

A central difficulty is class imbalance. Modern machine learning models learn dominant IoT traffic patterns efficiently, but majority labels can also dominate loss functions, validation choices and headline performance measures \cite{{he2009imbalanced,branco2016imbalanced,krawczyk2016imbalanced}}. Accuracy is therefore a weak security metric when rare labels have low recall. Macro-F1, balanced accuracy, macro precision recall area and minority recall give a more direct view of fine grained intrusion detection.

Existing strategies solve only part of the problem. Gradient tree boosting provides a strong tabular learner for this setting \cite{{chen2016xgboost}}. SMOTE and Borderline-SMOTE increase exposure to underrepresented classes, although synthetic samples can be unreliable when the minority boundary is noisy \cite{{chawla2002smote,han2005borderline}}. Class weighting increases sensitivity to rare classes, often at the cost of precision or global class balance. Ensembles can combine operating points \cite{{galar2012ensembles}}, but many intrusion detection studies use fixed weights or select configurations after repeated observation of test performance. Such designs risk optimistic evaluation because the ensemble configuration is influenced directly or indirectly by the test data.

The recent literature is also broad in model family. Traditional machine learning studies still report competitive results with tree models and feature selection because network flow tables are structured and high dimensional. Deep learning studies use convolutional, recurrent, attention and transformer style models to learn richer traffic representations. Other work combines feature selection with large language model based augmentation, focal loss or class sensitive objectives to address imbalance. Edge and lightweight intrusion detection studies add an efficiency constraint because a detector may need to run near constrained devices. These strands are useful, but they answer different questions: some emphasize architecture novelty, some emphasize accuracy, and some emphasize computational cost.

The methodological gap is therefore not simply the absence of another classifier. Recent Scientific Reports studies show that machine learning intrusion detection remains active \cite{{alsubaei2025smart,yu2025attack,amine2025improved,ma2025llm,sarwar2025securing,singh2025attentional}}, while a supervised intrusion detection review highlights fragmentation across datasets, metrics and evaluation criteria \cite{{abushareha2026review}}. Several studies report high headline accuracy or detection rate under their own data splits and task definitions. Those results are important field context, but they are not direct substitutes for rare class recall, frozen test evaluation, repeated split uncertainty and device held out validation. Supplementary Table S12 therefore compares recent Scientific Reports and adjacent intrusion detection studies by validation design rather than treating incompatible headline scores as a leaderboard.

This manuscript consequently makes a conservative claim. It does not propose a new deep architecture and it does not claim the highest reported accuracy on the complete original CICIoT2023 corpus. Instead, it asks whether imbalance aware model choices can be fixed by validation data and then evaluated under a controlled evidence chain. The answer matters because a high accuracy detector that misses rare attacks may be less useful than a detector with a slightly lower global score but a better documented rare class operating point.

We address this gap by treating validation control as part of the learning framework. A Borderline-SMOTE LightGBM component and a class weighted XGBoost component are mixed through a probability weight selected on internal validation data only \cite{{chen2016xgboost}}. Final performance on the CICIoT2023 public subsample is evaluated once on a frozen test split \cite{{neto2023ciciot}}. IoTID20 \cite{{ullah2020iotid20}} and N-BaIoT \cite{{meidan2018nbaiot}} are used as boundary checks for split stability and generalization to unseen devices, not as extra leaderboard claims. Additional public intrusion detection datasets motivate the broader benchmark context \cite{{moustafa2015unsw,sharafaldin2018cicids,koroniotis2019botiot,ferrag2022edgeiiot}}.

The study makes three contributions. First, it introduces a reusable model selection framework that controls validation for imbalanced multi class security classification. Second, it evaluates the framework with rare class metrics, bootstrap uncertainty, repeated holdouts and capped leave one device out validation. Third, it shows that the transferable finding is imbalance aware validation and weighting rather than a universal claim that one ensemble dominates every dataset. The article next reports the validation evidence, discusses the boundaries of the claim and then provides the full implementation details needed for reproduction.

\section*{{Methods}}

\subsection*{{Study framework}}

Three validation roles structure the study (Figure~\ref{{fig:design}}). The CICIoT2023 public subsample serves as the primary confirmatory benchmark because it provides a large public fine grained IoT attack setting. IoTID20 is an independent check of split stability with repeated stratified holdouts. N-BaIoT is a capped validation problem where each device is removed completely from training and used as an unseen test device.

{fig1}

\subsection*{{Validation-controlled ensemble method}}

Probability mixing uses two complementary components (Figure~\ref{{fig:method}}). Borderline-SMOTE LightGBM supplies the component that preserves Macro-F1. XGBoost with class weights supplies the component that is sensitive to recall. For the CICIoT2023 public subsample, the 1,143,802 row training split was further divided into an 80\% fitting split and a 20\% validation split with stratified sampling and random seed 42. The mixing weight $\alpha$ was selected only on this validation split. For observation $i$ and class $c$, the ensemble probability is

\begin{{equation}}
\hat{{p}}_{{i,c}}^{{ens}}(\alpha)
=
\alpha \hat{{p}}_{{i,c}}^{{LGBM}}
+
(1-\alpha)\hat{{p}}_{{i,c}}^{{XGB}},
\label{{eq:ensemble}}
\end{{equation}}

where $\hat{{p}}_{{i,c}}^{{LGBM}}$ and $\hat{{p}}_{{i,c}}^{{XGB}}$ are component probabilities and $\alpha$ is selected from 0.00 to 1.00 in increments of 0.05. The convex constraint keeps the output on the probability simplex and prevents extrapolation beyond the two fitted components. On the CICIoT2023 public subsample, both Macro-F1 and a composite Macro-F1 plus minority recall objective selected $\alpha=0.50$; the validation curve is reported in Supplementary Figure S2.

{fig2}

\begin{{center}}
\noindent\textbf{{Algorithm 1. Validation-controlled ensemble selection.}} The procedure fixes all model choices before the frozen test split is evaluated.
\smallskip
\small
\begin{{tabularx}}{{\linewidth}}{{L{{0.9cm}} Y}}
\toprule
Step & Operation \\
\midrule
1 & Split the CICIoT2023 public subsample training file into a fitting split and an internal validation split using stratified sampling. \\
2 & Fit Borderline-SMOTE LightGBM and XGBoost with class weights on the fitting sub-split only. \\
3 & Evaluate candidate $\alpha$ values from 0.00 to 1.00 on the validation sub-split. \\
4 & Select $\alpha$ by validation Macro-F1, with minority recall used as the secondary criterion. \\
5 & Refit the two components on the full CICIoT2023 public subsample training split and freeze $\alpha$. \\
6 & Evaluate the frozen ensemble once on the CICIoT2023 public subsample test split. \\
\bottomrule
\end{{tabularx}}
\end{{center}}

\subsection*{{Dataset preparation and leakage control}}

Only numeric traffic features were used. The CICIoT2023 public subsample contained 47 numeric predictors after label and metadata columns were excluded. Non finite values were replaced with missing values and then imputed as zero for CICIoT2023 public subsample tree models; IoTID20 rows with missing or infinite values were removed before splitting. No categorical feature encoding was applied because categorical labels and identifiers were excluded from the feature matrix unless a variable was explicitly part of the task definition. Label encoders were fitted on training data only. Feature ranking, oversampling and class weight computation were also fitted within the training portion of each split. For the CICIoT2023 public subsample, the predefined test file was not used for feature selection, model choice, threshold tuning or ensemble weight selection.

The IoTID20 repeated experiment used 10 stratified 70/30 holdouts with seeds 42 through 51. Fixed factors included data cleaning, feature space, model hyperparameters, class weighting and the top ten mutual information feature selection procedure. The varying factor was the split seed. The N-BaIoT experiment used a cap of 20,000 rows per source file after non finite rows were removed. Leave one device out folds were then constructed so that each held out device represented an unseen entity rather than a random subset of the same device traffic. Table~\ref{{tab:design}} summarizes the dataset roles and leakage control rules.

\begin{{table}}[H]
\centering
\caption{{\textbf{{Dataset roles and validation design.}} Each dataset was assigned a distinct inferential role so that primary performance, repeated split stability and unseen-device generalization are not collapsed into a single overbroad claim.}}
\label{{tab:design}}
\small
\begin{{tabularx}}{{\linewidth}}{{L{{2.15cm}} L{{2.65cm}} L{{2.25cm}} L{{2.55cm}} Y}}
\toprule
Dataset & Role & Rows used & Target & Leakage-control rule \\
\midrule
CICIoT2023 public subsample & Primary confirmatory benchmark & 1,143,802 train; 285,951 test & 34 fine grained labels & Predefined test split frozen; internal validation only for alpha selection \\
IoTID20 public mirror & Repeated independent holdout replication & 625,783 after cleaning & Nine labels & Ten stratified 70/30 splits; training-only feature ranking; split-level bootstrap \\
N-BaIoT UCI archive & Capped unseen device validation & 1,772,641 after cleaning & Binary, family and attack labels & One complete device held out in each fold \\
\bottomrule
\end{{tabularx}}
\end{{table}}

\subsection*{{Evaluation metrics}}

The primary metric for fine grained classification was Macro-F1. Secondary metrics included accuracy, balanced accuracy, macro precision recall area, weighted F1, minority recall, worst class recall and inference time per 1,000 rows. Precision recall analysis is particularly informative under class imbalance \cite{{davis2006pr,saito2015pr}}. Minority recall was defined as

\begin{{equation}}
R_{{minority}} =
\frac{{1}}{{|\mathcal{{C}}_{{min}}|}}
\sum_{{c \in \mathcal{{C}}_{{min}}}}
\frac{{TP_c}}{{TP_c + FN_c}},
\label{{eq:minority}}
\end{{equation}}

where $\mathcal{{C}}_{{min}}=\left\{{c:n_c=\min_j n_j,\ n_j>0\right\}}$ is the set of classes with the lowest positive support in the evaluation split, $n_c$ is the support of class $c$, and $TP_c$ and $FN_c$ are true positives and false negatives for class $c$. In the CICIoT2023 public subsample test split, this set contains Uploading\_Attack only, with 267 test rows. Figure~\ref{{fig:ciciot-rare}} is a separate diagnostic for the four lowest support attack labels and is not the definition of minority recall. For N-BaIoT, Macro-F1 for classes present in the fold was also reported because some held out devices lack attack labels that are present in the training devices.

\subsection*{{Statistical analysis}}

For the main CICIoT2023 public subsample comparison, paired row bootstrap intervals were computed on the frozen test file using 2,000 resamples \cite{{efron1979bootstrap,efron1987bca}}. These intervals quantify uncertainty from resampling the fixed test file; they do not estimate uncertainty from alternative CICIoT2023 public subsample train test partitions. That limitation is deliberate because the public subsample test split was kept frozen. Split uncertainty is instead examined in IoTID20. For IoTID20, paired deltas were computed at the split level for each of the 10 repeated holdouts:

\begin{{equation}}
\Delta M_s = M_{{A,s}} - M_{{B,s}}, \qquad s=1,\ldots,S,
\label{{eq:splitdelta}}
\end{{equation}}

where $M_{{A,s}}$ is the metric for the imbalance-aware model, $M_{{B,s}}$ is the metric for flat LightGBM and $S=10$ for IoTID20. Percentile intervals were estimated from 10,000 bootstrap resamples of the paired split-level deltas:

\begin{{equation}}
\mathrm{{CI}}_{{1-\gamma}} =
\left[
q_{{\gamma/2}}\left(\Delta M^*\right),
q_{{1-\gamma/2}}\left(\Delta M^*\right)
\right],
\label{{eq:bootstrap}}
\end{{equation}}

where $\Delta M^*$ is the bootstrap distribution of paired performance differences and $q$ denotes the empirical quantile.

As a second check for IoTID20, an exact sign flip test was applied to the 10 paired split level deltas \cite{{dietterich1998tests,ernst2004permutation}}. The null distribution was generated by all $2^{{10}}$ possible sign assignments to the paired deltas. This test is reported as a robustness check for direction consistency rather than as a replacement for effect sizes and intervals.

\subsection*{{Software and reproducibility}}

Analyses were implemented in Python using pandas, scikit learn, imbalanced learn, LightGBM, XGBoost, NumPy, matplotlib, seaborn and SHAP \cite{{lundberg2020shap}}. Package requirements are pinned in \texttt{{requirements.txt}}. LightGBM used 220 estimators, learning rate 0.06, 63 leaves and \texttt{{random\_state=42}}. XGBoost used 220 estimators, maximum depth 7, learning rate 0.08 and the histogram tree method. Borderline-SMOTE used an adaptive \texttt{{k\_neighbors}} value from 1 to 5 according to the smallest training class; \texttt{{m\_neighbors}} used the imbalanced learn default. All stochastic splits, model seeds, bootstrap resamples and SHAP sampling steps used fixed random seeds recorded in the executable scripts. Experiments were run on Windows 11 with an AMD Ryzen 9 8945HS processor and 31.3 GB RAM. Runtime summaries are reported in Supplementary Table S8. AI assisted coding and drafting tools were used to help generate scripts, check numerical consistency and improve manuscript wording; the authors reviewed all generated text and verified all numerical claims against result files.

\section*{{Results}}

\subsection*{{CICIoT2023 public subsample validation performance}}

To determine whether validation controlled selection improves fine grained intrusion detection under severe class imbalance, the CICIoT2023 public subsample was used as the primary benchmark. Flat LightGBM reached high accuracy but weak minority recall. The ensemble selected on internal validation data raised Macro-F1 from {fmt(flat['macro_f1'])} to {fmt(ens['macro_f1'])} and minority recall from {fmt(flat['minority_recall'])} to {fmt(ens['minority_recall'])}. Macro PR-AUC also increased from {fmt(flat['pr_auc_macro'])} to {fmt(ens['pr_auc_macro'])} (Figure~\ref{{fig:ciciot-main}}).

{fig3}

Borderline-SMOTE LightGBM preserved stronger Macro-F1 than the flat baseline. Weighted XGBoost gave the highest minority recall, but at lower Macro-F1. Probability mixing selected a middle operating point with stronger class balance than either a flat model or a recall only component.

\begin{{table}}[H]
\centering
\caption{{\textbf{{CICIoT2023 public subsample main results.}} Metrics are computed on the frozen public subsample test split. The final row reports ensemble minus flat LightGBM paired row bootstrap point differences from 2,000 resamples.}}
\label{{tab:ciciot}}
\scriptsize
\begin{{tabularx}}{{\linewidth}}{{L{{3.9cm}} c c c c c}}
\toprule
Model or comparison & Accuracy & Bal. acc. & Macro-F1 & Minority recall & Macro PR-AUC \\
\midrule
{ciciot_rows}
\bottomrule
\end{{tabularx}}
\end{{table}}

Paired row bootstrap intervals supported the CICIoT2023 public subsample differences under the fixed test split. The ensemble minus flat LightGBM Macro-F1 delta was {fmt(d_macro['point_estimate'])}, with a 95\% interval from {fmt(d_macro['ci_low_2_5'])} to {fmt(d_macro['ci_high_97_5'])}. Minority recall increased by {fmt(d_min['point_estimate'])}, with a 95\% interval from {fmt(d_min['ci_low_2_5'])} to {fmt(d_min['ci_high_97_5'])}. Balanced accuracy increased by {fmt(d_bal['point_estimate'])}. These findings support the ensemble as the primary CICIoT2023 public subsample operating point under the fixed public subsample split.

A wider model family screen is reported in Supplementary Table S13. It includes Random Forest, ExtraTrees, XGBoost, CatBoost, LightGBM variants and a simple multilayer perceptron where the quick baseline run is available. This screen is not used to replace the frozen full CICIoT2023 public subsample comparison, but it reduces the risk that the main result is only a contrast against a weak baseline family.
{smoteenn_text}

\subsection*{{Improvement of minority attack recognition}}

To investigate whether the aggregate gain reflected rare attack recognition rather than only majority class performance, recall was examined for four low support attack labels (Figure~\ref{{fig:ciciot-rare}}). The ensemble increased Uploading\_Attack recall from {fmt(upload_flat['recall'])} to {fmt(upload_ens['recall'])}, Recon-PingSweep recall from {fmt(ping_flat['recall'])} to {fmt(ping_ens['recall'])}, Backdoor\_Malware recall from {fmt(backdoor_flat['recall'])} to {fmt(backdoor_ens['recall'])} and XSS recall from {fmt(xss_flat['recall'])} to {fmt(xss_ens['recall'])}. Weighted XGBoost alone gave higher recall for several rare labels. This compromise is the intended behavior: rare attacks become more visible without allowing a recall only component to dominate the final model.

{fig4}

Class wise diagnostics are expanded in Supplementary Tables S14 and S15. These tables report precision, recall and F1 for the hardest and easiest CICIoT2023 public subsample classes, plus a focused low support label table. The diagnostic pattern is consistent with the main minority recall result: the selected ensemble improves several rare labels, while some rare classes remain only partially recovered.
{rare_prior_text}

\subsection*{{Cross-dataset validation}}

\subsubsection*{{IoTID20 repeated holdout stability}}

To determine whether the imbalance aware pattern was stable beyond a single holdout, IoTID20 was evaluated with 10 repeated stratified 70/30 splits and bootstrap at the split level. Across the 10 splits, flat LightGBM achieved mean Macro-F1 {fmt(iot_flat['mean_macro_f1'])} and mean minority recall {fmt(iot_flat['mean_minority_recall'])}. Top ten flat LightGBM achieved mean Macro-F1 {fmt(iot_top10_flat['mean_macro_f1'])} and minority recall {fmt(iot_top10_flat['mean_minority_recall'])}. Top ten weighted LightGBM achieved mean Macro-F1 {fmt(iot_top10['mean_macro_f1'])} (SD {fmt(iot_top10['sd_macro_f1'])}) and minority recall {fmt(iot_top10['mean_minority_recall'])} (SD {fmt(iot_top10['sd_minority_recall'])}).

The ablation separates feature selection from imbalance handling. Relative to flat LightGBM, top ten flat LightGBM improved Macro-F1 by only {fmt(iot_top10_flat_d_f1['mean_delta_vs_flat_lgbm'])} and changed minority recall by {fmt_signed(iot_top10_flat_d_min['mean_delta_vs_flat_lgbm'])}. Top ten weighted LightGBM improved Macro-F1 by {fmt(iot_d_f1['mean_delta_vs_flat_lgbm'])}, with a 95\% split bootstrap interval from {fmt(iot_d_f1['ci_low_2_5'])} to {fmt(iot_d_f1['ci_high_97_5'])}. Minority recall increased by {fmt(iot_d_min['mean_delta_vs_flat_lgbm'])}, with a 95\% interval from {fmt(iot_d_min['ci_low_2_5'])} to {fmt(iot_d_min['ci_high_97_5'])}. Exact sign flip tests gave two sided $p={fmt(iot_sign_f1['exact_two_sided_p'])}$ for Macro-F1 and $p={fmt(iot_sign_min['exact_two_sided_p'])}$ for minority recall. Macro PR-AUC remained essentially unchanged: the top ten weighted LightGBM delta was {fmt(iot_d_pr['mean_delta_vs_flat_lgbm'])}, with an interval from {fmt(iot_d_pr['ci_low_2_5'])} to {fmt(iot_d_pr['ci_high_97_5'])}. The validation controlled ensemble was close, with mean Macro-F1 {fmt(iot_ens['mean_macro_f1'])} and minority recall {fmt(iot_ens['mean_minority_recall'])}, but it did not surpass the compact weighted LightGBM route. The stable effect is class weighting under validation control, not the specific ensemble architecture (Figure~\ref{{fig:iotid}}).

{fig5}

Supplementary Table S16 reports the repeated split class wise IoTID20 diagnostics. It shows that the minority recall gain is not a single split accident, but the per class pattern is uneven, which explains why the claim is written as split stable imbalance aware recall rather than dataset universal superiority.

\subsubsection*{{N-BaIoT unseen-device validation}}

To investigate whether performance was retained when complete devices were held out, N-BaIoT was evaluated with capped leave one device out folds. Binary and attack family settings were near saturated, with mean Macro-F1 of {fmt(nb_binary['mean_macro_f1'])} and {fmt(nb_family['mean_macro_f1'])}, respectively. Such near perfect values should be read cautiously because N-BaIoT statistics may separate benign and attack periods unusually well and because the 20,000 row per file cap may influence the apparent ceiling. Fine grained attack labels were more heterogeneous: mean Macro-F1 was {fmt(nb_attack['mean_macro_f1'])}, minimum Macro-F1 was {fmt(nb_attack['min_macro_f1'])}, mean Macro-F1 for classes present in the fold was {fmt(nb_attack['mean_present_macro_f1'])} and the weakest present class recall across folds was {fmt(nb_attack['min_present_class_recall'])}. The N-BaIoT results are best interpreted as capped sample device transfer evidence rather than a direct estimate of live deployment performance (Figure~\ref{{fig:nbaiot}}).

{fig6}

Supplementary Table S17 compares the available N-BaIoT per file caps. The sensitivity table is used only to check whether the capped device transfer pattern changes materially with sample size; it does not convert N-BaIoT into live deployment evidence.

SHAP analysis performed at the component level is reported in Supplementary Figure S1 and Supplementary Table S5. The highest ranked CICIoT2023 public subsample LightGBM features were {top_features}. These timing, packet size, protocol and flag count variables are plausible traffic level signals. The purpose of SHAP here is to check that the model attends to reasonable traffic features, not to identify causal features of attacks.

\section*{{Discussion}}

This study is best understood as a validation framework rather than as a new IoT classifier architecture. Recent intrusion detection papers in Scientific Reports often emphasize deep, attention based, large language model, feature selection or deployment oriented architectures \cite{{alsubaei2025smart,yu2025attack,amine2025improved,ma2025llm,sarwar2025securing,singh2025attentional}}. Our contribution is different: model weights, imbalance treatment and feature choices are fixed before the final test evaluation, and the claim is judged with rare class metrics, uncertainty estimates and boundary datasets. The CICIoT2023 public subsample result supports this discipline as a useful way to improve Macro-F1 and minority recall without using the test split for selection.

The validation controls changed the interpretation of the experiments. If the study reported only accuracy on one split, the flat LightGBM model would already look strong and the rare class failure would be easy to miss. Adding minority recall exposed the Uploading\_Attack weakness. Adding the alpha validation curve prevented the ensemble weight from being chosen after observing test performance. Adding row bootstrap quantified uncertainty on the frozen CICIoT2023 public subsample test file. Adding repeated IoTID20 holdouts showed that the stable effect was class weighting under validation control, not the specific ensemble architecture. Adding N-BaIoT device holdouts showed that near perfect binary or family performance can coexist with less secure fine grained attack transfer.

The framework is useful in this setting because its components occupy different operating points. Borderline-SMOTE LightGBM preserves Macro-F1. XGBoost with class weights contributes recall sensitivity. Validation then selects the probability mixture on held out internal data. This keeps the frozen test split out of model selection while still allowing a compromise between sensitivity and balance. This interpretation also explains why the CICIoT2023 public subsample Macro-F1 should not be compared directly with papers that report very high accuracy or detection rate under different label granularity, data versions, binary tasks or random split protocols. The manuscript therefore avoids a leaderboard claim and treats published high score studies as benchmark context rather than direct evidence against or for the present model.

The failure analysis is as important as the positive result. IoTID20 did not identify the CICIoT2023 public subsample ensemble as the most stable route. A compact top ten weighted LightGBM model performed slightly better, while the ensemble remained close. The top ten flat ablation shows why: feature selection alone produced only a small Macro-F1 gain and did not improve minority recall, whereas class weighting changed rare class behavior. IoTID20 has fewer labels and a different feature distribution than the CICIoT2023 public subsample, so the best operating point shifts toward a simpler LightGBM heavy solution. This bounds the claim to imbalance aware validation and weighting, not universal ensemble dominance.

N-BaIoT adds a different boundary rather than a stronger leaderboard result. It is included because complete devices can be held out, which asks a question not answered by random row splits. At the same time, binary and family tasks are nearly saturated under the capped leave one device out setting, which may reflect strong separability in the engineered traffic statistics rather than realistic live world difficulty. We therefore treat N-BaIoT as a capped sample upper bound device transfer check. Fine grained attack labels still vary by held out device, which is the more informative result for deployment. The cap sensitivity analysis in Supplementary Table S17 is reported to check the sampling boundary, but it does not remove the need for future validation on live or temporally shifted traffic.

The computational cost is moderate for an offline validation study but not free. On the CICIoT2023 public subsample, the ensemble required training both components ({fmt_seconds(cost_ens['train_seconds'])} s in total), whereas flat LightGBM required {fmt_seconds(cost_flat['train_seconds'])} s. This cost is justified for model development when the goal is to select a safer operating point for rare labels, but it may not be justified for every edge deployment. The IoTID20 result is therefore practically useful: a compact weighted LightGBM can retain much of the imbalance benefit when a simpler model is preferred. Runtime and model size details are reported in Supplementary Table S8 and Supplementary Table S18.

The feature design is deliberately conservative. The CICIoT2023 public subsample analysis uses numeric traffic features and excludes labels, identifiers and metadata fields that could create leakage or dataset identity shortcuts. This choice limits representational richness compared with graph, sequence, transformer or large language model based approaches, but it makes the validation question cleaner. Future work can combine the same validation discipline with richer traffic sequence representations, provided that feature availability, device identity leakage and split design are audited with the same care.

Several limitations remain. Public benchmark datasets cannot fully capture concept drift, encrypted traffic changes or adversarial adaptation in live deployments. The CICIoT2023 public subsample uses one frozen public train test split, so the paired row bootstrap intervals should not be read as split uncertainty. The CICIoT2023 public subsample and IoTID20 also have different feature spaces, preventing a single frozen cross dataset model from being transferred directly. The study uses three public datasets rather than a broad multi dataset benchmark suite. These limits mean that the article supports a reproducible validation discipline for imbalanced IoT intrusion detection, not a claim that the proposed ensemble is the strongest possible IDS model.

\section*{{Conclusion}}

This study presents validation controlled imbalance aware learning as a reproducible framework for imbalanced IoT intrusion detection.

The scientific finding is that rare class recall can be improved when imbalance treatment, feature choice and ensemble weighting are fixed by internal validation rather than by the final test split.

The implication is broader than one dataset: imbalanced security classifiers should be judged by validation discipline, rare-label metrics and explicit boundary tests, not by headline accuracy alone.

\section*{{Data availability}}

The datasets used in this study are publicly available. No new primary data were generated. CICIoT2023 public subsample: \url{{https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample}}. Original CICIoT2023 project page: \url{{https://www.unb.ca/cic/datasets/iotdataset-2023.html}}. IoTID20 preprocessed file: \url{{https://huggingface.co/datasets/KathiS/IoTID20_Preprocessed_File}}. N-BaIoT UCI archive: \url{{https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot}}.

\section*{{Code availability}}

The reproducibility package is publicly available at GitHub: \url{{https://github.com/williamjay1/validation-controlled-iot-ids}}. The archived Zenodo release is available at \url{{https://doi.org/10.5281/zenodo.21273069}}. The archive contains executable scripts, pinned environment requirements, generated result CSV files, figure generation code, manuscript source files and checksum records for the submitted outputs.

{REFERENCES}

\section*{{Acknowledgements}}

This research was funded by the National Social Science Fund of China (General Program), grant 25BGJ089.

\section*{{Author contributions statement}}

J.Z. and S.W. conceived the study. J.Z. curated the data, implemented the experiments, analysed the results and prepared the first draft. S.W. supervised the study, contributed to methodology and reviewed and edited the manuscript. Both authors approved the final manuscript.

\section*{{Additional information}}

\textbf{{Competing interests}} The authors declare no competing interests. \textbf{{Ethics statement}} This study used publicly available network intrusion datasets and did not involve human participants, human tissue or animal subjects. \textbf{{Generative AI and tool-use disclosure}} AI-assisted coding and drafting tools were used as described in Methods; the authors remain responsible for the manuscript, code and numerical claims.

\end{{document}}
"""


def generate_supplementary_tex() -> str:
    ciciot = read_csv_rows(TABLE_SRC / "table1_ciciot_main_results.csv")
    iotid = read_csv_rows(TABLE_SRC / "table3_iotid20_replication.csv")
    iot_delta = read_csv_rows(IOTID_REPEATED_SRC / "paired_delta_bootstrap_summary.csv")
    iot_sign = read_csv_rows(IOTID_REPEATED_SRC / "paired_delta_signflip_summary.csv")
    nbaiot = read_csv_rows(TABLE_SRC / "table4_nbaiot_unseen_device_summary.csv")
    shap = read_csv_rows(TABLE_SRC / "table5_ciciot_shap_top_features.csv")[:20]
    boot = read_csv_rows(BOOTSTRAP_SRC / "ciciot_bootstrap_summary.csv")
    alpha_grid = read_csv_rows(CICIOT_ENSEMBLE_SRC / "validation_alpha_grid.csv")
    ciciot_cost = read_csv_rows(CICIOT_CONFIRMATORY_SRC / "experiment_results.csv")
    ciciot_ens_cost = read_csv_rows(CICIOT_ENSEMBLE_SRC / "experiment_results.csv")
    ciciot_rare_map_path = TABLE_SRC / "ciciot_rare_label_map.csv"
    nbaiot_map_path = TABLE_SRC / "nbaiot_device_label_map.csv"
    ciciot_rare_map = read_csv_rows(ciciot_rare_map_path) if ciciot_rare_map_path.exists() else []
    nbaiot_map = read_csv_rows(nbaiot_map_path) if nbaiot_map_path.exists() else []
    model_family = read_csv_rows_if_exists(TABLE_SRC / "table6_model_family_checks.csv")
    ciciot_hard = read_csv_rows_if_exists(TABLE_SRC / "table7_ciciot_hardest_easiest_classes.csv")
    ciciot_low = read_csv_rows_if_exists(TABLE_SRC / "table8_ciciot_low_support_class_diagnostics.csv")
    iotid_class = read_csv_rows_if_exists(TABLE_SRC / "table9_iotid20_repeated_classwise_diagnostics.csv")
    nb_sensitivity = read_csv_rows_if_exists(TABLE_SRC / "table10_nbaiot_cap_sensitivity.csv")
    runtime_complexity = read_csv_rows_if_exists(TABLE_SRC / "table11_runtime_complexity.csv")
    rare_prior = read_csv_rows_if_exists(ROOT / "results" / "ciciot_rare_prior_tuning_full" / "experiment_results.csv")
    rare_prior_source = "full CICIoT2023 public subsample split"
    if not rare_prior:
        rare_prior = read_csv_rows_if_exists(ROOT / "results" / "ciciot_rare_prior_tuning_quick" / "experiment_results.csv")
        rare_prior_source = "quick stratified screen"

    ciciot_rows = "\n".join(
        rf"{tex_escape(r['model'])} & {fmt(r['accuracy'])} & {fmt(r['balanced_accuracy'])} & {fmt(r['macro_f1'])} & {fmt(r['minority_recall'])} & {fmt(r['pr_auc_macro'])} \\"
        for r in ciciot
    )
    iotid_rows = "\n".join(
        rf"{tex_escape(r['model'])} & {r['n_splits']} & {fmt(r['mean_macro_f1'])} & {fmt(r['sd_macro_f1'])} & {fmt(r['mean_minority_recall'])} & {fmt(r['sd_minority_recall'])} & {fmt(r['mean_pr_auc_macro'])} \\"
        for r in iotid
    )
    iot_delta_rows = "\n".join(
        rf"{tex_escape(r['run_id'])} & {tex_escape(r['metric'])} & {fmt(r['mean_delta_vs_flat_lgbm'])} & {fmt(r['ci_low_2_5'])} & {fmt(r['ci_high_97_5'])} & {r['n_splits']} & {r['bootstrap_reps']} \\"
        for r in iot_delta
        if r["metric"] in {"f1_macro", "minority_recall_mean", "pr_auc_macro", "balanced_accuracy"}
    )
    iot_sign_rows = "\n".join(
        rf"{tex_escape(r['run_id'])} & {tex_escape(r['metric'])} & {fmt(r['mean_delta_vs_flat_lgbm'])} & {r['positive_splits']} & {r['negative_splits']} & {r['zero_splits']} & {fmt(r['exact_two_sided_p'])} \\"
        for r in iot_sign
        if r["metric"] in {"f1_macro", "minority_recall_mean", "pr_auc_macro"}
    )
    nb_rows = "\n".join(
        rf"{tex_escape(r['task'])} & {r['folds']} & {fmt(r['mean_macro_f1'])} & {fmt(r['min_macro_f1'])} & {fmt(r['mean_present_macro_f1'])} & {fmt(r['min_present_macro_f1'])} & {fmt(r['min_present_class_recall'])} \\"
        for r in nbaiot
    )
    shap_rows = "\n".join(
        rf"{r['rank']} & {tex_escape(r['feature'])} & {fmt(r['mean_abs_shap'])} & {fmt(r['lightgbm_gain_importance'], 1)} \\"
        for r in shap
    )
    boot_rows = "\n".join(
        rf"{tex_escape(r['quantity'])} & {fmt(r['point_estimate'])} & {fmt(r['ci_low_2_5'])} & {fmt(r['ci_high_97_5'])} & {r['n_bootstrap']} \\"
        for r in boot
    )
    alpha_rows = "\n".join(
        rf"{fmt(r['alpha_lgbm'], 2)} & {fmt(r['f1_macro'])} & {fmt(r['minority_recall_mean'])} & {fmt(r['pr_auc_macro'])} & {fmt(r['composite_score'])} \\"
        for r in alpha_grid
    )
    cost_source = [
        row_by(ciciot_cost, "run_id", "fine_lgbm_full"),
        row_by(ciciot_cost, "run_id", "fine_lgbm_borderline_smote"),
        row_by(ciciot_cost, "run_id", "fine_xgb_full_weighted"),
        row_by(ciciot_ens_cost, "objective", "macro_f1"),
    ]
    cost_labels = ["Flat LightGBM", "Borderline-SMOTE LightGBM", "Weighted XGBoost", "Validation-controlled ensemble"]
    cost_row_lines = []
    for label, row in zip(cost_labels, cost_source):
        model_size = "--" if label == "Validation-controlled ensemble" else fmt(row.get("model_size_kb") or 0, 1)
        cost_row_lines.append(
            rf"{label} & {fmt_seconds(row['train_seconds'])} & {fmt(row['inference_ms_per_1000'], 2)} & {model_size} \\"
        )
    cost_rows = "\n".join(cost_row_lines)
    ciciot_rare_map_rows = "\n".join(
        rf"{tex_escape(r['display_label'])} & {tex_escape(r['original_label'])} \\"
        for r in ciciot_rare_map
    ) or r"No short labels were generated. \\"
    nbaiot_map_rows = "\n".join(
        rf"{tex_escape(r['device_code'])} & {tex_escape(r['holdout_device'])} \\"
        for r in nbaiot_map
    ) or r"No device code map was generated. \\"
    benchmark_rows = "\n".join(
        [
            r"Alsubaei 2025 & NSL-KDD, UNSW-NB15, CICIDS2017 and related IDS benchmarks & XGBoost and optimized sequential neural network & Class imbalance considered through model and data choices & Cross validation and train test experiments; no split bootstrap or device held out test reported in the extracted manuscript & Not reported as paired uncertainty & Different datasets and task definitions; headline scores not directly comparable & Present study adds rare recall, frozen test selection, IoTID20 repeated holdouts and N-BaIoT device holdouts \\",
            r"Yu et al. 2025 & NSL-KDD and CIC-IDS2017 & Feature selection with CNN-LSTM & Equalized loss style class imbalance treatment & Repeated or fold based evaluation; no independent device holdout reported in the extracted manuscript & No paired split uncertainty table found & Strong architecture focus but less emphasis on frozen validation selection & Present study focuses on validation discipline and rare label diagnostics \\",
            r"Amine et al. 2025 & IoT intrusion detection benchmarks & Deep learning based IDS & Benchmark specific imbalance handling & Extensive benchmark figures and tables & No row bootstrap or split bootstrap reported in the extracted manuscript & Model novelty focus; validation boundary less explicit & Present study treats validation controls as the main contribution \\",
            r"Ma et al. 2025 & NF-ToN-IoT-v2, NF-UNSW-NB15-v2, NF-BoT-IoT-v2, NF-CSE-CIC-IDS2018-v2 and CIC-ToN-IoT & Feature selection, synthetic samples and LightGBM & Focal loss and synthetic minority support & Multiple datasets and train test validation & No paired uncertainty table found in the extracted manuscript & Strong multi dataset framing, but incompatible feature spaces and tasks & Present study complements this route with split and device boundary tests \\",
            r"Sarwar et al. 2025 & N-BaIoT and UNSW-NB15 & Decision tree, SVM, random forest and neural network & Feature selection and conventional classifiers & Five fold style evaluation and runtime reporting & No leave one device out N-BaIoT boundary reported in the extracted manuscript & Strong deployment context, but device transfer boundary is less direct & Present study uses complete held out devices in N-BaIoT \\",
            r"Singh et al. 2025 & Smart grid intrusion detection data & Attentional LSTM ensemble & Severe minority class treatment with large recall gains in its task & Domain specific training and evaluation & Uncertainty treatment differs from this study & Different domain and label granularity, so scores are not a direct CICIoT2023 comparison & Present study positions rare recall gains under public IoT benchmark validation \\",
            r"Abu-Shareha et al. 2026 & Supervised IDS literature & Review and multi criteria evaluation & Reviews imbalance as an evaluation dimension & Not an empirical detector & Not applicable & No new model result & Present study supplies an empirical validation controlled case \\",
        ]
    )
    model_family_rows = "\n".join(
        rf"{tex_escape(r['dataset'])} & {tex_escape(r['scope'])} & {tex_escape(r['model'])} & {fmt_maybe(r.get('n_features'), 0)} & {fmt_maybe(r.get('macro_f1'))} & {fmt_maybe(r.get('minority_recall'))} & {fmt_maybe(r.get('macro_pr_auc'))} & {fmt_maybe(r.get('train_seconds'), 1)} & {fmt_maybe(r.get('inference_ms_per_10000'), 1)} \\"
        for r in model_family
    ) or r"\multicolumn{9}{l}{No model family screen table was available when this file was generated.}\\"
    ciciot_hard_rows = "\n".join(
        rf"{tex_escape(r['diagnostic_group'])} & {tex_escape(r['class_label'])} & {fmt_maybe(r.get('support'), 0)} & {fmt_maybe(r.get('recall_flat'))} & {fmt_maybe(r.get('recall_ensemble'))} & {fmt_maybe(r.get('recall_delta'))} & {fmt_maybe(r.get('f1_flat'))} & {fmt_maybe(r.get('f1_ensemble'))} \\"
        for r in ciciot_hard
    ) or r"\multicolumn{8}{l}{No CICIoT2023 hardest class diagnostic table was available when this file was generated.}\\"
    ciciot_low_rows = "\n".join(
        rf"{tex_escape(r['class_label'])} & {fmt_maybe(r.get('support'), 0)} & {fmt_maybe(r.get('precision_flat'))} & {fmt_maybe(r.get('recall_flat'))} & {fmt_maybe(r.get('f1_flat'))} & {fmt_maybe(r.get('precision_ensemble'))} & {fmt_maybe(r.get('recall_ensemble'))} & {fmt_maybe(r.get('f1_ensemble'))} \\"
        for r in ciciot_low
    ) or r"\multicolumn{8}{l}{No CICIoT2023 low support diagnostic table was available when this file was generated.}\\"
    iotid_class_rows = "\n".join(
        rf"{tex_escape(r['class_label'])} & {tex_escape(r['model'])} & {fmt_maybe(r.get('mean_support'), 1)} & {fmt_maybe(r.get('mean_recall'))} & {fmt_maybe(r.get('sd_recall'))} & {fmt_maybe(r.get('mean_f1'))} & {fmt_maybe(r.get('delta_recall_top10_weighted_vs_flat'))} & {fmt_maybe(r.get('delta_f1_top10_weighted_vs_flat'))} \\"
        for r in iotid_class
    ) or r"\multicolumn{8}{l}{No IoTID20 class wise repeated split table was available when this file was generated.}\\"
    nb_sensitivity_rows = "\n".join(
        rf"{fmt_maybe(r.get('cap_per_file'), 0)} & {tex_escape(r['task'])} & {tex_escape(r['run_id'])} & {fmt_maybe(r.get('folds'), 0)} & {fmt_maybe(r.get('mean_macro_f1'))} & {fmt_maybe(r.get('min_macro_f1'))} & {fmt_maybe(r.get('mean_present_macro_f1'))} & {fmt_maybe(r.get('min_present_class_recall'))} & {fmt_maybe(r.get('mean_pr_auc_macro'))} \\"
        for r in nb_sensitivity
    ) or r"\multicolumn{9}{l}{No N-BaIoT cap sensitivity table was available when this file was generated.}\\"
    runtime_complexity_rows = "\n".join(
        rf"{tex_escape(r['dataset'])} & {tex_escape(r['scope'])} & {tex_escape(r['model'])} & {fmt_maybe(r.get('train_seconds'), 1)} & {fmt_maybe(r.get('inference_ms_per_10000'), 1)} & {fmt_maybe(r.get('model_size_kb'), 1)} & {fmt_maybe(r.get('peak_memory_mb'), 1)} \\"
        for r in runtime_complexity
    ) or r"\multicolumn{7}{l}{No runtime complexity table was available when this file was generated.}\\"
    rare_prior_rows = "\n".join(
        rf"{tex_escape(r['objective'])} & {fmt_maybe(r.get('alpha_lgbm'), 2)} & {tex_escape(r['rare_scope'])} & {fmt_maybe(r.get('rare_multiplier'), 2)} & {fmt_maybe(r.get('accuracy'))} & {fmt_maybe(r.get('f1_macro'))} & {fmt_maybe(r.get('minority_recall_mean'))} & {fmt_maybe(r.get('pr_auc_macro'))} & {tex_escape(r['worst_class_label'])} \\"
        for r in rare_prior
    ) or r"\multicolumn{9}{l}{No rare prior tuning result was available when this file was generated.}\\"

    return rf"""
\documentclass[10pt]{{article}}
\usepackage[margin=2cm]{{geometry}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{tabularx}}
\usepackage{{graphicx}}
\usepackage{{url}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\Urlmuskip=0mu plus 1mu
\emergencystretch=3em

\title{{Supplementary Information: Validation controlled imbalance aware learning for fine grained IoT intrusion detection}}
\author{{Junjie Zhang and Siyu Wang}}
\date{{}}

\begin{{document}}
\raggedright
\maketitle

\section*{{Supplementary Methods}}

This supplementary file records overflow tables, result sources and reproduction commands for the Scientific Reports LaTeX submission package. Complete CSV files are supplied in the \path{{supplementary_tables/}} directory.

\section*{{Supplementary Table S0. CICIoT2023 public subsample baseline variants}}

\begin{{center}}
\scriptsize
\begin{{tabular}}{{lccccc}}
\toprule
Model & Accuracy & Balanced accuracy & Macro-F1 & Minority recall & Macro PR-AUC \\
\midrule
{ciciot_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{Supplementary Table S1. IoTID20 repeated holdout summary}}

\begin{{center}}
\tiny
\begin{{tabular}}{{lcccccc}}
\toprule
Model & Splits & Mean Macro-F1 & SD Macro-F1 & Mean minority recall & SD minority recall & Mean PR-AUC \\
\midrule
{iotid_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{Supplementary Table S2. IoTID20 split-bootstrap deltas}}

\begin{{center}}
\tiny
\begin{{longtable}}{{llccccc}}
\toprule
Run ID & Metric & Mean delta & 2.5\% quantile & 97.5\% quantile & Splits & Resamples \\
\midrule
\endhead
{iot_delta_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

\section*{{Supplementary Table S3. IoTID20 exact sign-flip tests}}

\begin{{center}}
\tiny
\begin{{longtable}}{{llccccc}}
\toprule
Run ID & Metric & Mean delta & Positive splits & Negative splits & Zero splits & Exact two-sided $p$ \\
\midrule
\endhead
{iot_sign_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

\section*{{Supplementary Table S4. N-BaIoT leave-one-device-out summary}}

\begin{{center}}
\scriptsize
\begin{{tabular}}{{lcccccc}}
\toprule
Task & Folds & Mean F1 & Min F1 & Mean present F1 & Min present F1 & Min present recall \\
\midrule
{nb_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

Complete per-fold and per-class N-BaIoT outputs are supplied as \path{{supplementary_tables/nbaiot_experiment_results.csv}} and \path{{supplementary_tables/nbaiot_classwise_metrics.csv}}.

\section*{{Supplementary Figure S1. CICIoT2023 SHAP feature contributions}}

\begin{{center}}
\centering
\includegraphics[width=0.82\linewidth]{{figures/supplementary_figure_s1_ciciot_shap_top_features.png}}
\par\smallskip
\small Mean absolute SHAP values for the highest-ranked features in the CICIoT2023 Borderline-SMOTE LightGBM component. The analysis is used for component-level attribution, not causal interpretation.
\end{{center}}

\section*{{Supplementary Table S5. CICIoT2023 SHAP feature contributions}}

\begin{{center}}
\small
\begin{{tabular}}{{r l c c}}
\toprule
Rank & Feature & Mean absolute SHAP & LightGBM gain \\
\midrule
{shap_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{Supplementary Table S6. CICIoT2023 bootstrap summary}}

\begin{{center}}
\scriptsize
\begin{{longtable}}{{lcccc}}
\toprule
Quantity & Point estimate & 2.5\% quantile & 97.5\% quantile & Resamples \\
\midrule
\endhead
{boot_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

The full bootstrap sample table is supplied as \path{{supplementary_tables/ciciot_bootstrap_samples.csv}}.

\section*{{Supplementary Figure S2. CICIoT2023 alpha sensitivity}}

\begin{{center}}
\centering
\includegraphics[width=0.82\linewidth]{{figures/supplementary_figure_s2_ciciot_alpha_sensitivity.png}}
\par\smallskip
\small Validation-subsplit Macro-F1, minority recall and macro PR-AUC across candidate ensemble weights. The selected value was $\alpha=0.50$ for the Borderline-SMOTE LightGBM component.
\end{{center}}

\section*{{Supplementary Table S7. CICIoT2023 alpha grid}}

\begin{{center}}
\scriptsize
\begin{{longtable}}{{ccccc}}
\toprule
Alpha & Macro-F1 & Minority recall & Macro PR-AUC & Composite score \\
\midrule
\endhead
{alpha_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

\section*{{Supplementary Table S8. Runtime summary}}

\begin{{center}}
\small
\begin{{tabular}}{{lccc}}
\toprule
Model & Training seconds & Inference ms per 1,000 rows & Model size KB \\
\midrule
{cost_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

Runtime was measured on Windows 11 with an AMD Ryzen 9 8945HS processor and 31.3 GB RAM. Ensemble model size is not shown because it is a probability-level combination of two separately fitted components.

\section*{{Supplementary Table S9. Hyperparameters and implementation details}}

Core hyperparameters are supplied in \path{{supplementary_tables/HYPERPARAMETER_TABLE.md}}. The final CICIoT2023 public subsample ensemble used Borderline-SMOTE LightGBM and class weighted XGBoost probability outputs with validation selected alpha equal to 0.50. Borderline-SMOTE used adaptive \path{{k_neighbors}} from 1 to 5 according to the smallest class in the training split and the imbalanced learn default \path{{m_neighbors}}.

\section*{{Supplementary Table S10. Short labels for Figure 4}}

\begin{{center}}
\small
\begin{{tabular}}{{ll}}
\toprule
Display label & Original CICIoT2023 public subsample label \\
\midrule
{ciciot_rare_map_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{Supplementary Table S11. Device codes for Figure 6}}

\begin{{center}}
\small
\begin{{tabular}}{{ll}}
\toprule
Device code & Original N-BaIoT held out device name \\
\midrule
{nbaiot_map_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{Supplementary Table S12. Benchmark context against recent intrusion detection studies}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{p{{1.4cm}}p{{2.0cm}}p{{2.0cm}}p{{1.9cm}}p{{2.5cm}}p{{1.6cm}}p{{2.1cm}}p{{2.6cm}}}}
\toprule
Study & Dataset or task & Model family & Imbalance handling & Validation and boundary test & Uncertainty & Main limitation for direct comparison & Present distinction \\
\midrule
\endhead
{benchmark_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

This matrix is a benchmark context rather than a leaderboard. The studies differ in datasets, label granularity, task definitions and split protocols, so headline accuracy and detection rate are not directly comparable with the CICIoT2023 public subsample Macro-F1 reported in the main manuscript.

\section*{{Supplementary Table S13. Model family and baseline screen}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{p{{2.1cm}}p{{3.0cm}}p{{2.4cm}}cccccc}}
\toprule
Dataset & Scope & Model & Features & Macro-F1 & Minority recall & Macro PR-AUC & Train s & Inference ms per 10,000 \\
\midrule
\endhead
{model_family_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

The model family screen includes quick CICIoT2023 public subsample and IoTID20 checks, additional tree baselines and a simple MLP baseline. It is not used to replace the full frozen CICIoT2023 public subsample result in the main manuscript.

\section*{{Supplementary Table S14. CICIoT2023 public subsample hardest and easiest class diagnostics}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{p{{2.7cm}}p{{2.5cm}}cccccc}}
\toprule
Diagnostic group & Class & Support & Flat recall & Ensemble recall & Recall delta & Flat F1 & Ensemble F1 \\
\midrule
\endhead
{ciciot_hard_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

\section*{{Supplementary Table S15. CICIoT2023 public subsample low support class diagnostics}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{p{{3.0cm}}ccccccc}}
\toprule
Class & Support & Flat precision & Flat recall & Flat F1 & Ensemble precision & Ensemble recall & Ensemble F1 \\
\midrule
\endhead
{ciciot_low_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

\section*{{Supplementary Table S16. IoTID20 repeated split class wise diagnostics}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{p{{2.4cm}}p{{2.6cm}}cccccc}}
\toprule
Class & Model & Mean support & Mean recall & SD recall & Mean F1 & Recall delta & F1 delta \\
\midrule
\endhead
{iotid_class_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

\section*{{Supplementary Table S17. N-BaIoT cap sensitivity}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{ccccccccc}}
\toprule
Cap & Task & Run ID & Folds & Mean F1 & Min F1 & Mean present F1 & Min present recall & Mean PR-AUC \\
\midrule
\endhead
{nb_sensitivity_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

The 50,000 row per file sensitivity was run for the fine grained attack task because binary and family settings were already near saturated at the smaller caps.

\section*{{Supplementary Table S18. Runtime and model complexity}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{p{{2.4cm}}p{{3.0cm}}p{{2.8cm}}cccc}}
\toprule
Dataset & Scope & Model & Train s & Inference ms per 10,000 & Model size KB & Peak memory MB \\
\midrule
\endhead
{runtime_complexity_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

Peak memory was not measured in the current reproducibility run. This is retained as a transparent limitation rather than replaced with an estimate.

\section*{{Supplementary Table S19. CICIoT2023 rare prior operating point screen}}

\begin{{center}}
\tiny
\setlength{{\tabcolsep}}{{2pt}}
\begin{{longtable}}{{ccccccccc}}
\toprule
Objective & Alpha & Rare scope & Multiplier & Accuracy & Macro-F1 & Minority recall & Macro PR-AUC & Worst class \\
\midrule
\endhead
{rare_prior_rows}
\bottomrule
\end{{longtable}}
\end{{center}}

The source for this table is the {rare_prior_source}. Rare prior tuning multiplies probabilities for the lowest support label or labels selected from the training split and selects the multiplier on an internal validation split. It is reported as a recall sensitive operating point, not as a replacement for the primary Macro-F1 operating point.

\section*{{Reproduction commands}}

\begin{{verbatim}}
.\.venv\Scripts\python.exe scripts\run_ciciot_confirmatory_experiments.py `
  --out-dir ciciot_confirmatory_full
.\.venv\Scripts\python.exe scripts\run_ciciot_recall_aware_ensemble.py `
  --out-dir ciciot_ensemble_full
.\.venv\Scripts\python.exe scripts\run_ciciot_rare_prior_tuning.py `
  --out-dir ciciot_rare_prior_tuning_full
.\.venv\Scripts\python.exe scripts\run_ciciot_smoteenn_ensemble.py `
  --train-n 220000 --test-n 80000 --out-dir ciciot_ensemble_smoteenn_quick
.\.venv\Scripts\python.exe scripts\run_iotid20_repeated_split_uncertainty.py
.\.venv\Scripts\python.exe scripts\run_nbaiot_unseen_device.py `
  --n-per-file 20000 --out-dir nbaiot_unseen_device_20k `
  --run-id nb_binary_lgbm_weighted `
  --run-id nb_family_lgbm_weighted `
  --run-id nb_attack_lgbm_weighted
.\.venv\Scripts\python.exe scripts\run_ciciot_explainability.py `
  --shap-sample 3000
.\.venv\Scripts\python.exe scripts\run_ciciot_bootstrap_uncertainty.py `
  --n-bootstrap 2000 --out-dir statistical_uncertainty
.\.venv\Scripts\python.exe scripts\run_mlp_baselines.py `
  --out-dir mlp_baselines
.\.venv\Scripts\python.exe scripts\make_result_figures.py
\end{{verbatim}}

\end{{document}}
"""


def generate_cover_letter() -> str:
    return """
# Cover Letter

Date: July 9, 2026

Dear Editors,

We are pleased to submit our manuscript, "Validation controlled imbalance aware learning for fine grained IoT intrusion detection", for consideration as an Article in Scientific Reports.

The manuscript addresses a practical limitation in IoT intrusion detection: high aggregate accuracy can hide weak recall for rare but security relevant attack classes. We evaluate a validation controlled model selection framework across the CICIoT2023 public subsample, IoTID20 and N-BaIoT. On the CICIoT2023 public subsample, the validation controlled ensemble improved Macro-F1 and minority recall relative to flat LightGBM. The latest IoTID20 experiment strengthens the boundary evidence by showing that the imbalance aware recall pattern is stable across 10 stratified repeated holdouts, including a top ten flat LightGBM ablation and exact sign flip tests. N-BaIoT capped leave one device out experiments define the upper bound unseen device boundary of the claim.

We believe the study fits Scientific Reports because it provides a reproducible applied machine learning validation study using public network intrusion datasets, leakage controlled model selection, multiple baselines, uncertainty estimation, component level explainability and explicit claim boundaries. The revised manuscript follows a Scientific Reports style narrative: problem, method principle, validation evidence, generalization boundary and limitations.

The study used only publicly available network intrusion datasets and did not involve human participants, human tissue or animal subjects. The authors declare no competing interests. The reproducibility package is publicly available at GitHub and archived with Zenodo DOI https://doi.org/10.5281/zenodo.21273069.

Sincerely,

Siyu Wang

Shanghai Academy of Global Governance & Area Studies, Shanghai International Studies University

wangsiyu_real@126.com
"""


def generate_readme(template_notes: list[str]) -> str:
    notes = "\n".join(f"- {note}" for note in template_notes)
    return rf"""
# Scientific Reports LaTeX Candidate v2

Generated: 2026-07-09

This package implements the Scientific Reports LaTeX route for the IoT intrusion detection manuscript, updated with the IoTID20 repeated split bootstrap experiment and the reviewer driven transparency revisions.

## Main files

- `main.tex`: main article file using `\documentclass[fleqn,10pt]{{wlscirep}}`.
- `wlscirep.cls`: Scientific Reports/Overleaf class file or local fallback.
- `supplementary_information.tex`: supplementary information source.
- `cover_letter.md`: draft cover letter with corresponding author information.
- `figures/`: PNG files referenced in `main.tex` and TIFF files for separate upload.
- `supplementary_tables/`: CSV and markdown source tables used by the manuscript and supplementary information.
- `checksums.txt`: SHA-256 checksums for package files.

## Structural notes

- Figures and tables are inserted in the main text after first substantive citation, not collected at the end.
- Figure 5 and Supplementary Tables S1 to S3 use the latest IoTID20 repeated split bootstrap, top ten flat ablation and exact sign flip outputs.
- Supplementary Figure S2 reports the CICIoT2023 public subsample internal validation alpha sensitivity curve used to justify the frozen test ensemble weight.
- Supplementary Tables S12 to S19 add benchmark context, model family baselines, class wise diagnostics, N-BaIoT cap sensitivity, runtime complexity and rare prior operating point results.
- N-BaIoT is framed as capped sample device transfer evidence because binary and family tasks are near saturated and the 20,000 row per file cap is a limitation.
- The manuscript states that IoTID20 supports a split stable imbalance aware recall pattern, but does not claim universal ensemble dominance.
- References are embedded in `main.tex` as numbered `thebibliography` entries with DOI links rather than supplied as a separate `.bib` file.

## Template support

{notes}

## Scientific Reports initial submission checklist status

- Title page contains author names, numbered affiliations and corresponding author email.
- Abstract has no citations or subheadings.
- Main text includes editable tables and embedded figure captions.
- Data availability and code availability sections are present before references.
- Author contributions, acknowledgements, competing interests, ethics and AI tool disclosure are included.
- Supplementary information is supplied as a separate TeX file.
- Code availability is complete: the public GitHub repository and Zenodo DOI are inserted in `main.tex`.
"""


def copy_inputs() -> None:
    fig_dir = OUT_DIR / "figures"
    table_dir = OUT_DIR / "supplementary_tables"
    fig_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    for name in MAIN_FIGURES:
        src = FIG_SRC / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, fig_dir / name)

    for table in sorted(TABLE_SRC.glob("*.csv")):
        shutil.copy2(table, table_dir / table.name)
    for table in sorted(BOOTSTRAP_SRC.glob("ciciot_bootstrap_*.csv")):
        shutil.copy2(table, table_dir / table.name)
    for table in sorted(IOTID_REPEATED_SRC.glob("*.csv")):
        shutil.copy2(table, table_dir / f"iotid20_repeated_{table.name}")

    extra_sources = [
        ROOT / "results" / "nbaiot_unseen_device_20k" / "experiment_results.csv",
        ROOT / "results" / "nbaiot_unseen_device_20k" / "classwise_metrics.csv",
        ROOT / "results" / "nbaiot_unseen_device_50k_attack" / "experiment_results.csv",
        ROOT / "results" / "nbaiot_unseen_device_50k_attack" / "classwise_metrics.csv",
        ROOT / "results" / "ciciot_smoteenn_quick" / "experiment_results.csv",
        ROOT / "results" / "ciciot_ensemble_smoteenn_quick" / "experiment_results.csv",
        ROOT / "results" / "ciciot_rare_prior_tuning_quick" / "experiment_results.csv",
        ROOT / "results" / "ciciot_rare_prior_tuning_full" / "experiment_results.csv",
        ROOT / "results" / "ciciot_rare_prior_tuning_full" / "validation_rare_prior_grid.csv",
        ROOT / "docs" / "IOTID20_REPEATED_SPLIT_RESULT_NOTE.md",
        ROOT / "docs" / "HYPERPARAMETER_TABLE.md",
        ROOT / "docs" / "SCIENTIFIC_REPORTS_BENCHMARK_MATRIX.md",
        ROOT / "docs" / "CLAIM_STRENGTH_AUDIT.md",
        ROOT / "docs" / "RESULT_LEDGER.md",
        ROOT / "docs" / "ARTICLE_BUILD_SPEC.md",
    ]
    for src in extra_sources:
        if src.exists():
            target_name = src.name
            if src.name == "experiment_results.csv":
                if src.parent.name == "nbaiot_unseen_device_20k":
                    target_name = "nbaiot_experiment_results.csv"
                else:
                    target_name = f"{src.parent.name}_experiment_results.csv"
            elif src.name == "classwise_metrics.csv":
                if src.parent.name == "nbaiot_unseen_device_20k":
                    target_name = "nbaiot_classwise_metrics.csv"
                else:
                    target_name = f"{src.parent.name}_classwise_metrics.csv"
            shutil.copy2(src, table_dir / target_name)


def write_checksums() -> None:
    rows = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_file() and path.name != "checksums.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(f"{digest}  {path.relative_to(OUT_DIR).as_posix()}")
    write_text(OUT_DIR / "checksums.txt", "\n".join(rows))


def scientific_reports_section_order(main_tex: str) -> str:
    """Place Methods after Discussion to follow the usual Scientific Reports flow."""
    methods_marker = r"\section*{Methods}"
    results_marker = r"\section*{Results}"
    conclusion_marker = r"\section*{Conclusion}"
    try:
        methods_start = main_tex.index(methods_marker)
        results_start = main_tex.index(results_marker)
        conclusion_start = main_tex.index(conclusion_marker)
    except ValueError:
        return main_tex
    if not (methods_start < results_start < conclusion_start):
        return main_tex

    before_methods = main_tex[:methods_start]
    methods_block = main_tex[methods_start:results_start]
    results_and_discussion = main_tex[results_start:conclusion_start]
    after_discussion = main_tex[conclusion_start:]
    return before_methods + results_and_discussion + methods_block + after_discussion


def main() -> None:
    resolved_out = OUT_DIR.resolve()
    package_root = (ROOT / "submission_package").resolve()
    if package_root not in resolved_out.parents:
        raise RuntimeError(f"Refusing to write outside submission_package: {resolved_out}")
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    copy_inputs()
    template_notes = copy_template_files()
    write_text(OUT_DIR / "main.tex", scientific_reports_section_order(generate_main_tex()))
    write_text(OUT_DIR / "supplementary_information.tex", generate_supplementary_tex())
    write_text(OUT_DIR / "cover_letter.md", generate_cover_letter())
    write_text(OUT_DIR / "README_SUBMISSION.md", generate_readme(template_notes))
    write_checksums()
    print(f"Wrote {OUT_DIR}")


if __name__ == "__main__":
    main()

