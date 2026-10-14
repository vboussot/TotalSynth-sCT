# Configurations

`evaluation/predictions/` holds one KonfAI evaluation configuration per kind of
metric (`image`: MAE, PSNR and SSIM; `seg`: Dice; `perceptual`: SAM and Reg;
`uncertainty`). `scripts/evaluate.py` fills in the source image and the encoder
of Reg, the dataset, the predictions folder, the patient list and the run name.

The inference configuration is the released one: each model folder fetched by
`scripts/download.py` holds its `Prediction.yml` (five folds, the original image
and two flips, 15 predictions per patient, averaged). `scripts/predict.py`
replaces its input stage, which estimates a body mask and resamples the image,
by the prepared pair: body mask and source image already on the CT grid.
