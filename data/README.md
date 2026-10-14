# Data layout

No medical images are in this repository. The held-out cases are prepared with
[RegistrationBias-sCT](https://github.com/vboussot/RegistrationBias-sCT) and
read from `data/processed/synthrad{year}/Task_{task}/{region}/{patient}` and
`data/processed/external/Task_1/CSIRO/{patient}`.

`splits/` holds, for each task, the held-out list of the dedicated model
(`Validation.txt`), shared by the dedicated and the unified models, and
the quick-check list (`Check.txt`). `task_1/MultimodalHC.txt` lists the MTBD
subjects of Table 6.

The layout and the preparation are detailed in `docs/DATA.md`.
