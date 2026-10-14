#!/usr/bin/env python3
"""Predict the held-out cases with the released TotalSynth models.

Task 1 is MRI-to-CT and Task 2 CBCT-to-CT. Each task is predicted by its dedicated model and by the unified
MRI/CBCT-to-CT model. A prediction is the five-fold ensemble (``CV``): each fold checkpoint runs on the
original image plus two flips, and the 15 predictions are averaged. The output tree is the one
scripts/evaluate.py reads:

    predictions/Task_{t}/{MODEL}/CV/Output/{case}/sCT.mha            the synthetic CT
    predictions/Task_{t}/{MODEL}/CV/Output/{case}/Uncertainty.mha    voxel-wise variance of the 15 predictions

MODEL is ``Dedicated`` or ``Unified``. The checkpoints and their inference configuration are the released ones
(models/, fetched by scripts/download.py). The prepared pairs supply the body mask and the source image on the
CT grid, so the mask estimation and the resampling of the released pipeline are not run again. Datasets are
predicted one after the other: what is already there is skipped, so an interrupted run resumes where it stopped.
"""

import argparse
import sys
from pathlib import Path

import SimpleITK as sitk
import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _konfai import ROOT, device_args, resolve, run

REGIONS = {
    1: ["synthrad2025/Task_1/AB", "synthrad2025/Task_1/HN", "synthrad2025/Task_1/TH",
        "synthrad2023/Task_1/brain", "synthrad2023/Task_1/pelvis", "external/Task_1/CSIRO"],
    2: ["synthrad2025/Task_2/AB", "synthrad2025/Task_2/HN", "synthrad2025/Task_2/TH",
        "synthrad2023/Task_2/brain", "synthrad2023/Task_2/pelvis"],
}
SOURCE = {1: "MR", 2: "CBCT"}
# (task, MODEL) -> folder of the released model under models/
MODELS = {(1, "Dedicated"): "MR", (2, "Dedicated"): "CBCT", (1, "Unified"): "MR_CBCT", (2, "Unified"): "MR_CBCT"}


def subset(task: int, model: str, check: bool) -> str:
    """Case list of a model: the held-out cases of the task, the same for the dedicated and the unified model."""
    name = "Check" if check else "Validation"
    return f"./data/splits/task_{task}/{name}.txt"


def finish(output: Path) -> None:
    """Replace each 15-member stack (1 to 2 GB) by its variance; compress the sCT (lossless)."""
    for stack in sorted(output.glob("*/InferenceStack.mha")):
        image = sitk.ReadImage(str(stack))
        members = torch.from_numpy(sitk.GetArrayFromImage(image))
        if image.GetNumberOfComponentsPerPixel() > 1:
            members = members.movedim(-1, 0)
        variance = sitk.GetImageFromArray(torch.var(members.float(), 0).numpy())  # as KonfAI's Variance
        variance.CopyInformation(sitk.ReadImage(str(stack.with_name("sCT.mha"))))
        sitk.WriteImage(variance, str(stack.with_name("Uncertainty.mha")), True)
        stack.unlink()
    for path in sorted(output.glob("*/sCT.mha")):
        with path.open("rb") as handle:
            if b"CompressedData = True" not in handle.read(1024):
                sitk.WriteImage(sitk.ReadImage(str(path)), str(path), True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", type=int, choices=(1, 2), nargs="+", default=[1, 2])
    parser.add_argument("--model", choices=("Dedicated", "Unified"), nargs="+", default=["Dedicated", "Unified"])
    parser.add_argument("--checkpoints", type=Path, default=ROOT / "models",
                        help="root with {MR,CBCT,MR_CBCT}/CV_{i}.pt and their inference configuration")
    parser.add_argument("--regions", nargs="+", default=["synthrad2025", "synthrad2023", "external"],
                        help="restrict to prepared datasets containing these names")
    parser.add_argument("--check", action="store_true",
                        help="quick check: two held-out cases per region (data/splits/task_{t}/Check.txt)")
    parser.add_argument("--batch-size", type=int, default=0,
                        help="patches per forward; 0 lets KonfAI measure what the GPU holds (default)")
    parser.add_argument("--gpu", type=int, nargs="+")
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--force", action="store_true", help="recompute existing predictions")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for (task, model), folder in MODELS.items():
        if task not in args.task or model not in args.model:
            continue
        name = f"Task_{task}/{model}/CV"
        output = ROOT / "predictions" / name / "Output"
        release = resolve(args.checkpoints) / folder
        models = [release / f"CV_{index}.pt" for index in range(5)]
        missing = [str(path) for path in [*models, release / "Prediction.yml"] if not path.is_file()]
        if missing:
            print(f"miss  {name}: " + ", ".join(missing))
            continue
        held_out = set((ROOT / subset(task, model, args.check)).read_text().split())
        for region in REGIONS[task]:
            dataset = ROOT / "data/processed" / region
            if not dataset.is_dir() or not any(r in region for r in args.regions):
                continue
            cases = [case.name for case in dataset.iterdir() if case.name in held_out]
            if not cases or (not args.force and all((output / case / "sCT.mha").is_file() for case in cases)):
                print(f"skip  {name} {region}")
                continue

            config = yaml.safe_load((release / "Prediction.yml").read_text())
            predictor = config["Predictor"]
            predictor["Model"]["classpath"] = str(release / predictor["Model"]["classpath"])
            source = SOURCE[task] + "_IMPACT"
            volume = predictor["Dataset"]["groups_src"]["Volume_0"]["groups_dest"]["Volume"]
            # The prepared pairs are already masked and on the CT grid: only the intensity normalization remains.
            volume["transforms"] = {"Clip": volume["transforms"]["Clip#2"], "Normalize": volume["transforms"]["Normalize"]}
            predictor["Dataset"]["groups_src"] = {
                "MASK": {"groups_dest": {"MASK": {"transforms": "None", "patch_transforms": "None", "is_input": False}}},
                source: {"groups_dest": {"Volume": volume}},
            }
            predictor["Dataset"]["dataset_filenames"] = [f"{dataset}:a:mha"]
            predictor["Dataset"]["subset"] = str(ROOT / subset(task, model, args.check))
            predictor["Dataset"]["batch_size"] = args.batch_size
            predictor["train_name"] = name
            head = predictor["outputs_dataset"]["Tanh"]["OutputDataset"]
            head["same_as_group"] = f"{source}:Volume"
            head["after_reduction_transforms"]["InferenceStack"]["dataset"] = f"{output}:mha"
            # KonfAI rewrites the config it reads, so a fresh copy is generated for every run.
            path = ROOT / "predictions/configs" / (f"{name}/{region}".replace("/", "_") + ".yaml")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(config, sort_keys=False))
            # KonfAI runs from the released model's folder, where the configuration finds its network.
            run(["konfai", "PREDICTION", "-y", "--config", str(path), *device_args(args.gpu, args.cpu),
                 "--models", *map(str, models), "--predictions-dir", str(ROOT / "predictions")], args.dry_run, cwd=release)
            if not args.dry_run:
                finish(output)


if __name__ == "__main__":
    main()
