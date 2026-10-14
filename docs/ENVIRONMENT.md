# Environment

## Versions

The repository runs with the versions pinned in `requirements.txt`:

| Component | Version |
|---|---|
| Python | 3.12 |
| PyTorch | 2.7.1 (CUDA 12.8 wheels) |
| torchvision | 0.22.1 |
| KonfAI, konfai-apps | 1.8.7 |
| segmentation-models-pytorch | 0.4.0 |
| SimpleITK | 2.5.6 |
| NumPy | 2.5.2 |
| PyYAML | 6.0.3 |

The TotalSegmentator model behind the Dice is the KonfAI port
`VBoussot/TotalSegmentator-KonfAI`, revision `0718569`, fetched by KonfAI. The
released models are read at revision `b3c0592` of `VBoussot/ImpactSynth`.

## Hardware notes

Prediction and evaluation fit one 10 GB GPU; the durations given in
[REPRODUCE.md](REPRODUCE.md) are for an NVIDIA RTX 3080 with 78 GB of RAM. Keep
one prediction process on the GPU at a time.

## Installation notes

- Install a PyTorch build compatible with the local driver.
- Table extraction and repository tests need neither a GPU nor medical images.
