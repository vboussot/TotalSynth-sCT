"""Shared by the table scripts: read the patient-level metrics, average them, render the LaTeX of the paper."""

from __future__ import annotations

import json
import os
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# The paper's metrics by default; TOTALSYNTH_EVALUATIONS=results/generated/Evaluations for those of a new run.
EVALUATIONS = ROOT / os.environ.get("TOTALSYNTH_EVALUATIONS", "results/raw/Evaluations")
OUTPUT = ROOT / os.environ.get("TOTALSYNTH_TABLES", "tables/from_metrics")

MRI = ("AB", "HN", "TH", "brain", "pelvis", "CSIRO")
CBCT = ("AB", "HN", "TH", "brain", "pelvis")
MULTIMODAL_HC = ("MultimodalHC_in", "MultimodalHC_out")
# column -> (branch suffix, end of the metric key, factor, decimals); SAM is reported x100
COLUMNS = {
    "MAE": ("", ":MAE", 1, 2),
    "PSNR": ("", ":PSNR", 1, 2),
    "SSIM": ("", ":SSIM", 1, 3),
    "Dice": ("_SEG", None, 1, 3),
    "SAM": ("_PERCEPTUAL", ":SAM_Perceptual", 100, 3),
    "Reg": ("_PERCEPTUAL", ":Reg", 1, 3),
    "Uncertainty": ("_Uncertainty", ":Uncertainty", 1, 2),
}
ALL = tuple(COLUMNS)


def values(branch: str, column: str, regions: tuple[str, ...]) -> list[float]:
    """Patient values of a column for ``Task_{t}/{MODEL}``, pooled over the regions. The Dice of a patient is
    the mean over the labels present in its segmentations."""
    suffix, key, factor, _ = COLUMNS[column]
    pooled: list[float] = []
    for region in regions:
        path = EVALUATIONS / branch / f"CV{suffix}" / region / "Metric_TRAIN.json"
        if not path.is_file():  # a metric that was not evaluated leaves its cells empty
            continue
        cases = json.loads(path.read_text(encoding="utf-8"))["case"]
        if key is None:
            labels: dict[str, list[float]] = {}
            for name, per_patient in cases.items():
                if ":Dice:" in name:  # one key per label
                    for patient, value in per_patient.items():
                        if value is not None and value == value:
                            labels.setdefault(patient, []).append(value)
            pooled += [statistics.mean(scores) for scores in labels.values()]
        else:
            pooled += [value * factor for name, per_patient in cases.items() if name.endswith(key)
                       for value in per_patient.values()]
    return pooled


def cell(branch: str, column: str, regions: tuple[str, ...]) -> str:
    pooled = values(branch, column, regions)
    if len(pooled) < 2:
        return "--"
    decimals = COLUMNS[column][3]
    return rf"\mstd{{{statistics.mean(pooled):.{decimals}f}}}{{{statistics.pstdev(pooled):.{decimals}f}}}"


def row(label: str, branch: str, regions: tuple[str, ...], columns: tuple[str, ...] = ALL) -> str:
    return " & ".join([label, *(cell(branch, column, regions) for column in columns)]) + r" \\"


def count(branch: str, regions: tuple[str, ...]) -> int:
    return len(values(branch, "MAE", regions))


def write(name: str, caption: str, label: str, layout: str, header: str, rows: list[str], size: str = r"\scriptsize") -> None:
    lines = [r"\begin{table}[!ht]", r"\centering", rf"\caption{{{caption}}}", rf"\label{{{label}}}", size,
             rf"\begin{{tabular}}{{{layout}}}", r"\toprule", header + r" \\", r"\midrule", *rows, r"\bottomrule",
             r"\end{tabular}", r"\end{table}", ""]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT / name}")
