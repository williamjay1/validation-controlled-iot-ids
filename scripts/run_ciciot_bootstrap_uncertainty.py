from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split

import run_ciciot_quick_experiments as exp
import run_ciciot_recall_aware_ensemble as ens


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "statistical_uncertainty"
DOCS_DIR = ROOT / "docs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paired bootstrap uncertainty for CICIoT2023 main comparison.")
    parser.add_argument("--train-n", type=int, default=None)
    parser.add_argument("--test-n", type=int, default=None)
    parser.add_argument("--validation-frac", type=float, default=0.2)
    parser.add_argument("--n-bootstrap", type=int, default=500)
    parser.add_argument("--out-dir", default="statistical_uncertainty")
    return parser.parse_args()


def ensure_dirs(args: argparse.Namespace) -> None:
    global OUT_DIR
    OUT_DIR = ROOT / "results" / args.out_dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def metric_values(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    minority_classes: np.ndarray,
    n_classes: int,
) -> dict[str, float]:
    recalls = recall_score(
        y_true,
        y_pred,
        labels=np.arange(n_classes),
        average=None,
        zero_division=0,
    )
    return {
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "minority_recall": float(np.mean(recalls[minority_classes])),
        "worst_class_recall": float(np.min(recalls)),
    }


def bootstrap(
    y_true: np.ndarray,
    baseline_pred: np.ndarray,
    ensemble_pred: np.ndarray,
    n_bootstrap: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(exp.RANDOM_STATE)
    counts = np.bincount(y_true)
    minority_classes = np.where(counts == counts[counts > 0].min())[0]
    n_classes = len(counts)
    rows = []
    n = len(y_true)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        base = metric_values(y_true[idx], baseline_pred[idx], minority_classes, n_classes)
        ens_metrics = metric_values(y_true[idx], ensemble_pred[idx], minority_classes, n_classes)
        row = {"bootstrap_id": i}
        for metric, value in base.items():
            row[f"baseline_{metric}"] = value
            row[f"ensemble_{metric}"] = ens_metrics[metric]
            row[f"delta_{metric}"] = ens_metrics[metric] - value
        rows.append(row)
    return pd.DataFrame(rows)


def summarize(point: dict[str, float], boot: pd.DataFrame, n_bootstrap: int) -> pd.DataFrame:
    rows = []
    for prefix in ["baseline", "ensemble", "delta"]:
        for metric in ["macro_f1", "balanced_accuracy", "minority_recall", "worst_class_recall"]:
            col = f"{prefix}_{metric}"
            values = boot[col].to_numpy()
            rows.append(
                {
                    "quantity": col,
                    "point_estimate": point[col],
                    "ci_low_2_5": np.quantile(values, 0.025),
                    "ci_high_97_5": np.quantile(values, 0.975),
                    "n_bootstrap": n_bootstrap,
                }
            )
    return pd.DataFrame(rows)


def write_note(summary: pd.DataFrame, alpha: float) -> None:
    key = summary[summary["quantity"].str.startswith("delta_")].copy()
    lines = ["# CICIoT2023 Bootstrap Uncertainty", ""]
    lines.append(f"- Ensemble alpha selected from the internal validation split: {alpha:.2f}")
    lines.append("- Bootstrap design: paired row bootstrap on the frozen CICIoT2023 test file.")
    lines.append("- Confidence intervals are percentile intervals.")
    lines.append("- PR-AUC is not bootstrapped here because multiclass PR-AUC resampling is computationally expensive; point estimates remain in the main result tables.")
    lines.append("")
    lines.append("## Delta Intervals")
    lines.append("")
    lines.append(key.to_markdown(index=False))
    (DOCS_DIR / "CICIOT_BOOTSTRAP_UNCERTAINTY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    ensure_dirs(args)
    train, test = exp.load_data(args.train_n, args.test_n)
    fit_df, val_df = train_test_split(
        train,
        test_size=args.validation_frac,
        random_state=exp.RANDOM_STATE,
        stratify=train["Label"],
    )
    features = exp.feature_cols(train)
    baseline_cfg = exp.RunConfig("fine_lgbm_full", "fine", "Label", "lgbm")
    lgbm_cfg = exp.RunConfig(
        "fine_lgbm_borderline_smote",
        "fine",
        "Label",
        "lgbm",
        imbalance="borderline_smote",
    )
    xgb_cfg = exp.RunConfig(
        "fine_xgb_full_weighted",
        "fine",
        "Label",
        "xgb",
        imbalance="class_weight",
    )

    print("Selecting ensemble alpha on validation split...")
    _, val_y, lgbm_val, _, labels, _ = ens.fit_model(fit_df, val_df, lgbm_cfg, features)
    _, xgb_val_y, xgb_val, _, xgb_labels, _ = ens.fit_model(fit_df, val_df, xgb_cfg, features)
    if not np.array_equal(val_y, xgb_val_y) or labels != xgb_labels:
        raise RuntimeError("Validation labels differ between base models.")
    _, alpha_map = ens.choose_alpha(val_y, lgbm_val, xgb_val, labels, composite_lambda=0.08)
    alpha = alpha_map["macro_f1"]

    print("Fitting final baseline LightGBM...")
    _, test_y, baseline_proba, _, labels, _ = ens.fit_model(train, test, baseline_cfg, features)
    baseline_pred = np.argmax(baseline_proba, axis=1)
    print("Fitting final Borderline-SMOTE LightGBM...")
    _, lgbm_test_y, lgbm_proba, _, lgbm_labels, _ = ens.fit_model(train, test, lgbm_cfg, features)
    print("Fitting final weighted XGBoost...")
    _, xgb_test_y, xgb_proba, _, xgb_labels, _ = ens.fit_model(train, test, xgb_cfg, features)
    if not np.array_equal(test_y, lgbm_test_y) or not np.array_equal(test_y, xgb_test_y):
        raise RuntimeError("Test labels differ between models.")
    if labels != lgbm_labels or labels != xgb_labels:
        raise RuntimeError("Class label order differs between models.")
    ensemble_proba = alpha * lgbm_proba + (1.0 - alpha) * xgb_proba
    ensemble_pred = np.argmax(ensemble_proba, axis=1)

    counts = np.bincount(test_y)
    minority_classes = np.where(counts == counts[counts > 0].min())[0]
    point_base = metric_values(test_y, baseline_pred, minority_classes, len(counts))
    point_ens = metric_values(test_y, ensemble_pred, minority_classes, len(counts))
    point = {}
    for metric in point_base:
        point[f"baseline_{metric}"] = point_base[metric]
        point[f"ensemble_{metric}"] = point_ens[metric]
        point[f"delta_{metric}"] = point_ens[metric] - point_base[metric]

    print(f"Running paired bootstrap with {args.n_bootstrap} resamples...")
    boot = bootstrap(test_y, baseline_pred, ensemble_pred, args.n_bootstrap)
    summary = summarize(point, boot, args.n_bootstrap)
    boot.to_csv(OUT_DIR / "ciciot_bootstrap_samples.csv", index=False)
    summary.to_csv(OUT_DIR / "ciciot_bootstrap_summary.csv", index=False)
    write_note(summary, alpha)
    print(f"Wrote {OUT_DIR / 'ciciot_bootstrap_summary.csv'}")


if __name__ == "__main__":
    main()
