# TotalSynth-sCT

Code, configurations and patient-level results of **“TotalSynth: Robust
Whole-Body Synthetic CT from MRI and CBCT images”**
([arXiv:2609.13838](https://arxiv.org/abs/2609.13838)).

The paper releases three five-fold model families for synthetic CT generation:
a dedicated MRI-to-CT model (Task 1), a dedicated CBCT-to-CT model (Task 2) and
a unified model that accepts both modalities. It evaluates them on held-out
SynthRAD2023 and SynthRAD2025 cases and on an external MRI/CT set, then on
MTBD whole-body MRI before and after fine-tuning.

## What you can do

| Goal | You need | Time | Start here |
|---|---|---|---|
| Read the reported numbers and build the tables from the patient-level metrics | Python, no data, no GPU | a minute | [Quick check](#quick-check-no-data) |
| Run prediction and evaluation with the released models | one 10 GB GPU, the prepared held-out cases | about half a day | [Reproduce the paper](#reproduce-the-paper) |
| Use a model on your own images | 3D Slicer or KonfAI | minutes per image | [models/README.md](models/README.md) |

## Quick check (no data)

```bash
git clone https://github.com/vboussot/TotalSynth-sCT && cd TotalSynth-sCT
pip install pytest pyyaml

make test      # repository integrity
make tables    # tables/from_metrics/: Tables 2 to 6 from the patient-level metrics
```

## Reproduce the paper

One file per step. Each command is detailed in
[docs/REPRODUCE.md](docs/REPRODUCE.md), with what it needs, what it writes and
how long it takes.

```bash
python scripts/download.py            # 1. the released models (2.1 GB)
ln -s /path/to/RegistrationBias-sCT/data/processed data/processed   # 2. the prepared held-out cases
python scripts/predict.py --gpu 0     # 3. predictions: dedicated and unified models, both tasks
python scripts/evaluate.py --gpu 0    # 4. evaluations: MAE/PSNR/SSIM, Dice, SAM, Reg, uncertainty
python scripts/compare_metrics.py     # 5. your metrics against the paper's, patient by patient
python scripts/compare_tables.py      #    your tables against the paper's, cell by cell
```

The held-out cases are prepared with
[RegistrationBias-sCT](https://github.com/vboussot/RegistrationBias-sCT), which
downloads the SynthRAD images and the IMPACT registrations and writes the pairs
this repository reads ([docs/DATA.md](docs/DATA.md)).

Steps 3 and 4 skip what is already done, so they can be interrupted and
relaunched, and they take `--task` and `--model` filters. `--check` restricts
them to two held-out cases per region.

Each table has its own script:

| Result | Script |
|---|---|
| Table 2 | `scripts/tables/table_02_summary.py` |
| Table 3 | `scripts/tables/table_03_mri.py` |
| Table 4 | `scripts/tables/table_04_cbct.py` |
| Table 5 | `scripts/tables/table_05_unified.py` |
| Table 6 | `scripts/tables/table_06_multimodal_hc.py` |

The full correspondence between the paper and the files is in
[docs/PAPER_MAP.md](docs/PAPER_MAP.md).

## Repository layout

```text
scripts/download.py              step 1: the released models
scripts/predict.py               step 3: predictions
scripts/evaluate.py              step 4: evaluations
scripts/compare_*.py             step 5: comparison with the paper
scripts/tables/                  one script per table
configs/                         evaluation configurations
src/totalsynth/                  the SAM metric
data/splits/                     held-out patient lists
models/manifest.csv              the 20 checkpoints, with size and SHA-256
results/raw/                     patient-level metrics of the paper
tables/                          the 6 tables of the paper; from_metrics/ holds those built by scripts/tables/
figures/                         the three figures of the paper
paper/                           source of the paper
tests/                           repository integrity tests
```

Images, predictions and model weights are not in the repository:
`scripts/download.py` fetches the models.

## Documentation

| File | Content |
|---|---|
| [docs/REPRODUCE.md](docs/REPRODUCE.md) | Step-by-step guide: requirements, commands, outputs, durations |
| [docs/PAPER_MAP.md](docs/PAPER_MAP.md) | Each table and figure of the paper: script and metrics |
| [docs/RESULTS.md](docs/RESULTS.md) | The result files of the repository |
| [docs/DATA.md](docs/DATA.md) | Datasets, layout on disk, held-out lists |
| [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | Software versions and hardware notes |

## External test sets

Besides SynthRAD, the paper uses two external sets
([docs/DATA.md](docs/DATA.md#external-data)):

- **CSIRO** (Task 1): 24 expert-aligned T2 MRI/CT cases, to request from their
  authors; RegistrationBias-sCT prepares them.
- **MTBD**, the Multimodal Total-Body Dynamic dataset (Table 6): whole-body
  Dixon MRI/CT of healthy volunteers, distributed by its authors as `DEPICT-RH/Multimodal-HC`. Table 6 is built from the patient-level metrics
  of the paper.

## Citation

Citation metadata is in [CITATION.cff](CITATION.cff).

## License

The code is released under the [Apache License 2.0](LICENSE). The SynthRAD
images, the external sets, the third-party weights and the IMPACT
transformations keep their own licenses.
