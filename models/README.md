# Model files

Model weights are not tracked: the 20 checkpoints total 2.1 GB, 105 MB each.
They are in the Hugging Face repository `VBoussot/ImpactSynth`;
`scripts/download.py` places them under `models/{MR,CBCT,MR_CBCT,Finetune}/`
with the layout of `manifest.csv`, checks the SHA-256 digest recorded there and
fetches the inference configuration of each model (`Prediction.yml`,
`UNetPlusPlus.yml`, `Model.py`).

| Folder | Model |
|---|---|
| `MR` | dedicated MRI-to-CT model |
| `CBCT` | dedicated CBCT-to-CT model |
| `MR_CBCT` | unified MRI/CBCT-to-CT model |
| `Finetune` | MRI-to-CT model fine-tuned on MTBD |

Each folder is a KonfAI application. On your own images, it runs from the
IMPACT-Synth 3D Slicer extension or from the command line:

```bash
konfai-apps infer VBoussot/ImpactSynth:MR -i mr.nii.gz -o output/ --ensemble 5 --tta 2 --gpu 0
```

It estimates the body mask with ImpactSeg, resamples the image to 1 × 1 × 3 mm
and writes the synthetic CT in the geometry of the input.

The TorchScript SAM encoder used by the SAM metric (`SAM2.1_Small.pt`, 136 MB,
SHA-256 `10c2fb000e57fa4adcb5f1c23aa7dfe6f622e1f649643ceb7e43e8188f024899`) is
in the same Hugging Face repository; KonfAI's `SAM_Perceptual` fetches it
automatically. The encoders of the Reg metric (`TS/M291.pt`, `MRSeg/MRSeg.pt`)
are fetched by KonfAI from `VBoussot/impact-torchscript-models`.

The TotalSegmentator model used for the Dice is fetched by KonfAI from
`VBoussot/TotalSegmentator-KonfAI`, pinned to revision `0718569`.
