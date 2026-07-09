from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import run_ciciot_quick_experiments as exp


ROOT = Path(__file__).resolve().parents[1]
LABEL_COL = "Label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run recall-aware CICIoT2023 probability ensembles.")
    parser.add_argument("--train-n", type=int, default=None)
    parser.add_argument("--test-n", type=int, default=None)
    parser.add_argument("--validation-frac", type=float, default=0.2)
    parser.add_argument("--out-dir", default="ciciot_ensemble_full")
    parser.add_argument("--composite-lambda", type=float, default=0.08)
    return parser.parse_args()


def fit_model(
    train_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    config: exp.RunConfig,
    features: list[str],
) -> tuple[object, np.ndarray, np.ndarray, np.ndarray, list[str], float]:
    y_train, y_eval, encoder = exp.encode_target(train_df[config.target_col], eval_df[config.target_col])
    X_train = train_df[features]
    X_eval = eval_df[features]
    X_fit, y_fit, sample_weight, _ = exp.apply_imbalance(
        X_train.to_numpy(dtype=np.float32),
        y_train,
        config.task,
        config.imbalance,
    )
    model = exp.make_model(config.model_name, len(encoder.classes_))
    start = time.perf_counter()
    if sample_weight is None:
        model.fit(X_fit, y_fit)
    else:
        model.fit(X_fit, y_fit, sample_weight=sample_weight)
    train_seconds = time.perf_counter() - start
    proba = model.predict_proba(X_eval)
    return model, y_eval, proba, y_train, list(encoder.classes_), train_seconds


def metric_row(
    run_id: str,
    y_true: np.ndarray,
    proba: np.ndarray,
    labels: list[str],
    train_seconds: float,
    inference_seconds: float,
    n_features: int,
    alpha: float,
    objective: str,
) -> dict[str, object]:
    y_pred = np.argmax(proba, axis=1)
    row = exp.metric_dict(
        y_true,
        y_pred,
        proba,
        labels,
        train_seconds=train_seconds,
        inference_seconds=inference_seconds,
        n_features=n_features,
        model_kb=np.nan,
    )
    row.update(
        {
            "run_id": run_id,
            "task": "fine",
            "model_name": "lgbm_xgb_probability_ensemble",
            "imbalance": "borderline_smote_plus_class_weight",
            "feature_strategy": "all",
            "top_k": np.nan,
            "alpha_lgbm": alpha,
            "objective": objective,
        }
    )
    return row


def choose_alpha(
    val_y: np.ndarray,
    lgbm_val: np.ndarray,
    xgb_val: np.ndarray,
    labels: list[str],
    n_features: int,
    composite_lambda: float,
) -> tuple[pd.DataFrame, dict[str, float]]:
    rows: list[dict[str, object]] = []
    for alpha in np.linspace(0.0, 1.0, 21):
        proba = alpha * lgbm_val + (1.0 - alpha) * xgb_val
        row = metric_row(
            "validation_alpha_grid",
            val_y,
            proba,
            labels,
            train_seconds=0.0,
            inference_seconds=0.0,
            n_features=n_features,
            alpha=float(alpha),
            objective="grid",
        )
        row["composite_score"] = row["f1_macro"] + composite_lambda * row["minority_recall_mean"]
        rows.append(row)
    grid = pd.DataFrame(rows)
    best_macro = grid.sort_values(["f1_macro", "minority_recall_mean"], ascending=False).iloc[0]
    best_composite = grid.sort_values(["composite_score", "f1_macro"], ascending=False).iloc[0]
    return grid, {
        "macro_f1": float(best_macro["alpha_lgbm"]),
        "macro_f1_plus_minority": float(best_composite["alpha_lgbm"]),
    }


def summarize(results: pd.DataFrame, grid: pd.DataFrame, train_n: int | None, test_n: int | None) -> str:
    cols = [
        "run_id",
        "objective",
        "alpha_lgbm",
        "accuracy",
        "balanced_accuracy",
        "f1_macro",
        "f1_weighted",
        "minority_recall_mean",
        "worst_class_recall",
        "worst_class_label",
        "pr_auc_macro",
        "train_seconds",
        "inference_ms_per_1000",
    ]
    lines = ["# CICIoT2023 Recall-Aware Ensemble Ledger", ""]
    lines.append("## Data")
    lines.append("")
    lines.append(f"- Train sampling argument: {train_n}")
    lines.append(f"- Test sampling argument: {test_n}")
    lines.append("- Weight selection used only an internal validation split from the training file.")
    lines.append("")
    lines.append("## Test Results")
    lines.append("")
    results_table = results.copy()
    for col in cols:
        if col not in results_table.columns:
            results_table[col] = np.nan
    lines.append(results_table[cols].to_markdown(index=False))
    lines.append("")
    lines.append("## Validation Alpha Grid")
    lines.append("")
    grid_cols = [
        "alpha_lgbm",
        "accuracy",
        "balanced_accuracy",
        "f1_macro",
        "minority_recall_mean",
        "worst_class_recall",
        "pr_auc_macro",
        "composite_score",
    ]
    grid_table = grid.copy()
    for col in grid_cols:
        if col not in grid_table.columns:
            grid_table[col] = np.nan
    lines.append(
        grid_table[grid_cols].to_markdown(index=False)
    )
    lines.append("")
    lines.append("## Claim Control")
    lines.append("")
    lines.append("- The ensemble is valid only as an internally tuned model because alpha is chosen on a split of the training file.")
    lines.append("- The test file is not used for alpha selection.")
    lines.append("- If the composite objective sacrifices too much Macro-F1, it should be written as a recall-sensitive operating point rather than the default model.")
    return "\n".join(lines) + "\n"


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()
    out_dir = ROOT / "results" / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    train, test = exp.load_data(args.train_n, args.test_n)
    fit_df, val_df = train_test_split(
        train,
        test_size=args.validation_frac,
        random_state=exp.RANDOM_STATE,
        stratify=train[LABEL_COL],
    )
    features = exp.feature_cols(train)
    lgbm_cfg = exp.RunConfig(
        "fine_lgbm_borderline_smote",
        "fine",
        LABEL_COL,
        "lgbm",
        imbalance="borderline_smote",
    )
    xgb_cfg = exp.RunConfig(
        "fine_xgb_full_weighted",
        "fine",
        LABEL_COL,
        "xgb",
        imbalance="class_weight",
    )

    print("Fitting validation LightGBM Borderline-SMOTE...")
    _, val_y, lgbm_val, _, labels, lgbm_val_train_s = fit_model(fit_df, val_df, lgbm_cfg, features)
    print("Fitting validation XGBoost class-weighted...")
    _, xgb_val_y, xgb_val, _, xgb_labels, xgb_val_train_s = fit_model(fit_df, val_df, xgb_cfg, features)
    if not np.array_equal(val_y, xgb_val_y) or labels != xgb_labels:
        raise RuntimeError("Validation labels differ between base models.")

    grid, alpha_map = choose_alpha(val_y, lgbm_val, xgb_val, labels, len(features), args.composite_lambda)
    grid.to_csv(out_dir / "validation_alpha_grid.csv", index=False)
    print(f"Selected alphas: {alpha_map}")

    print("Fitting final LightGBM Borderline-SMOTE...")
    lgbm_model, test_y, _, _, labels, lgbm_train_s = fit_model(train, test, lgbm_cfg, features)
    print("Fitting final XGBoost class-weighted...")
    xgb_model, xgb_test_y, _, _, xgb_labels, xgb_train_s = fit_model(train, test, xgb_cfg, features)
    if not np.array_equal(test_y, xgb_test_y) or labels != xgb_labels:
        raise RuntimeError("Test labels differ between base models.")

    X_test = test[features]
    rows: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []
    for objective, alpha in alpha_map.items():
        start = time.perf_counter()
        lgbm_test = lgbm_model.predict_proba(X_test)
        xgb_test = xgb_model.predict_proba(X_test)
        blended = alpha * lgbm_test + (1.0 - alpha) * xgb_test
        inference_seconds = time.perf_counter() - start
        row = metric_row(
            f"fine_lgbm_xgb_ensemble_{objective}",
            test_y,
            blended,
            labels,
            train_seconds=lgbm_train_s + xgb_train_s,
            inference_seconds=inference_seconds,
            n_features=len(features),
            alpha=alpha,
            objective=objective,
        )
        row["validation_lgbm_train_seconds"] = lgbm_val_train_s
        row["validation_xgb_train_seconds"] = xgb_val_train_s
        rows.append(row)
        classwise.append(exp.classwise_frame(test_y, np.argmax(blended, axis=1), labels, row["run_id"]))

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "experiment_results.csv", index=False)
    pd.concat(classwise, ignore_index=True).to_csv(out_dir / "classwise_metrics.csv", index=False)
    (out_dir / "RESULT_LEDGER.md").write_text(
        summarize(results, grid, args.train_n, args.test_n),
        encoding="utf-8",
    )
    print(f"Wrote {out_dir / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
