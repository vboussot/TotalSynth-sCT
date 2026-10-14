#!/usr/bin/env python3
"""Evaluate every prediction produced by scripts/predict.py.

Each metric has its KonfAI configuration in configs/evaluation/predictions. Results go to
results/generated/Evaluations with the same tree as results/raw/Evaluations, so the
table scripts can read either (TOTALSYNTH_EVALUATIONS=results/generated/Evaluations).

Branch suffix -> metric:
  (none)         MAE, PSNR, SSIM in the body mask
  _SEG           TotalSegmentator Dice between the sCT and the CT
  _PERCEPTUAL    SAM: calibrated d_SAM between the sCT and the CT
                 Reg: IMPACT distance between the sCT and its source image
  _Uncertainty   variance of the 15 predictions, mean over the volume
"""

import argparse
import shutil
import sys
from pathlib import Path
from string import Template

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _konfai import ROOT, device_args, run
from predict import MODELS, REGIONS, SOURCE, subset

OUTPUT = "results/generated/Evaluations"
TEMPLATES = ROOT / "configs/evaluation/predictions"
# branch suffix -> configuration
KINDS = {"": "image", "_SEG": "seg", "_PERCEPTUAL": "perceptual", "_Uncertainty": "uncertainty"}
# source modality -> frozen encoder of Reg and the weights of its feature levels
ENCODERS = {"MR": ("MRSeg/MRSeg.pt", [0, 0, 0, 0, 0, 0, 1]), "CBCT": ("TS/M291.pt", [1, 1])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", type=int, choices=(1, 2), nargs="+", default=[1, 2])
    parser.add_argument("--model", choices=("Dedicated", "Unified"), nargs="+", default=["Dedicated", "Unified"])
    parser.add_argument("--kind", nargs="+", choices=[k.strip("_") or "image" for k in KINDS],
                        default=[k.strip("_") or "image" for k in KINDS])
    parser.add_argument("--regions", nargs="+", default=["synthrad2025", "synthrad2023", "external"],
                        help="restrict to prepared datasets containing these names")
    parser.add_argument("--check", action="store_true",
                        help="quick check: two held-out cases per region (data/splits/task_{t}/Check.txt)")
    parser.add_argument("--gpu", type=int, nargs="+")
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--force", action="store_true", help="recompute existing metrics")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for task, model in MODELS:
        if task not in args.task or model not in args.model:
            continue
        predictions = ROOT / f"predictions/Task_{task}/{model}/CV/Output"
        if not predictions.is_dir():
            continue
        encoder, weights = ENCODERS[SOURCE[task]]
        for region in REGIONS[task]:
            dataset = ROOT / "data/processed" / region
            if not dataset.is_dir() or not any(r in region for r in args.regions):
                continue
            if not any((predictions / case.name / "sCT.mha").is_file() for case in dataset.iterdir()):
                continue
            for suffix, config in KINDS.items():
                if (suffix.strip("_") or "image") not in args.kind:
                    continue
                name = f"Task_{task}/{model}/CV{suffix}/{region.rsplit('/', 1)[1]}"
                if (ROOT / OUTPUT / name / "Metric_TRAIN.json").is_file() and not args.force:
                    print(f"skip  {name}")
                    continue
                shutil.rmtree(ROOT / OUTPUT / name, ignore_errors=True)
                # KonfAI rewrites the config it reads, so a fresh copy is generated for every run.
                path = ROOT / "results/generated/configs" / (name.replace("/", "_") + ".yml")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(Template((TEMPLATES / f"{config}.yml").read_text()).substitute(
                    source=SOURCE[task], encoder=encoder, weights=weights, name=name,
                    dataset=f"./data/processed/{region}", predictions=predictions.relative_to(ROOT),
                    subset=subset(task, model, args.check)))
                run(["konfai", "EVALUATION", "-y", "--config", str(path), *device_args(args.gpu, args.cpu),
                     "--evaluations-dir", OUTPUT], args.dry_run)


if __name__ == "__main__":
    main()
