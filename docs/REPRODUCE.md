# Reproducing the paper, step by step

Every command runs from the repository root. Steps 1 to 5 reproduce the
evaluation of the released models (Tables 2 to 5) from their checkpoints.
Table 6 is built from the patient-level metrics of the paper.

| Step | File | Writes |
|---|---|---|
| [1. Download](#1-download) | `scripts/download.py` | `models/` |
| [2. Pairs](#2-pairs) | RegistrationBias-sCT | `data/processed/` |
| [3. Predictions](#3-predictions) | `scripts/predict.py` | `predictions/` |
| [4. Evaluations](#4-evaluations) | `scripts/evaluate.py` | `results/generated/Evaluations/` |
| [5. Comparison and tables](#5-comparison-and-tables) | `scripts/compare_*.py`, `scripts/tables/` | `tables/generated/` |

## Before you start

| | |
|---|---|
| GPU | one GPU with 10 GB of memory |
| Disk | about 40 GB besides the prepared pairs: 2 GB of models, 15 GB of predictions and up to 20 GB of temporary files during step 3 |
| Time | about half a day for steps 3 and 4 on an RTX 3080. `--check` (two cases per region) takes about half an hour |
| Accounts | none: every download is public |

```bash
conda env create -f environment.yml      # Python 3.12, PyTorch 2.7.1, KonfAI 1.8.7
conda activate totalsynth-sct
pip install -e .
```

Versions and hardware notes are in
[ENVIRONMENT.md](ENVIRONMENT.md).

## 1. Download

```bash
python scripts/download.py --dry-run     # list what will be fetched
python scripts/download.py
```

| What | From | Size |
|---|---|---|
| The 20 checkpoints of the four models, checked against `models/manifest.csv`, and their inference configuration | Hugging Face `VBoussot/ImpactSynth` | 2.1 GB |

`--only MR CBCT MR_CBCT Finetune` selects models. Files already present are
kept.

## 2. Pairs

The held-out cases are the pairs of
[RegistrationBias-sCT](https://github.com/vboussot/RegistrationBias-sCT). Its
steps 1 and 2 download the 266 held-out SynthRAD cases and their IMPACT
registrations and write the pairs:

```bash
git clone https://github.com/vboussot/RegistrationBias-sCT ../RegistrationBias-sCT
(cd ../RegistrationBias-sCT && python scripts/download.py --only data transforms && make pairs)
ln -s "$(realpath ../RegistrationBias-sCT/data/processed)" data/processed
```

This repository reads, under
`data/processed/synthrad{2023,2025}/Task_{1,2}/{region}/{case}/`:

| File | Content |
|---|---|
| `CT.mha` | planning CT, the reference of every metric |
| `MR_IMPACT.mha` or `CBCT_IMPACT.mha` | source image warped onto the CT with the IMPACT transform, the input of the models |
| `MASK.mha` | body mask |

The 24 CSIRO cases of Task 1 go under `data/processed/external/Task_1/CSIRO/`
([DATA.md](DATA.md#external-data)). Regions that are absent are skipped.

## 3. Predictions

```bash
python scripts/predict.py --gpu 0
```

For each task, the script predicts:

| Model | Held-out cases | Predictions per case |
|---|---|---|
| Dedicated (MRI-to-CT for Task 1, CBCT-to-CT for Task 2) | 140 and 150 | 5 folds × 3 views (original, two flips), averaged |
| Unified MRI/CBCT-to-CT | 136 and 144 | 5 folds × 3 views, averaged |

Output: `predictions/Task_{t}/{MODEL}/CV/Output/{case}/sCT.mha`, where `MODEL`
is `Dedicated` or `Unified`, with `Uncertainty.mha`, the variance of the 15
predictions.

The script works one dataset at a time and skips what exists, so it can be
stopped and relaunched. It holds the 15 predictions of every case of the
current dataset (up to 19 GB for Task 1 thorax) and replaces them by their
variance at the end of the dataset. The four runs take about three hours on an
RTX 3080.

Useful options:

```bash
python scripts/predict.py --gpu 0 --check                      # two cases per region
python scripts/predict.py --gpu 0 --task 2 --model Unified     # one part of the plan
python scripts/predict.py --dry-run                            # print the KonfAI commands
```

## 4. Evaluations

```bash
python scripts/evaluate.py --gpu 0
```

| `--kind` | Metric | Column |
|---|---|---|
| `image` | MAE, PSNR, SSIM in the body mask | MAE, PSNR, SSIM |
| `SEG` | TotalSegmentator Dice between sCT and CT segmentations | Dice |
| `PERCEPTUAL` | calibrated SAM distance between sCT and CT; IMPACT distance between sCT and its source image | SAM, Reg |
| `Uncertainty` | mean variance of the 15 predictions in the body mask | Uncertainty |

Output: `results/generated/Evaluations/`, one `Metric_TRAIN.json` per branch and
region, with the same tree as the paper's metrics in `results/raw/Evaluations/`.
Existing files are skipped; the options of step 3 apply (`--check`, `--task`,
`--model`).

## 5. Comparison and tables

```bash
python scripts/compare_metrics.py     # every metric, patient by patient
python scripts/compare_tables.py      # every table, cell by cell
```

`compare_metrics.py` prints, for each branch and metric, the largest absolute
and relative difference with the paper's values. `compare_tables.py` rebuilds
the tables from your metrics into `tables/generated/` and prints, for each, the
number of identical cells and the largest difference. Rows of datasets you did
not evaluate stay empty. The metric files are described in [RESULTS.md](RESULTS.md).

One table at a time, from the paper's metrics (default) or from yours:

```bash
python scripts/tables/table_03_mri.py
TOTALSYNTH_EVALUATIONS=results/generated/Evaluations TOTALSYNTH_TABLES=tables/generated \
  python scripts/tables/table_03_mri.py
```

## If something goes wrong

| Symptom | Cause and fix |
|---|---|
| `miss ... CV_i.pt` in step 3 | A checkpoint is missing: rerun `python scripts/download.py` |
| Step 3 or 4 stopped | Relaunch the same command: finished datasets and metrics are skipped |
| `No space left on device` in step 3 | The 15 predictions of a dataset need up to 19 GB: free the space and relaunch |
| `SAM_Perceptual needs KonfAI >= 1.8.7` | An older KonfAI is installed: `pip install -r requirements.txt` |
