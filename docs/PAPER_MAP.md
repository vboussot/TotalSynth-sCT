# From the paper to the files

For each table and figure of the paper: the script that produces it and the
patient-level metrics it reads. The tables of the paper are in
`tables/table_NN_*.tex`, those built by the scripts in `tables/from_metrics/`,
the paper's metrics in `results/raw/Evaluations/` and the metrics of a new run
in `results/generated/Evaluations/`.

## The experiment in brief

- **Data.** SynthRAD2023 (brain, pelvis) and SynthRAD2025 (abdomen, head and
  neck, thorax) after registration quality control, four prostate MRI/CT
  cohorts, and MTBD for fine-tuning and external evaluation. The held-out
  cases are never seen by any of the five folds.
- **Pairs.** The released IMPACT-Reg registration: the source image is warped
  onto the planning CT.
- **Model.** 2.5D U-Net++ with a ResNet-34 encoder, five adjacent axial slices,
  26,084,881 parameters. Three families of five folds: MRI-to-CT, CBCT-to-CT,
  unified MRI/CBCT-to-CT; and the MRI-to-CT model fine-tuned on MTBD.
- **Inference.** Five folds × three views (original and two flips), voxel-wise
  mean; voxels outside the body mask are set to air (`scripts/predict.py`).
- **Metrics.** MAE, PSNR, SSIM, TotalSegmentator Dice, calibrated SAM distance,
  IMPACT distance to the source image (Reg), variance of the 15 predictions in the
  body mask
  (`configs/evaluation/predictions/`, `src/totalsynth/metrics.py`,
  `scripts/evaluate.py`).

## Tables

| Table | Content | Script | Metrics |
|---|---|---|---|
| 1 | Datasets after eligibility screening | — | |
| 2 | Overall performance of the released models and of fine-tuning | `table_02_summary.py` | the `CV` branches of Tables 3 to 6 |
| 3 | Dedicated MRI-to-CT model by region | `table_03_mri.py` | `Task_1/Dedicated/CV*` |
| 4 | Dedicated CBCT-to-CT model by region | `table_04_cbct.py` | `Task_2/Dedicated/CV*` |
| 5 | Unified model by input domain and region | `table_05_unified.py` | `Task_{1,2}/Unified/CV*` |
| 6 | MTBD before and after fine-tuning | `table_06_multimodal_hc.py` | `Task_1/{Unified,Finetune}/CV*`, regions `MultimodalHC_{in,out}` |

All table scripts are in `scripts/tables/`. Table 1 has no script; like the
others, it is in `tables/` as LaTeX, written from the paper source by
`published_tables.py`.

## Figures

| Figure | Content |
|---|---|
| 1 | Data coverage by source modality and anatomical region |
| 2 | TotalSynth pipeline |
| 3 | Representative synthesis examples, axial plane |
| S1, S2 | Representative synthesis examples, coronal and sagittal planes |

## Which predictions feed which table

| Predictions (`scripts/predict.py`) | Evaluations (`scripts/evaluate.py --kind`) | Tables |
|---|---|---|
| `--task 1 --model Dedicated` | `image`, `SEG`, `PERCEPTUAL`, `Uncertainty` | 2, 3 |
| `--task 2 --model Dedicated` | same | 2, 4 |
| `--model Unified` | same | 2, 5 |

## Notes

### Table 6

The rows are computed on the in-phase and the out-of-phase image of each MTBD
subject, and “Overall” pools the two.
