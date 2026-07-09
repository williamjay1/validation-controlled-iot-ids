from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests
from huggingface_hub import hf_hub_download
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DOCS_DIR = ROOT / "docs"


@dataclass
class DataAsset:
    name: str
    source_type: str
    source_url: str
    mirror_or_access: str
    license_note: str
    local_paths: list[str]
    status: str
    downloaded_utc: str
    notes: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dirs() -> None:
    for path in [RAW_DIR, DOCS_DIR, ROOT / "data" / "processed", ROOT / "results", ROOT / "figures"]:
        path.mkdir(parents=True, exist_ok=True)


def copy_hf_file(repo_id: str, repo_file: str, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / repo_file
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return target
    cached = Path(
        hf_hub_download(
            repo_id=repo_id,
            filename=repo_file,
            repo_type="dataset",
            local_dir=target_dir,
            local_dir_use_symlinks=False,
        )
    )
    if cached.resolve() != target.resolve():
        shutil.copy2(cached, target)
    return target


def download_hf_ciciot_subsample() -> DataAsset:
    repo_id = "lacg030175/CIC-IoT-2023-neto-subsample"
    target_dir = RAW_DIR / "ciciot2023_hf_neto_subsample"
    files = [
        "README.md",
        "feature_importance.json",
        "random/train-00000-of-00001.parquet",
        "random/test-00000-of-00001.parquet",
    ]
    paths = [copy_hf_file(repo_id, f, target_dir) for f in files]
    return DataAsset(
        name="CICIoT2023 Neto subsample",
        source_type="public mirror of CICIoT2023",
        source_url="https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample",
        mirror_or_access="Hugging Face dataset files downloaded by huggingface_hub",
        license_note="Mirror card reports CC BY 4.0. Official CICIoT2023 access should be checked before redistribution.",
        local_paths=[str(p.relative_to(ROOT)) for p in paths],
        status="downloaded",
        downloaded_utc=utc_now(),
        notes="Used for quick, scriptable experiments. The official CICIoT2023 page uses a request/form workflow.",
    )


def download_hf_iotid20() -> DataAsset:
    repo_id = "KathiS/IoTID20_Preprocessed_File"
    target_dir = RAW_DIR / "iotid20_hf_preprocessed"
    paths = [copy_hf_file(repo_id, "Preprocessed_file.csv", target_dir)]
    return DataAsset(
        name="IoTID20 preprocessed file",
        source_type="public mirror of IoTID20",
        source_url="https://huggingface.co/datasets/KathiS/IoTID20_Preprocessed_File",
        mirror_or_access="Hugging Face dataset file downloaded by huggingface_hub",
        license_note="Mirror card has no detailed license metadata; original IoTID20 terms need confirmation before manuscript submission.",
        local_paths=[str(p.relative_to(ROOT)) for p in paths],
        status="downloaded",
        downloaded_utc=utc_now(),
        notes="Candidate external/lightweight validation data. Not used as primary evidence until provenance is checked.",
    )


def download_large_file(url: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return target
    temp = target.with_suffix(target.suffix + ".part")
    headers = {}
    existing = temp.stat().st_size if temp.exists() else 0
    if existing:
        headers["Range"] = f"bytes={existing}-"
    with requests.get(url, stream=True, timeout=60, headers=headers) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0)) + existing
        mode = "ab" if existing else "wb"
        with temp.open(mode) as fh, tqdm(
            total=total,
            initial=existing,
            unit="B",
            unit_scale=True,
            desc=target.name,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)
                    bar.update(len(chunk))
    temp.replace(target)
    return target


def download_nbaiot(extract: bool) -> DataAsset:
    url = "https://archive.ics.uci.edu/static/public/442/detection+of+iot+botnet+attacks+n+baiot.zip"
    target_dir = RAW_DIR / "n_baiot_uci"
    archive = download_large_file(url, target_dir / "n_baiot.zip")
    paths = [archive]
    status = "downloaded"
    notes = "Official UCI archive. Extraction can take time and disk space."
    if extract:
        extract_dir = target_dir / "extracted"
        marker = extract_dir / ".extracted"
        if not marker.exists():
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(extract_dir)
            marker.write_text(utc_now(), encoding="utf-8")
        paths.append(extract_dir)
        status = "downloaded_and_extracted"
    return DataAsset(
        name="N-BaIoT",
        source_type="official UCI Machine Learning Repository dataset",
        source_url="https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot",
        mirror_or_access=url,
        license_note="UCI page reports CC BY 4.0 metadata in current repository API/card.",
        local_paths=[str(p.relative_to(ROOT)) for p in paths],
        status=status,
        downloaded_utc=utc_now(),
        notes=notes,
    )


def write_asset_ledger(assets: list[DataAsset]) -> None:
    ledger = {
        "created_utc": utc_now(),
        "workspace_root": str(ROOT),
        "assets": [asdict(asset) for asset in assets],
    }
    out = DOCS_DIR / "DATA_ASSET_INVENTORY.json"
    out.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
    md_lines = [
        "# Data Asset Inventory",
        "",
        f"Created UTC: {ledger['created_utc']}",
        "",
        "| Dataset | Source | Access | Status | Local paths | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for asset in assets:
        md_lines.append(
            "| "
            + " | ".join(
                [
                    asset.name,
                    asset.source_url,
                    asset.mirror_or_access,
                    asset.status,
                    "<br>".join(asset.local_paths),
                    asset.notes.replace("|", "/"),
                ]
            )
            + " |"
        )
    (DOCS_DIR / "DATA_ASSET_INVENTORY.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download public IoT IDS datasets for reproducible experiments.")
    parser.add_argument("--quick", action="store_true", help="Download scriptable quick datasets: CICIoT2023 subsample and IoTID20.")
    parser.add_argument("--include-nbaiot", action="store_true", help="Download the full N-BaIoT UCI archive.")
    parser.add_argument("--extract-nbaiot", action="store_true", help="Extract the N-BaIoT archive after download.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    assets: list[DataAsset] = []
    if args.quick or not args.include_nbaiot:
        assets.append(download_hf_ciciot_subsample())
        assets.append(download_hf_iotid20())
    if args.include_nbaiot:
        assets.append(download_nbaiot(extract=args.extract_nbaiot))
    write_asset_ledger(assets)
    print(f"Wrote {DOCS_DIR / 'DATA_ASSET_INVENTORY.md'}")


if __name__ == "__main__":
    main()
