#!/usr/bin/env python3
"""Download the released TotalSynth models.

Standard library only, so it runs before any environment is installed.

The four models are in the Hugging Face repository VBoussot/ImpactSynth, pinned here to one revision: the
dedicated MRI-to-CT model (MR), the dedicated CBCT-to-CT model (CBCT), the unified model (MR_CBCT) and the
MTBD fine-tuned model (Finetune). Each folder holds five fold checkpoints, checked against
models/manifest.csv, and its inference configuration (Prediction.yml, UNetPlusPlus.yml, Model.py).

TotalSegmentator (Dice), the SAM 2.1 encoder (SAM) and the segmentation encoders (Reg) are fetched
automatically by KonfAI on first use. The images are prepared with RegistrationBias-sCT: see docs/DATA.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY, REVISION = "VBoussot/ImpactSynth", "b3c0592ab7f52f5aab7bf4f0b38d8a46d879c2a8"
MODELS = ("MR", "CBCT", "MR_CBCT", "Finetune")
CONFIGURATION = ("Prediction.yml", "UNetPlusPlus.yml", "Model.py")


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def fetch(relative: str, target: Path, digest: str | None, dry_run: bool) -> None:
    if target.is_file() and (digest is None or sha256(target) == digest):
        print(f"keep  {target.relative_to(ROOT)}")
        return
    print(f"get   {target.relative_to(ROOT)}")
    if dry_run:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    with urllib.request.urlopen(f"https://huggingface.co/{REPOSITORY}/resolve/{REVISION}/{relative}") as response, \
            partial.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    if digest is not None and sha256(partial) != digest:
        raise SystemExit(f"{relative}: SHA-256 differs from models/manifest.csv")
    partial.replace(target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", choices=MODELS, nargs="+", default=list(MODELS))
    parser.add_argument("--dry-run", action="store_true", help="list what would be fetched")
    args = parser.parse_args()

    with (ROOT / "models/manifest.csv").open(newline="") as handle:
        checkpoints = [row for row in csv.DictReader(handle) if row["model"] in args.only]
    for row in checkpoints:
        fetch(row["repository_path"].removeprefix("models/"), ROOT / row["repository_path"], row["sha256"], args.dry_run)
    for model in args.only:
        for name in CONFIGURATION:
            fetch(f"{model}/{name}", ROOT / "models" / model / name, None, args.dry_run)


if __name__ == "__main__":
    main()
