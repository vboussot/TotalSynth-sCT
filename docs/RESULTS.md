# Result files

| Path | Content |
|---|---|
| `tables/table_NN_*.tex` | the 6 tables of the paper, written from `paper/manuscript.tex` by `scripts/tables/published_tables.py` |
| `results/raw/Evaluations/` | 108 `Metric_TRAIN.json` files: one per model branch and region, with the value of every metric for every patient |
| `tables/from_metrics/` | Tables 2 to 6 built from those files by `scripts/tables/` |

## Metric files

The tree is `Task_{t}/{MODEL}/CV{KIND}/{REGION}/Metric_TRAIN.json`:

| Element | Values |
|---|---|
| `Task_{t}` | source modality: `Task_1` for MRI, `Task_2` for CBCT |
| `MODEL` | `Dedicated`, `Unified`, or `Finetune` for the model fine-tuned on MTBD |
| `KIND` | empty for MAE, PSNR and SSIM; `_SEG` for the Dice; `_PERCEPTUAL` for SAM and Reg; `_Uncertainty` |
| `REGION` | `AB`, `HN`, `TH`, `brain`, `pelvis`; `CSIRO` (Task 1); `MultimodalHC_in` and `MultimodalHC_out` for the in-phase and out-of-phase images of MTBD |

A run of `scripts/evaluate.py` writes the same tree under
`results/generated/Evaluations/`.

The tables report the mean and the population standard deviation over the
patients. The Dice of a patient is the mean over the TotalSegmentator labels
present in its segmentations, background included. SAM is reported ×100.

`tests/test_repository.py` checks that every cell the scripts build is the
paper's, to the last printed digit.

## Comparing a new run

```bash
python scripts/compare_metrics.py     # every metric, patient by patient
python scripts/compare_tables.py      # every table, cell by cell
```

SAM is computed on one 512×512 frame per axial slice, zero-padded or cropped at
the end of the axes. SAM, Reg and the uncertainty are not restricted to the
body mask.
