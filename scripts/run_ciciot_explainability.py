from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap

import run_ciciot_quick_experiments as exp


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "explainability"
FIG_DIR = ROOT / "figures" / "paper_figures"
TABLE_DIR = ROOT / "results" / "paper_tables"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute CICIoT2023 LightGBM component explainability.")
    parser.add_argument("--train-n", type=int, default=None)
    parser.add_argument("--test-n", type=int, default=None)
    parser.add_argument("--shap-sample", type=int, default=3000)
    return parser.parse_args()


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def stratified_test_sample(test: pd.DataFrame, n: int) -> pd.DataFrame:
    if n >= len(test):
        return test.copy()
    parts = []
    for _, group in test.groupby("Label", sort=False):
        take = max(1, int(round(n * len(group) / len(test))))
        take = min(take, len(group))
        parts.append(group.sample(n=take, random_state=exp.RANDOM_STATE))
    out = pd.concat(parts).sample(frac=1, random_state=exp.RANDOM_STATE)
    if len(out) > n:
        out = out.sample(n=n, random_state=exp.RANDOM_STATE)
    return out.reset_index(drop=True)


def mean_abs_shap(shap_values: object, n_features: int) -> np.ndarray:
    values = np.asarray(shap_values)
    if isinstance(shap_values, list):
        values = np.stack([np.asarray(v) for v in shap_values], axis=0)
    if values.ndim == 3:
        if values.shape[1] == n_features:
            return np.abs(values).mean(axis=(0, 2))
        return np.abs(values).mean(axis=(0, 1))
    if values.ndim == 2:
        return np.abs(values).mean(axis=0)
    raise ValueError(f"Unexpected SHAP shape: {values.shape}")


def save_bar(df: pd.DataFrame) -> None:
    top = df.head(20).copy()
    plt.figure(figsize=(8, 7))
    sns.barplot(data=top, y="feature", x="mean_abs_shap", color="#4C78A8")
    plt.xlabel("Mean absolute SHAP value")
    plt.ylabel("")
    plt.title("Top CICIoT2023 features in the LightGBM ensemble component")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "figure6_ciciot_shap_top_features.png", dpi=300, bbox_inches="tight")
    plt.savefig(FIG_DIR / "figure6_ciciot_shap_top_features.tiff", dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    ensure_dirs()
    train, test = exp.load_data(args.train_n, args.test_n)
    features = exp.feature_cols(train)
    y_train, _, encoder = exp.encode_target(train["Label"], test["Label"])
    X_train = train[features].astype("float32")
    X_fit, y_fit, sample_weight, sampling_note = exp.apply_imbalance(
        X_train.to_numpy(dtype=np.float32),
        y_train,
        "fine",
        "borderline_smote",
    )
    model = exp.make_model("lgbm", len(encoder.classes_))
    print("Fitting Borderline-SMOTE LightGBM component for explainability...")
    model.fit(X_fit, y_fit, sample_weight=sample_weight)

    sample = stratified_test_sample(test, args.shap_sample)
    X_sample = sample[features].astype("float32")
    print(f"Computing SHAP values for {len(X_sample)} test rows...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    shap_importance = mean_abs_shap(shap_values, len(features))
    gain_importance = np.asarray(model.feature_importances_, dtype=float)

    out = pd.DataFrame(
        {
            "feature": features,
            "mean_abs_shap": shap_importance,
            "lightgbm_gain_importance": gain_importance,
        }
    ).sort_values("mean_abs_shap", ascending=False)
    out["rank"] = np.arange(1, len(out) + 1)
    out["sampling_note"] = sampling_note
    out["shap_sample_rows"] = len(X_sample)
    out.to_csv(OUT_DIR / "ciciot_lgbm_component_shap_importance.csv", index=False)
    out.head(30).to_csv(TABLE_DIR / "table5_ciciot_shap_top_features.csv", index=False)
    save_bar(out)
    print(f"Wrote {OUT_DIR / 'ciciot_lgbm_component_shap_importance.csv'}")
    print(f"Wrote {FIG_DIR / 'figure6_ciciot_shap_top_features.png'}")


if __name__ == "__main__":
    args = parse_args()
    main()
