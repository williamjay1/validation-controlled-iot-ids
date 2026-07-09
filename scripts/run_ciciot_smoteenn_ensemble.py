from __future__ import annotations

import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import run_ciciot_quick_experiments as exp
from run_ciciot_recall_aware_ensemble import metric_row, summarize


ROOT = Path(__file__).resolve().parents[1]
LABEL_COL = "Label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a validation selected CICIoT2023 three component ensemble with SMOTEENN.",
    )
    parser.add_argument("--train-n", type=int, default=None)
    parser.add_argument("--test-n", type=int, default=None)
    parser.add_argument("--validation-frac", type=float, default=0.2)
    parser.add_argument("--out-dir", default="ciciot_ensemble_smoteenn_full")
    parser.add_argument("--grid-step", type=float, default=0.05)
    parser.add_argument("--composite-lambda", type=float, default=0.08)
    parser.add_argument("--recall-lambda", type=float, default=0.16)
    return parser.parse_args()


def fit_model(
    train_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    config: exp.RunConfig,
    features: list[str],
) -> tuple[object, np.ndarray, np.ndarray, list[str], float]:
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
    proba = model.predict_proba(X_eval.to_numpy(dtype=np.float32))
    return model, y_eval, proba, list(encoder.classes_), train_seconds


def simplex_weights(step: float) -> list[tuple[float, float, float]]:
    ticks = np.arange(0.0, 1.0 + step / 2.0, step)
    weights: list[tuple[float, float, float]] = []
    for w_lgbm in ticks:
        for w_xgb in ticks:
            w_smoteenn = 1.0 - w_lgbm - w_xgb
            if w_smoteenn < -1e-9:
                continue
            if abs(round(w_smoteenn / step) * step - w_smoteenn) > 1e-8:
                continue
            weights.append((float(w_lgbm), float(w_xgb), float(max(0.0, w_smoteenn))))
    return weights


def choose_weights(
    val_y: np.ndarray,
    lgbm_val: np.ndarray,
    xgb_val: np.ndarray,
    smoteenn_val: np.ndarray,
    labels: list[str],
    grid_step: float,
    composite_lambda: float,
    recall_lambda: float,
) -> tuple[pd.DataFrame, dict[str, tuple[float, float, float]]]:
    rows: list[dict[str, object]] = []
    for w_lgbm, w_xgb, w_smoteenn in simplex_weights(grid_step):
        proba = w_lgbm * lgbm_val + w_xgb * xgb_val + w_smoteenn * smoteenn_val
        row = metric_row(
            "validation_three_component_grid",
            val_y,
            proba,
            labels,
            train_seconds=0.0,
            inference_seconds=0.0,
            n_features=lgbm_val.shape[1],
            alpha=w_lgbm,
            objective="grid",
        )
        row["model_name"] = "three_component_probability_ensemble"
        row["imbalance"] = "borderline_smote_plus_class_weight_plus_smoteenn"
        row["w_lgbm_borderline"] = w_lgbm
        row["w_xgb_weighted"] = w_xgb
        row["w_lgbm_smoteenn"] = w_smoteenn
        row["composite_score"] = row["f1_macro"] + composite_lambda * row["minority_recall_mean"]
        row["recall_weighted_score"] = row["f1_macro"] + recall_lambda * row["minority_recall_mean"]
        rows.append(row)
    grid = pd.DataFrame(rows)
    best_macro = grid.sort_values(["f1_macro", "minority_recall_mean"], ascending=False).iloc[0]
    best_composite = grid.sort_values(["composite_score", "f1_macro"], ascending=False).iloc[0]
    best_recall = grid.sort_values(["recall_weighted_score", "f1_macro"], ascending=False).iloc[0]

    def tup(row: pd.Series) -> tuple[float, float, float]:
        return (
            float(row["w_lgbm_borderline"]),
            float(row["w_xgb_weighted"]),
            float(row["w_lgbm_smoteenn"]),
        )

    return grid, {
        "macro_f1": tup(best_macro),
        "macro_f1_plus_minority": tup(best_composite),
        "recall_sensitive": tup(best_recall),
    }


def summarize_three(results: pd.DataFrame, grid: pd.DataFrame, train_n: int | None, test_n: int | None) -> str:
    lines = ["# CICIoT2023 SMOTEENN Three Component Ensemble Ledger", ""]
    lines.append("## Data")
    lines.append("")
    lines.append(f"- Train sampling argument: {train_n}")
    lines.append(f"- Test sampling argument: {test_n}")
    lines.append("- Weight selection used only an internal validation split from the training file.")
    lines.append("")
    lines.append("## Test Results")
    lines.append("")
    show_cols = [
        "run_id",
        "objective",
        "w_lgbm_borderline",
        "w_xgb_weighted",
        "w_lgbm_smoteenn",
        "accuracy",
        "balanced_accuracy",
        "f1_macro",
        "minority_recall_mean",
        "worst_class_recall",
        "worst_class_label",
        "pr_auc_macro",
        "train_seconds",
        "inference_ms_per_1000",
    ]
    lines.append(results[show_cols].to_markdown(index=False))
    lines.append("")
    lines.append("## Best Validation Weights")
    lines.append("")
    best = grid.sort_values(["recall_weighted_score", "f1_macro"], ascending=False).head(20)
    lines.append(
        best[
            [
                "w_lgbm_borderline",
                "w_xgb_weighted",
                "w_lgbm_smoteenn",
                "f1_macro",
                "minority_recall_mean",
                "pr_auc_macro",
                "composite_score",
                "recall_weighted_score",
            ]
        ].to_markdown(index=False)
    )
    lines.append("")
    lines.append("## Claim Control")
    lines.append("")
    lines.append("- If the recall sensitive operating point sacrifices Macro-F1, it should be written as an optional operating point.")
    lines.append("- A stronger manuscript claim requires full train/test confirmation and comparison against the current two component ensemble.")
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
    configs = [
        exp.RunConfig("fine_lgbm_borderline_smote", "fine", LABEL_COL, "lgbm", imbalance="borderline_smote"),
        exp.RunConfig("fine_xgb_full_weighted", "fine", LABEL_COL, "xgb", imbalance="class_weight"),
        exp.RunConfig("fine_lgbm_smoteenn", "fine", LABEL_COL, "lgbm", imbalance="smoteenn"),
    ]

    val_probas: dict[str, np.ndarray] = {}
    final_models: dict[str, object] = {}
    train_seconds: dict[str, float] = {}
    labels_ref: list[str] | None = None
    val_y_ref: np.ndarray | None = None
    for cfg in configs:
        print(f"Fitting validation {cfg.run_id}...")
        _, val_y, proba, labels, seconds = fit_model(fit_df, val_df, cfg, features)
        if val_y_ref is None:
            val_y_ref = val_y
            labels_ref = labels
        elif not np.array_equal(val_y_ref, val_y) or labels_ref != labels:
            raise RuntimeError("Validation labels differ across components.")
        val_probas[cfg.run_id] = proba
        train_seconds[f"validation_{cfg.run_id}"] = seconds

    assert val_y_ref is not None and labels_ref is not None
    grid, weight_map = choose_weights(
        val_y_ref,
        val_probas["fine_lgbm_borderline_smote"],
        val_probas["fine_xgb_full_weighted"],
        val_probas["fine_lgbm_smoteenn"],
        labels_ref,
        args.grid_step,
        args.composite_lambda,
        args.recall_lambda,
    )
    grid.to_csv(out_dir / "validation_weight_grid.csv", index=False)
    print(f"Selected weights: {weight_map}")

    test_y_ref: np.ndarray | None = None
    test_labels_ref: list[str] | None = None
    for cfg in configs:
        print(f"Fitting final {cfg.run_id}...")
        model, test_y, _, labels, seconds = fit_model(train, test, cfg, features)
        if test_y_ref is None:
            test_y_ref = test_y
            test_labels_ref = labels
        elif not np.array_equal(test_y_ref, test_y) or test_labels_ref != labels:
            raise RuntimeError("Test labels differ across components.")
        final_models[cfg.run_id] = model
        train_seconds[cfg.run_id] = seconds

    assert test_y_ref is not None and test_labels_ref is not None
    X_test = test[features].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(dtype=np.float32)
    start = time.perf_counter()
    test_probas = {run_id: model.predict_proba(X_test) for run_id, model in final_models.items()}
    base_inference_seconds = time.perf_counter() - start

    rows: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []
    total_train_seconds = sum(train_seconds[cfg.run_id] for cfg in configs)
    for objective, (w_lgbm, w_xgb, w_smoteenn) in weight_map.items():
        blended = (
            w_lgbm * test_probas["fine_lgbm_borderline_smote"]
            + w_xgb * test_probas["fine_xgb_full_weighted"]
            + w_smoteenn * test_probas["fine_lgbm_smoteenn"]
        )
        row = metric_row(
            f"fine_lgbm_xgb_smoteenn_ensemble_{objective}",
            test_y_ref,
            blended,
            test_labels_ref,
            train_seconds=total_train_seconds,
            inference_seconds=base_inference_seconds,
            n_features=len(features),
            alpha=w_lgbm,
            objective=objective,
        )
        row["model_name"] = "three_component_probability_ensemble"
        row["imbalance"] = "borderline_smote_plus_class_weight_plus_smoteenn"
        row["w_lgbm_borderline"] = w_lgbm
        row["w_xgb_weighted"] = w_xgb
        row["w_lgbm_smoteenn"] = w_smoteenn
        for key, value in train_seconds.items():
            row[key + "_seconds"] = value
        rows.append(row)
        y_pred = np.argmax(blended, axis=1)
        classwise.append(exp.classwise_frame(test_y_ref, y_pred, test_labels_ref, row["run_id"]))

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "experiment_results.csv", index=False)
    pd.concat(classwise, ignore_index=True).to_csv(out_dir / "classwise_metrics.csv", index=False)
    (out_dir / "RESULT_LEDGER.md").write_text(
        summarize_three(results, grid, args.train_n, args.test_n),
        encoding="utf-8",
    )
    print(f"Wrote {out_dir / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
