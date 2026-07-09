from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import run_ciciot_quick_experiments as ciciot
import run_iotid20_quick_experiments as iotid


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "mlp_baselines"


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_mlp() -> MLPClassifier:
    return MLPClassifier(
        hidden_layer_sizes=(128,),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=8192,
        learning_rate_init=1e-3,
        max_iter=45,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=5,
        random_state=ciciot.RANDOM_STATE,
        verbose=False,
    )


def run_ciciot_mlp(train_n: int, test_n: int) -> tuple[dict[str, object], pd.DataFrame]:
    train, test = ciciot.load_data(train_n, test_n)
    features = ciciot.feature_cols(train)
    y_train, y_test, enc = ciciot.encode_target(train["Label"], test["Label"])
    X_train = train[features].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(dtype=np.float32)
    X_test = test[features].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(dtype=np.float32)
    model = make_pipeline(StandardScaler(), make_mlp())
    start = time.perf_counter()
    model.fit(X_train, y_train)
    train_seconds = time.perf_counter() - start
    start = time.perf_counter()
    y_pred = model.predict(X_test)
    proba = model.predict_proba(X_test)
    inference_seconds = time.perf_counter() - start
    labels = list(enc.classes_)
    metrics = ciciot.metric_dict(
        y_test,
        np.asarray(y_pred).reshape(-1).astype(int),
        np.asarray(proba),
        labels,
        train_seconds=train_seconds,
        inference_seconds=inference_seconds,
        n_features=len(features),
        model_kb=ciciot.model_size_kb(model),
    )
    metrics.update(
        {
            "dataset": "CICIoT2023 public subsample",
            "scope": f"stratified quick screen, train_n={train_n}, test_n={test_n}",
            "run_id": "ciciot_fine_mlp_quick",
            "task": "fine",
            "target_col": "Label",
            "model_name": "mlp",
            "imbalance": "none",
            "feature_strategy": "all",
            "top_k": np.nan,
            "train_rows": len(train),
            "test_rows": len(test),
            "feature_names": json.dumps(features),
        }
    )
    classwise = ciciot.classwise_frame(y_test, np.asarray(y_pred).reshape(-1).astype(int), labels, metrics["run_id"])
    classwise["dataset"] = metrics["dataset"]
    return metrics, classwise


def run_iotid_mlp(max_rows: int | None) -> tuple[dict[str, object], pd.DataFrame]:
    df = iotid.load_iotid(max_rows)
    from sklearn.model_selection import train_test_split

    train, test = train_test_split(
        df,
        test_size=0.3,
        random_state=iotid.RANDOM_STATE,
        stratify=df["Label"],
    )
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    features = [c for c in train.columns if c not in ["Label", "binary_label"]]
    y_train, y_test, enc = iotid.encode(train["Label"], test["Label"])
    X_train = train[features].astype("float32").to_numpy()
    X_test = test[features].astype("float32").to_numpy()
    model = make_pipeline(StandardScaler(), make_mlp())
    start = time.perf_counter()
    model.fit(X_train, y_train)
    train_seconds = time.perf_counter() - start
    start = time.perf_counter()
    y_pred = model.predict(X_test)
    proba = model.predict_proba(X_test)
    inference_seconds = time.perf_counter() - start
    labels = list(enc.classes_)
    metrics = iotid.metric_dict(
        y_test,
        np.asarray(y_pred).reshape(-1).astype(int),
        np.asarray(proba),
        labels,
        train_seconds=train_seconds,
        inference_seconds=inference_seconds,
        n_features=len(features),
        model_kb=iotid.model_size_kb(model),
    )
    metrics.update(
        {
            "dataset": "IoTID20 public mirror",
            "scope": "stratified 70/30 quick screen" if max_rows is None else f"stratified quick screen, max_rows={max_rows}",
            "run_id": "iotid_fine_mlp_quick",
            "task": "fine",
            "target_col": "Label",
            "model_name": "mlp",
            "imbalance": "none",
            "feature_strategy": "all",
            "top_k": np.nan,
            "train_rows": len(train),
            "test_rows": len(test),
            "feature_names": json.dumps(features),
        }
    )
    classwise = iotid.classwise_frame(y_test, np.asarray(y_pred).reshape(-1).astype(int), labels, metrics["run_id"])
    classwise["dataset"] = metrics["dataset"]
    return metrics, classwise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run supplementary MLP baselines for model family screening.")
    parser.add_argument("--ciciot-train-n", type=int, default=220_000)
    parser.add_argument("--ciciot-test-n", type=int, default=80_000)
    parser.add_argument("--iotid-max-rows", type=int, default=None)
    parser.add_argument("--dataset", choices=["all", "ciciot", "iotid20"], default="all")
    return parser.parse_args()


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()
    ensure_dirs()
    rows: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []
    if args.dataset in {"all", "ciciot"}:
        print("Running CICIoT2023 public subsample MLP quick baseline...")
        metrics, cw = run_ciciot_mlp(args.ciciot_train_n, args.ciciot_test_n)
        rows.append(metrics)
        classwise.append(cw)
    if args.dataset in {"all", "iotid20"}:
        print("Running IoTID20 MLP quick baseline...")
        metrics, cw = run_iotid_mlp(args.iotid_max_rows)
        rows.append(metrics)
        classwise.append(cw)
    pd.DataFrame(rows).to_csv(OUT_DIR / "experiment_results.csv", index=False)
    if classwise:
        pd.concat(classwise, ignore_index=True).to_csv(OUT_DIR / "classwise_metrics.csv", index=False)
    print(f"Wrote {OUT_DIR / 'experiment_results.csv'}")


if __name__ == "__main__":
    main()
