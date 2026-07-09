from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

sys.path.append(str(Path(__file__).resolve().parent))
from run_ciciot_quick_experiments import (  # noqa: E402
    RANDOM_STATE,
    class_sample_weight,
    classwise_frame,
    make_model,
    metric_dict,
    model_size_kb,
    predict_proba_safe,
    rank_features,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "raw" / "n_baiot_uci" / "extracted"
OUT_DIR = ROOT / "results" / "nbaiot_unseen_device"
DOCS_DIR = ROOT / "docs"


@dataclass
class NbRunConfig:
    run_id: str
    task: str
    target_col: str
    model_name: str
    feature_strategy: str = "all"
    top_k: int | None = None
    class_weight: bool = True


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def manifest() -> pd.DataFrame:
    rows = []
    for p in DATA_ROOT.rglob("*.csv"):
        if p.name == "demonstrate_structure.csv":
            continue
        rel = p.relative_to(DATA_ROOT).parts
        if len(rel) < 2:
            continue
        device = rel[0]
        if p.name == "benign_traffic.csv":
            family = "benign"
            attack = "benign"
        else:
            family = rel[1].replace("_attacks", "") if len(rel) > 2 else "unknown"
            attack = p.stem
        rows.append({"device": device, "family": family, "attack": attack, "path": str(p)})
    return pd.DataFrame(rows).sort_values(["device", "family", "attack"]).reset_index(drop=True)


def read_sample(path: str, n_per_file: int | None) -> pd.DataFrame:
    if n_per_file is None:
        return pd.read_csv(path)
    chunks = []
    remaining = n_per_file
    for chunk in pd.read_csv(path, chunksize=max(remaining, 10000)):
        take = min(remaining, len(chunk))
        chunks.append(chunk.head(take))
        remaining -= take
        if remaining <= 0:
            break
    return pd.concat(chunks, ignore_index=True)


def load_dataset(n_per_file: int | None) -> pd.DataFrame:
    rows = []
    man = manifest()
    for _, item in man.iterrows():
        df = read_sample(item["path"], n_per_file)
        df["device"] = item["device"]
        df["family"] = item["family"]
        df["attack"] = item["attack"]
        df["binary_label"] = int(item["attack"] != "benign")
        rows.append(df)
    out = pd.concat(rows, ignore_index=True)
    out = out.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
    return out.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)


def feature_columns(df: pd.DataFrame) -> list[str]:
    meta = {"device", "family", "attack", "binary_label"}
    return [c for c in df.columns if c not in meta and pd.api.types.is_numeric_dtype(df[c])]


def encode(train_y: pd.Series, test_y: pd.Series) -> tuple[np.ndarray, np.ndarray, LabelEncoder]:
    enc = LabelEncoder()
    train = enc.fit_transform(train_y.astype(str))
    known = set(enc.classes_)
    if not set(test_y.astype(str)).issubset(known):
        missing = sorted(set(test_y.astype(str)) - known)
        raise ValueError(f"Test labels missing from training labels: {missing}")
    test = enc.transform(test_y.astype(str))
    return train, test, enc


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
        cols = rank_features(X_train, y_train, strategy, max_rows=80000)[: top_k or X_train.shape[1]]
    return X_train[cols], X_test[cols], cols


def run_fold(df: pd.DataFrame, holdout_device: str, config: NbRunConfig) -> tuple[dict[str, object], pd.DataFrame]:
    train = df[df["device"] != holdout_device].copy()
    test = df[df["device"] == holdout_device].copy()
    features = feature_columns(df)
    X_train_all = train[features].astype("float32")
    X_test_all = test[features].astype("float32")
    y_train, y_test, enc = encode(train[config.target_col], test[config.target_col])
    X_train_df, X_test_df, cols = select_features(X_train_all, y_train, X_test_all, config.feature_strategy, config.top_k)
    X_train_np = X_train_df.to_numpy(dtype=np.float32)
    X_test_np = X_test_df.to_numpy(dtype=np.float32)
    model = make_model(config.model_name, len(enc.classes_))
    sample_weight = class_sample_weight(y_train) if config.class_weight else None
    start = time.perf_counter()
    if sample_weight is not None:
        model.fit(X_train_np, y_train, sample_weight=sample_weight)
    else:
        model.fit(X_train_np, y_train)
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
    metrics["holdout_device"] = holdout_device
    metrics["train_rows"] = len(train)
    metrics["test_rows"] = len(test)
    metrics["feature_names"] = json.dumps(cols)
    cw = classwise_frame(y_test, y_pred, labels, f"{config.run_id}__{holdout_device}")
    present = cw[cw["support"] > 0]
    metrics["present_class_count"] = int(len(present))
    metrics["f1_macro_present_support"] = float(present["f1"].mean())
    metrics["mean_present_class_recall"] = float(present["recall"].mean())
    metrics["min_present_class_recall"] = float(present["recall"].min())
    cw["holdout_device"] = holdout_device
    cw["task"] = config.task
    return metrics, cw


def configs(include_model_zoo: bool) -> list[NbRunConfig]:
    out = [
        NbRunConfig("nb_binary_lgbm_weighted", "binary", "binary_label", "lgbm"),
        NbRunConfig("nb_family_lgbm_weighted", "family", "family", "lgbm"),
        NbRunConfig("nb_attack_lgbm_weighted", "attack", "attack", "lgbm"),
        NbRunConfig("nb_attack_lgbm_mi_top40_weighted", "attack", "attack", "lgbm", feature_strategy="mi", top_k=40),
        NbRunConfig("nb_attack_lgbm_importance_top40_weighted", "attack", "attack", "lgbm", feature_strategy="importance", top_k=40),
    ]
    if include_model_zoo:
        out.extend(
            [
                NbRunConfig("nb_attack_rf_weighted", "attack", "attack", "rf"),
                NbRunConfig("nb_attack_xgb_weighted", "attack", "attack", "xgb"),
                NbRunConfig("nb_attack_catboost_weighted", "attack", "attack", "catboost"),
            ]
        )
    return out


def write_docs(df: pd.DataFrame, n_per_file: int | None) -> None:
    device_counts = df.groupby("device").size().sort_values(ascending=False)
    attack_counts = df.groupby(["family", "attack"]).size().sort_values(ascending=False)
    device_counts.to_csv(OUT_DIR / "nbaiot_device_counts.csv")
    attack_counts.to_csv(OUT_DIR / "nbaiot_attack_counts.csv")
    text = f"""# N-BaIoT Unseen Device Validation Design

## Role

N-BaIoT is used for the independent unseen-device validation route. The validation simulates deployment on an IoT device absent from training.

## Data

- Rows used in this run: {len(df):,}
- Per-file row cap: {n_per_file}
- Devices: {df['device'].nunique()}
- Attack labels: {df['attack'].nunique()}
- Numeric features: {len(feature_columns(df))}

## Split

Leave-one-device-out. For each fold, one device is held out entirely for testing and all other devices form the training set.

## Claim Control

This is stronger than a random split because device identity is held out. If per-file caps are used, results are quick-stage evidence and should be confirmed with a larger cap before final manuscript claims.
"""
    (DOCS_DIR / "NBAIOT_UNSEEN_DEVICE_DESIGN.md").write_text(text, encoding="utf-8")


def summarize(results: pd.DataFrame) -> str:
    cols = [
        "run_id",
        "task",
        "model_name",
        "feature_strategy",
        "top_k",
        "holdout_device",
        "n_features",
        "accuracy",
        "balanced_accuracy",
        "f1_macro",
        "minority_recall_mean",
        "worst_class_recall",
        "worst_class_label",
        "pr_auc_macro",
        "roc_auc_ovr_macro",
        "train_seconds",
        "inference_ms_per_1000",
    ]
    use_cols = [c for c in cols if c in results.columns]
    lines = ["# N-BaIoT Leave-One-Device-Out Result Ledger", ""]
    summary = (
        results.groupby(["run_id", "task", "model_name", "feature_strategy", "top_k"], dropna=False)
        .agg(
            folds=("holdout_device", "nunique"),
            mean_macro_f1=("f1_macro", "mean"),
            std_macro_f1=("f1_macro", "std"),
            mean_present_macro_f1=("f1_macro_present_support", "mean"),
            min_present_macro_f1=("f1_macro_present_support", "min"),
            mean_balanced_accuracy=("balanced_accuracy", "mean"),
            mean_minority_recall=("minority_recall_mean", "mean"),
            mean_worst_class_recall=("worst_class_recall", "mean"),
            min_present_class_recall=("min_present_class_recall", "min"),
            mean_pr_auc_macro=("pr_auc_macro", "mean"),
            mean_train_seconds=("train_seconds", "mean"),
            mean_inference_ms_per_1000=("inference_ms_per_1000", "mean"),
        )
        .reset_index()
        .sort_values(["task", "mean_macro_f1"], ascending=[True, False])
    )
    lines.append("## Fold-Averaged Results")
    lines.append("")
    lines.append(summary.to_markdown(index=False))
    lines.append("")
    lines.append("## Per-Fold Results")
    lines.append("")
    lines.append(results[use_cols].sort_values(["task", "run_id", "holdout_device"]).to_markdown(index=False))
    lines.append("")
    lines.append("## Claim Control")
    lines.append("")
    lines.append("- This validation can support an unseen-device generalization claim only if the fold-average and weakest-device results are acceptable.")
    lines.append("- Any high mean with a very weak held-out device must be written as heterogeneous generalization, not universal robustness.")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run N-BaIoT leave-one-device-out experiments.")
    parser.add_argument("--n-per-file", type=int, default=5000)
    parser.add_argument("--include-model-zoo", action="store_true")
    parser.add_argument("--tasks", nargs="*", default=None, choices=["binary", "family", "attack"])
    parser.add_argument("--run-id", action="append", dest="run_ids")
    parser.add_argument("--out-dir", default="nbaiot_unseen_device")
    return parser.parse_args()


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()
    global OUT_DIR
    OUT_DIR = ROOT / "results" / args.out_dir
    ensure_dirs()
    df = load_dataset(args.n_per_file)
    write_docs(df, args.n_per_file)
    devices = sorted(df["device"].unique())
    rows = []
    classwise = []
    selected_configs = configs(args.include_model_zoo)
    if args.tasks:
        selected_configs = [c for c in selected_configs if c.task in set(args.tasks)]
    if args.run_ids:
        selected_configs = [c for c in selected_configs if c.run_id in set(args.run_ids)]
    for config in selected_configs:
        for device in devices:
            print(f"Running {config.run_id} holdout={device}...")
            try:
                metrics, cw = run_fold(df, device, config)
                rows.append(metrics)
                classwise.append(cw)
                pd.DataFrame(rows).to_csv(OUT_DIR / "experiment_results_partial.csv", index=False)
            except Exception as exc:
                row = asdict(config)
                row["holdout_device"] = device
                row["error"] = repr(exc)
                rows.append(row)
                print(f"ERROR {config.run_id} {device}: {exc!r}")
    results = pd.DataFrame(rows)
    results.to_csv(OUT_DIR / "experiment_results.csv", index=False)
    if classwise:
        pd.concat(classwise, ignore_index=True).to_csv(OUT_DIR / "classwise_metrics.csv", index=False)
    (OUT_DIR / "RESULT_LEDGER.md").write_text(summarize(results), encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
