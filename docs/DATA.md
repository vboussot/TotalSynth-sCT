# Data layout and preparation

Medical images are not in this repository. The public ones are fetched and
prepared with
[RegistrationBias-sCT](https://github.com/vboussot/RegistrationBias-sCT) and
remain under the terms of their datasets.

## Expected layout

```text
data/
├── processed/
│   ├── synthrad2023/Task_{1,2}/{brain,pelvis}/PATIENT/
│   ├── synthrad2025/Task_{1,2}/{AB,HN,TH}/PATIENT/
│   └── external/Task_1/CSIRO/PATIENT/
└── splits/
    └── task_{1,2}/{Validation,Check}.txt
```

`data/processed` is the folder of the same name in RegistrationBias-sCT, linked
or copied. Processed cases expose KonfAI groups, of which this repository reads:

- `CT.mha`: planning CT, the reference of every metric;
- `MR_IMPACT.mha` or `CBCT_IMPACT.mha`: source image warped onto the CT with the
  IMPACT transform, the input of the models;
- `MASK.mha`: body mask.

## IMPACT registrations

- <https://huggingface.co/datasets/VBoussot/synthrad2023-impact-registration>
- <https://huggingface.co/datasets/VBoussot/synthrad2025-impact-registration>

These Elastix B-spline parameter files are released under CC BY-NC 4.0. The
SynthRAD images keep their own license.

## Preparation

In RegistrationBias-sCT:

```bash
python scripts/download.py --only data transforms    # the 266 held-out SynthRAD cases and their IMPACT transforms
make pairs
```

## Held-out lists

| File | Cases |
|---|---|
| `task_1/Validation.txt` | 140: the held-out cases of Task 1 (AB 22, HN 21, TH 23, brain 27, pelvis 23, CSIRO 24) |
| `task_2/Validation.txt` | 150: the held-out cases of Task 2 (AB 32, HN 37, TH 34, brain 26, pelvis 21) |
| `task_{1,2}/Check.txt` | two cases per region, for `--check` |
| `task_1/MultimodalHC.txt` | the 15 MTBD subjects of Table 6 |

## External data

- **CSIRO:** 24 expert-aligned T2 MRI/CT cases (Dowling et al., CSIRO), to
  request from their authors. RegistrationBias-sCT prepares them under
  `external/Task_1/CSIRO` with its `prepare_external.py --ext-t2 DIR`.
- **MTBD** (Multimodal Total-Body Dynamic dataset): whole-body Dixon MRI/CT of healthy volunteers
  (Hinge et al.), distributed by its authors as `DEPICT-RH/Multimodal-HC`. Each of the 15 held-out subjects is evaluated with
  its in-phase and its out-of-phase image; Table 6 is built from the
  patient-level metrics of the paper.
