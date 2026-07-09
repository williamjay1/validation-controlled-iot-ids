from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import run_iotid20_quick_experiments as iot


ROOT = Path(__file__).resolve().parents[1]
LABEL_COL = "Label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run IoTID20 recall-aware probability ensemble.")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--validation-frac", type=float, default=0.2)
    parser.add_argument("--test-frac", type=float, default=0.3)
    parser.add_argument("--out-dir", default="iotid20_ensemble")
    parser.add_argument("--composite-lambda", type=float, default=0.08)
    return parser.parse_args()


def fit_model(
    train_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    config: iot.RunConfig,
) -> tuple[object, np.ndarray, np.ndarray, list[str], list[str], float]:
    features = [c for c in train_df.columns if c not in ["Label", "binary_label"]]
    X_train_all = train_df[features].astype("float32")
    X_eval_all = eval_df[features].astype("float32")
    y_train, y_eval, encoder = iot.encode(train_df[config.target_col], eval_df[config.target_col])
    X_train_df, X_eval_df, cols = iot.select_features(
        X_train_all,
        y_train,
        X_eval_all,
        config.feature_strategy,
        config.top_k,
    )
    X_fit, y_fit, sample_weight, _ = iot.apply_imbalance(
        X_train_df.to_numpy(dtype=np.float32),
        y_train,
        config.task,
        config.imbalance,
    )
    if config.imbalance == "class_weight" and sample_weight is None:
        sample_weight = iot.class_sample_weight(y_fit)
    model = iot.make_model(config.model_name, len(encoder.classes_))
    start = time.perf_counter()
    if sample_weight is not None:
        model.fit(X_fit, y_fit, sample_weight=sample_weight)
    else:
        model.fit(X_fit, y_fit)
    train_seconds = time.perf_counter() - start
    proba = iot.predict_proba_safe(model, X_eval_df.to_numpy(dtype=np.float32), len(encoder.classes_))
    return model, y_eval, proba, list(encoder.classes_), cols, train_seconds


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
    row = iot.metric_dict(
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
            "model_name": "lgbm_top10_xgb_probability_ensemble",
            "imbalance": "class_weight",
            "feature_strategy": "mixed_mi_top10_plus_all",
            "top_k": 10,
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
            n_features=22,
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


def summarize(results: pd.DataFrame, grid: pd.DataFrame, n_rows: int) -> str:
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
    lines = ["# IoTID20 Recall-Aware Ensemble Ledger", ""]
    lines.append("## Data")
    lines.append("")
    lines.append(f"- Rows after cleaning/sampling: {n_rows:,}")
    lines.append("- Split: stratified train/test holdout; alpha selected only on an internal validation split of the training portion.")
    lines.append("")
    lines.append("## Test Results")
    lines.append("")
    lines.append(results[cols].to_markdown(index=False))
    lines.append("")
    lines.append("## Validation Alpha Grid")
    lines.append("")
    lines.append(
        grid[
            [
                "alpha_lgbm",
                "accuracy",
                "balanced_accuracy",
                "f1_macro",
                "minority_recall_mean",
                "worst_class_recall",
                "pr_auc_macro",
                "composite_score",
            ]
        ].to_markdown(index=False)
    )
    lines.append("")
    lines.append("## Claim Control")
    lines.append("")
    lines.append("- This is an independent holdout replication because the downloaded IoTID20 mirror does not provide an official train/test split.")
    lines.append("- Any cross-dataset claim should be framed as corroboration of the imbalance/recall tradeoff, not direct transfer learning.")
    return "\n".join(lines) + "\n"


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()
    out_dir = ROOT / "results" / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = iot.load_iotid(args.max_rows)
    train, test = train_test_split(
        df,
        test_size=args.test_frac,
        random_state=iot.RANDOM_STATE,
        stratify=df[LABEL_COL],
    )
    fit_df, val_df = train_test_split(
        train,
        test_size=args.validation_frac,
        random_state=iot.RANDOM_STATE,
        stratify=train[LABEL_COL],
    )
    lgbm_cfg = iot.RunConfig(
        "iotid_fine_lgbm_mi_top10_weighted",
        "fine",
        LABEL_COL,
        "lgbm",
        imbalance="class_weight",
        feature_strategy="mi",
        top_k=10,
    )
    xgb_cfg = iot.RunConfig(
        "iotid_fine_xgb_weighted",
        "fine",
        LABEL_COL,
        "xgb",
        imbalance="class_weight",
    )

    print("Fitting validation IoTID20 LightGBM MI top-10...")
    _, val_y, lgbm_val, labels, lgbm_cols, lgbm_val_s = fit_model(fit_df, val_df, lgbm_cfg)
    print("Fitting validation IoTID20 XGBoost weighted...")
    _, xgb_val_y, xgb_val, xgb_labels, xgb_cols, xgb_val_s = fit_model(fit_df, val_df, xgb_cfg)
    if not np.array_equal(val_y, xgb_val_y) or labels != xgb_labels:
        raise RuntimeError("Validation labels differ between base models.")
    grid, alpha_map = choose_alpha(val_y, lgbm_val, xgb_val, labels, args.composite_lambda)
    grid.to_csv(out_dir / "validation_alpha_grid.csv", index=False)
    print(f"Selected alphas: {alpha_map}")

    print("Fitting final IoTID20 LightGBM MI top-10...")
    lgbm_model, test_y, _, labels, lgbm_cols, lgbm_train_s = fit_model(train, test, lgbm_cfg)
    print("Fitting final IoTID20 XGBoost weighted...")
    xgb_model, xgb_test_y, _, xgb_labels, xgb_cols, xgb_train_s = fit_model(train, test, xgb_cfg)
    if not np.array_equal(test_y, xgb_test_y) or labels != xgb_labels:
        raise RuntimeError("Test labels differ between base models.")

    rows: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []
    X_test_all = test[[c for c in test.columns if c not in ["Label", "binary_label"]]].astype("float32")
    for objective, alpha in alpha_map.items():
        start = time.perf_counter()
        lgbm_test = iot.predict_proba_safe(lgbm_model, X_test_all[lgbm_cols].to_numpy(dtype=np.float32), len(labels))
        xgb_test = iot.predict_proba_safe(xgb_model, X_test_all[xgb_cols].to_numpy(dtype=np.float32), len(labels))
        blended = alpha * lgbm_test + (1.0 - alpha) * xgb_test
        inference_seconds = time.perf_counter() - start
        row = metric_row(
            f"iotid_lgbm_xgb_ensemble_{objective}",
            test_y,
            blended,
            labels,
            train_seconds=lgbm_train_s + xgb_train_s,
            inference_seconds=inference_seconds,
            n_features=len(set(lgbm_cols).union(xgb_cols)),
            alpha=alpha,
            objective=objective,
        )
        row["validation_lgbm_train_seconds"] = lgbm_val_s
        row["validation_xgb_train_seconds"] = xgb_val_s
        rows.append(row)
        classwise.append(iot.classwise_frame(test_y, np.argmax(blended, axis=1), labels, row["run_id"]))

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "experiment_results.csv", index=False)
    pd.concat(classwise, ignore_index=True).to_csv(out_dir / "classwise_metrics.csv", index=False)
    (out_dir / "RESULT_LEDGER.md").write_text(summarize(results, grid, len(df)), encoding="utf-8")
    print(f"Wrote {out_dir / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
