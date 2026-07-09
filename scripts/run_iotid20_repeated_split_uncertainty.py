from __future__ import annotations

import argparse
import time
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import run_iotid20_quick_experiments as iot


ROOT = Path(__file__).resolve().parents[1]
LABEL_COL = "Label"
BASELINE_RUN_ID = "iotid_fine_lgbm_full"
OUT_DIR = ROOT / "results" / "iotid20_repeated_split"
DOCS_DIR = ROOT / "docs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run repeated stratified IoTID20 splits and split-level bootstrap uncertainty."
    )
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--test-frac", type=float, default=0.3)
    parser.add_argument("--validation-frac", type=float, default=0.2)
    parser.add_argument("--n-splits", type=int, default=10)
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--bootstrap-reps", type=int, default=10000)
    parser.add_argument("--out-dir", default="iotid20_repeated_split")
    parser.add_argument("--include-catboost", action="store_true")
    return parser.parse_args()


def ensure_dirs(args: argparse.Namespace) -> None:
    global OUT_DIR
    OUT_DIR = ROOT / "results" / args.out_dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def base_configs(include_catboost: bool) -> list[iot.RunConfig]:
    configs = [
        iot.RunConfig(BASELINE_RUN_ID, "fine", LABEL_COL, "lgbm"),
        iot.RunConfig("iotid_fine_lgbm_weighted", "fine", LABEL_COL, "lgbm", imbalance="class_weight"),
        iot.RunConfig(
            "iotid_fine_lgbm_mi_top10_flat",
            "fine",
            LABEL_COL,
            "lgbm",
            feature_strategy="mi",
            top_k=10,
        ),
        iot.RunConfig(
            "iotid_fine_lgbm_mi_top10_weighted",
            "fine",
            LABEL_COL,
            "lgbm",
            imbalance="class_weight",
            feature_strategy="mi",
            top_k=10,
        ),
        iot.RunConfig("iotid_fine_xgb_weighted", "fine", LABEL_COL, "xgb", imbalance="class_weight"),
    ]
    if include_catboost:
        configs.append(iot.RunConfig("iotid_fine_catboost_weighted", "fine", LABEL_COL, "catboost", imbalance="class_weight"))
    return configs


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
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    row = iot.metric_dict(
        y_true,
        np.argmax(proba, axis=1),
        proba,
        labels,
        train_seconds=train_seconds,
        inference_seconds=inference_seconds,
        n_features=n_features,
        model_kb=np.nan,
    )
    row["run_id"] = run_id
    if extra:
        row.update(extra)
    return row


def choose_alpha(
    val_y: np.ndarray,
    lgbm_val: np.ndarray,
    xgb_val: np.ndarray,
    labels: list[str],
) -> tuple[float, pd.DataFrame]:
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
            n_features=lgbm_val.shape[1],
            extra={"alpha_lgbm": float(alpha)},
        )
        row["composite_score"] = row["f1_macro"] + 0.08 * row["minority_recall_mean"]
        rows.append(row)
    grid = pd.DataFrame(rows)
    best = grid.sort_values(["f1_macro", "minority_recall_mean"], ascending=False).iloc[0]
    return float(best["alpha_lgbm"]), grid


def run_single_split(df: pd.DataFrame, seed: int, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    train, test = train_test_split(
        df,
        test_size=args.test_frac,
        random_state=seed,
        stratify=df[LABEL_COL],
    )
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    rows: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []

    for config in base_configs(args.include_catboost):
        print(f"Split seed={seed}: fitting {config.run_id}", flush=True)
        start = time.perf_counter()
        metrics, cw = iot.run_one(train, test, config)
        metrics["split_seed"] = seed
        metrics["wall_seconds"] = time.perf_counter() - start
        rows.append(metrics)
        cw["split_seed"] = seed
        classwise.append(cw)

    fit_df, val_df = train_test_split(
        train,
        test_size=args.validation_frac,
        random_state=seed,
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
    xgb_cfg = iot.RunConfig("iotid_fine_xgb_weighted", "fine", LABEL_COL, "xgb", imbalance="class_weight")
    print(f"Split seed={seed}: selecting ensemble alpha", flush=True)
    _, val_y, lgbm_val, labels, lgbm_cols, _ = fit_model(fit_df, val_df, lgbm_cfg)
    _, xgb_val_y, xgb_val, xgb_labels, xgb_cols, _ = fit_model(fit_df, val_df, xgb_cfg)
    if not np.array_equal(val_y, xgb_val_y) or labels != xgb_labels:
        raise RuntimeError(f"Validation label mismatch for split seed {seed}.")
    alpha, grid = choose_alpha(val_y, lgbm_val, xgb_val, labels)
    grid["split_seed"] = seed

    print(f"Split seed={seed}: fitting final ensemble alpha={alpha:.2f}", flush=True)
    lgbm_model, test_y, _, labels, lgbm_cols, lgbm_train_seconds = fit_model(train, test, lgbm_cfg)
    xgb_model, xgb_test_y, _, xgb_labels, xgb_cols, xgb_train_seconds = fit_model(train, test, xgb_cfg)
    if not np.array_equal(test_y, xgb_test_y) or labels != xgb_labels:
        raise RuntimeError(f"Test label mismatch for split seed {seed}.")
    X_test_all = test[[c for c in test.columns if c not in ["Label", "binary_label"]]].astype("float32")
    start = time.perf_counter()
    lgbm_test = iot.predict_proba_safe(lgbm_model, X_test_all[lgbm_cols].to_numpy(dtype=np.float32), len(labels))
    xgb_test = iot.predict_proba_safe(xgb_model, X_test_all[xgb_cols].to_numpy(dtype=np.float32), len(labels))
    blended = alpha * lgbm_test + (1.0 - alpha) * xgb_test
    inference_seconds = time.perf_counter() - start
    ensemble_row = metric_row(
        "iotid_fine_lgbm_xgb_validation_ensemble",
        test_y,
        blended,
        labels,
        train_seconds=lgbm_train_seconds + xgb_train_seconds,
        inference_seconds=inference_seconds,
        n_features=len(set(lgbm_cols).union(xgb_cols)),
        extra={
            "split_seed": seed,
            "model_name": "lgbm_top10_xgb_probability_ensemble",
            "imbalance": "class_weight",
            "feature_strategy": "mixed_mi_top10_plus_all",
            "top_k": 10,
            "alpha_lgbm": alpha,
            "task": "fine",
            "target_col": LABEL_COL,
        },
    )
    rows.append(ensemble_row)
    cw = iot.classwise_frame(test_y, np.argmax(blended, axis=1), labels, ensemble_row["run_id"])
    cw["split_seed"] = seed
    classwise.append(cw)
    grid.to_csv(OUT_DIR / f"validation_alpha_grid_seed_{seed}.csv", index=False)
    return pd.DataFrame(rows), pd.concat(classwise, ignore_index=True)


def split_level_ci(values: np.ndarray, reps: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = np.empty(reps, dtype=np.float64)
    n = len(values)
    for i in range(reps):
        idx = rng.integers(0, n, size=n)
        means[i] = float(np.mean(values[idx]))
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def exact_signflip_pvalue(values: np.ndarray) -> float:
    observed = abs(float(np.mean(values)))
    n = len(values)
    extreme = 0
    total = 2**n
    for mask in range(total):
        signs = np.array([1 if (mask >> bit) & 1 else -1 for bit in range(n)], dtype=float)
        if abs(float(np.mean(signs * values))) >= observed - 1e-15:
            extreme += 1
    return float(extreme / total)


def summarize(results: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    metric_cols = [
        "accuracy",
        "balanced_accuracy",
        "f1_macro",
        "minority_recall_mean",
        "worst_class_recall",
        "pr_auc_macro",
    ]
    model_summary = (
        results.groupby("run_id", dropna=False)
        .agg(
            n_splits=("split_seed", "nunique"),
            mean_macro_f1=("f1_macro", "mean"),
            sd_macro_f1=("f1_macro", "std"),
            mean_balanced_accuracy=("balanced_accuracy", "mean"),
            mean_minority_recall=("minority_recall_mean", "mean"),
            sd_minority_recall=("minority_recall_mean", "std"),
            mean_pr_auc_macro=("pr_auc_macro", "mean"),
            mean_train_seconds=("train_seconds", "mean"),
            mean_inference_ms_per_1000=("inference_ms_per_1000", "mean"),
        )
        .reset_index()
        .sort_values(["mean_macro_f1", "mean_minority_recall"], ascending=False)
    )
    baseline = results[results["run_id"] == BASELINE_RUN_ID][["split_seed"] + metric_cols].copy()
    delta_rows: list[dict[str, object]] = []
    signflip_rows: list[dict[str, object]] = []
    for run_id, group in results.groupby("run_id", dropna=False):
        if run_id == BASELINE_RUN_ID:
            continue
        merged = group[["split_seed"] + metric_cols].merge(baseline, on="split_seed", suffixes=("", "_baseline"))
        for metric in metric_cols:
            delta = merged[metric] - merged[f"{metric}_baseline"]
            delta_values = delta.to_numpy(dtype=float)
            low, high = split_level_ci(delta.to_numpy(dtype=float), args.bootstrap_reps, args.seed_start)
            delta_rows.append(
                {
                    "run_id": run_id,
                    "metric": metric,
                    "mean_delta_vs_flat_lgbm": float(delta.mean()),
                    "sd_delta": float(delta.std(ddof=1)) if len(delta) > 1 else 0.0,
                    "ci_low_2_5": low,
                    "ci_high_97_5": high,
                    "n_splits": int(len(delta)),
                    "bootstrap_reps": int(args.bootstrap_reps),
                }
            )
            signflip_rows.append(
                {
                    "run_id": run_id,
                    "metric": metric,
                    "mean_delta_vs_flat_lgbm": float(delta_values.mean()),
                    "positive_splits": int(np.sum(delta_values > 0)),
                    "negative_splits": int(np.sum(delta_values < 0)),
                    "zero_splits": int(np.sum(delta_values == 0)),
                    "n_splits": int(len(delta_values)),
                    "exact_two_sided_p": exact_signflip_pvalue(delta_values),
                }
            )
    delta_summary = pd.DataFrame(delta_rows).sort_values(["metric", "mean_delta_vs_flat_lgbm"], ascending=[True, False])
    signflip_summary = pd.DataFrame(signflip_rows).sort_values(["metric", "mean_delta_vs_flat_lgbm"], ascending=[True, False])
    focus = delta_summary[delta_summary["metric"].isin(["f1_macro", "minority_recall_mean", "pr_auc_macro"])]
    sign_focus = signflip_summary[signflip_summary["metric"].isin(["f1_macro", "minority_recall_mean", "pr_auc_macro"])]
    lines = [
        "# IoTID20 Repeated Split Uncertainty",
        "",
        "## Design",
        "",
        f"- Dataset rows after cleaning/sampling: {int(results['train_rows'].iloc[0] + results['test_rows'].iloc[0]):,}",
        f"- Repeated splits: {args.n_splits}",
        f"- Split seeds: {args.seed_start} to {args.seed_start + args.n_splits - 1}",
        f"- Test fraction: {args.test_frac}",
        "- Fixed factors: data cleaning, feature space, model families, class-weighting strategy, metric definitions.",
        "- Varying factor: stratified train/test split random seed.",
        "",
        "## Model Summary",
        "",
        model_summary.to_markdown(index=False),
        "",
        "## Paired Delta Summary vs Flat LightGBM",
        "",
        focus.to_markdown(index=False),
        "",
        "## Exact Sign-Flip Summary vs Flat LightGBM",
        "",
        sign_focus.to_markdown(index=False),
        "",
        "## Claim Control",
        "",
        "- Positive intervals for minority recall support the robustness of imbalance-aware recall gains across random holdout splits.",
        "- Positive Macro-F1 intervals support split-stable gains for the tested IoTID20 holdout design, but the gains are modest and should be presented alongside the larger recall gains.",
        "- IoTID20 remains an independent holdout replication because the local mirror lacks an official split.",
    ]
    return model_summary, delta_summary, signflip_summary, "\n".join(lines) + "\n"


def write_audit(args: argparse.Namespace) -> None:
    text = f"""# IoTID20 Repeated Split Experiment Design

## Route

SCI machine-learning validation experiment.

## Matrix

| Run group | Varying factor | Fixed factors | Expected outcome |
|---|---|---|---|
| IoTID20 repeated split | Stratified split seed, {args.n_splits} levels | cleaning, metrics, model parameters, feature space | Estimate whether the single 70/30 result is split-stable |

## Models

- Flat LightGBM baseline.
- Class-weighted LightGBM.
- Top-10 mutual-information flat LightGBM.
- Top-10 mutual-information class-weighted LightGBM.
- Class-weighted XGBoost.
- Validation-selected LightGBM/XGBoost probability ensemble.

## Metrics

Primary: Macro-F1, minority-class recall, macro PR-AUC.

Secondary: accuracy, balanced accuracy, worst-class recall, train time, inference time.

## Uncertainty

The script reports per-split metrics and split-level nonparametric bootstrap intervals for paired deltas versus flat LightGBM.
"""
    (DOCS_DIR / "IOTID20_REPEATED_SPLIT_EXPERIMENT_DESIGN.md").write_text(text, encoding="utf-8")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()
    ensure_dirs(args)
    write_audit(args)
    df = iot.load_iotid(args.max_rows)
    all_rows: list[pd.DataFrame] = []
    all_classwise: list[pd.DataFrame] = []
    for offset in range(args.n_splits):
        seed = args.seed_start + offset
        rows, classwise = run_single_split(df, seed, args)
        all_rows.append(rows)
        all_classwise.append(classwise)
        pd.concat(all_rows, ignore_index=True).to_csv(OUT_DIR / "experiment_results_partial.csv", index=False)
    results = pd.concat(all_rows, ignore_index=True)
    classwise = pd.concat(all_classwise, ignore_index=True)
    results.to_csv(OUT_DIR / "experiment_results.csv", index=False)
    classwise.to_csv(OUT_DIR / "classwise_metrics.csv", index=False)
    model_summary, delta_summary, signflip_summary, ledger = summarize(results, args)
    model_summary.to_csv(OUT_DIR / "model_summary.csv", index=False)
    delta_summary.to_csv(OUT_DIR / "paired_delta_bootstrap_summary.csv", index=False)
    signflip_summary.to_csv(OUT_DIR / "paired_delta_signflip_summary.csv", index=False)
    (OUT_DIR / "RESULT_LEDGER.md").write_text(ledger, encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
