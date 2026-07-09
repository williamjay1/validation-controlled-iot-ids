from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.append(str(Path(__file__).resolve().parent))
from run_ciciot_quick_experiments import (  # noqa: E402
    RANDOM_STATE,
    RunConfig,
    apply_imbalance,
    class_sample_weight,
    classwise_frame,
    make_model,
    metric_dict,
    model_size_kb,
    predict_proba_safe,
    rank_features,
)


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "iotid20_hf_preprocessed" / "Preprocessed_file.csv"
OUT_DIR = ROOT / "results" / "iotid20_quick"
DOCS_DIR = ROOT / "docs"


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def load_iotid(max_rows: int | None) -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
    if max_rows and max_rows < len(df):
        parts = []
        counts = df["Label"].value_counts()
        for label, group in df.groupby("Label", sort=False):
            take = max(1, int(round(max_rows * counts[label] / len(df))))
            parts.append(group.sample(n=min(take, len(group)), random_state=RANDOM_STATE))
        df = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=RANDOM_STATE)
        if len(df) > max_rows:
            df = df.sample(n=max_rows, random_state=RANDOM_STATE)
        df = df.reset_index(drop=True)
    df["binary_label"] = (df["Label"].astype(str) != "Normal").astype(int)
    return df


def encode(y_train: pd.Series, y_test: pd.Series) -> tuple[np.ndarray, np.ndarray, LabelEncoder]:
    enc = LabelEncoder()
    y_tr = enc.fit_transform(y_train.astype(str))
    y_te = enc.transform(y_test.astype(str))
    return y_tr, y_te, enc


def select_features(
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: pd.DataFrame,
    strategy: str,
    top_k: int | None,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    if strategy == "all":
        cols = list(X_train.columns)
    else:
        cols = rank_features(X_train, y_train, strategy, max_rows=60000)[: top_k or X_train.shape[1]]
    return X_train[cols], X_test[cols], cols


def run_one(train: pd.DataFrame, test: pd.DataFrame, config: RunConfig) -> tuple[dict[str, object], pd.DataFrame]:
    features = [c for c in train.columns if c not in ["Label", "binary_label"]]
    X_train_all = train[features].astype("float32")
    X_test_all = test[features].astype("float32")
    y_train, y_test, enc = encode(train[config.target_col], test[config.target_col])
    X_train_df, X_test_df, cols = select_features(X_train_all, y_train, X_test_all, config.feature_strategy, config.top_k)
    X_train_np = X_train_df.to_numpy(dtype=np.float32)
    X_test_np = X_test_df.to_numpy(dtype=np.float32)
    X_fit, y_fit, sample_weight, sampling_note = apply_imbalance(X_train_np, y_train, config.task, config.imbalance)
    model = make_model(config.model_name, len(enc.classes_))
    start = time.perf_counter()
    if config.imbalance == "class_weight" and sample_weight is None:
        sample_weight = class_sample_weight(y_fit)
    if sample_weight is not None:
        model.fit(X_fit, y_fit, sample_weight=sample_weight)
    else:
        model.fit(X_fit, y_fit)
    train_seconds = time.perf_counter() - start
    start = time.perf_counter()
    y_pred = np.asarray(model.predict(X_test_np)).reshape(-1).astype(int)
    proba = predict_proba_safe(model, X_test_np, len(enc.classes_))
    inference_seconds = time.perf_counter() - start
    labels = list(enc.classes_)
    metrics = metric_dict(
        y_test,
        y_pred,
        proba,
        labels,
        train_seconds=train_seconds,
        inference_seconds=inference_seconds,
        n_features=len(cols),
        model_kb=model_size_kb(model),
    )
    metrics.update(asdict(config))
    metrics["sampling_note"] = sampling_note
    metrics["train_rows"] = len(train)
    metrics["fit_rows"] = len(y_fit)
    metrics["test_rows"] = len(test)
    metrics["feature_names"] = json.dumps(cols)
    return metrics, classwise_frame(y_test, y_pred, labels, config.run_id)


def configs(include_model_zoo: bool) -> list[RunConfig]:
    out = [
        RunConfig("iotid_binary_lgbm_weighted", "binary", "binary_label", "lgbm", imbalance="class_weight"),
        RunConfig("iotid_fine_lgbm_full", "fine", "Label", "lgbm"),
        RunConfig("iotid_fine_lgbm_weighted", "fine", "Label", "lgbm", imbalance="class_weight"),
        RunConfig("iotid_fine_lgbm_random_over", "fine", "Label", "lgbm", imbalance="random_over"),
        RunConfig("iotid_fine_lgbm_smote", "fine", "Label", "lgbm", imbalance="smote"),
        RunConfig("iotid_fine_lgbm_borderline_smote", "fine", "Label", "lgbm", imbalance="borderline_smote"),
        RunConfig("iotid_fine_lgbm_mi_top10_weighted", "fine", "Label", "lgbm", imbalance="class_weight", feature_strategy="mi", top_k=10),
        RunConfig("iotid_fine_lgbm_importance_top10_weighted", "fine", "Label", "lgbm", imbalance="class_weight", feature_strategy="importance", top_k=10),
    ]
    if include_model_zoo:
        out.extend(
            [
                RunConfig("iotid_fine_rf_weighted", "fine", "Label", "rf", imbalance="class_weight"),
                RunConfig("iotid_fine_xgb_weighted", "fine", "Label", "xgb", imbalance="class_weight"),
                RunConfig("iotid_fine_catboost_weighted", "fine", "Label", "catboost", imbalance="class_weight"),
            ]
        )
    return out


def write_docs(df: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> None:
    df["Label"].value_counts().to_csv(OUT_DIR / "iotid20_label_distribution.csv")
    text = f"""# IoTID20 Quick Experiment Note

## Role

IoTID20 is used as an independent public IoT IDS replication dataset. It is not treated as a direct external test for CICIoT2023 because the feature schemas differ.

## Data

- Full usable rows after NA/inf removal: {len(df):,}
- Train rows: {len(train):,}
- Test rows: {len(test):,}
- Features: {len([c for c in df.columns if c not in ['Label', 'binary_label']])}
- Labels: {df['Label'].nunique()}

## Validation

The current mirror does not include an official split in the downloaded file, so this quick run uses a stratified 70/30 holdout with a fixed seed. Manuscript claims from this dataset must describe it as independent replication, not as official external validation.
"""
    (DOCS_DIR / "IOTID20_VALIDATION_NOTE.md").write_text(text, encoding="utf-8")


def summarize(results: pd.DataFrame) -> str:
    cols = [
        "run_id",
        "model_name",
        "imbalance",
        "feature_strategy",
        "top_k",
        "n_features",
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
    use_cols = [c for c in cols if c in results.columns]
    fine = results[results["task"] == "fine"].sort_values(["f1_macro", "minority_recall_mean"], ascending=False)
    lines = ["# IoTID20 Quick Result Ledger", "", fine[use_cols].to_markdown(index=False), ""]
    if "iotid_fine_lgbm_full" in set(results["run_id"]):
        base = results.loc[results["run_id"] == "iotid_fine_lgbm_full"].iloc[0]
        lines.append("## Comparisons Against IoTID20 Flat LightGBM")
        lines.append("")
        for _, row in fine.iterrows():
            if row["run_id"] == "iotid_fine_lgbm_full":
                continue
            lines.append(
                f"- `{row['run_id']}`: Macro-F1 delta {row['f1_macro'] - base['f1_macro']:+.4f}, "
                f"minority-recall delta {row['minority_recall_mean'] - base['minority_recall_mean']:+.4f}, "
                f"features {int(row['n_features'])}."
            )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run quick IoTID20 replication experiments.")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--include-model-zoo", action="store_true")
    return parser.parse_args()


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    ensure_dirs()
    args = parse_args()
    df = load_iotid(args.max_rows)
    train, test = train_test_split(df, test_size=0.3, stratify=df["Label"], random_state=RANDOM_STATE)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    write_docs(df, train, test)
    rows = []
    classwise = []
    for config in configs(args.include_model_zoo):
        print(f"Running {config.run_id}...")
        try:
            metrics, cw = run_one(train, test, config)
            rows.append(metrics)
            classwise.append(cw)
            pd.DataFrame(rows).to_csv(OUT_DIR / "experiment_results_partial.csv", index=False)
        except Exception as exc:
            error_row = asdict(config)
            error_row["error"] = repr(exc)
            rows.append(error_row)
            print(f"ERROR {config.run_id}: {exc!r}")
    results = pd.DataFrame(rows)
    results.to_csv(OUT_DIR / "experiment_results.csv", index=False)
    if classwise:
        pd.concat(classwise, ignore_index=True).to_csv(OUT_DIR / "classwise_metrics.csv", index=False)
    (OUT_DIR / "RESULT_LEDGER.md").write_text(summarize(results), encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
