from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import run_ciciot_quick_experiments as exp
from run_ciciot_recall_aware_ensemble import fit_model, metric_row


ROOT = Path(__file__).resolve().parents[1]
LABEL_COL = "Label"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tune rare class probability multipliers on a CICIoT2023 internal validation split.",
    )
    parser.add_argument("--train-n", type=int, default=None)
    parser.add_argument("--test-n", type=int, default=None)
    parser.add_argument("--validation-frac", type=float, default=0.2)
    parser.add_argument("--out-dir", default="ciciot_rare_prior_tuning_full")
    parser.add_argument("--alpha-step", type=float, default=0.05)
    parser.add_argument("--rare-k", type=int, default=4)
    parser.add_argument("--multipliers", default="1,1.15,1.3,1.5,1.75,2,2.5,3,4,5,6")
    parser.add_argument("--composite-lambda", type=float, default=0.08)
    parser.add_argument("--recall-lambda", type=float, default=0.18)
    parser.add_argument("--max-macro-drop", type=float, default=0.01)
    return parser.parse_args()


def parse_multipliers(value: str) -> list[float]:
    out = [float(part.strip()) for part in value.split(",") if part.strip()]
    if not out:
        raise ValueError("At least one multiplier is required.")
    if 1.0 not in out:
        out.insert(0, 1.0)
    return sorted(set(out))


def support_order(df: pd.DataFrame, labels: list[str]) -> list[str]:
    counts = df[LABEL_COL].astype(str).value_counts()
    ordered = sorted(labels, key=lambda label: (int(counts.get(label, 0)), label))
    return ordered


def rare_scope_map(fit_df: pd.DataFrame, labels: list[str], rare_k: int) -> dict[str, list[str]]:
    ordered = support_order(fit_df, labels)
    return {
        "lowest_support": ordered[:1],
        f"lowest_{rare_k}_support": ordered[:rare_k],
        f"lowest_{max(rare_k * 2, rare_k)}_support": ordered[: max(rare_k * 2, rare_k)],
    }


def apply_multiplier(proba: np.ndarray, labels: list[str], rare_labels: list[str], multiplier: float) -> np.ndarray:
    tuned = proba.copy()
    index = {label: idx for idx, label in enumerate(labels)}
    cols = [index[label] for label in rare_labels if label in index]
    if cols and multiplier != 1.0:
        tuned[:, cols] *= multiplier
        tuned_sum = tuned.sum(axis=1, keepdims=True)
        tuned = tuned / np.maximum(tuned_sum, 1e-12)
    return tuned


def tune_grid(
    val_y: np.ndarray,
    lgbm_val: np.ndarray,
    xgb_val: np.ndarray,
    labels: list[str],
    scope_map: dict[str, list[str]],
    multipliers: list[float],
    alpha_step: float,
    composite_lambda: float,
    recall_lambda: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    alphas = np.arange(0.0, 1.0 + alpha_step / 2.0, alpha_step)
    for alpha in alphas:
        blended = float(alpha) * lgbm_val + (1.0 - float(alpha)) * xgb_val
        for scope, rare_labels in scope_map.items():
            for multiplier in multipliers:
                tuned = apply_multiplier(blended, labels, rare_labels, multiplier)
                row = metric_row(
                    "validation_rare_prior_grid",
                    val_y,
                    tuned,
                    labels,
                    train_seconds=0.0,
                    inference_seconds=0.0,
                    n_features=lgbm_val.shape[1],
                    alpha=float(alpha),
                    objective="grid",
                )
                row["rare_scope"] = scope
                row["rare_labels"] = json.dumps(rare_labels)
                row["rare_multiplier"] = float(multiplier)
                row["composite_score"] = row["f1_macro"] + composite_lambda * row["minority_recall_mean"]
                row["recall_weighted_score"] = row["f1_macro"] + recall_lambda * row["minority_recall_mean"]
                rows.append(row)
    return pd.DataFrame(rows)


def choose_operating_points(grid: pd.DataFrame, max_macro_drop: float) -> dict[str, pd.Series]:
    best_macro = grid.sort_values(["f1_macro", "minority_recall_mean", "pr_auc_macro"], ascending=False).iloc[0]
    best_composite = grid.sort_values(["composite_score", "f1_macro", "pr_auc_macro"], ascending=False).iloc[0]
    best_recall = grid.sort_values(["recall_weighted_score", "f1_macro", "pr_auc_macro"], ascending=False).iloc[0]
    floor = float(best_macro["f1_macro"]) - max_macro_drop
    constrained = grid[grid["f1_macro"] >= floor]
    if constrained.empty:
        constrained = grid
    best_constrained = constrained.sort_values(
        ["minority_recall_mean", "f1_macro", "pr_auc_macro"],
        ascending=False,
    ).iloc[0]
    return {
        "macro_f1": best_macro,
        "macro_f1_plus_minority": best_composite,
        "recall_sensitive": best_recall,
        "minority_recall_constrained": best_constrained,
    }


def summarize(
    results: pd.DataFrame,
    grid: pd.DataFrame,
    scope_map: dict[str, list[str]],
    train_n: int | None,
    test_n: int | None,
    max_macro_drop: float,
) -> str:
    show_cols = [
        "run_id",
        "objective",
        "alpha_lgbm",
        "rare_scope",
        "rare_multiplier",
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
    lines = ["# CICIoT2023 Rare Prior Tuning Ledger", ""]
    lines.append("## Data")
    lines.append("")
    lines.append(f"- Train sampling argument: {train_n}")
    lines.append(f"- Test sampling argument: {test_n}")
    lines.append("- Rare class scopes were defined from the fit portion of the training split.")
    lines.append("- Multipliers and ensemble weights were selected only on the internal validation split.")
    lines.append(f"- Constrained recall objective allowed at most {max_macro_drop:.4f} validation Macro-F1 drop.")
    lines.append("")
    lines.append("## Rare Scopes")
    lines.append("")
    for scope, labels in scope_map.items():
        lines.append(f"- `{scope}`: {', '.join(labels)}")
    lines.append("")
    lines.append("## Test Results")
    lines.append("")
    lines.append(results[show_cols].to_markdown(index=False))
    lines.append("")
    lines.append("## Best Validation Rows")
    lines.append("")
    best = grid.sort_values(["recall_weighted_score", "f1_macro"], ascending=False).head(20)
    lines.append(
        best[
            [
                "alpha_lgbm",
                "rare_scope",
                "rare_multiplier",
                "accuracy",
                "balanced_accuracy",
                "f1_macro",
                "minority_recall_mean",
                "worst_class_recall",
                "pr_auc_macro",
                "composite_score",
                "recall_weighted_score",
            ]
        ].to_markdown(index=False)
    )
    lines.append("")
    lines.append("## Claim Control")
    lines.append("")
    lines.append("- This experiment is a validation selected operating point, not a new model architecture.")
    lines.append("- If test Macro-F1 drops more than the primary ensemble, report it as a recall sensitive variant only.")
    lines.append("- If validation chooses multiplier 1.0, rare prior calibration should not be claimed as useful.")
    return "\n".join(lines) + "\n"


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()
    out_dir = ROOT / "results" / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    multipliers = parse_multipliers(args.multipliers)
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

    print("Fitting validation LightGBM BorderlineSMOTE...")
    _, val_y, lgbm_val, _, labels, lgbm_val_train_s = fit_model(fit_df, val_df, lgbm_cfg, features)
    print("Fitting validation XGBoost weighted...")
    _, xgb_val_y, xgb_val, _, xgb_labels, xgb_val_train_s = fit_model(fit_df, val_df, xgb_cfg, features)
    if not np.array_equal(val_y, xgb_val_y) or labels != xgb_labels:
        raise RuntimeError("Validation labels differ between base models.")

    scope_map = rare_scope_map(fit_df, labels, args.rare_k)
    grid = tune_grid(
        val_y,
        lgbm_val,
        xgb_val,
        labels,
        scope_map,
        multipliers,
        args.alpha_step,
        args.composite_lambda,
        args.recall_lambda,
    )
    grid.to_csv(out_dir / "validation_rare_prior_grid.csv", index=False)
    choices = choose_operating_points(grid, args.max_macro_drop)
    print("Selected operating points:")
    for name, row in choices.items():
        print(
            name,
            "alpha=",
            row["alpha_lgbm"],
            "scope=",
            row["rare_scope"],
            "multiplier=",
            row["rare_multiplier"],
            "val_f1=",
            row["f1_macro"],
            "val_minority=",
            row["minority_recall_mean"],
        )

    print("Fitting final LightGBM BorderlineSMOTE...")
    lgbm_model, test_y, _, _, labels, lgbm_train_s = fit_model(train, test, lgbm_cfg, features)
    print("Fitting final XGBoost weighted...")
    xgb_model, xgb_test_y, _, _, xgb_labels, xgb_train_s = fit_model(train, test, xgb_cfg, features)
    if not np.array_equal(test_y, xgb_test_y) or labels != xgb_labels:
        raise RuntimeError("Test labels differ between base models.")

    X_test = test[features].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(dtype=np.float32)
    start = time.perf_counter()
    lgbm_test = lgbm_model.predict_proba(X_test)
    xgb_test = xgb_model.predict_proba(X_test)
    inference_seconds = time.perf_counter() - start

    rows: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []
    for objective, choice in choices.items():
        alpha = float(choice["alpha_lgbm"])
        scope = str(choice["rare_scope"])
        multiplier = float(choice["rare_multiplier"])
        rare_labels = json.loads(str(choice["rare_labels"]))
        blended = alpha * lgbm_test + (1.0 - alpha) * xgb_test
        tuned = apply_multiplier(blended, labels, rare_labels, multiplier)
        row = metric_row(
            f"fine_lgbm_xgb_rare_prior_{objective}",
            test_y,
            tuned,
            labels,
            train_seconds=lgbm_train_s + xgb_train_s,
            inference_seconds=inference_seconds,
            n_features=len(features),
            alpha=alpha,
            objective=objective,
        )
        row["rare_scope"] = scope
        row["rare_labels"] = json.dumps(rare_labels)
        row["rare_multiplier"] = multiplier
        row["validation_lgbm_train_seconds"] = lgbm_val_train_s
        row["validation_xgb_train_seconds"] = xgb_val_train_s
        rows.append(row)
        y_pred = np.argmax(tuned, axis=1)
        classwise.append(exp.classwise_frame(test_y, y_pred, labels, row["run_id"]))

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "experiment_results.csv", index=False)
    pd.concat(classwise, ignore_index=True).to_csv(out_dir / "classwise_metrics.csv", index=False)
    (out_dir / "RESULT_LEDGER.md").write_text(
        summarize(results, grid, scope_map, args.train_n, args.test_n, args.max_macro_drop),
        encoding="utf-8",
    )
    print(f"Wrote {out_dir / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
