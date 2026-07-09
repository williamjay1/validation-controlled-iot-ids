from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELEASE_ROOT = PROJECT_ROOT / "release_packages"
REPO_NAME = "validation-controlled-iot-ids"
VERSION = "1.0.2"
RELEASE_DATE = date(2026, 7, 9)
TARGET = RELEASE_ROOT / f"{REPO_NAME}_v{VERSION}_github_ready"
ZIP_PATH = RELEASE_ROOT / f"{REPO_NAME}_v{VERSION}_github_ready.zip"
MANUSCRIPT_PACKAGE = (
    PROJECT_ROOT
    / "submission_package"
    / "scientific_reports_20260709_sr_balanced_candidate_v3"
)


TEXT_FILES = {
    "README.md": """# Validation controlled imbalance aware learning for IoT intrusion detection

This repository is the reproducibility package for the manuscript:

**Validation controlled imbalance aware learning for fine grained IoT intrusion detection**

Authors: Junjie Zhang and Siyu Wang.

The package contains the executable scripts, pinned Python requirements, generated result tables, figure assets, manuscript source files, and checksum records used for the Scientific Reports submission candidate.

## What is included

- `scripts/`: data download, experiment, uncertainty, explainability, figure generation, and manuscript package scripts.
- `results/`: generated CSV and Markdown result ledgers used in the manuscript.
- `figures/`: publication figure files used by the manuscript.
- `manuscript/scientific_reports_latex_v3/`: LaTeX source, generated PDF, figures, supplementary tables, cover letter, and submission checklist for the current candidate.
- `docs/`: provenance, claim strength, numerical consistency, reference DOI, and submission readiness records.
- `data/DATA_SOURCES.md`: public data source and download notes.

Raw public datasets are **not** stored in this repository. They are downloaded from their public sources by `scripts/download_datasets.py`.

## Environment

Create and activate a Python environment, then install the pinned requirements.

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install --upgrade pip
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

The manuscript experiments were run on Windows 11 with an AMD Ryzen 9 8945HS processor and 31.3 GB RAM. The code should also run on Linux or macOS with equivalent Python packages, but paths in the manuscript audit were generated on Windows.

## Data download

Quick public data download:

```powershell
.\\.venv\\Scripts\\python.exe scripts\\download_datasets.py --quick
```

N BaIoT download and extraction:

```powershell
.\\.venv\\Scripts\\python.exe scripts\\download_datasets.py --quick --include-nbaiot --extract-nbaiot
```

The raw data files are written under `data/raw/`, which is ignored by git.

## Main reproduction commands

```powershell
.\\.venv\\Scripts\\python.exe scripts\\run_ciciot_recall_aware_ensemble.py --out-dir ciciot_ensemble_full
.\\.venv\\Scripts\\python.exe scripts\\run_iotid20_repeated_split_uncertainty.py --out-dir iotid20_repeated_split
.\\.venv\\Scripts\\python.exe scripts\\run_nbaiot_unseen_device.py --n-per-file 20000 --out-dir nbaiot_unseen_device_20k --run-id nb_binary_lgbm_weighted --run-id nb_family_lgbm_weighted --run-id nb_attack_lgbm_weighted
.\\.venv\\Scripts\\python.exe scripts\\run_ciciot_bootstrap_uncertainty.py --n-bootstrap 2000 --out-dir statistical_uncertainty
.\\.venv\\Scripts\\python.exe scripts\\run_ciciot_explainability.py --shap-sample 3000
.\\.venv\\Scripts\\python.exe scripts\\make_result_figures.py
.\\.venv\\Scripts\\python.exe scripts\\build_scientific_reports_balanced_package.py
```

Additional baseline and sensitivity scripts are retained in `scripts/` and their generated outputs are under `results/`.

## Primary manuscript results

- CICIoT2023 public subsample ensemble Macro-F1: 0.8828.
- CICIoT2023 public subsample ensemble minority recall: 0.5131.
- IoTID20 repeated split top ten weighted LightGBM Macro-F1: 0.6222.
- IoTID20 repeated split top ten weighted LightGBM minority recall: 0.4820.
- N BaIoT capped leave one device out fine grained attack Macro-F1: 0.9435.

See `results/`, `docs/RESULT_LEDGER.md`, and `manuscript/scientific_reports_latex_v3/main.tex` for the exact reporting context and limitations.

## Checksums

File hashes for this repository snapshot are recorded in `checksums_sha256.txt`.

## License

Code is released under the MIT License. Manuscript text, figures, and result tables are released under CC BY 4.0 unless a publisher agreement later requires a different submitted manuscript handling policy.

## Citation

Please cite the archived Zenodo release: https://doi.org/10.5281/zenodo.21273069. The public repository is available at https://github.com/williamjay1/validation-controlled-iot-ids.
""",
    ".gitignore": """.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
data/raw/
tmp/
*.log
*.aux
*.out
*.fls
*.fdb_latexmk
*.synctex.gz
*.bak
desktop.ini
""",
    "LICENSE": """MIT License

Copyright (c) 2026 Junjie Zhang and Siyu Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "DATA_AVAILABILITY.md": """# Data availability

This repository does not redistribute raw third party datasets.

The experiments use the following public sources:

1. CICIoT2023 public subsample mirror:
   https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample
2. Original CICIoT2023 project page:
   https://www.unb.ca/cic/datasets/iotdataset-2023.html
3. IoTID20 preprocessed file mirror:
   https://huggingface.co/datasets/KathiS/IoTID20_Preprocessed_File
4. N BaIoT UCI archive:
   https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot

Use `scripts/download_datasets.py` to retrieve the public files. Downloaded files are written to `data/raw/`, which is ignored by git.
""",
    "REPRODUCIBILITY_CHECKLIST.md": """# Reproducibility checklist

- [x] Executable scripts are included.
- [x] Python requirements are pinned.
- [x] Public data source URLs are listed.
- [x] Raw third party datasets are excluded from the repository.
- [x] Result CSV files used by the manuscript are included.
- [x] Figure files and figure generation code are included.
- [x] Manuscript LaTeX source is included.
- [x] Checksums are generated for the repository snapshot.
- [x] Final GitHub URL is inserted: https://github.com/williamjay1/validation-controlled-iot-ids.
- [x] Final Zenodo DOI is inserted: https://doi.org/10.5281/zenodo.21273069.
- [x] Manuscript Code availability statement is updated with the final DOI before journal portal submission.
""",
    "RELEASE_NOTES_v1.0.0.md": """# Release notes v1.0.0

Initial reproducibility snapshot for the Scientific Reports submission candidate dated 2026-07-09.

The release contains:

- validation controlled CICIoT2023 public subsample ensemble scripts and results;
- IoTID20 repeated split and split bootstrap scripts and results;
- N BaIoT capped leave one device out scripts and results;
- bootstrap uncertainty, SHAP, model family, runtime, and diagnostic outputs;
- Scientific Reports LaTeX manuscript source and supplementary material.

Known limitation: raw datasets are not redistributed. Users must download them from public sources with the provided script.
""",
    "CITATION.cff": """cff-version: 1.2.0
message: "If you use this code or result package, please cite the archived release."
title: "Validation controlled imbalance aware learning for fine grained IoT intrusion detection"
version: "1.0.2"
date-released: "2026-07-09"
type: software
authors:
  - family-names: Zhang
    given-names: Junjie
    affiliation: "Shanghai Academy of Global Governance & Area Studies, Shanghai International Studies University; School of Economics and Finance, Shanghai International Studies University"
    email: "junjiezhang2024@shisu.edu.cn"
  - family-names: Wang
    given-names: Siyu
    affiliation: "Shanghai Academy of Global Governance & Area Studies, Shanghai International Studies University"
    email: "wangsiyu_real@126.com"
keywords:
  - Internet of Things
  - intrusion detection
  - class imbalance
  - rare attack recognition
  - ensemble learning
  - external validation
license: MIT
doi: 10.5281/zenodo.21273069
url: "https://github.com/williamjay1/validation-controlled-iot-ids"
repository-code: "https://github.com/williamjay1/validation-controlled-iot-ids"
""",
    "codemeta.json": json.dumps(
        {
            "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
            "@type": "SoftwareSourceCode",
            "name": "Validation controlled imbalance aware learning for fine grained IoT intrusion detection",
            "version": VERSION,
            "datePublished": RELEASE_DATE.isoformat(),
            "programmingLanguage": "Python",
            "runtimePlatform": "Python 3",
            "license": "https://spdx.org/licenses/MIT",
            "author": [
                {
                    "@type": "Person",
                    "givenName": "Junjie",
                    "familyName": "Zhang",
                    "email": "junjiezhang2024@shisu.edu.cn",
                    "affiliation": "Shanghai International Studies University",
                },
                {
                    "@type": "Person",
                    "givenName": "Siyu",
                    "familyName": "Wang",
                    "email": "wangsiyu_real@126.com",
                    "affiliation": "Shanghai International Studies University",
                },
            ],
            "description": "Reproducibility package for validation controlled imbalance aware learning experiments in IoT intrusion detection.",
            "keywords": [
                "Internet of Things",
                "intrusion detection",
                "class imbalance",
                "rare attack recognition",
                "ensemble learning",
                "external validation",
            ],
        },
        indent=2,
    )
    + "\n",
    ".zenodo.json": json.dumps(
        {
            "title": "Validation controlled imbalance aware learning for fine grained IoT intrusion detection",
            "upload_type": "software",
            "publication_date": RELEASE_DATE.isoformat(),
            "creators": [
                {
                    "name": "Zhang, Junjie",
                    "affiliation": "Shanghai International Studies University",
                },
                {
                    "name": "Wang, Siyu",
                    "affiliation": "Shanghai International Studies University",
                },
            ],
            "description": "Reproducibility package for validation controlled imbalance aware learning experiments for rare IoT attack recognition.",
            "version": "1.0.2",
            "access_right": "open",
            "license": "MIT",
            "keywords": [
                "Internet of Things",
                "intrusion detection",
                "class imbalance",
                "rare attack recognition",
                "ensemble learning",
                "external validation",
            ],
            "related_identifiers": [
                {
                    "identifier": "https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample",
                    "relation": "references",
                    "scheme": "url",
                    "resource_type": "dataset",
                },
                {
                    "identifier": "https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot",
                    "relation": "references",
                    "scheme": "url",
                    "resource_type": "dataset",
                },
            ],
        },
        indent=2,
    )
    + "\n",
}


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree_filtered(src: Path, dst: Path, allowed_suffixes: set[str] | None = None) -> None:
    if not src.exists():
        return
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        parts = {part.lower() for part in path.relative_to(src).parts}
        if "__pycache__" in parts or ".git" in parts:
            continue
        if path.suffix.lower() in {".pyc", ".pyo", ".log", ".aux", ".out", ".fls", ".fdb_latexmk", ".synctex.gz"}:
            continue
        if allowed_suffixes is not None and path.suffix.lower() not in allowed_suffixes:
            continue
        copy_file(path, dst / path.relative_to(src))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(root: Path) -> None:
    rows: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "checksums_sha256.txt":
            continue
        rows.append(f"{sha256(path)}  {path.relative_to(root).as_posix()}")
    write_text(root / "checksums_sha256.txt", "\n".join(rows) + "\n")


def make_zip(root: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(root.parent).as_posix())


def main() -> None:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)

    for relative, content in TEXT_FILES.items():
        write_text(TARGET / relative, content)

    copy_file(PROJECT_ROOT / "requirements.txt", TARGET / "requirements.txt")
    copy_tree_filtered(PROJECT_ROOT / "scripts", TARGET / "scripts", {".py"})
    copy_tree_filtered(
        PROJECT_ROOT / "results",
        TARGET / "results",
        {".csv", ".md", ".txt"},
    )
    copy_tree_filtered(
        PROJECT_ROOT / "figures" / "paper_figures",
        TARGET / "figures" / "paper_figures",
        {".png", ".tiff"},
    )

    docs_to_copy = [
        "ARTICLE_BUILD_SPEC.md",
        "CLAIM_STRENGTH_AUDIT.md",
        "CICIOT_BOOTSTRAP_UNCERTAINTY.md",
        "DATA_ASSET_INVENTORY.md",
        "EXPERIMENT_DESIGN_GATE.md",
        "FINAL_READINESS_AUDIT.md",
        "HYPERPARAMETER_TABLE.md",
        "IOTID20_REPEATED_SPLIT_EXPERIMENT_DESIGN.md",
        "IOTID20_REPEATED_SPLIT_RESULT_NOTE.md",
        "NBAIOT_UNSEEN_DEVICE_DESIGN.md",
        "NUMERIC_CONSISTENCY_AUDIT.md",
        "REFERENCE_DOI_AUDIT.md",
        "RESULT_LEDGER.md",
        "SCIENTIFIC_REPORTS_BENCHMARK_MATRIX.md",
        "STAGE_QUALITY_GATE.md",
        "SUBMISSION_COMPLIANCE_CHECKLIST.md",
        "VENUE_ROUTE_CARD.md",
    ]
    for name in docs_to_copy:
        src = PROJECT_ROOT / "docs" / name
        if src.exists():
            copy_file(src, TARGET / "docs" / name)

    data_sources = TARGET / "data" / "DATA_SOURCES.md"
    copy_file(PROJECT_ROOT / "docs" / "DATA_ASSET_INVENTORY.md", data_sources)

    if MANUSCRIPT_PACKAGE.exists():
        copy_tree_filtered(
            MANUSCRIPT_PACKAGE,
            TARGET / "manuscript" / "scientific_reports_latex_v3",
            {".tex", ".cls", ".md", ".pdf", ".png", ".tiff", ".csv", ".txt", ".bst", ".ldf"},
        )

    write_checksums(TARGET)
    make_zip(TARGET, ZIP_PATH)

    print(f"repository_dir={TARGET}")
    print(f"zip={ZIP_PATH}")
    print(f"files={sum(1 for p in TARGET.rglob('*') if p.is_file())}")
    print(f"zip_bytes={ZIP_PATH.stat().st_size}")


if __name__ == "__main__":
    main()

