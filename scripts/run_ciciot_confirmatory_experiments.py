from __future__ import annotations

import argparse
import warnings
from dataclasses import asdict
from pathlib import Path

import pandas as pd

import run_ciciot_quick_experiments as exp


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_IDS = [
    "fine_lgbm_full",
    "fine_lgbm_random_over",
    "fine_lgbm_borderline_smote",
    "fine_lgbm_smote",
    "fine_lgbm_smoteenn",
    "fine_xgb_full_weighted",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run selected CICIoT2023 confirmatory experiments.")
    parser.add_argument("--train-n", type=int, default=None)
    parser.add_argument("--test-n", type=int, default=None)
    parser.add_argument("--out-dir", default="ciciot_confirmatory")
    parser.add_argument("--run-id", action="append", dest="run_ids")
    parser.add_argument("--include-hierarchical", action="store_true")
    return parser.parse_args()


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    args = parse_args()

    exp.OUT_DIR = ROOT / "results" / args.out_dir
    exp.FIG_DIR = ROOT / "figures" / args.out_dir
    exp.ensure_dirs()

    train, test = exp.load_data(args.train_n, args.test_n)
    exp.write_design_docs(train, test, args.train_n, args.test_n)

    all_configs = {cfg.run_id: cfg for cfg in exp.experiment_configs(include_model_zoo=True)}
    run_ids = args.run_ids or DEFAULT_RUN_IDS
    configs = [all_configs[run_id] for run_id in run_ids]

    results: list[dict[str, object]] = []
    classwise: list[pd.DataFrame] = []
    rank_cache: dict[tuple[str, str], list[str]] = {}
    for config in configs:
        print(f"Running {config.run_id}...")
        try:
            metrics, cw = exp.fit_predict_run(train, test, config, rank_cache)
            results.append(metrics)
            classwise.append(cw)
            pd.DataFrame(results).to_csv(exp.OUT_DIR / "experiment_results_partial.csv", index=False)
        except Exception as exc:
            error_row = asdict(config)
            error_row["error"] = repr(exc)
            results.append(error_row)
            print(f"ERROR {config.run_id}: {exc!r}")

    if args.include_hierarchical:
        print("Running fine_hier_lgbm_top20_weighted...")
        try:
            metrics, cw = exp.fit_predict_hierarchical(train, test, top_k=20)
            results.append(metrics)
            classwise.append(cw)
        except Exception as exc:
            error_row = asdict(
                exp.RunConfig(
                    "fine_hier_lgbm_top20_weighted",
                    "fine",
                    "Label",
                    "lgbm",
                    imbalance="class_weight",
                    feature_strategy="importance",
                    top_k=20,
                    hierarchical=True,
                )
            )
            error_row["error"] = repr(exc)
            results.append(error_row)
            print(f"ERROR hierarchical: {exc!r}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(exp.OUT_DIR / "experiment_results.csv", index=False)
    if classwise:
        pd.concat(classwise, ignore_index=True).to_csv(exp.OUT_DIR / "classwise_metrics.csv", index=False)
    summary = exp.summarize_results(results_df).replace("Quick Result Ledger", "Confirmatory Result Ledger")
    (exp.OUT_DIR / "RESULT_LEDGER.md").write_text(summary, encoding="utf-8")
    print(f"Wrote {exp.OUT_DIR / 'experiment_results.csv'}")
    print(f"Wrote {exp.OUT_DIR / 'RESULT_LEDGER.md'}")


if __name__ == "__main__":
    main()
