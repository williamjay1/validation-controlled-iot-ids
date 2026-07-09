from __future__ import annotations

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG_DIR = ROOT / "figures" / "paper_figures"
TABLE_DIR = RESULTS / "paper_tables"
IOTID_REPEATED = RESULTS / "iotid20_repeated_split"


def ensure_dirs() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def savefig(name: str, fig: plt.Figure | None = None) -> None:
    fig = fig or plt.gcf()
    fig.savefig(FIG_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG_DIR / f"{name}.tiff", dpi=300, bbox_inches="tight")
    plt.close(fig)


def read_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def model_label(run_id: str) -> str:
    labels = {
        "fine_lgbm_full": "Flat LightGBM",
        "fine_lgbm_full_weighted": "Weighted LightGBM",
        "fine_lgbm_random_over": "Random oversampling LightGBM",
        "fine_lgbm_smote": "SMOTE LightGBM",
        "fine_lgbm_smoteenn": "SMOTEENN LightGBM",
        "fine_lgbm_borderline_smote": "Borderline-SMOTE LightGBM",
        "fine_rf_full_weighted": "Weighted Random Forest",
        "fine_extratrees_full_weighted": "Weighted ExtraTrees",
        "fine_xgb_full_weighted": "Weighted XGBoost",
        "fine_catboost_full_weighted": "Weighted CatBoost",
        "fine_hier_lgbm_top20_weighted": "Hierarchical LightGBM",
        "ciciot_fine_mlp_quick": "Flat MLP",
        "iotid_fine_lgbm_full": "Flat LightGBM",
        "iotid_fine_lgbm_weighted": "Weighted LightGBM",
        "iotid_fine_lgbm_mi_top10_weighted": "Top ten weighted LightGBM",
        "iotid_fine_lgbm_importance_top10_weighted": "Top ten importance LightGBM",
        "iotid_fine_rf_weighted": "Weighted Random Forest",
        "iotid_fine_xgb_weighted": "Weighted XGBoost",
        "iotid_fine_catboost_weighted": "Weighted CatBoost",
        "iotid_fine_mlp_quick": "Flat MLP",
        "iotid_fine_lgbm_mi_top10_flat": "Top ten flat LightGBM",
        "iotid_fine_lgbm_xgb_validation_ensemble": "Validation controlled ensemble",
        "fine_lgbm_xgb_smoteenn_ensemble_macro_f1": "Three component ensemble screen",
        "fine_lgbm_xgb_smoteenn_ensemble_macro_f1_plus_minority": "Three component ensemble screen",
        "fine_lgbm_xgb_smoteenn_ensemble_recall_sensitive": "Three component ensemble screen",
        "fine_lgbm_xgb_rare_prior_macro_f1": "Rare prior ensemble, Macro F1",
        "fine_lgbm_xgb_rare_prior_macro_f1_plus_minority": "Rare prior ensemble, balanced recall",
        "fine_lgbm_xgb_rare_prior_recall_sensitive": "Rare prior ensemble, recall sensitive",
        "fine_lgbm_xgb_rare_prior_minority_recall_constrained": "Rare prior ensemble, constrained recall",
    }
    return labels.get(run_id, run_id)


def add_present_class_metrics(result_dir: Path, df: pd.DataFrame) -> pd.DataFrame:
    classwise_path = result_dir / "classwise_metrics.csv"
    if df.empty or not classwise_path.exists() or "f1_macro_present_support" in df.columns:
        return df
    classwise = pd.read_csv(classwise_path)
    classwise["base_run_id"] = classwise["run_id"].str.split("__").str[0]
    present = classwise[classwise["support"] > 0]
    present_summary = (
        present.groupby(["base_run_id", "holdout_device"])
        .agg(
            present_class_count=("class_label", "nunique"),
            f1_macro_present_support=("f1", "mean"),
            mean_present_class_recall=("recall", "mean"),
            min_present_class_recall=("recall", "min"),
        )
        .reset_index()
        .rename(columns={"base_run_id": "run_id"})
    )
    return df.merge(present_summary, on=["run_id", "holdout_device"], how="left")


def box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, color: str) -> None:
    rect = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.035,rounding_size=0.04",
        linewidth=1.0,
        edgecolor="#3F4852",
        facecolor=color,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9.2)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.25, "color": "#3F4852"})


def figure_validation_design() -> None:
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.set_axis_off()
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.8)

    datasets = [
        ("CICIoT2023", "Primary benchmark", "Frozen public test split", 0.75, "#DDEAF7"),
        ("IoTID20", "Split stability", "10 repeated 70/30 holdouts", 4.45, "#E4F2E5"),
        ("N-BaIoT", "Device boundary", "Leave-one-device-out", 8.15, "#F6E7D8"),
    ]
    for title, role, validation, x, color in datasets:
        box(ax, x, 3.45, 3.1, 0.72, title, color)
        box(ax, x, 2.35, 3.1, 0.72, validation, "#F7F7F5")
        box(ax, x, 1.25, 3.1, 0.72, role, "#FFFFFF")
        arrow(ax, (x + 1.55, 3.45), (x + 1.55, 3.07))
        arrow(ax, (x + 1.55, 2.35), (x + 1.55, 1.97))

    ax.text(0.25, 3.80, "Dataset", fontsize=9.5, fontweight="bold", ha="right", va="center")
    ax.text(0.25, 2.70, "Validation", fontsize=9.5, fontweight="bold", ha="right", va="center")
    ax.text(0.25, 1.60, "Use in claim", fontsize=9.5, fontweight="bold", ha="right", va="center")
    box(
        ax,
        1.7,
        0.28,
        8.6,
        0.52,
        "Metrics reported with leakage-controlled preprocessing and uncertainty estimates",
        "#F7F7F5",
    )

    fig.tight_layout()
    savefig("figure1_validation_design", fig)


def figure_validation_controlled_ensemble() -> None:
    fig, ax = plt.subplots(figsize=(11.4, 4.7))
    ax.set_axis_off()
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 4.7)

    ax.add_patch(patches.Rectangle((0.15, 0.35), 4.85, 3.95, facecolor="#EAF2FB", edgecolor="#8AAED1", lw=1.1))
    ax.add_patch(patches.Rectangle((5.25, 0.35), 2.45, 3.95, facecolor="#EAF6EA", edgecolor="#8BBE8A", lw=1.1))
    ax.add_patch(patches.Rectangle((8.0, 0.35), 3.15, 3.95, facecolor="#F2F2F2", edgecolor="#9A9A9A", lw=1.1))
    ax.text(2.58, 4.12, "Training only", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#355C84")
    ax.text(6.48, 4.12, "Internal validation", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#3F7B42")
    ax.text(9.58, 4.12, "Frozen test", ha="center", va="center", fontsize=10.5, fontweight="bold", color="#555555")

    box(ax, 0.55, 2.05, 1.6, 0.72, "Training\nsub-split", "#FFFFFF")
    box(ax, 2.7, 3.0, 2.0, 0.76, "Borderline-SMOTE\nLightGBM", "#DDEAF7")
    box(ax, 2.7, 1.05, 2.0, 0.76, "Class-weighted\nXGBoost", "#F6E7D8")
    box(ax, 5.55, 2.35, 1.85, 0.78, "Grid search\nalpha", "#FFFFFF")
    box(ax, 8.38, 2.35, 2.35, 0.78, "Evaluate once\non test split", "#FFFFFF")

    arrow(ax, (2.15, 2.40), (2.70, 3.38))
    arrow(ax, (2.15, 2.40), (2.70, 1.43))
    arrow(ax, (4.70, 3.38), (5.55, 2.85))
    arrow(ax, (4.70, 1.43), (5.55, 2.60))
    arrow(ax, (7.40, 2.74), (8.38, 2.74))

    ax.plot([7.82, 7.82], [0.48, 4.15], color="#555555", linestyle="--", lw=1.1)
    ax.text(7.82, 4.42, "test information blocked", ha="center", va="center", fontsize=9.2, color="#555555")
    ax.text(6.48, 1.45, r"$\hat{p}_{i,c}^{ens}=\alpha\hat{p}^{LGBM}_{i,c}+(1-\alpha)\hat{p}^{XGB}_{i,c}$", ha="center", fontsize=10.8)
    ax.text(9.55, 1.45, "Macro-F1, minority recall,\nPR-AUC and uncertainty", ha="center", fontsize=8.8, color="#3F4852")

    fig.tight_layout()
    savefig("figure2_validation_controlled_ensemble", fig)


def figure_ciciot_alpha_sensitivity() -> None:
    grid = pd.read_csv(RESULTS / "ciciot_ensemble_full" / "validation_alpha_grid.csv")
    plot = grid.melt(
        id_vars=["alpha_lgbm"],
        value_vars=["f1_macro", "minority_recall_mean", "pr_auc_macro"],
        var_name="metric",
        value_name="score",
    )
    plot["metric"] = plot["metric"].map(
        {"f1_macro": "Macro-F1", "minority_recall_mean": "Minority recall", "pr_auc_macro": "Macro PR-AUC"}
    )
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    sns.lineplot(
        data=plot,
        x="alpha_lgbm",
        y="score",
        hue="metric",
        marker="o",
        palette=["#4E79A7", "#59A14F", "#E15759"],
        ax=ax,
    )
    ax.axvline(0.50, color="#555555", linestyle="--", lw=1.1)
    ax.text(0.515, 0.935, "selected alpha = 0.50", fontsize=9, color="#555555", va="center")
    ax.set_xlabel("Alpha assigned to Borderline-SMOTE LightGBM")
    ax.set_ylabel("Validation score")
    ax.set_ylim(0.25, 0.96)
    ax.legend(title="", loc="lower left", frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    savefig("supplementary_figure_s2_ciciot_alpha_sensitivity", fig)


def ciciot_core_table() -> pd.DataFrame:
    base = pd.read_csv(RESULTS / "ciciot_confirmatory_full" / "experiment_results.csv")
    ens = pd.read_csv(RESULTS / "ciciot_ensemble_full" / "experiment_results.csv")
    ens = ens[ens["objective"] == "macro_f1"].copy()
    rows = []
    label_map = {
        "fine_lgbm_full": "Flat LightGBM",
        "fine_lgbm_borderline_smote": "Borderline-SMOTE LightGBM",
        "fine_lgbm_smote": "SMOTE LightGBM",
        "fine_lgbm_random_over": "Random oversampling LightGBM",
        "fine_xgb_full_weighted": "Weighted XGBoost",
        "fine_lgbm_xgb_ensemble_macro_f1": "Validation-controlled ensemble",
    }
    for df in (base, ens):
        for _, row in df.iterrows():
            run_id = row["run_id"]
            if run_id in label_map:
                rows.append(
                    {
                        "model": label_map[run_id],
                        "run_id": run_id,
                        "accuracy": row["accuracy"],
                        "balanced_accuracy": row["balanced_accuracy"],
                        "macro_f1": row["f1_macro"],
                        "weighted_f1": row["f1_weighted"],
                        "minority_recall": row["minority_recall_mean"],
                        "worst_class_recall": row["worst_class_recall"],
                        "pr_auc_macro": row["pr_auc_macro"],
                        "inference_ms_per_1000": row["inference_ms_per_1000"],
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "table1_ciciot_main_results.csv", index=False)
    return out


def ciciot_rare_table() -> pd.DataFrame:
    base = pd.read_csv(RESULTS / "ciciot_confirmatory_full" / "classwise_metrics.csv")
    ens = pd.read_csv(RESULTS / "ciciot_ensemble_full" / "classwise_metrics.csv")
    ens = ens[ens["run_id"] == "fine_lgbm_xgb_ensemble_macro_f1"]
    df = pd.concat([base, ens], ignore_index=True)
    rare = ["Uploading_Attack", "Recon-PingSweep", "Backdoor_Malware", "XSS"]
    label_map = {
        "fine_lgbm_full": "Flat LightGBM",
        "fine_lgbm_borderline_smote": "Borderline-SMOTE",
        "fine_xgb_full_weighted": "Weighted XGBoost",
        "fine_lgbm_xgb_ensemble_macro_f1": "Ensemble",
    }
    df = df[df["class_label"].isin(rare) & df["run_id"].isin(label_map)].copy()
    df["model"] = df["run_id"].map(label_map)
    rare_map = {
        "Uploading_Attack": "Uploading",
        "Recon-PingSweep": "Ping sweep",
        "Backdoor_Malware": "Backdoor",
        "XSS": "XSS",
    }
    df["display_label"] = df["class_label"].map(rare_map)
    pd.DataFrame(
        [{"display_label": v, "original_label": k} for k, v in rare_map.items()]
    ).to_csv(TABLE_DIR / "ciciot_rare_label_map.csv", index=False)
    df.to_csv(TABLE_DIR / "table2_ciciot_rare_class_recall.csv", index=False)
    return df


def figure_ciciot_main_metrics(table: pd.DataFrame) -> None:
    key_models = [
        "Flat LightGBM",
        "Borderline-SMOTE LightGBM",
        "Weighted XGBoost",
        "Validation-controlled ensemble",
    ]
    plot = table[table["model"].isin(key_models)].melt(
        id_vars=["model"],
        value_vars=["macro_f1", "minority_recall", "pr_auc_macro"],
        var_name="metric",
        value_name="value",
    )
    plot["metric"] = plot["metric"].map(
        {"macro_f1": "Macro-F1", "minority_recall": "Minority recall", "pr_auc_macro": "Macro PR-AUC"}
    )

    fig, ax = plt.subplots(figsize=(10.5, 4.1))
    sns.barplot(
        data=plot,
        x="model",
        y="value",
        hue="metric",
        order=key_models,
        palette=["#4E79A7", "#59A14F", "#E15759"],
        ax=ax,
    )
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("")
    ax.set_ylabel("Score")
    ax.tick_params(axis="x", rotation=10)
    ax.legend(title="", loc="upper center", bbox_to_anchor=(0.5, 1.22), ncol=3, frameon=False)
    fig.subplots_adjust(top=0.82, bottom=0.22)
    savefig("figure3_ciciot_main_metrics", fig)


def figure_ciciot_rare_class_recall(rare: pd.DataFrame) -> None:
    rare_order = ["Uploading_Attack", "Recon-PingSweep", "Backdoor_Malware", "XSS"]
    display_order = ["Uploading", "Ping sweep", "Backdoor", "XSS"]
    if "display_label" not in rare.columns:
        rare = rare.copy()
        rare["display_label"] = rare["class_label"].map(
            {
                "Uploading_Attack": "Uploading",
                "Recon-PingSweep": "Ping sweep",
                "Backdoor_Malware": "Backdoor",
                "XSS": "XSS",
            }
        )
    rare_model_order = ["Flat LightGBM", "Borderline-SMOTE", "Weighted XGBoost", "Ensemble"]

    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    sns.barplot(
        data=rare,
        x="display_label",
        y="recall",
        hue="model",
        order=display_order,
        hue_order=rare_model_order,
        palette=["#4E79A7", "#76B7B2", "#F28E2B", "#E15759"],
        ax=ax,
    )
    ax.set_ylim(0, 0.9)
    ax.set_xlabel("Rare attack label")
    ax.set_ylabel("Recall")
    ax.legend(title="", loc="upper center", bbox_to_anchor=(0.5, 1.21), ncol=4, frameon=False)
    fig.subplots_adjust(top=0.82, bottom=0.17)
    savefig("figure4_ciciot_rare_attack_recall", fig)


def iotid_repeated_table() -> pd.DataFrame:
    summary = pd.read_csv(IOTID_REPEATED / "model_summary.csv")
    label_map = {
        "iotid_fine_lgbm_full": "Flat LightGBM",
        "iotid_fine_lgbm_mi_top10_flat": "Top ten flat LightGBM",
        "iotid_fine_lgbm_mi_top10_weighted": "Top ten weighted LightGBM",
        "iotid_fine_lgbm_weighted": "Weighted LightGBM",
        "iotid_fine_xgb_weighted": "Weighted XGBoost",
        "iotid_fine_lgbm_xgb_validation_ensemble": "Validation-controlled ensemble",
    }
    summary["model"] = summary["run_id"].map(label_map)
    summary = summary[summary["model"].notna()].copy()
    summary = summary[
        [
            "model",
            "run_id",
            "n_splits",
            "mean_macro_f1",
            "sd_macro_f1",
            "mean_balanced_accuracy",
            "mean_minority_recall",
            "sd_minority_recall",
            "mean_pr_auc_macro",
            "mean_train_seconds",
            "mean_inference_ms_per_1000",
        ]
    ]
    summary.to_csv(TABLE_DIR / "table3_iotid20_replication.csv", index=False)
    return summary


def figure_iotid_repeated() -> None:
    delta = pd.read_csv(IOTID_REPEATED / "paired_delta_bootstrap_summary.csv")
    keep = [
        ("iotid_fine_lgbm_mi_top10_flat", "Top ten flat\nLightGBM"),
        ("iotid_fine_lgbm_mi_top10_weighted", "Top ten weighted\nLightGBM"),
        ("iotid_fine_lgbm_xgb_validation_ensemble", "Validation controlled\nensemble"),
        ("iotid_fine_xgb_weighted", "Weighted\nXGBoost"),
    ]
    metrics = [("f1_macro", "Macro-F1 delta vs flat LightGBM"), ("minority_recall_mean", "Minority recall delta vs flat LightGBM")]

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.5), sharey=True)
    colors = ["#4E79A7", "#59A14F", "#E15759", "#F28E2B"]
    y_positions = list(range(len(keep)))[::-1]
    for ax, (metric, xlabel) in zip(axes, metrics):
        rows = []
        for run_id, label in keep:
            row = delta[(delta["run_id"] == run_id) & (delta["metric"] == metric)].iloc[0]
            rows.append((label, row))
        for y, color, (label, row) in zip(y_positions, colors, rows):
            x = row["mean_delta_vs_flat_lgbm"]
            low = row["ci_low_2_5"]
            high = row["ci_high_97_5"]
            ax.errorbar(
                x,
                y,
                xerr=[[x - low], [high - x]],
                fmt="o",
                color=color,
                ecolor=color,
                capsize=4,
                markersize=6,
                lw=1.5,
            )
            if metric == "minority_recall_mean":
                ax.text(
                    high + 0.006,
                    y,
                    f"{x:+.3f}",
                    va="center",
                    fontsize=8.2,
                    color=color,
                )
        ax.axvline(0, color="#555555", lw=1.0, linestyle="--")
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", alpha=0.3)
        ax.set_ylim(-0.6, len(keep) - 0.4)
    axes[0].set_yticks(y_positions)
    axes[0].set_yticklabels([label for _, label in keep])
    axes[0].text(-0.16, 1.04, "a", transform=axes[0].transAxes, fontsize=12, fontweight="bold")
    axes[1].text(-0.08, 1.04, "b", transform=axes[1].transAxes, fontsize=12, fontweight="bold")
    fig.subplots_adjust(left=0.28, right=0.98, bottom=0.20, top=0.92, wspace=0.28)
    savefig("figure5_iotid20_repeated_split", fig)


def nbaiot_summary() -> pd.DataFrame:
    result_dir = RESULTS / "nbaiot_unseen_device_20k"
    if not (result_dir / "experiment_results.csv").exists():
        result_dir = RESULTS / "nbaiot_unseen_device"
    df = pd.read_csv(result_dir / "experiment_results.csv")
    df["source_result_dir"] = result_dir.name
    classwise_path = result_dir / "classwise_metrics.csv"
    if classwise_path.exists() and "f1_macro_present_support" not in df.columns:
        classwise = pd.read_csv(classwise_path)
        classwise["base_run_id"] = classwise["run_id"].str.split("__").str[0]
        present = classwise[classwise["support"] > 0]
        present_summary = (
            present.groupby(["base_run_id", "holdout_device"])
            .agg(
                present_class_count=("class_label", "nunique"),
                f1_macro_present_support=("f1", "mean"),
                mean_present_class_recall=("recall", "mean"),
                min_present_class_recall=("recall", "min"),
            )
            .reset_index()
            .rename(columns={"base_run_id": "run_id"})
        )
        df = df.merge(present_summary, on=["run_id", "holdout_device"], how="left")
    summary = (
        df.groupby(["source_result_dir", "run_id", "task", "model_name", "feature_strategy", "top_k"], dropna=False)
        .agg(
            folds=("holdout_device", "nunique"),
            mean_macro_f1=("f1_macro", "mean"),
            std_macro_f1=("f1_macro", "std"),
            min_macro_f1=("f1_macro", "min"),
            mean_present_macro_f1=("f1_macro_present_support", "mean"),
            min_present_macro_f1=("f1_macro_present_support", "min"),
            mean_present_classes=("present_class_count", "mean"),
            mean_balanced_accuracy=("balanced_accuracy", "mean"),
            mean_minority_recall=("minority_recall_mean", "mean"),
            mean_worst_class_recall=("worst_class_recall", "mean"),
            min_present_class_recall=("min_present_class_recall", "min"),
            mean_pr_auc_macro=("pr_auc_macro", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(TABLE_DIR / "table4_nbaiot_unseen_device_summary.csv", index=False)
    return df


def figure_nbaiot(df: pd.DataFrame) -> None:
    keep = [
        "nb_attack_lgbm_weighted",
        "nb_attack_lgbm_mi_top40_weighted",
        "nb_family_lgbm_weighted",
        "nb_binary_lgbm_weighted",
    ]
    label_map = {
        "nb_attack_lgbm_weighted": "Fine-grained attack",
        "nb_attack_lgbm_mi_top40_weighted": "Attack labels top-40",
        "nb_family_lgbm_weighted": "Attack family",
        "nb_binary_lgbm_weighted": "Binary",
    }
    plot = df[df["run_id"].isin(keep)].copy()
    plot["setting"] = plot["run_id"].map(label_map)
    device_order = sorted(plot["holdout_device"].dropna().unique())
    device_map = {device: f"D{i + 1}" for i, device in enumerate(device_order)}
    plot["device_code"] = plot["holdout_device"].map(device_map)
    pd.DataFrame(
        [{"device_code": code, "holdout_device": device} for device, code in device_map.items()]
    ).to_csv(TABLE_DIR / "nbaiot_device_label_map.csv", index=False)
    metric = "f1_macro_present_support" if "f1_macro_present_support" in plot.columns else "f1_macro"
    fig, axes = plt.subplots(2, 1, figsize=(11, 8.1), sharex=True)
    setting_order = ["Fine-grained attack", "Attack labels top-40", "Attack family", "Binary"]
    colors = {
        "Fine-grained attack": "#4E79A7",
        "Attack labels top-40": "#59A14F",
        "Attack family": "#F28E2B",
        "Binary": "#E15759",
    }
    offsets = {
        "Fine-grained attack": -0.24,
        "Attack labels top-40": -0.08,
        "Attack family": 0.08,
        "Binary": 0.24,
    }
    x_positions = {code: i for i, code in enumerate([device_map[d] for d in device_order])}
    for setting in setting_order:
        part = plot[plot["setting"] == setting]
        xs = [x_positions[code] + offsets[setting] for code in part["device_code"]]
        axes[0].scatter(xs, part[metric], label=setting, color=colors[setting], s=38, zorder=3)
    axes[0].set_ylim(0.94, 1.01)
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Present-class Macro-F1")
    axes[0].legend(title="", loc="upper center", bbox_to_anchor=(0.5, 1.26), ncol=2, frameon=False)
    axes[0].text(-0.08, 1.05, "a", transform=axes[0].transAxes, fontsize=12, fontweight="bold")
    for setting in setting_order:
        part = plot[plot["setting"] == setting]
        xs = [x_positions[code] + offsets[setting] for code in part["device_code"]]
        axes[1].scatter(xs, part["worst_class_recall"], color=colors[setting], s=38, zorder=3)
    axes[1].set_ylim(0.65, 1.02)
    axes[1].set_xlabel("Held out device")
    axes[1].set_ylabel("Worst present-class recall")
    axes[1].set_xticks(list(x_positions.values()))
    axes[1].set_xticklabels(list(x_positions.keys()))
    for ax in axes:
        ax.grid(axis="y", alpha=0.3)
    axes[1].text(-0.08, 1.04, "b", transform=axes[1].transAxes, fontsize=12, fontweight="bold")
    fig.subplots_adjust(top=0.86, bottom=0.16, hspace=0.20)
    savefig("figure6_nbaiot_unseen_device", fig)


def figure_shap_top_features() -> None:
    table = TABLE_DIR / "table5_ciciot_shap_top_features.csv"
    if not table.exists():
        return
    df = pd.read_csv(table).head(18).copy()
    fig, ax = plt.subplots(figsize=(8.2, 6.4))
    sns.barplot(data=df, y="feature", x="mean_abs_shap", color="#4E79A7", ax=ax)
    ax.set_xlabel("Mean absolute SHAP value")
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=8.5)
    fig.tight_layout()
    savefig("supplementary_figure_s1_ciciot_shap_top_features", fig)


def supplementary_model_family_checks() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    ciciot_quick = read_if_exists(RESULTS / "ciciot_quick" / "experiment_results.csv")
    if not ciciot_quick.empty:
        keep = {
            "fine_lgbm_full",
            "fine_lgbm_borderline_smote",
            "fine_lgbm_smoteenn",
            "fine_rf_full_weighted",
            "fine_extratrees_full_weighted",
            "fine_xgb_full_weighted",
            "fine_catboost_full_weighted",
            "fine_hier_lgbm_top20_weighted",
        }
        for _, row in ciciot_quick[(ciciot_quick["task"] == "fine") & (ciciot_quick["run_id"].isin(keep))].iterrows():
            rows.append(
                {
                    "dataset": "CICIoT2023 public subsample",
                    "scope": "stratified quick model family screen, 220000 train and 80000 test rows",
                    "model": model_label(row["run_id"]),
                    "run_id": row["run_id"],
                    "n_features": row["n_features"],
                    "macro_f1": row["f1_macro"],
                    "minority_recall": row["minority_recall_mean"],
                    "macro_pr_auc": row.get("pr_auc_macro"),
                    "train_seconds": row.get("train_seconds"),
                    "inference_ms_per_10000": row.get("inference_ms_per_1000") * 10,
                    "model_size_kb": row.get("model_size_kb"),
                }
            )

    extra_ciciot_screens = [
        (
            RESULTS / "ciciot_smoteenn_quick" / "experiment_results.csv",
            "stratified quick SMOTEENN screen, 220000 train and 80000 test rows",
        ),
        (
            RESULTS / "ciciot_ensemble_smoteenn_quick" / "experiment_results.csv",
            "stratified quick three component ensemble screen, 220000 train and 80000 test rows",
        ),
    ]
    for path, scope in extra_ciciot_screens:
        extra = read_if_exists(path)
        if extra.empty:
            continue
        for _, row in extra.iterrows():
            rows.append(
                {
                    "dataset": "CICIoT2023 public subsample",
                    "scope": scope,
                    "model": model_label(row["run_id"]),
                    "run_id": row["run_id"],
                    "n_features": row["n_features"],
                    "macro_f1": row["f1_macro"],
                    "minority_recall": row["minority_recall_mean"],
                    "macro_pr_auc": row.get("pr_auc_macro"),
                    "train_seconds": row.get("train_seconds"),
                    "inference_ms_per_10000": row.get("inference_ms_per_1000") * 10,
                    "model_size_kb": row.get("model_size_kb"),
                }
            )

    iotid_quick = read_if_exists(RESULTS / "iotid20_quick" / "experiment_results.csv")
    if not iotid_quick.empty:
        keep = {
            "iotid_fine_lgbm_full",
            "iotid_fine_lgbm_weighted",
            "iotid_fine_lgbm_mi_top10_weighted",
            "iotid_fine_rf_weighted",
            "iotid_fine_xgb_weighted",
            "iotid_fine_catboost_weighted",
        }
        for _, row in iotid_quick[(iotid_quick["task"] == "fine") & (iotid_quick["run_id"].isin(keep))].iterrows():
            rows.append(
                {
                    "dataset": "IoTID20 public mirror",
                    "scope": "stratified 70/30 quick model family screen",
                    "model": model_label(row["run_id"]),
                    "run_id": row["run_id"],
                    "n_features": row["n_features"],
                    "macro_f1": row["f1_macro"],
                    "minority_recall": row["minority_recall_mean"],
                    "macro_pr_auc": row.get("pr_auc_macro"),
                    "train_seconds": row.get("train_seconds"),
                    "inference_ms_per_10000": row.get("inference_ms_per_1000") * 10,
                    "model_size_kb": row.get("model_size_kb"),
                }
            )

    mlp = read_if_exists(RESULTS / "mlp_baselines" / "experiment_results.csv")
    if not mlp.empty:
        for _, row in mlp.iterrows():
            rows.append(
                {
                    "dataset": row["dataset"],
                    "scope": row["scope"],
                    "model": model_label(row["run_id"]),
                    "run_id": row["run_id"],
                    "n_features": row["n_features"],
                    "macro_f1": row["f1_macro"],
                    "minority_recall": row["minority_recall_mean"],
                    "macro_pr_auc": row.get("pr_auc_macro"),
                    "train_seconds": row.get("train_seconds"),
                    "inference_ms_per_10000": row.get("inference_ms_per_1000") * 10,
                    "model_size_kb": row.get("model_size_kb"),
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["dataset", "macro_f1"], ascending=[True, False])
    out.to_csv(TABLE_DIR / "table6_model_family_checks.csv", index=False)
    return out


def supplementary_classwise_diagnostics() -> None:
    base = read_if_exists(RESULTS / "ciciot_confirmatory_full" / "classwise_metrics.csv")
    ens = read_if_exists(RESULTS / "ciciot_ensemble_full" / "classwise_metrics.csv")
    if not base.empty and not ens.empty:
        flat = base[base["run_id"] == "fine_lgbm_full"].copy()
        ensemble = ens[ens["run_id"] == "fine_lgbm_xgb_ensemble_macro_f1"].copy()
        merged = flat.merge(ensemble, on=["class_id", "class_label"], suffixes=("_flat", "_ensemble"))
        merged["recall_delta"] = merged["recall_ensemble"] - merged["recall_flat"]
        merged["f1_delta"] = merged["f1_ensemble"] - merged["f1_flat"]
        merged["precision_delta"] = merged["precision_ensemble"] - merged["precision_flat"]
        merged = merged[
            [
                "class_label",
                "support_flat",
                "precision_flat",
                "recall_flat",
                "f1_flat",
                "precision_ensemble",
                "recall_ensemble",
                "f1_ensemble",
                "precision_delta",
                "recall_delta",
                "f1_delta",
            ]
        ].rename(columns={"support_flat": "support"})
        hardest = merged.sort_values(["recall_ensemble", "f1_ensemble", "support"]).head(12).copy()
        hardest["diagnostic_group"] = "hardest by ensemble recall"
        easiest = merged[merged["class_label"] != "BenignTraffic"].sort_values(
            ["recall_ensemble", "f1_ensemble"], ascending=False
        ).head(12).copy()
        easiest["diagnostic_group"] = "easiest non benign by ensemble recall"
        full_diag = pd.concat([hardest, easiest], ignore_index=True)
        full_diag.to_csv(TABLE_DIR / "table7_ciciot_hardest_easiest_classes.csv", index=False)
        merged.sort_values("support").head(12).to_csv(TABLE_DIR / "table8_ciciot_low_support_class_diagnostics.csv", index=False)

    iot_classwise = read_if_exists(IOTID_REPEATED / "classwise_metrics.csv")
    if not iot_classwise.empty:
        keep = {
            "iotid_fine_lgbm_full",
            "iotid_fine_lgbm_mi_top10_flat",
            "iotid_fine_lgbm_mi_top10_weighted",
            "iotid_fine_lgbm_xgb_validation_ensemble",
            "iotid_fine_xgb_weighted",
        }
        df = iot_classwise[iot_classwise["run_id"].isin(keep)].copy()
        summary = (
            df.groupby(["run_id", "class_label"], dropna=False)
            .agg(
                mean_support=("support", "mean"),
                mean_precision=("precision", "mean"),
                mean_recall=("recall", "mean"),
                mean_f1=("f1", "mean"),
                sd_recall=("recall", "std"),
                min_recall=("recall", "min"),
            )
            .reset_index()
        )
        flat = summary[summary["run_id"] == "iotid_fine_lgbm_full"][
            ["class_label", "mean_recall", "mean_f1"]
        ].rename(columns={"mean_recall": "flat_mean_recall", "mean_f1": "flat_mean_f1"})
        weighted = summary[summary["run_id"] == "iotid_fine_lgbm_mi_top10_weighted"][
            ["class_label", "mean_recall", "mean_f1"]
        ].rename(columns={"mean_recall": "top10_weighted_mean_recall", "mean_f1": "top10_weighted_mean_f1"})
        comparison = summary.merge(flat, on="class_label", how="left").merge(weighted, on="class_label", how="left")
        comparison["delta_recall_top10_weighted_vs_flat"] = (
            comparison["top10_weighted_mean_recall"] - comparison["flat_mean_recall"]
        )
        comparison["delta_f1_top10_weighted_vs_flat"] = comparison["top10_weighted_mean_f1"] - comparison["flat_mean_f1"]
        comparison["model"] = comparison["run_id"].map(model_label)
        comparison.sort_values(["class_label", "run_id"]).to_csv(
            TABLE_DIR / "table9_iotid20_repeated_classwise_diagnostics.csv",
            index=False,
        )


def supplementary_nbaiot_sensitivity() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    specs = [
        (5000, RESULTS / "nbaiot_unseen_device"),
        (20000, RESULTS / "nbaiot_unseen_device_20k"),
        (50000, RESULTS / "nbaiot_unseen_device_50k_attack"),
    ]
    for cap, result_dir in specs:
        df = read_if_exists(result_dir / "experiment_results.csv")
        if df.empty:
            continue
        df = add_present_class_metrics(result_dir, df)
        df["cap_per_file"] = cap
        rows.append(df)
    if not rows:
        out = pd.DataFrame()
    else:
        df = pd.concat(rows, ignore_index=True)
        out = (
            df.groupby(["cap_per_file", "run_id", "task", "model_name", "feature_strategy", "top_k"], dropna=False)
            .agg(
                folds=("holdout_device", "nunique"),
                mean_macro_f1=("f1_macro", "mean"),
                min_macro_f1=("f1_macro", "min"),
                mean_present_macro_f1=("f1_macro_present_support", "mean"),
                min_present_macro_f1=("f1_macro_present_support", "min"),
                mean_minority_recall=("minority_recall_mean", "mean"),
                mean_worst_class_recall=("worst_class_recall", "mean"),
                min_present_class_recall=("min_present_class_recall", "min"),
                mean_pr_auc_macro=("pr_auc_macro", "mean"),
                mean_train_rows=("train_rows", "mean"),
                mean_test_rows=("test_rows", "mean"),
            )
            .reset_index()
            .sort_values(["task", "run_id", "cap_per_file"])
        )
    out.to_csv(TABLE_DIR / "table10_nbaiot_cap_sensitivity.csv", index=False)
    return out


def supplementary_runtime_complexity() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    ciciot_full = read_if_exists(RESULTS / "ciciot_confirmatory_full" / "experiment_results.csv")
    ciciot_ens = read_if_exists(RESULTS / "ciciot_ensemble_full" / "experiment_results.csv")
    if not ciciot_full.empty:
        for run_id in ["fine_lgbm_full", "fine_lgbm_borderline_smote", "fine_xgb_full_weighted"]:
            part = ciciot_full[ciciot_full["run_id"] == run_id]
            if part.empty:
                continue
            row = part.iloc[0]
            rows.append(
                {
                    "dataset": "CICIoT2023 public subsample",
                    "scope": "full confirmatory split",
                    "model": model_label(run_id),
                    "train_seconds": row["train_seconds"],
                    "inference_ms_per_10000": row["inference_ms_per_1000"] * 10,
                    "model_size_kb": row.get("model_size_kb"),
                    "peak_memory_mb": "not measured",
                    "hardware": "Windows 11, AMD Ryzen 9 8945HS, 31.3 GB RAM",
                }
            )
    if not ciciot_ens.empty:
        part = ciciot_ens[ciciot_ens["objective"] == "macro_f1"]
        if not part.empty:
            row = part.iloc[0]
            component_size = None
            if not ciciot_full.empty:
                pieces = ciciot_full[ciciot_full["run_id"].isin(["fine_lgbm_borderline_smote", "fine_xgb_full_weighted"])]
                if "model_size_kb" in pieces:
                    component_size = pieces["model_size_kb"].sum()
            rows.append(
                {
                    "dataset": "CICIoT2023 public subsample",
                    "scope": "full confirmatory split",
                    "model": "Validation controlled ensemble",
                    "train_seconds": row["train_seconds"],
                    "inference_ms_per_10000": row["inference_ms_per_1000"] * 10,
                    "model_size_kb": component_size,
                    "peak_memory_mb": "not measured",
                    "hardware": "Windows 11, AMD Ryzen 9 8945HS, 31.3 GB RAM",
                }
            )
    iotid_summary = read_if_exists(IOTID_REPEATED / "model_summary.csv")
    if not iotid_summary.empty:
        for _, row in iotid_summary.iterrows():
            rows.append(
                {
                    "dataset": "IoTID20 public mirror",
                    "scope": "mean across 10 repeated 70/30 splits",
                    "model": model_label(row["run_id"]),
                    "train_seconds": row["mean_train_seconds"],
                    "inference_ms_per_10000": row["mean_inference_ms_per_1000"] * 10,
                    "model_size_kb": "not aggregated",
                    "peak_memory_mb": "not measured",
                    "hardware": "Windows 11, AMD Ryzen 9 8945HS, 31.3 GB RAM",
                }
            )
    model_family = read_if_exists(TABLE_DIR / "table6_model_family_checks.csv")
    if not model_family.empty:
        for _, row in model_family[model_family["model"].eq("Flat MLP")].iterrows():
            rows.append(
                {
                    "dataset": row["dataset"],
                    "scope": row["scope"],
                    "model": row["model"],
                    "train_seconds": row["train_seconds"],
                    "inference_ms_per_10000": row["inference_ms_per_10000"],
                    "model_size_kb": row["model_size_kb"],
                    "peak_memory_mb": "not measured",
                    "hardware": "Windows 11, AMD Ryzen 9 8945HS, 31.3 GB RAM",
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "table11_runtime_complexity.csv", index=False)
    return out


def main() -> None:
    ensure_dirs()
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.08)
    figure_validation_design()
    figure_validation_controlled_ensemble()
    ciciot = ciciot_core_table()
    rare = ciciot_rare_table()
    figure_ciciot_main_metrics(ciciot)
    figure_ciciot_rare_class_recall(rare)
    figure_ciciot_alpha_sensitivity()
    iotid_repeated_table()
    figure_iotid_repeated()
    nb = nbaiot_summary()
    figure_nbaiot(nb)
    figure_shap_top_features()
    supplementary_model_family_checks()
    supplementary_classwise_diagnostics()
    supplementary_nbaiot_sensitivity()
    supplementary_runtime_complexity()
    print(f"Wrote figures to {FIG_DIR}")
    print(f"Wrote tables to {TABLE_DIR}")


if __name__ == "__main__":
    main()
